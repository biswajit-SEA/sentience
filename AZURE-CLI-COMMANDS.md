# Azure CLI Quick Reference Guide

This guide provides the essential Azure CLI commands you'll need for deploying your Churn Prediction System to Azure.

## Authentication

```powershell
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set the active subscription
az account set --subscription "your-subscription-id"
```

## Resource Management

```powershell
# Create a resource group
az group create --name "churn-prediction-rg" --location "eastus"

# List resource groups
az group list --output table

# Delete a resource group (and all resources in it)
az group delete --name "churn-prediction-rg" --yes
```

## App Service

```powershell
# Create an App Service Plan
az appservice plan create --name "churn-prediction-plan" --resource-group "churn-prediction-rg" --sku "B1" --is-linux

# Create a Web App
az webapp create --name "churn-prediction-app" --resource-group "churn-prediction-rg" --plan "churn-prediction-plan" --runtime "PYTHON:3.10"

# Configure Web App settings
az webapp config appsettings set --name "churn-prediction-app" --resource-group "churn-prediction-rg" --settings "AZURE_STORAGE_CONNECTION_STRING=your-connection-string" "AZURE_SQL_CONNECTION_STRING=your-connection-string" "SECRET_KEY=your-secret-key"

# Deploy code to Web App
az webapp up --name "churn-prediction-app" --resource-group "churn-prediction-rg" --plan "churn-prediction-plan" --runtime "PYTHON:3.10"

# View Web App logs
az webapp log tail --name "churn-prediction-app" --resource-group "churn-prediction-rg"
```

## Storage Account

```powershell
# Create a Storage Account
az storage account create --name "churnpredictionstore" --resource-group "churn-prediction-rg" --location "eastus" --sku "Standard_LRS"

# Create a container
az storage container create --name "uploads" --account-name "churnpredictionstore" --auth-mode login

# Get Storage Account connection string
az storage account show-connection-string --name "churnpredictionstore" --resource-group "churn-prediction-rg"
```

## SQL Database

```powershell
# Create a SQL Server
az sql server create --name "churn-prediction-sql" --resource-group "churn-prediction-rg" --location "eastus" --admin-user "sqladmin" --admin-password "YourStrongPassword123!"

# Configure firewall rules
az sql server firewall-rule create --name "AllowAzureServices" --resource-group "churn-prediction-rg" --server "churn-prediction-sql" --start-ip-address "0.0.0.0" --end-ip-address "0.0.0.0"

# Create a SQL Database
az sql db create --name "churndb" --resource-group "churn-prediction-rg" --server "churn-prediction-sql" --service-objective "Basic"

# Get connection string
az sql db show-connection-string --name "churndb" --server "churn-prediction-sql" --client "ado.net"
```

## Application Insights

```powershell
# Create Application Insights
az monitor app-insights component create --app "churn-prediction-insights" --resource-group "churn-prediction-rg" --location "eastus" --application-type "web"

# Get instrumentation key
az monitor app-insights component show --app "churn-prediction-insights" --resource-group "churn-prediction-rg" --query "instrumentationKey"
```

## Communication Services

```powershell
# Create Communication Services
az communication create --name "churn-prediction-comm" --resource-group "churn-prediction-rg" --data-location "united-states"

# Get connection string (requires Azure portal)
```

## Common Tasks

```powershell
# Restart Web App
az webapp restart --name "churn-prediction-app" --resource-group "churn-prediction-rg"

# Scale up/down App Service Plan
az appservice plan update --name "churn-prediction-plan" --resource-group "churn-prediction-rg" --sku "P1V2"

# Create a deployment slot
az webapp deployment slot create --name "churn-prediction-app" --resource-group "churn-prediction-rg" --slot "staging"

# Swap deployment slots
az webapp deployment slot swap --name "churn-prediction-app" --resource-group "churn-prediction-rg" --slot "staging" --target-slot "production"
```

## Troubleshooting

```powershell
# Check Web App status
az webapp show --name "churn-prediction-app" --resource-group "churn-prediction-rg" --query "state"

# View detailed resource information
az resource show --resource-group "churn-prediction-rg" --name "churn-prediction-app" --resource-type "Microsoft.Web/sites" --query "properties"

# Get deployment logs
az webapp log download --name "churn-prediction-app" --resource-group "churn-prediction-rg"
```

Remember to replace placeholder values like "eastus" with the appropriate region for your deployment.
