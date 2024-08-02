# Function apps deployment

function Set-FunctionAppSettings {
    param (
        [string]$functionAppName,
        [string]$resourceGroupName,
        [hashtable]$settings
    )
    
    Write-Log "Setting app settings for $functionAppName..."
    
    foreach ($key in $settings.Keys) {
        $value = $settings[$key]
        
        # Special handling for SAS_TOKEN
        if ($key -eq "SAS_TOKEN") {
            # URL encode the SAS token to handle special characters
            $value = [System.Web.HttpUtility]::UrlEncode($value)
        }
        
        $value = $value -replace '"', '\"'  # Escape double quotes
        
        Write-Log "Executing command: az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroupName --settings $key=$value"
        $command = "az functionapp config appsettings set --name `"$functionAppName`" --resource-group `"$resourceGroupName`" --settings `"$key=$value`""
        $result = Invoke-Expression $command
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to set $key. Error: $result" -Level "ERROR"
            return
        }
    }
    
    Write-Log "Successfully set all app settings for $functionAppName."
}

function Create-Or-Update-FunctionApp {
    param (
        [string]$functionAppName,
        [string]$runtime,
        [string]$resourceGroupName,
        [string]$appServicePlanName,
        [string]$storageAccountName
    )

    # Check if Function App exists
    Write-Log "Executing command: az functionapp show --name $functionAppName --resource-group $resourceGroupName --query name --output tsv"
    $functionAppExists = az functionapp show --name $functionAppName --resource-group $resourceGroupName --query "name" --output tsv 2>$null
    
    if ($functionAppExists) {
        Write-Log "Function App $functionAppName already exists. Updating configuration..."
        
        Write-Log "Executing command: az functionapp config set --name $functionAppName --resource-group $resourceGroupName --linux-fx-version $runtime|3.11"
        az functionapp config set `
            --name $functionAppName `
            --resource-group $resourceGroupName `
            --linux-fx-version "$runtime|3.11"
        
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to update configuration of existing Function App $functionAppName."
        }
    } else {
        # Create the Function App
        Write-Log "Creating Function App $functionAppName..."
        Write-Log "Executing command: az functionapp create --resource-group $resourceGroupName --plan $appServicePlanName --name $functionAppName --storage-account $storageAccountName --runtime $runtime --runtime-version 3.11 --os-type Linux --functions-version 4"
        az functionapp create `
            --resource-group $resourceGroupName `
            --plan $appServicePlanName `
            --name $functionAppName `
            --storage-account $storageAccountName `
            --runtime $runtime `
            --runtime-version 3.11 `
            --os-type Linux `
            --functions-version 4
        
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to create Function App $functionAppName."
        }
    }
}

function Deploy-FunctionAppCode {
    param (
        [string]$functionAppName,
        [string]$sourceZip,
        [string]$resourceGroupName
    )

    # Deploy the zipped function app code
    Write-Log "Executing command: az functionapp deployment source config-zip --name $functionAppName --resource-group $resourceGroupName --src $sourceZip"
    $deployResult = az functionapp deployment source config-zip `
        --name $functionAppName `
        --resource-group $resourceGroupName `
        --src $sourceZip `
        --query "{status: provisioningState, url: deploymentLocalGitUrl}" `
        --output json | ConvertFrom-Json
    
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to deploy code for Function App $functionAppName."
    }

    if ($deployResult.status -eq $null -and $deployResult.url -eq $null) {
        Handle-Error "Deployment returned null status and url. This could indicate a failure."
    }

    Write-Log "Azure Function App $functionAppName deployed. Deployment details:"
    Write-Log ($deployResult | ConvertTo-Json -Depth 3)
}

function Deploy-FunctionApps {
    param (
        [string]$resourceGroupName,
        [string]$location,
        [string]$appServicePlanName,
        [string]$storageAccountName,
        $storageDetails,
        $cosmosDbDetails,
        $openAIService,
        $translationService
    )

    # Create the App Service Plan
    Write-Log "Creating App Service Plan..."
    Write-Log "Executing command: az appservice plan show --name $appServicePlanName --resource-group $resourceGroupName --query name --output tsv"
    $appServicePlanExists = az appservice plan show --name $appServicePlanName --resource-group $resourceGroupName --query "name" --output tsv 2>$null
    if (-not $appServicePlanExists) {
        Write-Log "Creating App Service Plan..."
        Write-Log "Executing command: az appservice plan create --name $appServicePlanName --resource-group $resourceGroupName --location $location --sku S1 --is-linux"
        az appservice plan create `
            --name $appServicePlanName `
            --resource-group $resourceGroupName `
            --location $location `
            --sku S1 `
            --is-linux
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to create App Service Plan."
        }
    }

    # Zip the function app code
    Write-Log "Zipping function app code..."
    Compress-Archive -Path "../../document-upload-function/*" -DestinationPath "document-upload-function.zip" -Force
    Compress-Archive -Path "../../document-translate-function/*" -DestinationPath "document-translate-function.zip" -Force

    # Prepare config settings
    $configSettings = @{
        "DB_HOST" = $cosmosDbDetails.Host
        "DB_PORT" = 5432
        "DB_NAME" = $cosmosDbDetails.DatabaseName
        "DB_USER" = $cosmosDbDetails.UserName
        "DB_PASSWORD" = $cosmosDbDetails.Password
        "DB_SSLMODE" = "require"
        "AZURE_CONNECTION_STRING" = $storageDetails.ConnectionString
        "SAS_TOKEN" = $storageDetails.SasToken
        "CONTAINER_NAME" = $storageDetails.ContainerName
        "AZURE_STORAGE_ACCOUNT" = $storageDetails.Name
    }

    # Deploy Upload Function (without translation settings)
    Write-Log "Deploying Upload Function..."
    Create-Or-Update-FunctionApp -functionAppName $functionAppNameUpload -runtime "python" -resourceGroupName $resourceGroupName -appServicePlanName $appServicePlanName -storageAccountName $storageAccountName
    Set-FunctionAppSettings -functionAppName $functionAppNameUpload -resourceGroupName $resourceGroupName -settings $configSettings
    Deploy-FunctionAppCode -functionAppName $functionAppNameUpload -sourceZip "document-upload-function.zip" -resourceGroupName $resourceGroupName

    # Deploy Translate Function (with translation and OpenAI settings)
    Write-Log "Deploying Translate Function..."
    $translateSettings = @{
        "TRANSLATE_SERVICE_NAME" = $translationService.ServiceName
        "TRANSLATE_SUBSCRIPTION_KEY" = $translationService.SubscriptionKey
        "TRANSLATE_DOCUMENT_ENDPOINT" = $translationService.DocumentTranslationEndpoint
        "TRANSLATE_CUSTOM_DOMAIN" = $translationService.CustomDomain
        "OPEN_AI_API_KEY" = $openAIService.ApiKey
        "AZURE_OPENAI_ENDPOINT" = $openAIService.Endpoint
        "CHAT_COMPLETIONS_DEPLOYMENT_NAME" = $openAIService.ChatCompletionsDeploymentName
    }
    $mergedTranslateSettings = $configSettings.Clone()
    foreach ($key in $translateSettings.Keys) {
        $mergedTranslateSettings[$key] = $translateSettings[$key]
    }
    Create-Or-Update-FunctionApp -functionAppName $functionAppNameTranslate -runtime "python" -resourceGroupName $resourceGroupName -appServicePlanName $appServicePlanName -storageAccountName $storageAccountName
    Set-FunctionAppSettings -functionAppName $functionAppNameTranslate -resourceGroupName $resourceGroupName -settings $mergedTranslateSettings
    Deploy-FunctionAppCode -functionAppName $functionAppNameTranslate -sourceZip "document-translate-function.zip" -resourceGroupName $resourceGroupName

    # # Deploy Watermark Function (without translation settings)
    # Write-Log "Deploying Watermark Function..."
    # Create-Or-Update-FunctionApp -functionAppName $functionAppNameWatermark -runtime "dotnet" -resourceGroupName $resourceGroupName -appServicePlanName $appServicePlanName -storageAccountName $storageAccountName
    # Set-FunctionAppSettings -functionAppName $functionAppNameWatermark -resourceGroupName $resourceGroupName -settings $configSettings
    # Deploy-FunctionAppCode -functionAppName $functionAppNameWatermark -sourceZip "document-watermark-function/watermark-function-package.zip" -resourceGroupName $resourceGroupName
}
