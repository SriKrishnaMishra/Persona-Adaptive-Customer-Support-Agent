# 🏗️ Architecture Documentation

## System Overview

The Persona-Adaptive Customer Support Agent is built on a **microservice architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Streamlit     │    │   Web Browser   │                │
│  │   Chat UI       │◄──►│   Interface     │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                    Backend Layer                            │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   FastAPI       │    │   AI Services   │                │
│  │   Orchestration │◄──►│   (OpenAI/LLM)  │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   ChromaDB      │    │   Knowledge     │                │
│  │   Vector Store  │◄──►│   Base Files    │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend (`frontend/app.py`)

**Responsibilities:**
- User interface and interaction
- Real-time chat display
- Persona visualization
- Analytics dashboard

**Key Features:**
- WebSocket-ready for real-time updates
- Responsive design
- Component-based architecture
- State management

### 2. Backend API (`backend/main.py`)

**Responsibilities:**
- HTTP request handling
- Business logic orchestration
- Component coordination
- API documentation

**Key Features:**
- FastAPI with automatic docs
- Pydantic models for validation
- CORS support
- Error handling

### 3. Core Components

#### Persona Detection (`backend/persona_detection.py`)
```
User Query → LLM Analysis → Persona Classification → Confidence Score
     ↓
Rule-based Fallback → Keyword Matching → Final Persona Result
```

#### RAG System (`backend/rag_system.py`)
```
Documents → Chunking → Embedding → Vector Store
     ↑
Query → Encoding → Similarity Search → Context Retrieval
```

#### Tone Adaptation (`backend/tone_adaptation.py`)
```
Persona + Context → Template Selection → Prompt Engineering → Response
```

#### Escalation Detection (`backend/escalation_detection.py`)
```
Query + Response → Analysis → Risk Assessment → Escalation Decision
```

## Data Flow Architecture

### Request Processing Pipeline
```
1. User Input (Streamlit)
   ↓
2. HTTP Request (FastAPI)
   ↓
3. Persona Detection
   ↓
4. Knowledge Retrieval (RAG)
   ↓
5. Tone Adaptation
   ↓
6. Response Generation
   ↓
7. Escalation Check
   ↓
8. Response Delivery
```

### Data Storage Architecture
```
Knowledge Base Files
   ↓ (Document Loading)
Text Chunks
   ↓ (Embedding Generation)
Vector Embeddings
   ↓ (Storage)
ChromaDB Vector Store
```

## Security Architecture

### Input Validation
- Pydantic model validation
- SQL injection prevention
- XSS protection
- Input sanitization

### Authentication & Authorization
- API key management
- Environment variable security
- Request rate limiting
- CORS configuration

### Data Protection
- No sensitive data persistence
- Secure API key handling
- Input/output validation
- Error message sanitization

## Performance Architecture

### Caching Strategy
- Vector similarity caching
- Persona detection caching
- Response template caching

### Scalability Design
- Stateless API design
- Horizontal scaling ready
- Load balancer compatible
- Microservice architecture

### Optimization Techniques
- Document chunking optimization
- Embedding model selection
- Async processing support
- Connection pooling

## Deployment Architecture

### Development Environment
```
Local Machine
├── Python 3.8+
├── Virtual Environment
├── Local ChromaDB
└── Development Servers
```

### Production Environment (Recommended)
```
Cloud Infrastructure
├── Load Balancer
├── API Gateway
├── Container Orchestration (Kubernetes/Docker)
├── Managed Database
├── Monitoring & Logging
└── CI/CD Pipeline
```

## Technology Stack Matrix

| Layer | Technology | Purpose |
|-------|-------------|---------|
| Frontend | Streamlit | Web UI |
| Backend | FastAPI | API Framework |
| AI/ML | OpenAI GPT-3.5 | LLM Processing |
| Embeddings | Sentence Transformers | Text Vectorization |
| Vector DB | ChromaDB | Semantic Search |
| Framework | LangChain | LLM Orchestration |
| Language | Python | Core Development |
| Deployment | Uvicorn | ASGI Server |

## Monitoring & Observability

### Metrics Collection
- API response times
- Persona detection accuracy
- Knowledge retrieval performance
- Escalation rates
- Error rates

### Logging Strategy
- Structured logging
- Component-level logs
- Request/Response logging
- Error tracking

### Health Checks
- API endpoint health
- Database connectivity
- AI service availability
- System resource monitoring

## Future Architecture Enhancements

### Planned Improvements
1. **Multi-modal Support**: Handle images, documents
2. **Advanced Analytics**: ML-based insights
3. **Multi-language Support**: Internationalization
4. **Voice Interface**: Speech-to-text integration
5. **Mobile App**: React Native frontend

### Scalability Roadmap
1. **Microservices Split**: Separate components
2. **Event Streaming**: Kafka/RabbitMQ integration
3. **Distributed Caching**: Redis implementation
4. **Database Sharding**: Multi-region deployment

This architecture ensures the system is **production-ready**, **scalable**, and **maintainable** while following industry best practices.
