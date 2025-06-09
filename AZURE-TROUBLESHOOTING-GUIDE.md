# Azure App Service Deployment Troubleshooting Guide

Based on the error logs you've shared, I've created this comprehensive guide to help you fix your Azure App Service deployment issues. The key problem is an import error in your Python application.

## Files Created/Modified

I've created several new files to help resolve this issue:

1. **application.py** - A simplified entry point for your Flask application
2. **index.py** - An alternative entry point that tries multiple import methods
3. **Updated startup.txt** - Now uses `application:app` instead of `app_azure:app`

## Step 1: Push the New Files to Your GitHub Repository

Make sure these new files are pushed to your GitHub repository that's connected to your Azure App Service:
- `application.py`
- `index.py`
- Updated `startup.txt`

## Step 2: Configure Your Azure App Service

1. Go to the Azure Portal (https://portal.azure.com)
2. Navigate to your App Service
3. Go to "Configuration" under Settings
4. Add/update these Application Settings:
   - `WEBSITE_PYTHON_VERSION` = `3.10`
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `PYTHONPATH` = `site\\wwwroot`

5. Under General Settings:
   - Make sure Python 3.10 is selected
   - Under "Startup Command", enter:
     ```
     gunicorn --bind=0.0.0.0:8000 application:app
     ```

## Step 3: Try Multiple Entry Points

If the approach with `application.py` doesn't work, you can try these alternative approaches:

### Option 1: Use index.py

Change your startup command to:
```
gunicorn --bind=0.0.0.0:8000 index:app
```

### Option 2: Direct Import from hackathon.py

If your hackathon.py file is self-contained enough, you can try:
```
gunicorn --bind=0.0.0.0:8000 hackathon:app
```

## Step 4: Troubleshooting Import Issues

If you're still having import issues, check:

1. **Python Path**: Make sure your application directory is in the Python path
2. **Dependencies**: Ensure all required packages are in requirements.txt
3. **File Structure**: Verify all needed files (models/, templates/, etc.) are deployed
4. **Permission Issues**: Check if Azure has permission to read your files

## Step 5: Check Logs for More Details

1. Go to "Log stream" under Monitoring in your App Service
2. Watch for error messages during startup

## Common Issues and Solutions

1. **ModuleNotFoundError**: 
   - Make sure the module exists in your deployment
   - Check if your Python path includes the directory containing the module

2. **ImportError**: 
   - Check if all dependencies are installed
   - Verify the versions of packages in requirements.txt

3. **Permission Errors**:
   - Make sure your app has permission to write to logs or upload folders

4. **Database Connection Issues**:
   - Verify connection strings and credentials

## Final Considerations

- The simplified `application.py` file focuses on importing your main application while providing fallbacks if anything fails
- The `/health` endpoint can be used to verify if your application is running at all
- Remember that Azure App Service expects your application to listen on port 8000

If you're still having issues, consider using Azure App Service's Advanced Tools (Kudu) to connect directly to your deployment and inspect the file structure and logs.
