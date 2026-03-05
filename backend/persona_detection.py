"""
Persona Detection Module
Identifies customer persona using LLM classification with structured output
"""

import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI

class PersonaDetector:
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize persona detector with OpenAI client
        """
        self.client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.persona_prompt = self._get_persona_prompt()
    
    def _get_persona_prompt(self) -> str:
        """
        Get the structured prompt for persona detection
        """
        return """
You are an AI system that identifies the persona of a customer based on their message.

Analyze the user's message and classify them into one of the following personas:

1. Technical Expert
   - Uses technical terms (API, endpoint, authentication, etc.)
   - Talks about specific error codes, logs, debugging
   - Asks detailed technical questions
   - Mentions programming concepts, frameworks, or tools

2. Frustrated User
   - Expresses anger, disappointment, or frustration
   - Uses emotional language (useless, broken, terrible, etc.)
   - Complains about product/service quality
   - May threaten to cancel or leave
   - Often uses exclamation marks and all caps

3. Business Executive
   - Interested in ROI, pricing, business value
   - Asks about enterprise features, scalability
   - Focuses on business metrics and performance
   - Uses business terminology (investment, productivity, efficiency)
   - Asks about compliance, security, SLA

Return your response in this exact JSON format:
{
    "persona": "Technical Expert|Frustrated User|Business Executive",
    "confidence": 0.00,
    "reasoning": "Brief explanation of why this persona was chosen",
    "key_indicators": ["list", "of", "key", "phrases", "that", "indicated", "this", "persona"]
}

User message: {query}
"""
    
    def detect_persona(self, query: str) -> Dict[str, Any]:
        """
        Detect persona from user query
        """
        try:
            # If no OpenAI client, use rule-based detection
            if not self.client:
                return self._rule_based_detection(query)
            
            # Use LLM for persona detection
            prompt = self.persona_prompt.format(query=query)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a persona detection expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(result_text)
                # Validate required fields
                if not all(key in result for key in ["persona", "confidence", "reasoning", "key_indicators"]):
                    raise ValueError("Missing required fields")
                return result
            except json.JSONDecodeError:
                # Fallback to rule-based if JSON parsing fails
                return self._rule_based_detection(query)
                
        except Exception as e:
            print(f"❌ Error in persona detection: {e}")
            # Fallback to rule-based detection
            return self._rule_based_detection(query)
    
    def _rule_based_detection(self, query: str) -> Dict[str, Any]:
        """
        Rule-based persona detection as fallback
        """
        query_lower = query.lower()
        
        # Technical indicators
        technical_keywords = [
            'api', 'endpoint', 'authentication', 'token', 'key', 'error',
            '500', '404', '401', 'debug', 'code', 'programming', 'sdk',
            'integration', 'server', 'database', 'request', 'response'
        ]
        
        # Frustration indicators
        frustration_keywords = [
            'useless', 'broken', 'terrible', 'awful', 'worst', 'hate',
            'frustrated', 'angry', 'disappointed', 'cancel', 'refund',
            'complaint', 'nothing works', 'waste of time'
        ]
        
        # Business indicators
        business_keywords = [
            'roi', 'pricing', 'cost', 'investment', 'enterprise', 'scalable',
            'productivity', 'efficiency', 'business', 'revenue', 'profit',
            'sla', 'compliance', 'security', 'team', 'organization'
        ]
        
        # Count keyword matches
        technical_score = sum(1 for kw in technical_keywords if kw in query_lower)
        frustration_score = sum(1 for kw in frustration_keywords if kw in query_lower)
        business_score = sum(1 for kw in business_keywords if kw in query_lower)
        
        # Determine persona based on scores
        if frustration_score >= 2:
            persona = "Frustrated User"
            confidence = min(0.9, 0.6 + frustration_score * 0.1)
            key_indicators = [kw for kw in frustration_keywords if kw in query_lower]
        elif technical_score >= 2:
            persona = "Technical Expert"
            confidence = min(0.9, 0.6 + technical_score * 0.1)
            key_indicators = [kw for kw in technical_keywords if kw in query_lower]
        elif business_score >= 2:
            persona = "Business Executive"
            confidence = min(0.9, 0.6 + business_score * 0.1)
            key_indicators = [kw for kw in business_keywords if kw in query_lower]
        else:
            # Default to Technical Expert if unclear
            persona = "Technical Expert"
            confidence = 0.5
            key_indicators = []
        
        reasoning = f"Detected {len(key_indicators)} key indicators for {persona}"
        
        return {
            "persona": persona,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_indicators": key_indicators
        }
    
    def get_persona_characteristics(self, persona: str) -> Dict[str, Any]:
        """
        Get characteristics and response style for each persona
        """
        characteristics = {
            "Technical Expert": {
                "response_style": "detailed_technical",
                "tone": "professional_direct",
                "content_focus": ["technical_details", "step_by_step", "code_examples"],
                "avoid": ["oversimplification", "excessive_empathy"],
                "key_phrases": ["Here's the technical solution", "Let me walk you through", "The issue is likely"]
            },
            "Frustrated User": {
                "response_style": "empathetic_reassuring",
                "tone": "calm_supportive",
                "content_focus": ["quick_solutions", "reassurance", "clear_steps"],
                "avoid": ["technical_jargon", "complex_explanations"],
                "key_phrases": ["I understand your frustration", "Let me help you resolve this", "I'm sorry you're experiencing this"]
            },
            "Business Executive": {
                "response_style": "business_focused",
                "tone": "professional_value_oriented",
                "content_focus": ["business_value", "roi", "efficiency", "scalability"],
                "avoid": ["technical_details", "emotional_language"],
                "key_phrases": ["From a business perspective", "This solution provides", "The value proposition is"]
            }
        }
        
        return characteristics.get(persona, characteristics["Technical Expert"])

# Singleton instance
persona_detector = None

def get_persona_detector(openai_api_key: Optional[str] = None) -> PersonaDetector:
    """
    Get or create persona detector instance
    """
    global persona_detector
    if persona_detector is None:
        persona_detector = PersonaDetector(openai_api_key)
    return persona_detector

if __name__ == "__main__":
    # Test the persona detector
    detector = PersonaDetector()
    
    test_queries = [
        "I'm getting a 500 error when calling the API endpoint",
        "This product is completely useless and nothing works!",
        "What's the ROI for the enterprise plan and how does it scale?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = detector.detect_persona(query)
        print(f"👤 Persona: {result['persona']}")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        print(f"💭 Reasoning: {result['reasoning']}")
        print(f"🔑 Key Indicators: {result['key_indicators']}")
