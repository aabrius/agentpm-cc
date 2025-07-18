# AgentPM - Quality-First Multi-Agent Documentation Platform

AgentPM is an intelligent multi-agent system powered by CrewAI that generates investor-grade documentation through conversational AI. Built with a quality-first approach featuring multi-pass document generation, enhanced agent prompts, and dynamic model selection.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- API Keys for:
  - Anthropic (Claude 3.5 Sonnet, Claude 4 Opus/Sonnet)
  - OpenAI (GPT-4o, GPT-4.5 Turbo) 
  - Google (Gemini 2.5 Pro, Gemini 2.0 Flash)
  - Pinecone (vector store)
  - Langfuse (observability - optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/aabrius/agentpm-cc.git
   cd agentpm-cc
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│  FastAPI Backend │
└─────────────────┘     └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   Orchestrator   │
                        │      Agent       │
                        └─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PM Agent      │     │ Designer Agent   │     │ Engineer Agent   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 📁 Project Structure

```
agentpm-cc/
├── backend/          # FastAPI backend
│   ├── agents/       # Agent implementations
│   ├── api/          # API endpoints
│   ├── core/         # Core utilities
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── templates/    # Document templates
├── frontend/         # Next.js frontend
│   ├── app/          # App router
│   ├── components/   # React components
│   └── lib/          # Utilities
├── generated_docs/   # Generated documents
└── docker-compose.yml
```

## 💻 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## ⭐ Key Features

### Quality-First Architecture (June 2025)
- **Multi-Pass Document Generation**: 5-pass review system (Structure → Content → Clarity → Strategy → Excellence)
- **Dynamic Model Selection**: Choose between latest AI models (Claude 4, GPT-4.5, Gemini 2.5)
- **Quality Levels**: Draft, Standard, Premium, Excellence (up to 95%+ quality scores)
- **Enhanced Agent Prompts**: 5-pass analysis framework with multi-perspective evaluation

### Core Platform Features
- **9 Specialized Agents**: Orchestrator, PM, Designer, Engineer, User Researcher, Business Analyst, Solution Architect, Database Engineer, Review Agent
- **Real-time Chat**: WebSocket-based conversational interface with token-level streaming
- **Comprehensive Documents**: PRD, BRD, SRS, UXDD, ERD, API specs, and more
- **Template-based**: Industry-standard document templates with 255+ line PRD template
- **RAG Integration**: Context-aware responses using Pinecone vector search
- **Cross-Document Consistency**: Batch processing with consistency validation
- **Observability**: Full LLM monitoring with Langfuse integration

## 🧪 Quality Testing

Run the comprehensive quality improvement test suite:

```bash
python test_quality_improvements.py
```

This validates:
- Multi-pass document generation with complex ideas
- Quality score improvements across different models
- Batch processing with consistency validation
- Model performance comparison (Claude, GPT, Gemini)

## 🔄 Development Workflow

### Quality Levels
- **Draft**: Basic structure, 1 pass, 5-minute limit
- **Standard**: Complete content, 2 passes, 10-minute limit  
- **Premium**: Enhanced quality, 3 passes, no time limits
- **Excellence**: 5-pass refinement, 95%+ quality target

### Agent Enhancement
- All agents use enhanced prompts with 5-pass analysis
- Sequential processing for quality control
- 15-25 iterations for comprehensive analysis
- Multi-perspective evaluation framework

## 📚 Documentation

- [Product Requirements Document](PRD.md)
- [Development TODO](TODO.md)
- [API Documentation](http://localhost:8000/docs)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## 📄 License

[To be determined]