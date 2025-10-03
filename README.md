#### `README.md`
```markdown
# Secondary Research Workflow

A comprehensive multi-agent secondary research system built with Google's Agent Development Kit (ADK). This system orchestrates specialized AI agents to conduct thorough market research, competitive analysis, and strategic planning through automated workflows.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for planning, orchestration, synthesis, SWOT analysis, and report generation
- **Google ADK Integration**: Built on Google's Agent Development Kit for robust agent coordination
- **Multi-Model Support**: Uses Gemini, Claude, and other LLMs via LiteLLM for optimal task performance  
- **Tool Integration**: Seamless integration with Notion, Google Sheets, Perplexity, and Claude APIs
- **Safety Guardrails**: Comprehensive callback system for quality control and rate limiting
- **Session Management**: Persistent state management across workflow phases
- **Apple M2 Optimized**: Specifically configured for Apple Silicon MacBooks

## 🏗️ Architecture

### Agent Workflow

### Core Components
- **Root Orchestrator**: Coordinates the entire research workflow
- **Research Plan Agent**: Creates structured research methodology  
- **Orchestration Agent**: Manages multi-source data collection
- **Synthesis Agent**: Analyzes and synthesizes research findings
- **SWOT Analysis Agent**: Conducts framework-based strategic analysis
- **Report Generation Agent**: Creates comprehensive final deliverables

## 📋 Prerequisites

- **Hardware**: Apple MacBook Air M2 (or compatible Apple Silicon Mac)
- **Software**: Python 3.11+, Node.js 18+, Git, Homebrew
- **API Keys**: Google AI Studio, Anthropic, Notion, Perplexity (optional), Google Sheets (optional)

## 🛠️ Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd secondary-research-workflow

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh