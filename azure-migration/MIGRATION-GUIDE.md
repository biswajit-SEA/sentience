# Step-by-Step Azure Migration Guide for Churn Prediction System

This guide provides detailed instructions for migrating your Flask-based Churn Prediction System to Azure.

## Prerequisites

1. An active Azure account with appropriate permissions
2. Azure CLI installed on your development machine
3. Git installed on your development machine
4. Python 3.8+ installed on your development machine

## Step 1: Set Up Azure Resources

### Log in to Azure

```bash
az login
```

### Create Azure Resources

1. Navigate to your project directory:

```bash
cd /path/to/techm-hackathon
```

2. Make the resource creation script executable:

```bash
chmod +x azure-migration/scripts/create-azure-resources.sh
```

3. Run the script to create all necessary Azure resources:

```bash
./azure-migration/scripts/create-azure-resources.sh
```

4. Note down the resource names and connection strings provided in the output.

## Step 2: Configure Your Application

### Install Required Packages

1. Run the environment setup script:

```bash
chmod +x azure-migration/scripts/setup-environment.sh
./azure-migration/scripts/setup-environment.sh
```

2. Copy `.env.template` to `.env`:

```bash
cp .env.template .env
```

3. Fill in the actual values in the `.env` file with the connection strings and keys from Step 1.

### Modify Your Application Code

1. Add Azure service integration:

   - Copy the Azure service files to your project:
   
   ```bash
   cp azure-migration/scripts/azure_services.py .
   cp azure-migration/scripts/azure_file_operations.py .
   cp azure-migration/scripts/azure_email.py .
   cp azure-migration/scripts/azure_database.py .
   ```

2. Update your main application file (`hackathon.py`) to use Azure services:

   - Import the Azure modules at the top of your file:
   
   ```python
   import os
   from dotenv import load_dotenv
   from azure_services import (
       setup_azure_blob_storage,
       setup_azure_email_service,
       setup_azure_logging,
       setup_azure_redis
   )
   from azure_database import configure_azure_sql_database
   from azure_file_operations import (
       save_file_to_azure_blob,
       get_file_from_azure_blob
   )
   from azure_email import send_email_via_azure
   
   # Load environment variables
   load_dotenv()
   ```

   - Initialize Azure services in your application setup:
   
   ```python
   # Initialize Flask app
   app = Flask(__name__)
   
   # Load configuration
   app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
   app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
   
   # Configure Azure services
   setup_azure_logging(app)
   setup_azure_blob_storage(app)
   setup_azure_email_service(app)
   setup_azure_redis(app)
   
   # Configure database
   db = configure_azure_sql_database(app)
   ```

   - Update your email sending function to use Azure Communication Services:
   
   ```python
   def send_email(subject, recipient, html_content, max_retries=2):
       if app.config.get('EMAIL_PROVIDER') == 'azure_communication':
           return send_email_via_azure(subject, recipient, html_content, max_retries)
       else:
           # Fallback to your original email function
           # ...
   ```

   - Update file upload handling to use Azure Blob Storage:
   
   ```python
   @app.route("/upload", methods=["POST"])
   @login_required
   def upload_files():
       try:
           audio_files = []
           data_files = []
           chat_files = []
   
           if (
               "audioFiles" not in request.files
               and "dataFiles" not in request.files
               and "chatFiles" not in request.files
           ):
               # Handle error
               pass
   
           # Save files to Azure Blob Storage
           for key in request.files:
               files = request.files.getlist(key)
               for file in files:
                   if file.filename == "":
                       continue
                   
                   # Save to Azure Blob Storage
                   filename = secure_filename(file.filename)
                   blob_url = save_file_to_azure_blob(file, filename)
                   
                   if blob_url:
                       if key == "audioFiles":
                           audio_files.append(blob_url)
                       elif key == "dataFiles":
                           data_files.append(blob_url)
                       elif key == "chatFiles":
                           chat_files.append(blob_url)
   
           # Rest of your function remains the same
           # ...
       except Exception as e:
           logger.error(f"Error in upload_files: {str(e)}")
           return jsonify({"error": "An error occurred while processing your files"}), 500
   ```

3. Create a health check endpoint for Azure App Service:

   ```python
   @app.route("/health")
   def health_check():
       return jsonify({"status": "healthy"}), 200
   ```

4. Update your `requirements.txt` file:

   ```
   Flask==2.3.3
   SQLAlchemy==2.0.9
   Flask-SQLAlchemy==3.1.1
   Flask-Login==0.6.2
   Flask-WTF==1.1.1
   Flask-Migrate==4.0.4
   email_validator==2.0.0
   python-dotenv==1.0.0
   Werkzeug==2.3.7
   gunicorn==21.2.0
   azure-storage-blob==12.17.0
   azure-identity==1.14.0
   azure-communication-email==1.0.0
   applicationinsights==0.11.11
   opencensus-ext-azure==1.1.9
   opencensus-ext-flask==0.8.10
   azure-monitor-opentelemetry==1.0.0
   pyodbc==4.0.39
   psycopg2-binary==2.9.7
   redis==4.6.0
   ```

## Step 3: Deploy Your Application to Azure

### Prepare for Deployment

1. Create a `.deployment` file in your project root:

```
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

2. Create a `startup.txt` file in your project root:

```
gunicorn --bind=0.0.0.0:5000 hackathon:app
```

### Deploy Using Git

1. Initialize a Git repository if you haven't already:

```bash
git init
git add .
git commit -m "Prepare for Azure deployment"
```

2. Configure the Azure Web App deployment source:

```bash
az webapp deployment source config-local-git --name <your-web-app-name> --resource-group <your-resource-group>
```

3. Add the Azure remote to your Git repository:

```bash
git remote add azure <git-clone-url-from-previous-command>
```

4. Push your code to Azure:

```bash
git push azure main
```

### Deploy Using Azure CLI

Alternatively, you can deploy using the Azure CLI:

```bash
az webapp up --name <your-web-app-name> --resource-group <your-resource-group> --sku B1 --location <your-location>
```

## Step 4: Configure Azure App Service Settings

1. Set the application settings:

```bash
az webapp config appsettings set --name <your-web-app-name> --resource-group <your-resource-group> --settings @azure-migration/scripts/appsettings.ini
```

2. Configure logging:

```bash
az webapp log config --name <your-web-app-name> --resource-group <your-resource-group> --application-logging filesystem --detailed-error-messages true --failed-request-tracing true --web-server-logging filesystem
```

## Step 5: Verify Deployment

1. Browse to your web application:

```
https://<your-web-app-name>.azurewebsites.net
```

2. Check logs for any issues:

```bash
az webapp log tail --name <your-web-app-name> --resource-group <your-resource-group>
```

## Step 6: Set Up Monitoring and Alerts

1. Navigate to the Azure Portal and open your Application Insights resource.

2. Configure alerts for:
   - High server response time
   - Failed requests
   - Server exceptions

3. Set up availability tests to monitor your application's health.

4. Create a dashboard to monitor key metrics.

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check the connection string format
   - Verify that the firewall rules allow your App Service to connect

2. **File Upload Issues**:
   - Verify storage account permissions
   - Check CORS settings if uploading directly from browser

3. **Email Sending Issues**:
   - Verify Communication Services is properly configured
   - Check for API permission issues

### Getting Help

If you encounter issues, check:
- Azure App Service logs
- Application Insights for exceptions
- Azure support portal for service-specific issues
