# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Main Rules

- For file edit, search or move, use FilesystemMCP.
- For package documentation always use the Context7 MCP.
- For research tasks you can use the Perplexity MCP.
- Always check the MCPs you have access to before each task or conversation.

## Development Commands

### Backend Development

```bash
# CrewAI backend (production)
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev  # Development server on port 3000
npm run build  # Production build
npm run lint  # ESLint checks
```

### Database Operations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Reset everything
docker-compose down -v && docker-compose up -d
```

### Testing

```bash
# Backend tests
cd backend
pytest -v
pytest tests/test_agents.py::test_specific_function  # Single test

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

## Architecture Overview

### Production Architecture (CrewAI)

This codebase uses CrewAI for simplified multi-agent orchestration:

**`backend/` - CrewAI System (PRODUCTION)**

- Simplified agent collaboration using CrewAI
- Preserves all agent knowledge and capabilities from original design
- Modern dependency stack (June 2025)
- High document quality with 40% less code complexity
- FastAPI + PostgreSQL + Redis + Pinecone
- Real-time WebSocket streaming

### Multi-Agent Architecture

Nine specialized agents work collaboratively:

1. **Orchestrator**: Flow management and routing
2. **Product Manager**: PRD/BRD generation with business focus
3. **Designer**: UXDD creation with accessibility compliance
4. **Database Engineer**: ERD generation with Mermaid diagrams
5. **Software Engineer**: SRS following IEEE 29148 standards
6. **User Researcher**: Persona development and journey mapping
7. **Business Analyst**: Requirements analysis and stakeholder mapping
8. **Solution Architect**: System design and integration patterns
9. **Review Agent**: Quality assurance and validation

### Document Generation Pipeline

```
User Input → Intent Analysis → Agent Routing → Template Processing → LLM Enhancement → Quality Review → Document Output
```

Each agent maintains:

- Specialized question frameworks (11 product questions, 8 design questions, etc.)
- Industry-standard templates (255-line PRD template, 319-line UXDD template)
- Quality validation criteria and completeness scoring

### Real-time Communication

- **WebSocket Architecture**: Token-level streaming for responsive UX
- **Agent Status Broadcasting**: Live updates on agent execution
- **Error Recovery**: Automatic reconnection and state restoration
- **Progress Tracking**: Visual progress indicators for long-running tasks

## Key Configuration

### Environment Variables

Critical variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/agentpm
REDIS_URL=redis://localhost:6379

# LLM Providers (primary/fallback strategy)
ANTHROPIC_API_KEY=  # Primary: Claude-3.5-Sonnet, Claude-4-Opus/Sonnet
OPENAI_API_KEY=     # Fallback: GPT-4o, GPT-4.5
GOOGLE_API_KEY=     # Alternative: Gemini-2.5-Pro, Gemini-2.0-Flash

# Vector Store
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=

# Observability
LANGFUSE_PUBLIC_KEY=   # LLM monitoring
LANGFUSE_SECRET_KEY=
```

### Agent Configuration

Agent models configured in `backend/core/config.py`:

- Default: `claude-3-5-sonnet-20241022` for best overall performance
- Quality Mode: `claude-4-opus` for complex reasoning (when available)
- Speed Mode: `gpt-4o-2024-11-20` for fast responses
- Budget Mode: `gemini-2.0-flash-exp` for cost-effective generation
- Dynamic selection: Users can choose models per conversation

## Template System

### YAML-Based Templates

All document templates in `backend/templates/`:

- **Core Documents**: PRD, BRD, SRS, UXDD
- **Technical Specs**: ERD, DBRD, API specifications
- **Design Artifacts**: Wireframes, design systems, journey maps

### Template Processing

1. **Structure Definition**: YAML defines sections, questions, validation rules
2. **Dynamic Content**: LLM generates contextual content for each section
3. **Quality Enhancement**: Secondary LLM pass for consistency and completeness
4. **Markdown Output**: Final documents in professional markdown format

## Production System Benefits

### CrewAI Architecture Advantages

- **Quality-First Approach**: 15 iterations, no time limits for comprehensive analysis
- **Dynamic Model Selection**: Choose between Claude, GPT, and Gemini models
- **40% Code Reduction**: Less orchestration boilerplate
- **Modern Dependencies**: June 2025 stack with latest AI models

### Preserved Agent Expertise

All specialized knowledge maintained:

- Question frameworks and decision patterns
- Template content and validation logic
- Specialized prompts and instructions
- Document quality standards

## Data Flow

### Conversation State Management

- **Redis Persistence**: Conversation checkpoints and recovery
- **Database Storage**: Permanent conversation and document history
- **Vector Store**: RAG-enabled context retrieval from past conversations

### Document Generation Flow

1. **User Input**: Natural language requirements
2. **Intent Analysis**: Orchestrator determines document types needed
3. **Agent Execution**: Specialized agents generate content sections
4. **Template Processing**: Jinja2 + LLM enhancement
5. **Quality Review**: Automated validation and human-readable feedback
6. **Export Options**: Markdown, PDF, integration with external tools

### RAG Integration

- **Pinecone Vector Store**: Semantic search in conversation history
- **Document Chunking**: Intelligent splitting for large documents
- **Context Synthesis**: Combine insights from multiple past projects

## Development Patterns

### Agent Development

When modifying agents:

1. Update CrewAI agents in `backend/agents/`
2. Preserve question frameworks in agent classes
3. Maintain template compatibility
4. Test document generation quality

### Frontend Integration

- **WebSocket Connection**: Auto-reconnecting client in `hooks/useWebSocket.ts`
- **State Management**: Zustand stores in `lib/stores/`
- **Error Boundaries**: Comprehensive error handling for agent failures
- **Progressive Enhancement**: SSR-compatible with client-side features

### Database Schema

- **Conversations**: Core conversation metadata and state
- **Messages**: Individual agent interactions and responses
- **Documents**: Generated document storage with versioning
- **Analytics**: LLM usage tracking and cost monitoring

## Observability

### Langfuse Integration

Comprehensive LLM monitoring:

- **Token Usage**: Track costs per conversation and agent
- **Performance Metrics**: Response times and quality scores
- **Conversation Flows**: Visualize agent interaction patterns
- **Error Tracking**: Debug failed generations and recovery

### Structured Logging

All logs include:

- `conversation_id`: For request correlation
- `agent_id`: Agent-specific context
- `document_type`: Current generation target
- `cost_tracking`: Token usage and pricing

## Production Considerations

### Scalability

- **Horizontal Scaling**: Queue-based agent execution
- **Database Optimization**: Indexed queries and connection pooling
- **Caching Strategy**: Redis for frequently accessed data
- **Rate Limiting**: API protection and cost control

### Security

- **Input Validation**: Comprehensive sanitization for LLM inputs
- **API Key Management**: Secure credential handling
- **Audit Logging**: Complete request/response tracking
- **Access Control**: Role-based permissions (planned Auth0 integration)

### Cost Management

- **Token Budgets**: Per-user and per-conversation limits
- **Model Selection**: Automatic fallback to cheaper models when appropriate
- **Caching**: Avoid duplicate LLM calls for similar requests
- **Monitoring**: Real-time cost tracking and alerts

## Quality-First Implementation (June 2025)

### Available AI Models

The system supports the latest models from major providers:

#### Anthropic Claude Models

- **Claude 3.5 Sonnet** (`claude-3-5-sonnet-20241022`): Best overall performance
  - 200K context window
  - Excellent coding and reasoning abilities
  - $3/$15 per million tokens (input/output)
- **Claude 4 Opus** (when available): Deepest reasoning and analysis
  - Extended thinking mode for complex problems
  - First model with ASL-3 safety protocols
- **Claude 4 Sonnet**: Free tier available with strong capabilities

#### OpenAI GPT Models

- **GPT-4o** (`gpt-4o-2024-11-20`): Fast multimodal processing
  - 128K context window
  - 116 tokens/sec processing speed
  - Strong all-around performance
- **GPT-4.5**: Premium model for Pro users
  - Improved reasoning and emotional intelligence
  - Reduced hallucination rates

#### Google Gemini Models

- **Gemini 2.5 Pro**: Million-token context window
  - Best for large document processing
  - Thinking model with chain-of-thought reasoning
- **Gemini 2.0 Flash** (`gemini-2.0-flash-exp`): Best value option
  - 250 tokens/sec (fastest processing)
  - $0.4 per million tokens
  - 90% coding ability benchmark

### Quality Configuration

```python
# backend/config.py settings
crew_max_iter: int = 15          # Increased from 5
crew_max_execution_time = None   # No time limits
crew_cache: bool = False         # Fresh analysis each time
max_tokens = 8192               # Increased from 4096
```

### Enhanced Agent Prompts

- **5-Pass Analysis Framework**: Surface → Hidden → Edge Cases → Long-term → Validation
- **Multi-Perspective Analysis**: Business, Technical, User, Risk, Future
- **Self-Review Questions**: Quality checkpoints throughout generation
- **Investor-Grade Documentation**: 4000-6000 word comprehensive documents

### Frontend Model Selection

Users can select their preferred model directly in the UI:

- Dropdown in conversation starter
- Model persisted per conversation
- Real-time model switching via WebSocket
