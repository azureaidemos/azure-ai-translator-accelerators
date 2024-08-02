# Variables

# Function to generate a random 5-character string
function Get-RandomString {
    -join ((97..122) | Get-Random -Count 5 | ForEach-Object { [char]$_ })
}

$randomString = Get-RandomString

$subscriptionId = ""
$resourceGroupName = ""
$location = "uksouth"
$storageAccountName = "" # Must be between 3 and 24 characters, only lower-case letters and numbers
$appServicePlanName = ""
$functionAppNameUpload = ""
$functionAppNameTranslate = ""
$functionAppNameWatermark = ""
$storageContainerName = ""
$translationSku = "S1"

# OpenAI specific variables
$openAIServiceName = "az-openai-service-$((Get-Random -Maximum 99999).ToString('00000'))"
$openAISku = "S0"
$chatCompletionsModelName = ""
$chatCompletionsDeploymentName = ""

# Static Web App variables
$repositoryUrl = "" # Replace this with your GitHub repository URL for the static web app https://github.com/azureaidemos/azure-ai-translator-accelerators
$branchName = "main"
$webAppFolder = ""
$accessToken = "" # Replace this with your GitHub access token
$staticWebAppName = ""
$staticSitesRegion = "" # Adjust as needed
