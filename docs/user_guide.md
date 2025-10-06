# User Guide - Secondary Research Workflow System

## Table of Contents
1. [Getting Started](#getting-started)
2. [Research Foundation Setup](#research-foundation-setup)
3. [Creating Research Plans](#creating-research-plans)
4. [Data Collection Configuration](#data-collection-configuration)
5. [Monitoring Research Progress](#monitoring-research-progress)
6. [Analyzing Results](#analyzing-results)
7. [Generating Reports](#generating-reports)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the System

1. **Open your web browser** and navigate to `http://localhost:8000`
2. **Landing Page**: You'll see the main landing page with navigation options
3. **Dashboard**: Click "Dashboard" to access the main system overview

### System Overview

The Secondary Research Workflow System consists of several key components:

- **Dashboard**: System overview and navigation hub
- **Research Foundation**: Questionnaire for defining research objectives
- **Research Plans**: Create and manage research projects
- **Data Collection**: Configure and monitor data sources
- **Results**: View and analyze research findings

## Research Foundation Setup

### Step 1: Access the Questionnaire

1. Navigate to the **Questionnaire** section from the main menu
2. You'll see a multi-step form with two main sections:
   - **Core Research Foundation**
   - **SWOT Analysis Assessment**

### Step 2: Complete Core Research Foundation

Answer the following questions to establish your research foundation:

#### Primary Research Objective
- **What is the primary objective of your research?**
  - Be specific about what you want to achieve
  - Example: "Assess market opportunities for AI-powered tax preparation software"

- **What key business decision will this research inform?**
  - Market entry decisions
  - Product launch strategies
  - Investment decisions
  - Strategic planning

#### Research Subject & Scope
- **What is the main subject of analysis?**
  - Company name, industry, market, or product/service
  - Example: "Financial Technology / Tax Preparation Software"

- **If analyzing a specific organization:**
  - Company name
  - Primary industry
  - Approximate size (revenue/employees)
  - Main products/services

- **What is the geographic scope?**
  - Local, regional, national, global
  - Specific countries/regions

#### Critical Research Questions
- **What are the 3-5 most important questions this research must answer?**
  - Example questions:
    - "What is the current market size for AI tax software?"
    - "Who are the key competitors in this space?"
    - "What are the main technological trends driving growth?"

- **Are there specific areas of concern or opportunity you want emphasized?**
  - Regulatory changes
  - Technology disruptions
  - Market opportunities

#### Timeline Requirements
- **What are the starting and finishing dates?**
- **What are important milestone dates in between?**

### Step 3: Complete SWOT Analysis Assessment

#### Business/Organization Context
- **What is the name and primary industry of the organization being analyzed?**
- **What is the organization's size (employees, revenue, market cap if public)?**
- **What are the organization's core products/services and primary markets?**
- **What is the time frame for this analysis?**
  - Current state
  - 1-year outlook
  - 3-year strategic

#### Analysis Scope
- **Is this a comprehensive organizational SWOT or focused on specific business units/products?**
- **What are the primary strategic decisions this analysis will inform?**
- **Are there specific competitors or market segments that should be prioritized?**
- **What geographical markets should be included?**

#### Stakeholder Requirements
- **Who is the primary audience for this analysis?**
  - Executives
  - Investors
  - Board members
  - Strategic planning teams

- **What level of detail is required?**
  - High-level strategic
  - Operational detail

- **Are there specific areas of concern or opportunity to emphasize?**
- **What format is preferred for final deliverables?**

### Step 4: Submit and Review

1. **Review your answers** before submitting
2. **Click "Submit"** to save your research foundation
3. **System validation** will ensure all required fields are completed
4. **Confirmation** will be displayed with your research foundation summary

## Creating Research Plans

### Step 1: Access Research Plans

1. Navigate to **Research Plans** from the main menu
2. Click **"Create New Research Plan"**

### Step 2: Plan Configuration

#### Basic Information
- **Plan Title**: Descriptive name for your research project
- **Description**: Brief overview of the research objectives
- **Priority Level**: High, Medium, or Low
- **Timeline**: Start and end dates

#### Research Context
The system will automatically populate this section based on your questionnaire responses:
- Research objectives
- Subject scope
- Critical questions
- SWOT context

#### Task Configuration
The system will automatically generate research tasks based on your objectives:

1. **Develop Comprehensive Research Plan**
   - Agent: Research Plan Agent
   - Dependencies: Initial setup
   - Status: Ready to start

2. **Execute Live Data Collection**
   - Agent: Orchestration Agent
   - Dependencies: Research plan completion
   - Status: Pending

3. **Analyze and Synthesize Collected Data**
   - Agent: Synthesis Agent
   - Dependencies: Data collection completion
   - Status: Pending

4. **Conduct Comprehensive SWOT Analysis**
   - Agent: SWOT Analysis Agent
   - Dependencies: Data synthesis completion
   - Status: Pending

5. **Generate Comprehensive Research Report**
   - Agent: Report Generation Agent
   - Dependencies: SWOT analysis completion
   - Status: Pending

### Step 3: Plan Execution

1. **Click "Start Research Plan"** to begin execution
2. **Monitor progress** in real-time through the dashboard
3. **View task status** and completion percentages
4. **Receive notifications** when tasks are completed or encounter issues

## Data Collection Configuration

### Step 1: Access Data Collection Configuration

1. Navigate to **Data Collection** from the main menu
2. You'll see the configuration interface with available data sources

### Step 2: Configure Collection Settings

#### Collection Strategy
- **Focused (Recommended)**: Optimized for specific research objectives
- **Comprehensive**: Broad data collection across all sources
- **Rapid**: Fast collection with limited depth

#### Performance Settings
- **Max Parallel Tasks**: Number of simultaneous data collection operations (1-10)
- **Timeout (seconds)**: Maximum time to wait for each data source (30-600)
- **Max Results per Source**: Maximum number of results per data source (1-50)

### Step 3: Select Data Sources

#### Available Categories

**Financial Data Sources**
- Yahoo Finance: Stock prices, financial metrics, company information
- Google Finance: Market data, financial news
- SEC EDGAR: Public company filings, 10-Ks, 10-Qs
- Crunchbase: Startup and private company data

**News & Media Sources**
- Google News: Current events, company news
- Reddit: Community insights, sentiment analysis
- LinkedIn: Company updates, executive movements
- Twitter/X: Real-time sentiment, trending topics

**Academic Sources**
- PubMed: Life sciences and biomedical research
- ArXiv: Pre-print scientific papers
- Google Scholar: Academic papers, research studies
- SSRN: Working papers, research

**Government Sources**
- FRED: Economic indicators, financial data
- FDA: Drug approvals, medical device data
- EPA: Environmental compliance data
- Census Bureau: Demographic and economic data

**Competitive Intelligence**
- Builtwith: Technology stack analysis
- Product Hunt: New product launches
- G2/Capterra: Software reviews and comparisons

#### Source Selection Process

1. **Browse available sources** by category
2. **Review source information**:
   - Description and capabilities
   - Reliability score (0-100%)
   - Category and type
   - Authentication requirements

3. **Use filters** to narrow down sources:
   - Category filter
   - Reliability level (High: 90%+, Medium: 70-89%, Low: <70%)
   - Show only enabled sources

4. **Test individual sources**:
   - Click "Test" button for any source
   - Enter a test query
   - Review test results and performance

5. **Select sources** by checking the boxes
6. **Use bulk actions**:
   - "Select All" to enable all sources
   - "Deselect All" to disable all sources

### Step 4: Save Configuration

1. **Review your configuration** before saving
2. **Click "Save Configuration"** to apply settings
3. **Confirmation** will be displayed with configuration summary

## Monitoring Research Progress

### Dashboard Overview

The main dashboard provides real-time insights into your research activities:

#### Key Metrics
- **Total Research Plans**: Number of active and completed plans
- **Data Sources**: Available and configured data sources
- **Completed Reports**: Number of finished research reports
- **Average Processing Time**: Typical time to complete research

#### Recent Research Plans
- **Plan Status**: Active, Completed, Paused, or Cancelled
- **Progress Indicators**: Visual progress bars for each plan
- **Quick Actions**: View, edit, or manage plans

#### System Status
- **Data Collection**: Active/Inactive status
- **Multi-Agent System**: Operational status
- **API Endpoints**: Service availability
- **Live Data Sources**: Number of available sources

### Plan-Specific Monitoring

#### Plan Status Tracking
- **Task Progress**: Individual task completion status
- **Agent Activity**: Which agents are currently working
- **Data Collection**: Real-time collection progress
- **Error Handling**: Any issues or failures

#### Performance Metrics
- **Collection Speed**: Items collected per minute
- **Success Rate**: Percentage of successful data retrievals
- **Source Performance**: Individual source reliability
- **Processing Time**: Time spent on each phase

### Real-Time Notifications

The system provides notifications for:
- **Task Completion**: When individual tasks are finished
- **Plan Milestones**: Major progress updates
- **Error Alerts**: Issues that require attention
- **Data Collection**: Source failures or successes

## Analyzing Results

### Accessing Results

1. Navigate to **Results** from the main menu
2. **Select a research plan** from the dropdown
3. **View comprehensive results** and analysis

### Results Dashboard

#### Key Metrics Summary
- **Data Items Collected**: Total number of data points gathered
- **Insights Generated**: Number of insights extracted from data
- **Strategic Recommendations**: Number of actionable recommendations
- **Overall Quality Score**: System-assessed quality rating

#### Data Collection Summary
- **Visual Chart**: Pie chart showing data distribution by category
- **Source Performance**: Success rates and reliability scores
- **Collection Timeline**: When data was collected
- **Data Quality**: Validation and completeness scores

### SWOT Analysis Matrix

#### Strengths
- **Internal advantages** and competitive strengths
- **Confidence levels** for each strength
- **Supporting evidence** from collected data

#### Weaknesses
- **Internal limitations** and areas for improvement
- **Risk assessments** and impact analysis
- **Mitigation strategies** where applicable

#### Opportunities
- **External opportunities** for growth and expansion
- **Market trends** and emerging possibilities
- **Strategic timing** and implementation guidance

#### Threats
- **External challenges** and competitive threats
- **Risk factors** and potential impacts
- **Defensive strategies** and contingency plans

### Strategic Recommendations

#### Recommendation Types
- **S-O Strategies**: Leverage strengths to capitalize on opportunities
- **W-O Strategies**: Address weaknesses to seize opportunities
- **S-T Strategies**: Use strengths to mitigate threats
- **W-T Strategies**: Minimize weaknesses and avoid threats

#### Implementation Guidance
- **Priority Levels**: High, Medium, Low, or Critical
- **Implementation Steps**: Detailed action plans
- **Resource Requirements**: Time, budget, and personnel needs
- **Success Metrics**: How to measure progress

### Key Insights

#### Insight Categories
- **Market Insights**: Industry trends and market dynamics
- **Competitive Intelligence**: Competitor analysis and positioning
- **Technology Trends**: Emerging technologies and innovations
- **Regulatory Changes**: Policy and compliance updates

#### Insight Details
- **Description**: Detailed explanation of the insight
- **Confidence Score**: System-assessed reliability (0-100%)
- **Source Attribution**: Which data sources provided the insight
- **Supporting Evidence**: Data points that validate the insight

## Generating Reports

### Report Types

#### Executive Summary
- **High-level overview** of research findings
- **Key recommendations** and strategic insights
- **Critical success factors** and risk factors
- **Implementation roadmap** and timeline

#### Detailed Analysis Report
- **Comprehensive findings** from all data sources
- **Detailed SWOT analysis** with supporting evidence
- **Strategic recommendations** with implementation guidance
- **Risk assessment** and mitigation strategies

#### Technical Report
- **Data collection methodology** and source details
- **Analysis techniques** and validation methods
- **Quality metrics** and reliability scores
- **Limitations** and assumptions

### Export Options

#### PDF Export
- **Professional formatting** suitable for presentations
- **Executive-ready** summary and recommendations
- **Visual charts** and SWOT matrix
- **Print-friendly** layout and formatting

#### Excel Export
- **Raw data** in spreadsheet format
- **Structured analysis** with formulas and charts
- **Data validation** and quality metrics
- **Customizable** for further analysis

#### HTML Export
- **Interactive reports** with embedded charts
- **Web-friendly** formatting and navigation
- **Shareable links** for stakeholder access
- **Responsive design** for mobile viewing

### Sharing and Collaboration

#### Share Results
- **Generate shareable links** for stakeholders
- **Email integration** for direct sharing
- **Access controls** and permission management
- **Version tracking** and update notifications

#### Stakeholder Access
- **Role-based permissions** for different user types
- **View-only access** for external stakeholders
- **Comment and feedback** capabilities
- **Update notifications** when reports are modified

## Best Practices

### Research Planning

#### Define Clear Objectives
- **Be specific** about what you want to achieve
- **Set measurable goals** and success criteria
- **Define scope** and boundaries clearly
- **Establish timelines** with realistic milestones

#### Choose Appropriate Sources
- **Select relevant sources** for your research domain
- **Balance breadth and depth** of data collection
- **Consider source reliability** and reputation
- **Test sources** before full deployment

#### Monitor Progress Regularly
- **Check dashboard** daily for updates
- **Review task progress** and identify bottlenecks
- **Address issues** promptly when they arise
- **Adjust plans** based on findings and feedback

### Data Collection

#### Optimize Configuration
- **Start with focused strategy** for initial research
- **Use appropriate timeouts** for different source types
- **Limit parallel tasks** to avoid overwhelming sources
- **Set reasonable result limits** per source

#### Quality Assurance
- **Validate data quality** regularly
- **Cross-reference findings** across multiple sources
- **Check for data freshness** and relevance
- **Monitor source reliability** and performance

#### Error Handling
- **Review error logs** for failed collections
- **Retry failed sources** with adjusted parameters
- **Report persistent issues** to system administrators
- **Have backup sources** for critical data needs

### Analysis and Reporting

#### Review Findings Thoroughly
- **Examine all insights** before drawing conclusions
- **Validate recommendations** against multiple data points
- **Consider alternative interpretations** of the data
- **Assess confidence levels** for each finding

#### Present Results Effectively
- **Use clear, concise language** in reports
- **Include visual elements** like charts and graphs
- **Provide context** for findings and recommendations
- **Highlight actionable insights** prominently

#### Follow Up and Iterate
- **Monitor implementation** of recommendations
- **Track outcomes** and measure success
- **Update research** as new information becomes available
- **Refine methodology** based on experience

## Troubleshooting

### Common Issues

#### Research Plan Not Starting
**Symptoms**: Plan remains in "Draft" status
**Solutions**:
- Check that all required questionnaire fields are completed
- Verify that data collection sources are properly configured
- Ensure system resources are available
- Contact system administrator if issues persist

#### Data Collection Failures
**Symptoms**: Low success rates or missing data
**Solutions**:
- Check internet connectivity and firewall settings
- Verify that data sources are accessible
- Review rate limiting settings
- Test individual sources for connectivity
- Check for API key requirements

#### Slow Performance
**Symptoms**: Long processing times or system delays
**Solutions**:
- Reduce number of parallel tasks
- Increase timeout settings
- Check system resource utilization
- Clear cache if necessary
- Restart the application

#### Missing Results
**Symptoms**: Incomplete or missing analysis results
**Solutions**:
- Verify that all research plan tasks completed successfully
- Check data collection logs for errors
- Ensure sufficient data was collected
- Review synthesis and analysis agent logs
- Re-run failed tasks if necessary

### Getting Help

#### System Documentation
- **User Guide**: This comprehensive guide
- **API Documentation**: Technical reference for developers
- **FAQ**: Frequently asked questions and answers
- **Video Tutorials**: Step-by-step walkthroughs

#### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Community Forum**: Ask questions and share experiences
- **Email Support**: Direct assistance for critical issues
- **Documentation**: Self-service help and guides

#### Escalation Process
1. **Check documentation** and FAQ first
2. **Search existing issues** for similar problems
3. **Create detailed issue report** with:
   - System configuration
   - Steps to reproduce
   - Error messages and logs
   - Expected vs actual behavior
4. **Contact support** with issue details

---

**Need more help?** Check out our [FAQ](faq.md) or [contact support](support.md) for additional assistance.
