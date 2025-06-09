# Deploy-AzureMinimal.ps1
# PowerShell script to prepare and deploy a minimal Flask application to Azure App Service

# Parameters
param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "your-resource-group",
    
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "your-app-service-name"
)

Write-Host "Creating minimal deployment package for Azure App Service..." -ForegroundColor Green

# Create a deployment directory
$deployDir = "azure-deploy-minimal"
if (Test-Path $deployDir) {
    Remove-Item -Path $deployDir -Recurse -Force
}
New-Item -Path $deployDir -ItemType Directory -Force | Out-Null

# Copy only the essential files
Write-Host "Copying essential files..." -ForegroundColor Cyan
Copy-Item -Path "app.py" -Destination "$deployDir\"
Copy-Item -Path "web.config" -Destination "$deployDir\"
Copy-Item -Path "requirements.txt" -Destination "$deployDir\"

# Create a deployment zip file
Write-Host "Creating deployment zip file..." -ForegroundColor Cyan
$zipPath = "azure-deploy-minimal.zip"
if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipPath -Force

Write-Host "Deployment package created: $zipPath" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Upload this zip file to your Azure App Service using the Azure Portal" -ForegroundColor Yellow
Write-Host "2. Extract it in the wwwroot directory" -ForegroundColor Yellow
Write-Host "3. Configure and restart your App Service" -ForegroundColor Yellow
Write-Host ""
Write-Host "For detailed instructions, see AZURE-SELF-CONTAINED-DEPLOYMENT.md" -ForegroundColor Yellow

# If Azure CLI is available, offer to deploy directly
if (Get-Command az -ErrorAction SilentlyContinue) {
    $deployNow = Read-Host "Would you like to deploy directly to Azure now? (y/n)"
    if ($deployNow -eq "y") {
        Write-Host "Logging in to Azure..." -ForegroundColor Cyan
        az login
        
        Write-Host "Deploying to Azure App Service: $AppServiceName..." -ForegroundColor Cyan
        az webapp deployment source config-zip --resource-group $ResourceGroupName --name $AppServiceName --src $zipPath
        
        Write-Host "Configuring application settings..." -ForegroundColor Cyan
        az webapp config set --resource-group $ResourceGroupName --name $AppServiceName --python-version "3.10"
        az webapp config appsettings set --resource-group $ResourceGroupName --name $AppServiceName --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true WEBSITE_RUN_FROM_PACKAGE=0
        
        Write-Host "Restarting the App Service..." -ForegroundColor Cyan
        az webapp restart --resource-group $ResourceGroupName --name $AppServiceName
        
        Write-Host "Deployment complete!" -ForegroundColor Green
        $appUrl = "https://$AppServiceName.azurewebsites.net"
        Write-Host "Your application should be available at: $appUrl" -ForegroundColor Green
    }
}
