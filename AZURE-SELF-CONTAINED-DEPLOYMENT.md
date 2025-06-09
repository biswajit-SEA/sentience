# Deploy to Azure App Service

This guide will help you deploy the simplified Flask application to Azure App Service.

## Step 1: Create a deployment package

First, create a deployment package with only the necessary files:

```powershell
# Create a new deployment directory
$deployDir = "azure-deploy-minimal"
New-Item -Path $deployDir -ItemType Directory -Force

# Copy only the essential files
Copy-Item -Path "app.py" -Destination "$deployDir\"
Copy-Item -Path "web.config" -Destination "$deployDir\"
Copy-Item -Path "requirements.txt" -Destination "$deployDir\"

# Create a deployment zip file
Compress-Archive -Path "$deployDir\*" -DestinationPath "azure-deploy-minimal.zip" -Force
```

## Step 2: Upload via Azure Portal

1. Go to the Azure Portal (https://portal.azure.com)
2. Navigate to your App Service
3. Select "Advanced Tools" under "Development Tools"
4. Click "Go"
5. In the Kudu interface, click "Debug console" and select "CMD"
6. Navigate to `site/wwwroot`
7. Delete any existing files (you can use `rm -rf *` in the console)
8. Click "Upload" and select your `azure-deploy-minimal.zip` file
9. Extract the zip file (you can use `unzip azure-deploy-minimal.zip` in the console)

## Step 3: Configure Azure App Service

1. Go back to your App Service in the Azure Portal
2. Select "Configuration" under "Settings"
3. Add/update these Application Settings:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `WEBSITE_RUN_FROM_PACKAGE` = `0`

4. Under General Settings:
   - Make sure Python 3.10 is selected
   - Clear any startup command that might be set (web.config will handle this)

## Step 4: Restart Your App Service

1. Go to the "Overview" page
2. Click "Restart" at the top
3. Wait for the restart to complete (can take a few minutes)

## Step 5: Check Your Application

Visit your app URL (usually https://your-app-name.azurewebsites.net) to see if your application is running.

## Troubleshooting

If you still encounter issues:

1. Check the logs:
   - Go to "Log stream" under Monitoring in your App Service
   - Look for specific error messages

2. Verify your Python virtual environment:
   - The web.config file expects the virtual environment to be in `antenv` folder
   - If your environment is in a different folder, update the web.config file

3. Check your application logs:
   - Log files should be in the LogFiles directory of your App Service
   - You can access them through the Kudu console
