# api-management.ps1

# Helper function for logging
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] [$Level] $Message"
}

# Helper function for error handling
function Handle-Error {
    param (
        [string]$ErrorMessage
    )
    Write-Log $ErrorMessage -Level "ERROR"
    throw $ErrorMessage
}

function Create-APIManagement {
    param (
        [string]$resourceGroupName,
        [string]$location,
        [string]$functionAppName
    )

    Write-Log "Creating API Management instance..."
    Write-Log "Resource Group: $resourceGroupName"
    Write-Log "Location: $location"
    Write-Log "Function App Name: $functionAppName"

    Write-Log "Creating API Management instance..."
    $uniqueString = $(Get-Random -Maximum 10000)
    $apimName = "translator-apim-$uniqueString"
    $publisherName = "Your Company Name"
    $publisherEmail = "admin@example.com"
    $apimSku = "Developer"

    # Check if the API Management name is available
    Write-Log "Executing command: az apim check-name --name $apimName"
    $nameAvailability = az apim check-name --name $apimName | ConvertFrom-Json
    if (-not $nameAvailability.nameAvailable) {
        Handle-Error "The API Management name $apimName is not available. Reason: $($nameAvailability.message)"
    }

    # Create API Management instance
    Write-Log "Executing command: az apim create --name $apimName --resource-group $resourceGroupName --publisher-name $publisherName --publisher-email $publisherEmail --sku-name $apimSku --location $location"
    $createApimResult = az apim create `
        --name $apimName `
        --resource-group $resourceGroupName `
        --publisher-name $publisherName `
        --publisher-email $publisherEmail `
        --sku-name $apimSku `
        --location $location

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create API Management instance."
    }

    # Get Function App host key
    Write-Log "Executing command: az functionapp keys list --name $functionAppName --resource-group $resourceGroupName --query functionKeys.default --output tsv"
    $functionAppKey = az functionapp keys list `
        --name $functionAppName `
        --resource-group $resourceGroupName `
        --query functionKeys.default `
        --output tsv

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to retrieve Function App host key."
    }

    # Get Function App URL
    Write-Log "Executing command: az functionapp show --name $functionAppName --resource-group $resourceGroupName --query defaultHostName --output tsv"
    $functionAppUrl = az functionapp show `
        --name $functionAppName `
        --resource-group $resourceGroupName `
        --query defaultHostName `
        --output tsv

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to retrieve Function App URL."
    }

    # Create API
    Write-Log "Executing command: az apim api create --resource-group $resourceGroupName --service-name $apimName --api-id translation-service-upload-function --display-name 'Translation Service Upload Function' --path translation-service-upload-function --protocols https --subscription-required true"
    $createApiResult = az apim api create `
        --resource-group $resourceGroupName `
        --service-name $apimName `
        --api-id "translation-service-upload-function" `
        --display-name "Translation Service Upload Function" `
        --path "translation-service-upload-function" `
        --protocols "https" `
        --subscription-required true

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create API in API Management."
    }
    else {
        Write-Log "API created successfully in API Management."
    }
    $apiDetails = $createApiResult | ConvertFrom-Json
    Write-Log "Created API with ID: $($apiDetails.name) and Display Name: $($apiDetails.displayName)"
    $apiId = $apiDetails.name

    # Import API specification
    Write-Log "Importing API specification..."
    $apiSpecification = @"
    {
        "openapi": "3.0.1",
        "info": {
            "title": "translation-service-upload-function",
            "description": "Import from \"translation-service-upload-function\" Function App",
            "version": "1.0"
        },
        "servers": [
            {
                "url": "https://$apimName.azure-api.net/translation-service-upload-function"
            }
        ],
        "paths": {
            "/upload_file": {
                "post": {
                    "summary": "upload_file",
                    "operationId": "post-upload-file",
                    "responses": {
                        "200": {
                            "description": null
                        }
                    }
                }
            },
            "/get_logs_by_date": {
                "get": {
                    "summary": "get_logs_by_date",
                    "description": "get_logs_by_date",
                    "operationId": "get-logs-by-dateget_logs_by_date",
                    "responses": {
                        "200": {
                            "description": null
                        }
                    }
                }
            },
            "/get_all_logs": {
                "get": {
                    "summary": "get_all_logs",
                    "description": "get_all_logs",
                    "operationId": "get_all_logs",
                    "responses": {
                        "200": {
                            "description": null
                        }
                    }
                }
            },
            "/get_all_prompts": {
                "get": {
                    "summary": "get_all_prompts",
                    "description": "get_all_prompts",
                    "operationId": "6696505c3adc542f15a8e74d",
                    "responses": {
                        "200": {
                            "description": null
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "apiKeyHeader": {
                    "type": "apiKey",
                    "name": "Ocp-Apim-Subscription-Key",
                    "in": "header"
                },
                "apiKeyQuery": {
                    "type": "apiKey",
                    "name": "subscription-key",
                    "in": "query"
                }
            }
        },
        "security": [
            {
                "apiKeyHeader": []
            },
            {
                "apiKeyQuery": []
            }
        ]
    }
"@

    $apiSpecification | Out-File -FilePath "api-spec.json" -Encoding UTF8

    Write-Log "Executing command: az apim api import --resource-group $resourceGroupName --service-name $apimName --path translation-service-upload-function --specification-format OpenApiJson --specification-path api-spec.json"
    $importApiResult = az apim api import `
        --resource-group $resourceGroupName `
        --service-name $apimName `
        --path "translation-service-upload-function" `
        --specification-format OpenApiJson `
        --specification-path "api-spec.json"


    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to import API specification."
    }

    # Set backend for the API
    Write-Log "Executing command: az apim api update --resource-group $resourceGroupName --service-name $apimName --api-id translation-service-upload-function --service-url https://$functionAppUrl/api"
    $updateApiResult = az apim api update `
        --resource-group $resourceGroupName `
        --service-name $apimName `
        --api-id "translation-service-upload-function" `
        --service-url "https://$functionAppUrl/api"

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set backend for the API."
    }

    # Create backend for the Function App
    Write-Log "Creating backend for the Function App..."
    $backendName = "function-upload"
    $backendUrl = "https://$functionAppUrl/api"

    Write-Log "Executing command: az apim backend create --resource-group $resourceGroupName --service-name $apimName --backend-id $backendName --url $backendUrl --protocol http"
    $createBackendResult = az apim backend create `
        --resource-group $resourceGroupName `
        --service-name $apimName `
        --backend-id $backendName `
        --url $backendUrl `
        --protocol http

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create backend for the Function App."
    }

    # Add backend authentication and CORS policy
    $policyXml = @"
<policies>
    <inbound>
        <base />
        <set-backend-service id="apim-generated-policy" backend-id="function-upload" />
        <cors allow-credentials="false">
            <allowed-origins>
                <origin>*</origin>
            </allowed-origins>
            <allowed-methods>
                <method>GET</method>
                <method>POST</method>
            </allowed-methods>
        </cors>
        <set-header name='x-functions-key' exists-action='override'>
            <value>$functionAppKey</value>
        </set-header>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
"@

    $policyXml | Out-File -FilePath "api-policy.xml" -Encoding UTF8

    Write-Log "Executing command: az apim api policy set --resource-group $resourceGroupName --service-name $apimName --api-id translation-service-upload-function --value api-policy.xml"
    $setPolicyResult = az apim api policy set `
        --resource-group $resourceGroupName `
        --service-name $apimName `
        --api-id "translation-service-upload-function" `
        --value "@api-policy.xml"

    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set API policy."
    }

    Write-Log "API Management setup complete."
    return @{
        Name = $apimName
        Url = "https://$apimName.azure-api.net"
    }
}