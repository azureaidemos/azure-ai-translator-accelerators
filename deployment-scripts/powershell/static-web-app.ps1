# Static Web App deployment
function Deploy-StaticWebApp {
    param (
        [string]$resourceGroupName,
        [string]$staticWebAppName,
        [string]$staticSitesRegion,
        [string]$repositoryUrl,
        [string]$branchName,
        [string]$webAppFolder,
        [string]$accessToken
    )
    
    Write-Log "Deploying Static Web App..."

    # Check if Static Web App is available in the deployment region
    # Write-Log "Executing command: az provider show --namespace Microsoft.Web --query resourceTypes[?resourceType=='staticSites'].locations[] --output tsv"
    # $availableRegions = az provider show --namespace Microsoft.Web --query "resourceTypes[?resourceType=='staticSites'].locations[]" --output tsv

    # if ($availableRegions -notcontains $staticSitesRegion) {
        # Write-Log "Static Web App is not available in the specified region: $staticSitesRegion. Available regions are: $availableRegions" -Level "ERROR"
        # Provide fallback logic here or choose a different region
        # For demonstration, let's use the first available region as fallback
        # $fallbackRegion = $availableRegions[0]
        # Write-Log "Falling back to region: $fallbackRegion"
        # $staticSitesRegion = $fallbackRegion
    # }

    # Check if Static Web App exists
    Write-Log "Executing command: az staticwebapp show --name $staticWebAppName --resource-group $resourceGroupName --query name --output tsv"
    $webAppExists = az staticwebapp show --name $staticWebAppName --resource-group $resourceGroupName --query "name" --output tsv 2>$null
    if ($webAppExists) {
        Write-Log "Static Web App $staticWebAppName exists. Deleting..."
        Write-Log "Executing command: az staticwebapp delete --name $staticWebAppName --resource-group $resourceGroupName --yes"
        az staticwebapp delete --name $staticWebAppName --resource-group $resourceGroupName --yes
        Write-Log "Deleted existing Static Web App $staticWebAppName."
    }

    # Create Azure Static Web App with Standard hosting plan
    Write-Log "Creating new Static Web App $staticWebAppName..."
    Write-Log "Executing command: az staticwebapp create --name $staticWebAppName --resource-group $resourceGroupName --location $staticSitesRegion --sku Standard --source $repositoryUrl --branch $branchName --app-location $webAppFolder --output-location build --token $accessToken"
    $createResult = az staticwebapp create `
        --name $staticWebAppName `
        --resource-group $resourceGroupName `
        --location $staticSitesRegion `
        --sku Standard `
        --source $repositoryUrl `
        --branch $branchName `
        --app-location $webAppFolder `
        --output-location "build" `
        --token $accessToken

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create Static Web App $staticWebAppName."
    }

    Write-Log "Static Web App deployment completed. Resource Group: $resourceGroupName"
    Write-Log "GitHub Actions integration completed for Static Web App: $staticWebAppName"
}