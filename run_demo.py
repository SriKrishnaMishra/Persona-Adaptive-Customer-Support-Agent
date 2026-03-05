"""
Demo script to test the Persona-Adaptive Customer Support Agent
Runs a series of test queries to demonstrate all capabilities
"""

import requests
import json
import time
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_api_connection() -> bool:
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_query(query: str, conversation_id: str = None) -> Dict[str, Any]:
    """Send a query to the chat API"""
    data = {
        "query": query,
        "conversation_id": conversation_id or f"demo_{int(time.time())}"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat", json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def print_demo_header():
    """Print demo header"""
    print("🤖" * 20)
    print("🤖 PERSONA-ADAPTIVE CUSTOMER SUPPORT DEMO")
    print("🤖" * 20)
    print()

def print_query_result(query: str, result: Dict[str, Any]):
    """Print formatted query result"""
    print(f"👤 USER: {query}")
    print()
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        print()
        return
    
    # Persona information
    persona_emoji = {
        "Technical Expert": "👨‍💻",
        "Frustrated User": "😤", 
        "Business Executive": "👔"
    }
    
    emoji = persona_emoji.get(result["persona"], "🤖")
    print(f"{emoji} PERSONA: {result['persona']} (Confidence: {result['confidence']:.1%})")
    
    # Response
    print(f"🤖 ASSISTANT: {result['response']}")
    
    # Warnings
    if result.get("escalate"):
        print("⚠️  ESCALATION: Flagged for human agent review")
    
    if result.get("scam_risk") in ["medium", "high"]:
        print(f"🔍 SCAM RISK: {result['scam_risk'].upper()}")
    
    # Sources
    if result.get("sources"):
        sources = [s.split("/")[-1] for s in result["sources"]]
        print(f"📚 SOURCES: {', '.join(sources)}")
    
    print("-" * 60)
    print()

def run_demo():
    """Run the complete demo"""
    print_demo_header()
    
    # Check API connection
    print("🔍 Checking API connection...")
    if not test_api_connection():
        print("❌ API is not running! Please start the backend first:")
        print("   cd backend && python main.py")
        return
    print("✅ API is running!")
    print()
    
    # Test queries for each persona
    test_queries = [
        # Technical Expert queries
        ("I'm getting a 500 error when calling the API endpoint", "Technical Expert"),
        ("How do I implement authentication with the API?", "Technical Expert"),
        ("What's the rate limit for API requests?", "Technical Expert"),
        
        # Frustrated User queries  
        ("This product is completely useless and nothing works!", "Frustrated User"),
        ("I'm very frustrated with the service and want a refund", "Frustrated User"),
        ("Why is this so complicated? I can't get anything to work", "Frustrated User"),
        
        # Business Executive queries
        ("What's the ROI for the enterprise plan?", "Business Executive"),
        ("How does this solution scale for large organizations?", "Business Executive"),
        ("What are the compliance and security features?", "Business Executive"),
        
        # Escalation test
        ("I want to speak to a manager immediately and cancel my subscription", "Escalation"),
        
        # Scam detection test
        ("Please share your OTP so I can verify your account", "Scam Detection"),
    ]
    
    print("🚀 Running demo queries...")
    print()
    
    conversation_id = f"demo_{int(time.time())}"
    
    for i, (query, expected_persona) in enumerate(test_queries, 1):
        print(f"📝 Test {i}/{len(test_queries)} - Expected: {expected_persona}")
        print()
        
        result = send_query(query, conversation_id)
        print_query_result(query, result)
        
        # Small delay between queries
        time.sleep(1)
    
    print("🎉 Demo completed!")
    print()
    print("💡 To try your own queries:")
    print("   1. Start the frontend: cd frontend && streamlit run app.py")
    print("   2. Open http://localhost:8501 in your browser")
    print("   3. Start chatting with the AI assistant!")

def test_individual_components():
    """Test individual API endpoints"""
    print("🧪 Testing individual components...")
    print()
    
    # Test persona detection
    print("👤 Testing Persona Detection:")
    test_query = "I'm getting API authentication errors"
    data = {"query": test_query}
    
    try:
        response = requests.post(f"{API_BASE_URL}/detect-persona", json=data, timeout=10)
        result = response.json()
        print(f"   Query: {test_query}")
        print(f"   Persona: {result['persona']} ({result['confidence']:.1%})")
        print(f"   Reasoning: {result['reasoning']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test knowledge search
    print("📚 Testing Knowledge Search:")
    search_query = "API troubleshooting"
    
    try:
        response = requests.get(f"{API_BASE_URL}/knowledge/search", params={"q": search_query}, timeout=10)
        result = response.json()
        print(f"   Query: {search_query}")
        print(f"   Context length: {len(result.get('context', ''))} characters")
        print(f"   Sources: {result.get('sources', [])}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test analytics
    print("📊 Testing Analytics:")
    
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/personas", timeout=10)
        result = response.json()
        print(f"   Total queries: {result.get('total_queries', 'N/A')}")
        print(f"   Escalation rate: {result.get('escalation_rate', 'N/A'):.1%}")
        print(f"   Persona distribution: {result.get('persona_distribution', {})}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--components":
        test_individual_components()
    else:
        run_demo()
