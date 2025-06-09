# Deploying to Azure Sandbox: Step-by-Step Guide

This guide will walk you through deploying your Churn Prediction System to the Azure Sandbox environment provided for your hackathon.

## Prerequisites

- Access to the Azure Sandbox environment
- The login credentials provided by the hackathon team
- Your project code ready for deployment

## Step 1: Log into the Azure Portal

1. Open your browser and navigate to [Azure Portal](https://portal.azure.com)
2. Log in using the sandbox-specific email and password provided by the hackathon team
3. You should now see the Azure dashboard

## Step 2: Create a Resource Group

Resource groups help you organize related Azure resources.

1. In the Azure Portal, click on "Resource groups" in the left sidebar
2. Click the "+ Create" button
3. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource group name**: `churn-prediction-rg`
   - **Region**: Select a region close to you (e.g., East US, West Europe)
4. Click "Review + create" and then "Create"

## Step 3: Create an App Service Plan

The App Service Plan defines the computing resources for your web app.

1. In the Azure Portal, click "Create a resource"
2. Search for "App Service Plan" and select it
3. Click "Create"
4. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource Group**: Select `churn-prediction-rg`
   - **Name**: `churn-prediction-plan`
   - **Operating System**: Linux
   - **Region**: Same as your resource group
   - **Pricing Tier**: Click "Change size" and select "B1" under the Dev/Test tab
5. Click "Review + create" and then "Create"

## Step 4: Create a Web App

1. In the Azure Portal, click "Create a resource"
2. Search for "Web App" and select it
3. Click "Create"
4. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource Group**: Select `churn-prediction-rg`
   - **Name**: `churn-prediction-app` (must be globally unique, add a suffix if needed)
   - **Publish**: Code
   - **Runtime stack**: Python 3.10
   - **Operating System**: Linux
   - **Region**: Same as your resource group
   - **Linux Plan**: Select the `churn-prediction-plan` you created
5. Click "Next: Deployment" and enable GitHub Actions (optional)
6. Click "Review + create" and then "Create"

## Step 5: Create a Storage Account for File Uploads

1. In the Azure Portal, click "Create a resource"
2. Search for "Storage account" and select it
3. Click "Create"
4. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource Group**: Select `churn-prediction-rg`
   - **Storage account name**: `churnpredictionstore` (must be globally unique, add a suffix if needed)
   - **Region**: Same as your resource group
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)
5. Click "Review + create" and then "Create"
6. After creation, navigate to your storage account
7. In the left sidebar, click "Containers"
8. Click "+ Container"
9. Name it "uploads" and set Public access level to "Private"
10. Click "Create"

## Step 6: Create a SQL Database

1. In the Azure Portal, click "Create a resource"
2. Search for "SQL Database" and select it
3. Click "Create"
4. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource Group**: Select `churn-prediction-rg`
   - **Database name**: `churndb`
   - **Server**: Create new
     - **Server name**: `churn-prediction-sql` (must be globally unique, add a suffix if needed)
     - **Location**: Same as your resource group
     - **Authentication method**: Use SQL authentication
     - **Server admin login**: Create a username (e.g., `sqladmin`)
     - **Password**: Create a secure password and note it down
   - **Want to use SQL elastic pool?**: No
   - **Compute + storage**: Click "Configure database" and select "Basic"
5. Click "Review + create" and then "Create"
6. After creation, navigate to your SQL server
7. In the left sidebar, click "Networking"
8. Under "Firewall rules", enable "Allow Azure services and resources to access this server"
9. Click "Save"

## Step 7: Create Communication Services for Email

1. In the Azure Portal, click "Create a resource"
2. Search for "Communication Services" and select it
3. Click "Create"
4. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource Group**: Select `churn-prediction-rg`
   - **Resource Name**: `churn-prediction-comm`
   - **Data location**: Same as your resource group
5. Click "Review + create" and then "Create"

## Step 8: Create Application Insights for Monitoring

1. In the Azure Portal, click "Create a resource"
2. Search for "Application Insights" and select it
3. Click "Create"
4. Fill out the form:
   - **Subscription**: Select the sandbox subscription
   - **Resource Group**: Select `churn-prediction-rg`
   - **Name**: `churn-prediction-insights`
   - **Region**: Same as your resource group
   - **Resource Mode**: Classic
5. Click "Review + create" and then "Create"

## Step 9: Get Connection Strings and Keys

Now, you need to collect all the connection strings and keys for your application:

### Storage Account Connection String:
1. Go to your storage account
2. In the left sidebar, click "Access keys"
3. Copy the "Connection string" value for key1

### SQL Database Connection String:
1. Go to your SQL database
2. In the left sidebar, click "Connection strings"
3. Copy the "ADO.NET (SQL authentication)" connection string
4. Replace `{your_username}` and `{your_password}` with the actual values

### Communication Services Connection String:
1. Go to your Communication Services resource
2. In the left sidebar, click "Keys"
3. Copy the "Connection string" value

### Application Insights Instrumentation Key:
1. Go to your Application Insights resource
2. In the left sidebar, click "Properties"
3. Copy the "Instrumentation Key" value

## Step 10: Configure Your Application

1. Open the `.env.azure` file in your project
2. Fill in all the connection strings and keys you collected
3. Save the file

## Step 11: Prepare Your Application for Deployment

1. Make sure all the Azure integration files have been added to your project:
   - `azure_integration.py`
   - `email_azure.py`
   - `file_operations_azure.py`
   - `app_azure.py`
   - `.deployment`
   - `startup.txt`
   - Updated `requirements.txt`

2. Rename `.env.azure` to `.env`

## Step 12: Deploy to Azure Web App

### Option 1: Using Azure CLI (Recommended)

1. Install the Azure CLI if you haven't already
2. Open PowerShell and run the following commands:

```powershell
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "your-sandbox-subscription-id"

# Deploy the application
cd "d:\Dev\hackathon\techm-hackathon"
az webapp up --name "churn-prediction-app" --resource-group "churn-prediction-rg" --plan "churn-prediction-plan" --runtime "PYTHON:3.10"
```

### Option 2: Using the Azure Portal

1. In the Azure Portal, go to your Web App
2. In the left sidebar, click "Deployment Center"
3. Choose "External Git" or "GitHub" as the source (instead of "Local Git")
   - For External Git: Provide your public repository URL
   - For GitHub: Connect your GitHub account and select the repository
4. Configure the branch to deploy (usually "main" or "master")
5. Review and complete the deployment setup:

```powershell
# No need to add a git remote as deployment will happen automatically from your configured source
```

6. Your code will be automatically deployed when you push to the configured branch

## Step 13: Configure Web App Settings

1. In the Azure Portal, go to your Web App
2. In the left sidebar, click "Configuration"
3. Under "Application settings", click "+ New application setting" to add each of these:
   - `AZURE_STORAGE_CONNECTION_STRING`: Your storage account connection string
   - `AZURE_SQL_CONNECTION_STRING`: Your SQL database connection string
   - `AZURE_COMMUNICATION_CONNECTION_STRING`: Your Communication Services connection string
   - `APPINSIGHTS_INSTRUMENTATIONKEY`: Your Application Insights instrumentation key
   - `SECRET_KEY`: A random string for security
   - `DEFAULT_FROM_EMAIL`: The email address to send from
4. Click "Save" at the top

## Step 14: Verify Your Deployment

1. In the Azure Portal, go to your Web App
2. Click the URL at the top (e.g., https://churn-prediction-app.azurewebsites.net)
3. Your application should now be running on Azure!

## Troubleshooting

If your application isn't working correctly:

1. Check the logs:
   - In the Azure Portal, go to your Web App
   - In the left sidebar, click "Log stream"
   - Review the logs for errors

2. Make sure all environment variables are set correctly:
   - In the Azure Portal, go to your Web App
   - Click "Configuration" and verify all application settings

3. Check if the database was created properly:
   - In the Azure Portal, go to your SQL Database
   - Click "Query editor" and try to connect
   - If you get an error, make sure your firewall rules allow Azure services

4. Verify the storage container exists:
   - In the Azure Portal, go to your Storage Account
   - Click "Containers" and make sure the "uploads" container exists
