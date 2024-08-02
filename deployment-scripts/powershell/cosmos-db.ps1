# Cosmos DB with PostgreSQL API creation

function Create-CosmosDBPostgresCluster {
    param (
        [string]$resourceGroupName,
        [string]$location
    )
    
    Write-Log "Creating Cosmos DB Account with PostgreSQL API..."

    $uniqueString = $(Get-Random -Maximum 10000)
    $cosmosDbPostgresName = "translateservice$uniqueString"
    $cosmosDbUserName = "citus"
    $cosmosDbPassword = "UNkC!k5Li5MKpH" # Securely store and retrieve in production environments

    # Check if the cluster name is available
    Write-Log "Executing command: az cosmosdb postgres check-name-availability --name $cosmosDbPostgresName --type Microsoft.DBforPostgreSQL/serverGroupsv2"
    $nameAvailability = az cosmosdb postgres check-name-availability --name "$cosmosDbPostgresName" --type "Microsoft.DBforPostgreSQL/serverGroupsv2" | ConvertFrom-Json
    if (-not $nameAvailability.nameAvailable) {
        Handle-Error "The Cosmos DB PostgreSQL cluster name $cosmosDbPostgresName is not available. Reason: $($nameAvailability.message)"
    }

    # Create Cosmos DB for PostgreSQL cluster
    Write-Log "Executing command: az cosmosdb postgres cluster create --cluster-name $cosmosDbPostgresName --resource-group $resourceGroupName --location $location --administrator-login $cosmosDbUserName --administrator-login-password $cosmosDbPassword --enable-ha false --coordinator-server-edition GeneralPurpose --coordinator-storage-quota-in-mb 131072 --coordinator-v-cores 2 --enable-shards-on-coord true --node-count 0 --preferred-primary-zone 1"
    $createClusterResult = az cosmosdb postgres cluster create `
        --cluster-name "$cosmosDbPostgresName" `
        --resource-group "$resourceGroupName" `
        --location "$location" `
        --administrator-login "$cosmosDbUserName" `
        --administrator-login-password "$cosmosDbPassword" `
        --enable-ha false `
        --coordinator-server-edition "GeneralPurpose" `
        --coordinator-storage-quota-in-mb 131072 `
        --coordinator-v-cores 2 `
        --enable-shards-on-coord true `
        --node-count 0 `
        --preferred-primary-zone "1"

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create Cosmos DB PostgreSQL cluster."
    }

    # Allow Azure services to access the cluster
    Write-Log "Executing command: az cosmosdb postgres firewall-rule create --name AllowAllAzureIPs --cluster-name $cosmosDbPostgresName --resource-group $resourceGroupName --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0"
    $firewallResult = az cosmosdb postgres firewall-rule create `
        --name "AllowAllAzureIPs" `
        --cluster-name "$cosmosDbPostgresName" `
        --resource-group "$resourceGroupName" `
        --start-ip-address "0.0.0.0" `
        --end-ip-address "0.0.0.0"

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create firewall rule for Cosmos DB PostgreSQL cluster."
    }

    # Retrieve Cosmos DB for PostgreSQL connection details
    Write-Log "Executing command: az cosmosdb postgres cluster show --name $cosmosDbPostgresName --resource-group $resourceGroupName --query serverNames[0].fullyQualifiedDomainName --output tsv"
    $cosmosDbPostgresHost = az cosmosdb postgres cluster show `
        --name "$cosmosDbPostgresName" `
        --resource-group "$resourceGroupName" `
        --query "serverNames[0].fullyQualifiedDomainName" `
        --output tsv

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to retrieve Cosmos DB PostgreSQL connection details."
    }

    Write-Log "Cosmos DB PostgreSQL cluster created successfully."

    return @{
        Host = $cosmosDbPostgresHost
        DatabaseName = "citus" # Using the default database name
        UserName = $cosmosDbUserName
        Password = $cosmosDbPassword
    }
}
