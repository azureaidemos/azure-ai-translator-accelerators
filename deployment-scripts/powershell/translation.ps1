# Azure AI Translation service creation

function Create-TranslationService {
    param (
        [string]$resourceGroupName,
        [string]$location,
        [string]$translationSku,
        [string]$customDomainPrefix = ""
    )
    
    $randomString = -join ((65..90) + (97..122) | Get-Random -Count 5 | ForEach-Object { [char]$_ })
    $translationServiceName = "ai-trans-service-$randomString"
    $customDomain = if ($customDomainPrefix) { "$customDomainPrefix-$randomString" } else { "ai-translator-$randomString" }

    Write-Log "Creating Azure AI Translation service..."
    Write-Log "Service Name: $translationServiceName"
    Write-Log "Custom Domain: $customDomain"

    Write-Log "Executing command: az cognitiveservices account create --name $translationServiceName --resource-group $resourceGroupName --kind TextTranslation --sku $translationSku --location $location --custom-domain $customDomain --yes"
    $createCommand = "az cognitiveservices account create " +
                     "--name $translationServiceName " +
                     "--resource-group $resourceGroupName " +
                     "--kind TextTranslation " +
                     "--sku $translationSku " +
                     "--location $location " +
                     "--custom-domain $customDomain " +
                     "--yes"

    $result = Invoke-Expression $createCommand

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create Azure AI Translation service."
    }

    Write-Log "Azure AI Translation service created successfully."

    Write-Log "Executing command: az cognitiveservices account keys list --name $translationServiceName --resource-group $resourceGroupName --query key1 --output tsv"
    $subscriptionKey = az cognitiveservices account keys list `
        --name $translationServiceName `
        --resource-group $resourceGroupName `
        --query key1 `
        --output tsv

    Write-Log "Executing command: az cognitiveservices account show --name $translationServiceName --resource-group $resourceGroupName --query properties.endpoints --output json"
    $accountInfo = az cognitiveservices account show `
        --name $translationServiceName `
        --resource-group $resourceGroupName `
        --query properties.endpoints `
        --output json | ConvertFrom-Json

    $documentTranslationEndpoint = $accountInfo.DocumentTranslation

    return @{
        ServiceName = $translationServiceName
        SubscriptionKey = $subscriptionKey
        DocumentTranslationEndpoint = $documentTranslationEndpoint
        CustomDomain = $customDomain
    }
}
