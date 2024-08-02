# Variables

# Function to generate a random 5-character string
function Get-RandomString {
    -join ((97..122) | Get-Random -Count 5 | ForEach-Object { [char]$_ })
}

$randomString = Get-RandomString

$subscriptionId = "MCAPS-Hybrid-REQ-71989-2024-mm"
$resourceGroupName = "ai-translator-accelerator-rg-$randomString"
$location = "uksouth"
$storageAccountName = "azaitranslator$randomString" # Must be between 3 and 24 characters, only lower-case letters and numbers
$appServicePlanName = "azure-ai-translator-plan-$randomString"
$functionAppNameUpload = "ai-translator-upload-func-$randomString"
$functionAppNameTranslate = "ai-translator-translate-func-$randomString"
$functionAppNameWatermark = "ai-translator-watermark-func-$randomString"
$storageContainerName = "documents-$randomString"
$translationSku = "S1"

# OpenAI specific variables
$openAIServiceName = "az-openai-service-$((Get-Random -Maximum 99999).ToString('00000'))"
$openAISku = "S0"
$chatCompletionsModelName = "gpt-35-turbo"
$chatCompletionsDeploymentName = "az-chat-$randomString"

# Static Web App variables
$repositoryUrl = "https://github.com/azureaidemos/azure-ai-translator-accelerators"
$branchName = "main"
$webAppFolder = "document-translate-web"
$accessToken = "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" # Replace this with your GitHub access token
$staticWebAppName = "ai-translator-static-webapp-$randomString"
$staticSitesRegion = "westeurope" # Adjust as needed


