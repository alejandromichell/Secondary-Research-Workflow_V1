#!/bin/bash

# Setup script for Secondary Research Workflow on Apple M2

echo "🚀 Setting up Secondary Research Workflow on Apple M2..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python 3.11
echo "📦 Installing Python 3.11..."
brew install python@3.11

# Install Node.js (for potential MCP server)
echo "📦 Installing Node.js..."
brew install node@18

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/outputs
mkdir -p credentials
mkdir -p logs

# Copy environment template
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "Please edit .env with your API keys"
fi

# Set up Google credentials template
if [ ! -f credentials/google_credentials.json ]; then
    echo "🔑 Creating Google credentials template..."
    cat > credentials/google_credentials.json.example << EOF
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
EOF
    echo "Please rename and configure credentials/google_credentials.json.example"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Configure Google credentials if using Google Sheets"
echo "3. Run: source .venv/bin/activate"
echo "4. Run: python src/main.py"