# Main orchestration script

# Import required assemblies
Add-Type -AssemblyName System.Web

# Source other scripts
. .\variables.ps1
. .\logging.ps1
. .\resource-group.ps1
. .\storage.ps1
. .\cosmos-db.ps1
. .\openai.ps1
. .\translation.ps1
. .\function-apps.ps1
. .\static-web-app.ps1
. .\api-management.ps1

# Function to get the last successful step
function Get-LastStep {
    if (Test-Path -Path ".\state.txt") {
        return Get-Content -Path ".\state.txt" -Raw
    }
    return ""
}

# Function to save the current step
function Save-Step {
    param (
        [string]$step
    )
    Set-Content -Path ".\state.txt" -Value $step
}

# Main execution flow
try {
    Write-Log "Starting Azure AI Translator Accelerator deployment script..."
    
    $lastStep = Get-LastStep
    Write-Log "Last successful step: $lastStep"

    # Set Azure subscription
    Write-Log "Setting Azure subscription to $subscriptionId"
    Set-AzureSubscription -subscriptionId $subscriptionId
    Save-Step "Set-AzureSubscription"

    # Create or update resource group    
    Write-Log "Creating or updating resource group $resourceGroupName in location $location"
    $resourceGroup = Create-ResourceGroup -resourceGroupName $resourceGroupName -location $location
    Write-Log "Resource group created: $($resourceGroup | ConvertTo-Json -Depth 3)"
    Save-Step "Create-ResourceGroup"

    # Create storage account and container    
    Write-Log "Creating storage account $storageAccountName and container $storageContainerName in resource group $resourceGroupName"
    $storageDetails = Create-StorageResources -resourceGroupName $resourceGroupName -location $location -storageAccountName $storageAccountName -storageContainerName $storageContainerName
    Write-Log "Storage details: $($storageDetails | ConvertTo-Json -Depth 3)"
    Save-Step "Create-StorageResources"    

    # Deploy Static Web App
    Write-Log "Deploying Static Web App $staticWebAppName in resource group $resourceGroupName"
    Deploy-StaticWebApp -resourceGroupName $resourceGroupName -staticWebAppName $staticWebAppName -staticSitesRegion $staticSitesRegion -repositoryUrl $repositoryUrl -branchName $branchName -webAppFolder $webAppFolder -accessToken $accessToken
    Save-Step "Deploy-StaticWebApp"
   
    # Create Cosmos DB with PostgreSQL API
    Write-Log "Creating Cosmos DB with PostgreSQL API in resource group $resourceGroupName"
    $cosmosDbDetails = Create-CosmosDBPostgresCluster -resourceGroupName $resourceGroupName -location $location
    Write-Log "Cosmos DB details: $($cosmosDbDetails | ConvertTo-Json -Depth 3)"
    Save-Step "Create-CosmosDBPostgresCluster"

    # Create OpenAI service
    Write-Log "Creating OpenAI service $openAIServiceName in resource group $resourceGroupName"
    $openAIService = Create-OpenAIService -resourceGroupName $resourceGroupName -location $location -openAIServiceName $openAIServiceName -openAISku $openAISku -chatCompletionsModelName $chatCompletionsModelName -chatCompletionsDeploymentName $chatCompletionsDeploymentName
    Write-Log "OpenAI service details: $($openAIService | ConvertTo-Json -Depth 3)"
    Save-Step "Create-OpenAIService"
    
    # Create Translation service
    Write-Log "Creating Translation service in resource group $resourceGroupName"
    $translationService = Create-TranslationService -resourceGroupName $resourceGroupName -location $location -translationSku $translationSku -customDomainPrefix "ai-trans"
    Write-Log "Translation service details: $($translationService | ConvertTo-Json -Depth 3)"
    Save-Step "Create-TranslationService"

    # Deploy Function Apps    
    Write-Log "Deploying Function Apps in resource group $resourceGroupName"
    Deploy-FunctionApps -resourceGroupName $resourceGroupName -location $location -appServicePlanName $appServicePlanName -storageAccountName $storageAccountName -storageDetails $storageDetails -cosmosDbDetails $cosmosDbDetails -openAIService $openAIService -translationService $translationService
    Save-Step "Deploy-FunctionApps"

    $apimDetails = Create-APIManagement -resourceGroupName $resourceGroupName -location $location -functionAppName $functionAppNameUpload
    Write-Log "API Management created successfully."
    Write-Log "API Management Name: $($apimDetails.Name)"
    Write-Log "API Management URL: $($apimDetails.Url)"


    # Final summary
    Write-Summary -resourceGroup $resourceGroup -storageDetails $storageDetails -cosmosDbDetails $cosmosDbDetails -openAIService $openAIService -translationService $translationService
    Save-Step "Write-Summary"

    Write-Log "Azure AI Translator Accelerator deployment completed successfully."
    Remove-Item -Path ".\state.txt" # Remove state file after successful completion
}
catch {
    Handle-Error $_.Exception.Message
}
