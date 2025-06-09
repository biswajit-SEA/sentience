# Visual Guide: Deploying to Azure Sandbox

This visual guide will walk you through the steps to deploy your Churn Prediction System to an Azure Sandbox environment.

## 1. Azure Portal Login

After logging in with your provided sandbox credentials, you'll see the Azure Portal dashboard:

![Azure Portal Dashboard](https://learn.microsoft.com/en-us/training/modules/create-linux-virtual-machine-in-azure/media/2-azure-portal-dashboard.png)

## 2. Create a Resource Group

1. Click on "Resource groups" in the left sidebar
2. Click "Create" button
3. Fill out the form:
   - Subscription: Select your sandbox subscription
   - Resource group name: `churn-prediction-rg`
   - Region: Select the closest region to you
4. Click "Review + create" and then "Create"

![Create Resource Group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/media/manage-resource-groups-portal/manage-resource-groups-add-group.png)

## 3. Create a Web App

1. Click "Create a resource" in the top left
2. Search for "Web App" and select it
3. Click "Create"
4. Fill out the form:
   - Subscription: Your sandbox subscription
   - Resource Group: `churn-prediction-rg`
   - Name: Choose a unique name like `churn-prediction-app-[yourname]`
   - Publish: Code
   - Runtime stack: Python 3.10
   - Operating System: Linux
   - Region: Choose the same region as your resource group
   - App Service Plan: Create new
     - Name: `churn-prediction-plan`
     - Pricing plan: Click "Change size" and select "Dev/Test" > "B1"
5. Click "Review + create" and then "Create"

![Create Web App](https://docs.microsoft.com/en-us/azure/app-service/media/app-service-web-get-started-python/create-web-app-resource.png)

## 4. Create a Storage Account

1. Click "Create a resource" 
2. Search for "Storage account" and select it
3. Click "Create"
4. Fill out the form:
   - Subscription: Your sandbox subscription
   - Resource Group: `churn-prediction-rg`
   - Storage account name: `churnprediction[uniqueid]`
   - Region: Same as resource group
   - Performance: Standard
   - Redundancy: Locally-redundant storage (LRS)
5. Click "Review + create" and then "Create"

![Create Storage Account](https://docs.microsoft.com/en-us/azure/storage/common/media/storage-quickstart-create-account/storage-quickstart-create-account-portal.png)

## 5. Create a SQL Database

1. Click "Create a resource"
2. Search for "SQL Database" and select it
3. Click "Create"
4. Fill out the form:
   - Subscription: Your sandbox subscription
   - Resource Group: `churn-prediction-rg`
   - Database name: `churndb`
   - Server: Create new
     - Server name: `churn-prediction-sql-[uniqueid]`
     - Location: Same as resource group
     - Authentication method: "Use SQL authentication"
     - Server admin login: Create a username
     - Password: Create a secure password
   - Want to use SQL elastic pool?: No
   - Compute + storage: Click "Configure database"
     - Service tier: Basic
5. Click "Review + create" and then "Create"

![Create SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/database/media/single-database-create-quickstart/create-database-s2.png)

## 6. Create a Communication Services Resource

1. Click "Create a resource"
2. Search for "Communication Services" and select it
3. Click "Create"
4. Fill out the form:
   - Subscription: Your sandbox subscription
   - Resource Group: `churn-prediction-rg`
   - Resource Name: `churn-prediction-comm`
   - Data location: Same region as resource group
5. Click "Review + create" and then "Create"

## 7. Create Application Insights

1. Click "Create a resource"
2. Search for "Application Insights" and select it
3. Click "Create"
4. Fill out the form:
   - Subscription: Your sandbox subscription
   - Resource Group: `churn-prediction-rg`
   - Name: `churn-prediction-insights`
   - Region: Same as resource group
   - Resource Mode: Workspace-based
5. Click "Review + create" and then "Create"

## 8. Get Connection Strings and Keys

### Storage Account Connection String:
1. Go to your storage account
2. In the left sidebar, under "Security + networking", click "Access keys"
3. Copy the "Connection string" for key1

### SQL Database Connection String:
1. Go to your SQL database
2. In the left sidebar, click "Connection strings"
3. Copy the "ADO.NET (SQL authentication)" connection string
4. Replace `{your_username}` and `{your_password}` with the values you created

### Communication Services Connection String:
1. Go to your Communication Services resource
2. In the left sidebar, under "Settings", click "Keys"
3. Copy the "Connection string"

### Application Insights Key:
1. Go to your Application Insights resource
2. In the left sidebar, under "Configure", click "Properties"
3. Copy the "Instrumentation Key"

## 9. Configure Web App Settings

1. Go to your Web App
2. In the left sidebar, under "Settings", click "Configuration"
3. Click "New application setting" to add each of these settings:
   - `AZURE_STORAGE_CONNECTION_STRING`: Paste your storage connection string
   - `AZURE_SQL_CONNECTION_STRING`: Paste your SQL connection string
   - `AZURE_COMMUNICATION_CONNECTION_STRING`: Paste your Communication Services connection string
   - `APPINSIGHTS_INSTRUMENTATIONKEY`: Paste your Application Insights key
   - `SECRET_KEY`: Generate a random string
   - `DEFAULT_FROM_EMAIL`: Set to `noreply@churnpredictionsystem.com`
   - `MAX_OTP_ATTEMPTS`: Set to `5`
   - `RATE_LIMIT_WINDOW_MINUTES`: Set to `15`
   - `MAX_OTP_REQUESTS_PER_EMAIL`: Set to `5`
   - `MAX_OTP_REQUESTS_PER_IP`: Set to `10`
   - `MAX_FAILED_VERIFICATIONS`: Set to `10`
4. Click "Save" at the top

![App Settings](https://docs.microsoft.com/en-us/azure/app-service/media/configure-common/application-settings.png)

## 10. Deploy Your Code to Azure

### Using Azure CLI (from your local machine):

1. Install the Azure CLI if you haven't already
2. Open a terminal/command prompt
3. Run the following commands:

```bash
# Login to Azure
az login

# Set the deployment source to local Git
az webapp deployment source config-local-git --name your-webapp-name --resource-group churn-prediction-rg

# Add Azure as a remote to your Git repository
git remote add azure <git-clone-url-from-previous-command>

# Push your code to Azure
git push azure main
```

### Using the Azure Portal (ZIP deployment):

1. Go to your Web App
2. In the left sidebar, under "Deployment", click "Deployment Center"
3. Choose "Local Git" and click "Continue"
4. Copy the Git Clone URI
5. Follow the instructions to push your code

## 11. Verify Your Deployment

1. Go to your Web App
2. Click the "Browse" button at the top to open your website
3. Your application should now be running on Azure!

## 12. Monitoring Your Application

1. Go to your Web App
2. In the left sidebar, under "Monitoring", click "Application Insights"
3. Here you can see performance metrics, failures, and usage patterns

## Troubleshooting

If your application isn't working correctly:

1. Check the logs:
   - Go to your Web App
   - In the left sidebar, under "Monitoring", click "Log stream"
   - Review the logs for errors

2. Verify your application settings:
   - Go to your Web App
   - In the left sidebar, under "Settings", click "Configuration"
   - Make sure all the connection strings and keys are correctly set

3. Check your database:
   - Go to your SQL Database
   - In the left sidebar, click "Query editor"
   - Sign in and check that your tables exist
