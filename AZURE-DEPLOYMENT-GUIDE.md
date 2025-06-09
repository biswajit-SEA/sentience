# Azure Deployment Guide

This guide will help you deploy your application to Azure App Service correctly to avoid the "Application Error" message.

## 1. Push these changes to your repository:

- Updated `startup.txt` to use port 8000
- Added `web.config` file
- Updated `app_azure.py` with improved logging

## 2. Configure Azure App Service:

1. Go to the Azure Portal (https://portal.azure.com)
2. Navigate to your App Service
3. Go to "Configuration" under Settings
4. Add/Update these Application Settings:
   - `WEBSITE_HTTPSCALEV2_ENABLED` = `1`
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `SECRET_KEY` = `[your-secure-random-string]`
   - Any other environment variables your app requires

5. Under General Settings:
   - Verify Python version is set to 3.10
   - Under "Startup Command", enter:
     ```
     gunicorn --bind=0.0.0.0:8000 app_azure:app
     ```

## 3. Restart your App Service:

1. Go to the "Overview" page
2. Click "Restart" at the top
3. Wait for the restart to complete (can take a few minutes)

## 4. View logs to identify any remaining issues:

1. Go to "Log stream" under Monitoring
2. Watch for error messages as your app starts up

## 5. If you still encounter issues:

1. Go to "Advanced Tools (Kudu)" under Development Tools
2. Click "Go" to open Kudu console
3. Go to "Debug console" → "CMD"
4. Navigate to `site/wwwroot`
5. Check for log files that might have more information
6. Verify all required files are present

## Troubleshooting Common Issues:

1. **Missing Dependencies**: Ensure all packages in requirements.txt are installed
2. **File Permissions**: Check if your app has permission to write to logs or upload folders
3. **Environment Variables**: Verify all required environment variables are set
4. **Python Version**: Make sure the Python version in Azure matches what your app requires
5. **Database Connection**: If using a database, check connection strings are correct
