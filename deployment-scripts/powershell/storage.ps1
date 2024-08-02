# Storage account and container creation

function Create-StorageResources {
    param (
        [string]$resourceGroupName,
        [string]$location,
        [string]$storageAccountName,
        [string]$storageContainerName
    )
    
    Write-Log "Executing command: az storage account create --name $storageAccountName --resource-group $resourceGroupName --location $location --sku Standard_LRS"
    az storage account create --name $storageAccountName --resource-group $resourceGroupName --location $location --sku Standard_LRS
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create Storage Account."
    }

    Write-Log "Executing command: az storage account show-connection-string --name $storageAccountName --resource-group $resourceGroupName --query connectionString --output tsv"
    $connectionString = az storage account show-connection-string --name $storageAccountName --resource-group $resourceGroupName --query connectionString --output tsv
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to retrieve storage account connection string."
    }

    Write-Log "Executing command: az storage container create --name $storageContainerName --account-name $storageAccountName"
    az storage container create --name $storageContainerName --account-name $storageAccountName
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create Storage Container."
    }

    Write-Log "Executing command: az storage account generate-sas --account-name $storageAccountName --permissions rwdlacupiytfx --services bqt --resource-types sco --expiry 2030-01-01 --https-only --output tsv"
    $sasToken = az storage account generate-sas `
        --account-name $storageAccountName `
        --permissions rwdlacupiytfx `
        --services bqt `
        --resource-types sco `
        --expiry 2030-01-01 `
        --https-only `
        --output tsv
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to generate SAS token."
    }

    return @{
        Name = $storageAccountName
        ConnectionString = $connectionString.Trim()
        SasToken = $sasToken.Trim()
        ContainerName = $storageContainerName
    }
}
