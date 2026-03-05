"""
Escalation and Scam Detection Module
Detects when to escalate to human agents and identifies potential scam attempts
"""

import json
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI

class EscalationDetector:
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize escalation detector with OpenAI client
        """
        self.client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.escalation_prompt = self._get_escalation_prompt()
        self.scam_prompt = self._get_scam_prompt()
        
        # Rule-based escalation keywords
        self.escalation_keywords = [
            "refund", "complaint", "cancel subscription", "angry", "not working",
            "lawsuit", "legal action", "sue", "disappointed", "terrible service",
            "manager", "supervisor", "escalate", "unacceptable", "worst experience"
        ]
        
        # Scam detection keywords
        self.scam_keywords = [
            "otp", "one time password", "verification code", "bank details",
            "credit card", "social security", "ssn", "password", "share your",
            "urgent", "immediate payment", "wire transfer", "gift card",
            "bitcoin", "cryptocurrency", "verify account", "suspicious activity"
        ]
    
    def _get_escalation_prompt(self) -> str:
        """
        Get the prompt for escalation detection
        """
        return """
You are a customer support escalation specialist. Determine if the customer issue should be escalated to a human agent.

ESCALATION CRITERIA:
- Customer is extremely angry or frustrated
- Legal threats or mentions of lawsuits
- Refund demands or cancellation requests
- Complex technical issues beyond AI capability
- Security or compliance concerns
- Multiple failed attempts to resolve
- Customer specifically requests human agent

User Message: {query}
AI Response: {response}

Return JSON format:
{
    "escalate": true/false,
    "reason": "Brief explanation of escalation decision",
    "urgency": "low|medium|high|critical",
    "recommended_action": "specific action for human agent"
}
"""
    
    def _get_scam_prompt(self) -> str:
        """
        Get the prompt for scam detection
        """
        return """
You are a cybersecurity AI detecting potential scam attempts in customer support conversations.

SCAM INDICATORS:
- Requesting sensitive information (OTP, passwords, bank details)
- Urgency tactics ("immediate action required")
- Payment requests via unusual methods (gift cards, wire transfers)
- Impersonation attempts
- Phishing links or suspicious URLs
- Requests for account verification with personal data

Analyze this message for scam risk:

User Message: {query}

Return JSON format:
{
    "scam_risk": "low|medium|high",
    "reason": "Explanation of risk assessment",
    "indicators": ["list", "of", "detected", "indicators"],
    "recommended_action": "monitor|block|investigate"
}
"""
    
    def should_escalate(self, query: str, ai_response: str, persona: str) -> Dict[str, Any]:
        """
        Determine if the issue should be escalated to a human agent
        """
        try:
            # If no OpenAI client, use rule-based detection
            if not self.client:
                return self._rule_based_escalation(query, persona)
            
            # Use LLM for escalation detection
            prompt = self.escalation_prompt.format(query=query, response=ai_response)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an escalation detection expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(result_text)
                if not all(key in result for key in ["escalate", "reason", "urgency", "recommended_action"]):
                    raise ValueError("Missing required fields")
                return result
            except json.JSONDecodeError:
                return self._rule_based_escalation(query, persona)
                
        except Exception as e:
            print(f"❌ Error in escalation detection: {e}")
            return self._rule_based_escalation(query, persona)
    
    def _rule_based_escalation(self, query: str, persona: str) -> Dict[str, Any]:
        """
        Rule-based escalation detection as fallback
        """
        query_lower = query.lower()
        
        # Count escalation keywords
        escalation_count = sum(1 for kw in self.escalation_keywords if kw in query_lower)
        
        # Determine escalation based on keywords and persona
        escalate = False
        urgency = "low"
        reason = "No escalation needed"
        recommended_action = "Continue AI support"
        
        if escalation_count >= 3:
            escalate = True
            urgency = "high"
            reason = "Multiple escalation keywords detected"
            recommended_action = "Immediate human agent intervention"
        elif escalation_count >= 2:
            escalate = True
            urgency = "medium"
            reason = "Escalation keywords present"
            recommended_action = "Human agent review required"
        elif "frustrated" in persona.lower() and escalation_count >= 1:
            escalate = True
            urgency = "medium"
            reason = "Frustrated user with escalation indicators"
            recommended_action = "Human agent to handle with empathy"
        elif "manager" in query_lower or "supervisor" in query_lower:
            escalate = True
            urgency = "medium"
            reason = "Customer requested supervisor"
            recommended_action = "Connect to team lead or manager"
        
        return {
            "escalate": escalate,
            "reason": reason,
            "urgency": urgency,
            "recommended_action": recommended_action
        }
    
    def detect_scam_risk(self, query: str) -> Dict[str, Any]:
        """
        Detect potential scam attempts in user messages
        """
        try:
            # If no OpenAI client, use rule-based detection
            if not self.client:
                return self._rule_based_scam_detection(query)
            
            # Use LLM for scam detection
            prompt = self.scam_prompt.format(query=query)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(result_text)
                if not all(key in result for key in ["scam_risk", "reason", "indicators", "recommended_action"]):
                    raise ValueError("Missing required fields")
                return result
            except json.JSONDecodeError:
                return self._rule_based_scam_detection(query)
                
        except Exception as e:
            print(f"❌ Error in scam detection: {e}")
            return self._rule_based_scam_detection(query)
    
    def _rule_based_scam_detection(self, query: str) -> Dict[str, Any]:
        """
        Rule-based scam detection as fallback
        """
        query_lower = query.lower()
        
        # Count scam keywords
        scam_count = sum(1 for kw in self.scam_keywords if kw in query_lower)
        
        # Find specific indicators
        indicators_found = []
        for kw in self.scam_keywords:
            if kw in query_lower:
                indicators_found.append(kw)
        
        # Determine risk level
        if scam_count >= 4:
            risk_level = "high"
            action = "block"
            reason = "Multiple high-risk scam indicators detected"
        elif scam_count >= 2:
            risk_level = "medium"
            action = "investigate"
            reason = "Potential scam indicators present"
        elif scam_count >= 1:
            risk_level = "low"
            action = "monitor"
            reason = "Minor scam indicators detected"
        else:
            risk_level = "low"
            action = "monitor"
            reason = "No significant scam indicators"
        
        return {
            "scam_risk": risk_level,
            "reason": reason,
            "indicators": indicators_found,
            "recommended_action": action
        }
    
    def create_escalation_package(self, query: str, persona: str, context: str, 
                                ai_response: str, escalation_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive package for human agent handoff
        """
        return {
            "status": "escalated",
            "timestamp": self._get_timestamp(),
            "customer_info": {
                "persona": persona,
                "query": query,
                "query_length": len(query),
                "sentiment": self._analyze_sentiment(query)
            },
            "ai_analysis": {
                "retrieved_context": context,
                "ai_response": ai_response,
                "escalation_reason": escalation_info["reason"],
                "urgency": escalation_info["urgency"],
                "recommended_action": escalation_info["recommended_action"]
            },
            "handoff_instructions": {
                "priority": escalation_info["urgency"],
                "suggested_approach": self._get_handoff_approach(persona, escalation_info),
                "key_points_to_address": self._extract_key_points(query, context)
            }
        }
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis
        """
        positive_words = ["good", "great", "excellent", "helpful", "thanks"]
        negative_words = ["bad", "terrible", "awful", "frustrated", "angry", "disappointed"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    def _get_handoff_approach(self, persona: str, escalation_info: Dict[str, Any]) -> str:
        """
        Get suggested approach for human agent
        """
        approaches = {
            "Technical Expert": "Provide detailed technical support and advanced troubleshooting",
            "Frustrated User": "Start with empathy, apologize for issues, focus on quick resolution",
            "Business Executive": "Focus on business impact, value, and efficient resolution"
        }
        
        base_approach = approaches.get(persona, "Provide standard support")
        
        if escalation_info["urgency"] == "critical":
            return f"URGENT: {base_approach} - Immediate attention required"
        elif escalation_info["urgency"] == "high":
            return f"HIGH PRIORITY: {base_approach} - Handle with care"
        else:
            return base_approach
    
    def _extract_key_points(self, query: str, context: str) -> List[str]:
        """
        Extract key points from query and context for human agent
        """
        key_points = []
        
        # Extract main topics from query
        if "api" in query.lower():
            key_points.append("API-related issue")
        if "error" in query.lower():
            key_points.append("Error handling required")
        if "account" in query.lower():
            key_points.append("Account management issue")
        if "billing" in query.lower() or "payment" in query.lower():
            key_points.append("Billing/payment concern")
        
        # Add context availability
        if context and "No relevant information found" not in context:
            key_points.append("Knowledge base information available")
        else:
            key_points.append("May need additional resources")
        
        return key_points

# Singleton instance
escalation_detector = None

def get_escalation_detector(openai_api_key: Optional[str] = None) -> EscalationDetector:
    """
    Get or create escalation detector instance
    """
    global escalation_detector
    if escalation_detector is None:
        escalation_detector = EscalationDetector(openai_api_key)
    return escalation_detector

if __name__ == "__main__":
    # Test the escalation detector
    detector = EscalationDetector()
    
    # Test escalation
    test_query = "I'm very angry and want to speak to a manager about getting a refund"
    test_response = "I understand your frustration. Let me help you with that."
    test_persona = "Frustrated User"
    
    escalation_result = detector.should_escalate(test_query, test_response, test_persona)
    print(f"🚨 Escalate: {escalation_result['escalate']}")
    print(f"⚠️ Urgency: {escalation_result['urgency']}")
    print(f"📝 Reason: {escalation_result['reason']}")
    
    # Test scam detection
    scam_query = "Please share your OTP to verify your account immediately"
    scam_result = detector.detect_scam_risk(scam_query)
    print(f"\n🔍 Scam Risk: {scam_result['scam_risk']}")
    print(f"📊 Indicators: {scam_result['indicators']}")
