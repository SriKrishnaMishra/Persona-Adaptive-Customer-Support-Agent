"""
FastAPI Backend for Persona-Adaptive Customer Support Agent
Main application with all API endpoints
"""

import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from rag_system import get_rag_system
from persona_detection import get_persona_detector
from tone_adaptation import get_tone_adapter
from escalation_detection import get_escalation_detector

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Persona-Adaptive Customer Support Agent",
    description="AI-powered customer support with persona detection, RAG, and escalation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    persona: str
    response: str
    escalate: bool
    scam_risk: str
    sources: List[str]
    confidence: float
    conversation_id: str

class EscalationResponse(BaseModel):
    status: str
    escalation_package: Dict[str, Any]

class PersonaResponse(BaseModel):
    persona: str
    confidence: float
    reasoning: str
    key_indicators: List[str]

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]

# Global instances
rag_system = None
persona_detector = None
tone_adapter = None
escalation_detector = None

def initialize_components():
    """
    Initialize all system components
    """
    global rag_system, persona_detector, tone_adapter, escalation_detector
    
    try:
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        print("🚀 Initializing components...")
        
        # Initialize components
        rag_system = get_rag_system()
        persona_detector = get_persona_detector(openai_api_key)
        tone_adapter = get_tone_adapter()
        escalation_detector = get_escalation_detector(openai_api_key)
        
        print("✅ All components initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """
    Initialize components on startup
    """
    initialize_components()

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint for health check
    """
    return HealthResponse(
        status="healthy",
        components={
            "rag_system": "ready" if rag_system else "not_initialized",
            "persona_detector": "ready" if persona_detector else "not_initialized",
            "tone_adapter": "ready" if tone_adapter else "not_initialized",
            "escalation_detector": "ready" if escalation_detector else "not_initialized"
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user queries
    """
    try:
        # Step 1: Detect persona
        persona_result = persona_detector.detect_persona(request.query)
        persona = persona_result["persona"]
        confidence = persona_result["confidence"]
        
        # Step 2: Retrieve relevant knowledge
        search_result = rag_system.search_knowledge_base(request.query)
        context = search_result["context"]
        sources = search_result["sources"]
        
        # Step 3: Generate tone-adapted response
        if "No relevant information found" in context:
            # Use fallback response
            response_text = tone_adapter.get_fallback_response(persona, request.query)
        else:
            # Generate response using LLM (simplified for demo)
            response_text = generate_response_from_context(persona, context, request.query)
        
        # Step 4: Check for escalation
        escalation_result = escalation_detector.should_escalate(
            request.query, response_text, persona
        )
        
        # Step 5: Check for scam risk
        scam_result = escalation_detector.detect_scam_risk(request.query)
        
        return ChatResponse(
            persona=persona,
            response=response_text,
            escalate=escalation_result["escalate"],
            scam_risk=scam_result["scam_risk"],
            sources=sources,
            confidence=confidence,
            conversation_id=request.conversation_id or "default"
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/detect-persona", response_model=PersonaResponse)
async def detect_persona_endpoint(request: ChatRequest):
    """
    Detect persona from user query
    """
    try:
        result = persona_detector.detect_persona(request.query)
        
        return PersonaResponse(
            persona=result["persona"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            key_indicators=result["key_indicators"]
        )
        
    except Exception as e:
        print(f"❌ Error in persona detection: {e}")
        raise HTTPException(status_code=500, detail=f"Persona detection failed: {str(e)}")

@app.post("/escalate", response_model=EscalationResponse)
async def escalate_endpoint(request: ChatRequest):
    """
    Create escalation package for human agent
    """
    try:
        # Get full analysis
        persona_result = persona_detector.detect_persona(request.query)
        search_result = rag_system.search_knowledge_base(request.query)
        
        # Generate response
        response_text = generate_response_from_context(
            persona_result["persona"], 
            search_result["context"], 
            request.query
        )
        
        # Check escalation
        escalation_result = escalation_detector.should_escalate(
            request.query, response_text, persona_result["persona"]
        )
        
        # Create escalation package
        escalation_package = escalation_detector.create_escalation_package(
            query=request.query,
            persona=persona_result["persona"],
            context=search_result["context"],
            ai_response=response_text,
            escalation_info=escalation_result
        )
        
        return EscalationResponse(
            status="escalated" if escalation_result["escalate"] else "no_escalation",
            escalation_package=escalation_package
        )
        
    except Exception as e:
        print(f"❌ Error in escalation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Escalation failed: {str(e)}")

@app.get("/knowledge/search")
async def search_knowledge(q: str, k: int = 3):
    """
    Search knowledge base directly
    """
    try:
        result = rag_system.search_knowledge_base(q)
        return result
        
    except Exception as e:
        print(f"❌ Error in knowledge search: {e}")
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {str(e)}")

@app.get("/analytics/personas")
async def get_persona_analytics():
    """
    Get persona analytics (mock data for demo)
    """
    return {
        "total_queries": 1250,
        "persona_distribution": {
            "Technical Expert": 45,
            "Frustrated User": 30,
            "Business Executive": 25
        },
        "escalation_rate": 0.12,
        "scam_detection_rate": 0.03
    }

def generate_response_from_context(persona: str, context: str, query: str) -> str:
    """
    Generate response from context (simplified version for demo)
    In production, this would use OpenAI/LLM API
    """
    # Get tone-adapted prompt
    tone_prompt = tone_adapter.get_adapted_prompt(persona, context, query)
    
    # For demo purposes, create a simple response based on persona and context
    if "No relevant information found" in context:
        return tone_adapter.get_fallback_response(persona, query)
    
    # Simple rule-based response generation
    if persona == "Technical Expert":
        if "api" in query.lower() and "error" in query.lower():
            return "Based on the technical documentation, API errors typically occur due to authentication issues, invalid endpoints, or rate limiting. Check your API key validity, verify the endpoint URL, and review your request format. The system returns specific error codes to help with debugging."
        elif "account" in query.lower():
            return "For account setup, you'll need to generate an API key from your dashboard, ensure proper authentication, and configure your environment variables. The API key should be kept secure and rotated regularly."
        else:
            return f"Technical analysis of your query: {query}. Based on the available documentation, I recommend following the standard troubleshooting procedures outlined in the knowledge base."
    
    elif persona == "Frustrated User":
        return "I understand your frustration, and I'm here to help you resolve this issue quickly. Let me walk you through the solution step by step. We'll get this sorted out for you right away. Please follow these simple steps, and don't hesitate to ask if anything is unclear."
    
    elif persona == "Business Executive":
        return f"From a business perspective, addressing '{query}' efficiently is crucial for maintaining productivity. Our solution provides significant ROI through streamlined processes and reliable performance. The enterprise features ensure scalability and compliance with your business requirements."
    
    else:
        return "I'm here to help you with your question. Let me provide you with the information you need based on our knowledge base."

if __name__ == "__main__":
    print("🚀 Starting Persona-Adaptive Customer Support Agent Backend...")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found. Using rule-based fallbacks.")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
