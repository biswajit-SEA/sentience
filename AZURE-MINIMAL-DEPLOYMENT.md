# Azure App Service Deployment Guide

This guide provides step-by-step instructions for deploying your Flask application to Azure App Service.

## Step 1: Prepare Your Files

I've created/updated the following files to ensure a successful deployment:

1. **app.py** - A minimal Flask application that will serve as your entry point
2. **startup.txt** - Updated to use `app:app` as the entry point
3. **web.config** - Updated with proper configuration for Azure App Service

These files form the minimal setup needed to get your application running on Azure.

## Step 2: Push to GitHub

Since you're using GitHub as your deployment source, push these changes to your GitHub repository:

```powershell
git add app.py startup.txt web.config
git commit -m "Add minimal Flask app for Azure App Service"
git push
```

## Step 3: Configure Azure App Service

1. Go to the Azure Portal (https://portal.azure.com)
2. Navigate to your App Service
3. Go to "Configuration" under Settings
4. Add/update these Application Settings:
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `PYTHONPATH` = `site\\wwwroot`
   - `WEBSITE_WEBDEPLOY_USE_SCM` = `false`

5. Under General Settings:
   - Make sure Python 3.10 is selected
   - Clear any startup command that might be set (the web.config will handle this)

## Step 4: Restart Your App Service

1. Go to the "Overview" page
2. Click "Restart" at the top
3. Wait for the restart to complete (can take a few minutes)

## Step 5: Check Deployment

1. After your app restarts, visit your app URL to see if the minimal app is working
2. If you see "Azure App Service is running. This is a minimal Flask application.", your app is working!

## Step 6: Incremental Improvements

Once the minimal app is working, you can incrementally improve it:

1. First, add basic routes and functionality
2. Then, add database integration
3. Finally, add more complex features

## Troubleshooting

If you still encounter issues:

### Possible Problems:

1. **Deployment hasn't completed yet**: Check the deployment status in the Azure Portal
2. **Python version mismatch**: Make sure Azure is using Python 3.10
3. **Path issues**: Make sure your PYTHONPATH is set correctly
4. **Package installation issues**: Check if all packages in requirements.txt are installing correctly

### View Logs:

1. Go to "Log stream" under Monitoring in your App Service
2. Check for detailed error messages

### Advanced Troubleshooting:

1. Use the Kudu console (Advanced Tools) to explore your deployed files
2. Check if app.py is present in the site/wwwroot directory
3. Try running your app directly using the console

## Next Steps

Once your minimal app is working, you can gradually add more functionality by:

1. Adding more routes to app.py
2. Importing modules from your hackathon.py
3. Setting up database connections
4. Adding authentication and other features

Remember to test each change before moving to the next one!
