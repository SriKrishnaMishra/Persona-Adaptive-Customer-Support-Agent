"""
Streamlit Frontend for Persona-Adaptive Customer Support Agent
Interactive chat interface with real-time persona detection and response generation
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, List
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Persona-Adaptive Customer Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .persona-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .technical-expert {
        background-color: #4caf50;
        color: white;
    }
    
    .frustrated-user {
        background-color: #ff9800;
        color: white;
    }
    
    .business-executive {
        background-color: #2196f3;
        color: white;
    }
    
    .escalation-warning {
        background-color: #ffebee;
        border: 1px solid #f44336;
        border-radius: 0.25rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .scam-warning {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 0.25rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .source-info {
        font-size: 0.75rem;
        color: #666;
        font-style: italic;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """
    Initialize session state variables
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"conv_{int(time.time())}"
    
    if "show_analytics" not in st.session_state:
        st.session_state.show_analytics = False

def call_api(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make API call to backend
    """
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {"error": str(e)}

def get_analytics() -> Dict[str, Any]:
    """
    Get analytics data
    """
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/personas", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"error": "Could not fetch analytics"}

def render_message(message: Dict[str, Any]):
    """
    Render a chat message with appropriate styling
    """
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message with persona and metadata
        persona_class = message["persona"].lower().replace(" ", "-")
        
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div>
                <span class="persona-badge {persona_class}">{message["persona"]}</span>
                <span style="font-size: 0.875rem; color: #666;">
                    Confidence: {message["confidence"]:.1%}
                </span>
            </div>
            <div style="margin-top: 0.5rem;">
                <strong>Assistant:</strong> {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show escalation warning if needed
        if message.get("escalate"):
            st.markdown("""
            <div class="escalation-warning">
                ⚠️ <strong>Escalation Recommended:</strong> This issue has been flagged for human agent review.
            </div>
            """, unsafe_allow_html=True)
        
        # Show scam warning if needed
        if message.get("scam_risk") in ["medium", "high"]:
            risk_color = "high" if message["scam_risk"] == "high" else "medium"
            st.markdown(f"""
            <div class="scam-warning">
                🔍 <strong>Scam Risk ({message["scam_risk"].upper()}):</strong> This message contains indicators of potential scam activity.
            </div>
            """, unsafe_allow_html=True)
        
        # Show sources if available
        if message.get("sources"):
            sources_text = ", ".join([s.split("/")[-1] for s in message["sources"]])
            st.markdown(f"""
            <div class="source-info">
                📚 Sources: {sources_text}
            </div>
            """, unsafe_allow_html=True)

def render_sidebar():
    """
    Render sidebar with controls and information
    """
    st.sidebar.title("🤖 Support Agent")
    
    # Connection status
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ Backend Connected")
        else:
            st.sidebar.error("❌ Backend Error")
    except:
        st.sidebar.error("❌ Backend Offline")
    
    # Conversation info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Conversation Info")
    st.sidebar.code(st.session_state.conversation_id)
    
    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = f"conv_{int(time.time())}"
        st.rerun()
    
    # Analytics toggle
    st.sidebar.markdown("---")
    if st.sidebar.button("📊 Show Analytics"):
        st.session_state.show_analytics = not st.session_state.show_analytics
        st.rerun()
    
    # Persona information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Persona Types")
    st.sidebar.markdown("""
    **👨‍💻 Technical Expert**
    - Uses technical language
    - Wants detailed solutions
    - Focuses on troubleshooting
    
    **😤 Frustrated User**
    - Expresses emotions
    - Needs empathy and quick help
    - May be angry or disappointed
    
    **👔 Business Executive**
    - Interested in ROI/value
    - Focuses on business impact
    - Wants high-level explanations
    """)

def render_analytics():
    """
    Render analytics dashboard
    """
    st.markdown("## 📊 Analytics Dashboard")
    
    analytics = get_analytics()
    
    if "error" in analytics:
        st.error("Could not load analytics data")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", analytics["total_queries"])
    
    with col2:
        st.metric("Escalation Rate", f"{analytics['escalation_rate']:.1%}")
    
    with col3:
        st.metric("Scam Detection Rate", f"{analytics['scam_detection_rate']:.1%}")
    
    with col4:
        st.metric("Active Conversations", len([m for m in st.session_state.messages if m["role"] == "user"]))
    
    # Persona distribution
    st.markdown("### Persona Distribution")
    persona_data = analytics["persona_distribution"]
    
    for persona, percentage in persona_data.items():
        st.progress(percentage / 100, text=f"{persona}: {percentage}%")

def main():
    """
    Main application function
    """
    initialize_session_state()
    
    # Header
    st.title("🤖 Persona-Adaptive Customer Support Agent")
    st.markdown("*AI-powered customer support with intelligent persona detection and tone adaptation*")
    
    # Render sidebar
    render_sidebar()
    
    # Show analytics if enabled
    if st.session_state.show_analytics:
        render_analytics()
        return
    
    # Chat interface
    st.markdown("## 💬 Chat Interface")
    
    # Display chat messages
    for message in st.session_state.messages:
        render_message(message)
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        
        # Show typing indicator
        with st.spinner("🤔 Analyzing your query..."):
            # Call API
            api_data = {
                "query": prompt,
                "conversation_id": st.session_state.conversation_id
            }
            
            response = call_api("/chat", api_data)
            
            if "error" not in response:
                # Add assistant response
                assistant_message = {
                    "role": "assistant",
                    "content": response["response"],
                    "persona": response["persona"],
                    "confidence": response["confidence"],
                    "escalate": response["escalate"],
                    "scam_risk": response["scam_risk"],
                    "sources": response["sources"],
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.messages.append(assistant_message)
            else:
                # Add error message
                error_message = {
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {response['error']}",
                    "persona": "Technical Expert",
                    "confidence": 0.0,
                    "escalate": False,
                    "scam_risk": "low",
                    "sources": [],
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.messages.append(error_message)
        
        # Rerun to display new messages
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.875rem;'>
        Powered by AI • Persona Detection • RAG Knowledge Base • Tone Adaptation • Escalation Detection
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
