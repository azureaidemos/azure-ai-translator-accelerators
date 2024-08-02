# Azure OpenAI service creation

function Create-OpenAIService {
    param (
        [string]$resourceGroupName,
        [string]$location,
        [string]$openAIServiceName,
        [string]$openAISku,
        [string]$chatCompletionsModelName,
        [string]$chatCompletionsDeploymentName
    )
    
    Write-Log "Creating Azure OpenAI service..."
    Write-Log "Service Name: $openAIServiceName"

    Write-Log "Executing command: az cognitiveservices account create --name $openAIServiceName --resource-group $resourceGroupName --kind OpenAI --sku $openAISku --location $location --yes"
    $createCommand = "az cognitiveservices account create " +
                     "--name $openAIServiceName " +
                     "--resource-group $resourceGroupName " +
                     "--kind OpenAI " +
                     "--sku $openAISku " +
                     "--location $location " +
                     "--yes"

    $result = Invoke-Expression $createCommand

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create Azure OpenAI service."
    }

    Write-Log "Azure OpenAI service created successfully."

    Write-Log "Executing command: az cognitiveservices account keys list --name $openAIServiceName --resource-group $resourceGroupName --query key1 --output tsv"
    $openAIKey = az cognitiveservices account keys list `
        --name $openAIServiceName `
        --resource-group $resourceGroupName `
        --query key1 `
        --output tsv

    Write-Log "Executing command: az cognitiveservices account show --name $openAIServiceName --resource-group $resourceGroupName --query properties.endpoint --output tsv"
    $openAIEndpoint = az cognitiveservices account show `
        --name $openAIServiceName `
        --resource-group $resourceGroupName `
        --query properties.endpoint `
        --output tsv

    # Deploy the chat completions model
    Write-Log "Executing command: az cognitiveservices account deployment create --name $openAIServiceName --resource-group $resourceGroupName --deployment-name $chatCompletionsDeploymentName --model-name $chatCompletionsModelName --model-version '0301' --model-format OpenAI --sku Standard --capacity 1"
    $deployCommand = "az cognitiveservices account deployment create " +
                     "--name $openAIServiceName " +
                     "--resource-group $resourceGroupName " +
                     "--deployment-name $chatCompletionsDeploymentName " +
                     "--model-name $chatCompletionsModelName " +
                     "--model-version '0301' " +
                     "--model-format OpenAI " +
                     "--sku Standard " +
                     "--capacity 1"

    $deployResult = Invoke-Expression $deployCommand

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to deploy chat completions model."
    }

    Write-Log "Chat completions model deployed successfully."

    return @{
        ServiceName = $openAIServiceName
        ApiKey = $openAIKey
        Endpoint = $openAIEndpoint
        ChatCompletionsDeploymentName = $chatCompletionsDeploymentName
    }
}
