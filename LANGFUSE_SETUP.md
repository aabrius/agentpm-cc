# Langfuse Observability Integration

This document explains how to set up and use Langfuse for observability in AgentPM.

## What is Langfuse?

Langfuse is an open-source observability platform for LLM applications that provides:

- **Tracing**: Track conversation flows across multiple agents
- **Token Usage**: Monitor token consumption and costs by model
- **Performance**: Analyze response times and success rates
- **Analytics**: Gain insights into system usage patterns
- **Debugging**: Debug failed conversations and agent interactions

## Setup Instructions

### 1. Create Langfuse Account

1. Go to [cloud.langfuse.com](https://cloud.langfuse.com) or set up self-hosted Langfuse
2. Create an account and project
3. Get your API keys from the project settings

### 2. Configure Environment Variables

Add these to your `.env` file:

```bash
# Langfuse Observability
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Install Dependencies

The Langfuse dependency is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Features Implemented

### 🔍 **Conversation Tracing**

Every conversation is automatically traced with:
- Conversation ID and type (idea/feature/tool)
- Agent interactions and handoffs
- Message flow between agents
- Phase transitions (discovery → definition → review)

### 📊 **LLM Call Monitoring**

All LLM calls are tracked with:
- Model used (Claude, GPT-4, etc.)
- Input and output tokens
- Response time
- Cost estimation
- Success/failure status

### 🤖 **Agent Performance**

Each agent's performance is monitored:
- Response times
- Success rates
- Error counts
- Token usage per agent

### 📋 **Document Generation Tracking**

Document generation is tracked with:
- Generation time
- Success/failure status
- Document types generated
- Quality metrics

## API Endpoints

The following analytics endpoints are available:

### System Overview
```
GET /api/v1/analytics/system/overview
```

### Conversation Analytics
```
GET /api/v1/analytics/conversations/{id}/metrics
GET /api/v1/analytics/conversations/{id}/flow
GET /api/v1/analytics/conversations/{id}/export
```

### Agent Performance
```
GET /api/v1/analytics/agents/{id}/metrics
```

### Token & Cost Analysis
```
GET /api/v1/analytics/system/tokens
GET /api/v1/analytics/system/costs?group_by=agent
```

### Full Reports
```
GET /api/v1/analytics/reports/full
```

## Usage Examples

### Basic Health Check

```bash
curl http://localhost:8000/api/v1/analytics/health
```

### Get System Overview

```bash
curl http://localhost:8000/api/v1/analytics/system/overview
```

### Get Conversation Metrics

```bash
curl http://localhost:8000/api/v1/analytics/conversations/abc-123/metrics
```

### Get Token Usage

```bash
curl http://localhost:8000/api/v1/analytics/system/tokens
```

### Get Cost Breakdown by Agent

```bash
curl http://localhost:8000/api/v1/analytics/system/costs?group_by=agent
```

## Langfuse Dashboard

Once configured, you can view rich analytics in the Langfuse dashboard:

1. **Traces**: See complete conversation flows
2. **Generations**: View all LLM calls with prompts and responses
3. **Users**: Track usage by conversation type
4. **Sessions**: Group related conversations
5. **Datasets**: Build datasets for evaluation
6. **Experiments**: A/B test different prompts and models

## Key Metrics Tracked

### Conversation Level
- Total messages exchanged
- Conversation duration
- Agents involved
- Documents generated
- Success/failure status
- Token usage and costs

### Agent Level
- Response times
- Success rates
- Error frequencies
- Token consumption
- Handoff patterns

### System Level
- Total conversations
- Most active agents
- Popular conversation types
- Daily/weekly trends
- Cost optimization opportunities

## Data Privacy

- All data is processed according to Langfuse's privacy policy
- No sensitive user data is logged in traces
- Only conversation metadata and analytics are stored
- You can use self-hosted Langfuse for complete data control

## Troubleshooting

### Langfuse Not Working?

1. **Check environment variables**: Ensure keys are correctly set
2. **Verify connectivity**: Test API connection to Langfuse
3. **Check logs**: Look for Langfuse-related error messages
4. **API limits**: Ensure you haven't exceeded rate limits

### Missing Data?

1. **Flush events**: Call `/api/v1/analytics/flush` to force event upload
2. **Check filters**: Verify date ranges in analytics queries
3. **Async processing**: Allow some time for data to appear in dashboard

### Common Error Messages

- `"Analytics not available - Langfuse not configured"`: Set environment variables
- `"Failed to initialize Langfuse"`: Check API keys and connectivity
- `"Failed to track LLM call"`: Network or configuration issue

## Benefits

✅ **Production Monitoring**: Track system health and performance  
✅ **Cost Optimization**: Identify expensive operations and optimize  
✅ **Quality Assurance**: Monitor conversation success rates  
✅ **Debugging**: Quickly identify and fix issues  
✅ **Analytics**: Understand usage patterns and user behavior  
✅ **Compliance**: Maintain audit logs for conversations  

## Next Steps

1. Set up Langfuse account and configure environment variables
2. Start a conversation and check the Langfuse dashboard
3. Explore the analytics API endpoints
4. Set up alerts for important metrics
5. Use data to optimize agent performance and costs

For more information, visit the [Langfuse documentation](https://langfuse.com/docs).