# Secondary Research Workflow System

A comprehensive, production-ready multi-agent system for conducting secondary research with live data collection, analysis, and reporting capabilities.

## 🚀 Features

### Core Capabilities
- **Multi-Agent Architecture**: Specialized agents for research planning, data collection, synthesis, SWOT analysis, and report generation
- **Live Data Collection**: Real-time data fetching from 20+ external sources including financial APIs, news feeds, academic databases, and government sources
- **Intelligent Analysis**: Advanced SWOT analysis with strategic recommendations and insights generation
- **Interactive Web Interface**: Modern, responsive dashboard with real-time monitoring and configuration
- **Production-Ready**: Comprehensive caching, rate limiting, error handling, monitoring, and security features

### Data Sources
- **Financial**: Yahoo Finance, Google Finance, SEC EDGAR, Crunchbase
- **News & Media**: Google News, Reddit, LinkedIn, Twitter/X
- **Academic**: PubMed, ArXiv, Google Scholar, SSRN
- **Government**: FRED, FDA, EPA, Census Bureau, World Bank
- **Competitive**: Builtwith, Product Hunt, G2/Capterra

### Performance & Reliability
- **Caching System**: TTL-based caching with memory and file storage
- **Rate Limiting**: Token bucket algorithm with per-source configuration
- **Error Handling**: Exponential backoff, circuit breakers, retry mechanisms
- **Monitoring**: Real-time system metrics, health checks, performance logging
- **Security**: Strong authentication, session management, configuration validation

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/alejandromichell/Secondary-Research-Workflow_V1.git
   cd Secondary-Research-Workflow_V1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**
   ```bash
   uvicorn src.main:app --reload
   ```

5. **Access the web interface**
   - Open your browser and go to `http://localhost:8000`
   - Navigate to the dashboard, questionnaire, or research plans

## 🎯 Usage

### 1. Research Foundation Setup
- Access the questionnaire interface at `/questionnaire`
- Complete the Core Research Foundation questions
- Answer SWOT Analysis Assessment questions
- Define your research objectives and scope

### 2. Research Plan Creation
- Navigate to `/research-plans` to create a new research plan
- Configure data collection sources and parameters
- Set up research tasks and dependencies
- Monitor plan progress in real-time

### 3. Data Collection Configuration
- Access `/data-collection-config` to configure data sources
- Test individual sources for connectivity and reliability
- Set rate limits and collection parameters
- Monitor data collection performance

### 4. Results and Reports
- View comprehensive results at `/results`
- Analyze SWOT matrix and strategic recommendations
- Export reports in multiple formats
- Share findings with stakeholders

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Dashboard  │  Questionnaire  │  Research Plans  │  Results │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                   │
├─────────────────────────────────────────────────────────────┤
│  REST Endpoints  │  WebSocket  │  Authentication  │  CORS   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Multi-Agent System                        │
├─────────────────────────────────────────────────────────────┤
│ Root Orchestrator │ Research Plan │ Orchestration │ Synthesis │
│                   │ Agent         │ Agent         │ Agent     │
├─────────────────────────────────────────────────────────────┤
│ SWOT Analysis │ Report Generation │ Foundation │ Assessment │
│ Agent         │ Agent             │ Agent     │ Agent      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Data Collection Framework                    │
├─────────────────────────────────────────────────────────────┤
│ Financial │ News │ Academic │ Government │ Competitive │ Web │
│ Collector │      │          │           │             │     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Performance & Infrastructure                 │
├─────────────────────────────────────────────────────────────┤
│ Cache Manager │ Rate Limiter │ Error Handler │ Monitoring  │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

- **Root Orchestrator Agent**: Coordinates the entire research workflow
- **Research Foundation Agent**: Gathers core research context and objectives
- **SWOT Assessment Agent**: Collects business context for SWOT analysis
- **Research Plan Agent**: Creates comprehensive research plans with tasks
- **Orchestration Agent**: Executes live data collection from external sources
- **Synthesis Agent**: Analyzes and interprets collected data
- **SWOT Analysis Agent**: Conducts strategic SWOT analysis
- **Report Generation Agent**: Compiles comprehensive research reports

## ⚙️ Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=research_workflow
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Redis Configuration (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your_very_long_secret_key_here_at_least_32_characters

# Data Collection
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
```

### Configuration Files

The system supports environment-specific configuration files:
- `config/development_config.json` - Development settings
- `config/staging_config.json` - Staging environment
- `config/production_config.json` - Production settings

## 🚀 Deployment

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t research-workflow .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Cloud Deployment

#### AWS Deployment
```bash
# Deploy to AWS ECS
aws ecs create-service --cluster research-cluster --service-name research-workflow
```

#### Google Cloud Deployment
```bash
# Deploy to Google Cloud Run
gcloud run deploy research-workflow --source .
```

#### Azure Deployment
```bash
# Deploy to Azure Container Instances
az container create --resource-group myResourceGroup --name research-workflow
```

### Production Checklist

- [ ] Set strong secret keys and passwords
- [ ] Configure database with proper credentials
- [ ] Set up Redis for caching
- [ ] Configure monitoring and alerting
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup and recovery
- [ ] Set up log aggregation
- [ ] Configure rate limiting for external APIs
- [ ] Test all data sources and endpoints
- [ ] Set up health checks and monitoring

## 📊 Monitoring and Observability

### Health Checks
- System health: `GET /api/status`
- Data collection status: `GET /data-collection/status/{plan_id}`
- System metrics: Available through monitoring dashboard

### Logging
- Application logs: `logs/app.log`
- Performance logs: `logs/performance.log`
- System monitoring: `logs/system_monitor.log`

### Metrics
- Cache hit/miss rates
- API response times
- Data collection success rates
- System resource utilization
- Error rates and types

## 🧪 Testing

### Run All Tests
```bash
# Run comprehensive test suite
python test_integrated_system.py

# Run performance optimization tests
python test_performance_optimization.py

# Run user interface tests
python test_user_interface.py
```

### Test Categories
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Caching, rate limiting, error handling
- **UI Tests**: Web interface functionality
- **Unit Tests**: Individual component testing

## 📚 API Documentation

### Core Endpoints

#### Research Management
- `POST /start-research` - Start a new research session
- `GET /research-status/{session_id}` - Get research status
- `GET /research-report/{session_id}` - Get research report

#### Research Plans
- `GET /research-plans/list` - List all research plans
- `POST /research-plans/create` - Create a new research plan
- `GET /research-plans/{plan_id}` - Get plan details
- `PUT /research-plans/{plan_id}/update` - Update plan

#### Data Collection
- `GET /data-collection/sources` - List available data sources
- `POST /data-collection/configure` - Configure data collection
- `GET /data-collection/status/{plan_id}` - Get collection status
- `POST /data-collection/test/{source_name}` - Test data source

#### Multi-Agent Workflow
- `POST /workflow/execute/{plan_id}` - Execute research workflow
- `GET /workflow/status/{plan_id}` - Get workflow status
- `POST /workflow/pause/{plan_id}` - Pause workflow
- `POST /workflow/resume/{plan_id}` - Resume workflow

### Web Interface
- `GET /` - Main landing page
- `GET /dashboard` - System dashboard
- `GET /questionnaire` - Research foundation questionnaire
- `GET /research-plans` - Research plan management
- `GET /data-collection-config` - Data collection configuration
- `GET /results` - Results and reports dashboard

## 🔧 Development

### Project Structure
```
src/
├── agents/                 # Multi-agent system
│   ├── root_orchestrator_agent.py
│   ├── research_foundation_agent.py
│   ├── swot_assessment_agent.py
│   ├── research_plan_agent.py
│   ├── orchestration_agent.py
│   ├── synthesis_agent.py
│   ├── swot_analysis_agent.py
│   └── report_generation_agent.py
├── data_collection/        # Data collection framework
│   ├── base_collector.py
│   ├── financial_collector.py
│   ├── news_collector.py
│   ├── academic_collector.py
│   ├── government_collector.py
│   ├── competitive_collector.py
│   ├── web_scraper.py
│   ├── data_validator.py
│   ├── data_aggregator.py
│   └── data_collection_manager.py
├── utils/                  # Utility modules
│   ├── cache_manager.py
│   ├── rate_limiter.py
│   ├── error_handler.py
│   ├── monitoring.py
│   ├── questionnaire_processor.py
│   └── research_plan_tracker.py
├── config/                 # Configuration management
│   └── production_config.py
├── templates/              # Web interface templates
│   ├── index.html
│   ├── dashboard.html
│   ├── questionnaire_interface.html
│   ├── research_plan_interface.html
│   ├── data_collection_config.html
│   └── results_dashboard.html
├── workflows/              # Workflow implementations
│   └── simple_live_workflow.py
└── main.py                 # FastAPI application
```

### Adding New Data Sources

1. **Create a new collector**
   ```python
   from src.data_collection.base_collector import BaseDataCollector
   
   class NewSourceCollector(BaseDataCollector):
       def get_supported_sources(self):
           return [DataSource(name="New Source", url="...", ...)]
       
       async def collect_data(self, query, context):
           # Implementation
           pass
   ```

2. **Register the collector**
   ```python
   # In data_collection_manager.py
   self.collectors.append(NewSourceCollector())
   ```

3. **Configure rate limits**
   ```python
   # In production_config.py
   "new_source": {"rate": 0.5, "burst": 3}
   ```

### Adding New Agents

1. **Create the agent class**
   ```python
   class NewAgent:
       def __init__(self):
           self.agent_name = "New Agent"
           # Initialize
       
       async def execute_task(self, task_data):
           # Implementation
           pass
   ```

2. **Integrate with orchestrator**
   ```python
   # In root_orchestrator_agent.py
   self.agents["NewAgent"] = NewAgent()
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check the comprehensive guides in the `docs/` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

### Troubleshooting
- **Common Issues**: See the [Troubleshooting Guide](docs/troubleshooting.md)
- **FAQ**: Check the [Frequently Asked Questions](docs/faq.md)
- **Performance**: See the [Performance Tuning Guide](docs/performance.md)

## 🎉 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for high-performance APIs
- Uses [Bootstrap](https://getbootstrap.com/) for responsive web interfaces
- Integrates with [Chart.js](https://www.chartjs.org/) for data visualization
- Leverages [psutil](https://psutil.readthedocs.io/) for system monitoring

## 📈 Roadmap

### Upcoming Features
- [ ] Advanced AI-powered insights generation
- [ ] Real-time collaboration features
- [ ] Mobile application
- [ ] Advanced data visualization
- [ ] Machine learning integration
- [ ] Multi-language support
- [ ] Advanced security features
- [ ] Cloud-native deployment options

---

**Ready to revolutionize your research workflow?** 🚀

Start your first research project today by visiting `http://localhost:8000` after installation!