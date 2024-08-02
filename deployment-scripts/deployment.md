# Deployment Guide for Azure Static Website and Function Apps

This guide provides detailed steps to deploy an Azure Static Website along with associated Function Apps. The scripts provided in `variables.ps1` are configured to set up the required Azure resources. Follow these steps to ensure a successful deployment.

# Prerequisites

- Azure CLI installed
- PowerShell installed
- GitHub account with access token
- Azure subscription

# Variables.ps1 Configuration

Before running the deployment script, you need to rename `variables.dev.ps1` to `variables.ps1`. Then, populate the `variables.ps1` file with the appropriate values. Below is a detailed description of each variable and the expected value.

## Variables

1. **$subscriptionId**: Your Azure subscription ID.
   - Example: `12345678-1234-1234-1234-123456789abc`

2. **$resourceGroupName**: Name of the resource group where resources will be deployed.
   - Example: `myResourceGroup`

3. **$location**: Azure region where resources will be deployed.
   - Default: `uksouth`
   - Example: `eastus`

4. **$storageAccountName**: Name of the Azure Storage Account.
   - Must be between 3 and 24 characters, only lower-case letters and numbers.
   - Example: `mystorageaccount`

5. **$appServicePlanName**: Name of the App Service Plan.
   - Example: `myAppServicePlan`

6. **$functionAppNameUpload**: Name of the Function App for the upload service.
   - Example: `myFunctionAppUpload`

7. **$functionAppNameTranslate**: Name of the Function App for the translation service.
   - Example: `myFunctionAppTranslate`

8. **$functionAppNameWatermark**: Name of the Function App for the watermark service.
   - Example: `myFunctionAppWatermark`

9. **$storageContainerName**: Name of the Storage Container.
   - Example: `myStorageContainer`

10. **$translationSku**: SKU for the translation service.
    - Default: `S1`
    - Example: `S1`

### OpenAI Specific Variables

1. **$openAIServiceName**: Name of the OpenAI service.
   - Example: `az-openai-service-12345`
   
2. **$openAISku**: SKU for the OpenAI service.
   - Default: `S0`
   - Example: `S0`

3. **$chatCompletionsModelName**: Model name for chat completions.
   - Example: `gpt-3`

4. **$chatCompletionsDeploymentName**: Deployment name for chat completions.
   - Example: `gpt-3-deployment`

### Static Web App Variables

1. **$repositoryUrl**: URL of your GitHub repository for the static web app.
   - Example: `https://github.com/azureaidemos/azure-ai-translator-accelerators`

2. **$branchName**: Branch name of your GitHub repository.
   - Default: `main`
   - Example: `main`

3. **$webAppFolder**: Folder in the repository where the web app resides.
   - Example: `webapp`

4. **$accessToken**: Your GitHub access token.
   - Example: `ghp_1234567890abcdef1234567890abcdef12345678`

5. **$staticWebAppName**: Name of the Static Web App.
   - Example: `myStaticWebApp`

6. **$staticSitesRegion**: Azure region for the Static Web App.
   - Example: `eastus`

# Steps to Deploy

1. **Clone the Repository**
   - Clone your GitHub repository to your local machine.

   ```sh
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Configure Variables**
   - Open `variables.ps1` and fill in the values as described above.

3. **Run Deployment Script**
   - Open PowerShell and navigate to the directory containing your scripts.
   - Run the deployment script.

   ```sh
   .\deploy.ps1
   ```

4. **Verify Deployment**
   - Once the script has completed, verify the deployment by checking the Azure portal for the created resources.

5. **Access Static Website**
   - Navigate to the URL of your deployed Static Web App to ensure it is running correctly.

# Script Breakdown

## Variables.ps1

The `variables.ps1` script is designed to initialize and store all the variables needed for the deployment. It includes:
- Definitions for Azure resource names, locations, and configurations.
- Initialization of variables for the OpenAI service and Static Web App.
- A function to generate a random string for unique naming purposes.

## Deploy.ps1

This is the main deployment script that orchestrates the deployment process. Here’s what each section does:

1. **Loading Variables**:
   - The script starts by loading the `variables.ps1` file to get all the necessary configuration settings.

   ```powershell
   . .\variables.ps1
   ```

2. **Azure Login and Subscription Setup**:
   - The script logs into Azure and sets the subscription ID where the resources will be deployed.

   ```powershell
   az login
   az account set --subscription $subscriptionId
   ```

3. **Resource Group Creation**:
   - Creates a resource group to organize and manage the related resources.

   ```powershell
   az group create --name $resourceGroupName --location $location
   ```

4. **Storage Account Creation**:
   - Creates a storage account which will be used by the Function Apps.

   ```powershell
   az storage account create --name $storageAccountName --location $location --resource-group $resourceGroupName --sku Standard_LRS
   ```

5. **App Service Plan Creation**:
   - Sets up an App Service Plan to host the Function Apps.

   ```powershell
   az appservice plan create --name $appServicePlanName --resource-group $resourceGroupName --location $location --sku B1 --is-linux
   ```

6. **Function Apps Creation**:
   - Creates the Function Apps for upload, translate, and watermark services.

   ```powershell
   az functionapp create --name $functionAppNameUpload --storage-account $storageAccountName --resource-group $resourceGroupName --plan $appServicePlanName --runtime dotnet
   az functionapp create --name $functionAppNameTranslate --storage-account $storageAccountName --resource-group $resourceGroupName --plan $appServicePlanName --runtime dotnet
   ```

7. **Storage Container Creation**:
   - Creates a storage container within the storage account.

   ```powershell
   az storage container create --name $storageContainerName --account-name $storageAccountName
   ```

8. **OpenAI Service Creation**:
   - Creates the OpenAI service and sets up the required configurations.

   ```powershell
   az cognitiveservices account create --name $openAIServiceName --resource-group $resourceGroupName --kind OpenAI --sku $openAISku --location $location
   ```

9. **Static Web App Deployment**:
   - Deploys the static web app from the GitHub repository.

   ```powershell
   az staticwebapp create --name $staticWebAppName --resource-group $resourceGroupName --location $staticSitesRegion --source $repositoryUrl --branch $branchName --token $accessToken --app-location $webAppFolder
   ```

10. **Verify and Test**:
    - The final step involves verifying the deployment in the Azure portal and testing the deployed static web app and function apps.


11. **UPDATE document-translate-web Project**:
    - Under document-translate-web folder, `src/constants/apiConstants.js` you need to update the below variables
   ```js
   export const API_KEY = "API_KEY"; // Replace with your API key
   export const BASE_URL = "https://apim-name.azure-api.net/translation-service-function"; // Replace with your API Management URL
   ```
# Troubleshooting

- Ensure all variables in `variables.ps1` are correctly populated.
- Check the Azure portal for any deployment errors and logs.
- Verify that your GitHub access token has the required permissions.
