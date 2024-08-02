# Logging and error handling functions

function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] [$Level] $Message"
}

function Handle-Error {
    param (
        [string]$errorMessage
    )
    Write-Log "Error occurred: $errorMessage" -Level "ERROR"
    Write-Log "Current values:" -Level "ERROR"
    Write-Log "  Resource Group: $resourceGroupName" -Level "ERROR"
    Write-Log "  Storage Account: $storageAccountName" -Level "ERROR"
    Write-Log "  Function App (Upload): $functionAppNameUpload" -Level "ERROR"
    exit 1
}

function Write-Summary {
    param (
        $resourceGroup,
        $storageDetails,
        $cosmosDbDetails,
        $openAIService,
        $translationService
    )
    Write-Log "Summary of deployed resources:"
    Write-Log "  Resource Group: $($resourceGroup.Name)"
    Write-Log "  Storage Account: $($storageDetails.Name)"
    Write-Log "  App Service Plan: $appServicePlanName"
    Write-Log "  Upload Function App: $functionAppNameUpload"
    Write-Log "  Translate Function App: $functionAppNameTranslate"
    Write-Log "  Watermark Function App: $functionAppNameWatermark"
    Write-Log "  OpenAI Service: $($openAIService.ServiceName)"
    Write-Log "  Translation Service: $($translationService.ServiceName)"

    Write-Log "Important Information:"
    Write-Log "  OpenAI Endpoint: $($openAIService.Endpoint)"
    Write-Log "  OpenAI API Key: $($openAIService.ApiKey.Substring(0,5))..." # Only show first 5 characters for security
    Write-Log "  Translation Endpoint: $($translationService.DocumentTranslationEndpoint)"
    Write-Log "  Translation API Key: $($translationService.SubscriptionKey.Substring(0,5))..." # Only show first 5 characters for security
}
