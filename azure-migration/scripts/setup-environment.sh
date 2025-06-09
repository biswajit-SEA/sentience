# Azure Configuration for Python Application

# Installation script for required packages

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/Scripts/activate  # For Windows use: venv\Scripts\activate

# Install required packages
echo "Installing required packages..."
pip install flask sqlalchemy flask-sqlalchemy flask-login flask-wtf flask-migrate flask-mail email_validator python-dotenv werkzeug azure-storage-blob azure-identity azure-communication-email applicationinsights opencensus-ext-azure opencensus-ext-flask azure-monitor-opentelemetry azure-mgmt-rdbms-postgresql pyodbc psycopg2-binary redis

# Create .env file for environment variables
echo "Creating .env file template..."
cat > .env.template << EOL
# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
AZURE_SQL_CONNECTION_STRING=your_sql_connection_string
AZURE_COMMUNICATION_CONNECTION_STRING=your_communication_connection_string
AZURE_REDIS_CONNECTION_STRING=your_redis_connection_string
APPINSIGHTS_INSTRUMENTATIONKEY=your_appinsights_key

# Application Configuration
SECRET_KEY=your_secret_key
DEBUG=False

# Email Configuration
DEFAULT_FROM_EMAIL=your_default_from_email
EOL

echo "Done! Please fill in the actual values in the .env.template file and rename it to .env"
