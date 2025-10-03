# Secondary Research Workflow Setup Guide

## Prerequisites

- Apple MacBook Air M2 (or compatible Apple Silicon Mac)
- Python 3.11+
- Node.js 18+ (for MCP server components)
- Git
- Homebrew package manager

## API Keys Required

Before setup, obtain the following API keys:

1. **Google AI Studio API Key**
   - Go to https://aistudio.google.com/app/apikey
   - Create or sign in to your Google account
   - Generate a new API key
   - Save securely

2. **Anthropic API Key**
   - Go to https://console.anthropic.com/settings/keys
   - Create account or sign in
   - Generate API key
   - Save securely

3. **Notion Integration Key** (Optional)
   - Go to https://www.notion.so/my-integrations
   - Create new integration
   - Copy Internal Integration Token
   - Share workspace with integration

4. **Google Sheets API Credentials** (Optional)
   - Go to https://console.cloud.google.com/
   - Create project and enable Google Sheets API
   - Create service account credentials
   - Download JSON credentials file

5. **Perplexity API Key** (Optional)
   - Go to https://www.perplexity.ai/settings/api
   - Create account and generate API key

## Installation Steps

### 1. Clone and Setup Project
```bash
# Clone the repository
git clone <repository-url>
cd secondary-research-workflow

# Make setup script executable
chmod +x scripts/setup.sh

# Run setup
./scripts/setup.sh