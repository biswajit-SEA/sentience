# Azure Resource Creation Script

# This script creates all necessary Azure resources for the Churn Prediction System

# Variables
resourceGroupName="churn-prediction-rg"
location="eastus"  # Change to your preferred region
appServicePlanName="churn-prediction-plan"
webAppName="churn-prediction-app"  # This needs to be globally unique
storageAccountName="churnpredictionstorage"  # This needs to be globally unique
databaseServerName="churn-prediction-sql"  # This needs to be globally unique
databaseName="churndb"
redisName="churn-prediction-redis"
commServicesName="churn-prediction-comm"
appInsightsName="churn-prediction-insights"

# 1. Create Resource Group
echo "Creating Resource Group..."
az group create --name $resourceGroupName --location $location

# 2. Create App Service Plan
echo "Creating App Service Plan..."
az appservice plan create --name $appServicePlanName --resource-group $resourceGroupName --sku B1 --is-linux

# 3. Create Web App
echo "Creating Web App..."
az webapp create --resource-group $resourceGroupName --plan $appServicePlanName --name $webAppName --runtime "PYTHON:3.10"

# 4. Create Storage Account
echo "Creating Storage Account..."
az storage account create --name $storageAccountName --resource-group $resourceGroupName --location $location --sku Standard_LRS --kind StorageV2

# 5. Create Blob Container for uploads
echo "Creating Blob Container..."
az storage container create --name "uploads" --account-name $storageAccountName --auth-mode login

# 6. Create SQL Server
echo "Creating SQL Server..."
az sql server create --name $databaseServerName --resource-group $resourceGroupName --location $location --admin-user "sqladmin" --admin-password "P@ssw0rd1234"

# 7. Configure Firewall for SQL Server
echo "Configuring SQL Server Firewall..."
az sql server firewall-rule create --resource-group $resourceGroupName --server $databaseServerName --name "AllowAzureServices" --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# 8. Create SQL Database
echo "Creating SQL Database..."
az sql db create --resource-group $resourceGroupName --server $databaseServerName --name $databaseName --service-objective Basic

# 9. Create Redis Cache
echo "Creating Redis Cache..."
az redis create --name $redisName --resource-group $resourceGroupName --location $location --sku Basic --vm-size C0

# 10. Create Application Insights
echo "Creating Application Insights..."
az monitor app-insights component create --app $appInsightsName --location $location --resource-group $resourceGroupName --application-type web

# 11. Create Communication Services
echo "Creating Communication Services..."
az communication create --name $commServicesName --resource-group $resourceGroupName --data-location $location

# Print the outputs
echo "Azure resources created successfully!"
echo "Resource Group: $resourceGroupName"
echo "App Service: $webAppName"
echo "Storage Account: $storageAccountName"
echo "SQL Server: $databaseServerName"
echo "SQL Database: $databaseName"
echo "Redis Cache: $redisName"
echo "Application Insights: $appInsightsName"
echo "Communication Services: $commServicesName"

# Notes:
# 1. You'll need to change default passwords in a production environment
# 2. You may need to enable Email service in Communication Services manually
# 3. Save the connection strings for each service to use in your application
