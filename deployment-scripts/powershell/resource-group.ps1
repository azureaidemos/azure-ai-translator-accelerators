# Resource group creation

function Create-ResourceGroup {
    param (
        [string]$resourceGroupName,
        [string]$location
    )
    
    Write-Log "Executing command: az group create --name $resourceGroupName --location $location"
    $resourceGroup = az group create --name $resourceGroupName --location $location | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create resource group."
    }
    return $resourceGroup
}

function Set-AzureSubscription {
    param (
        [string]$subscriptionId
    )
    
    Write-Log "Executing command: az account set --subscription $subscriptionId"
    az account set --subscription $subscriptionId
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set Azure subscription."
    }
}
