"""
Tone Adaptation Module
Generates persona-appropriate response prompts and tones
"""

from typing import Dict, Any, List
from persona_detection import get_persona_detector

class ToneAdapter:
    def __init__(self):
        """
        Initialize tone adapter with persona detector
        """
        self.persona_detector = get_persona_detector()
        self.tone_templates = self._get_tone_templates()
    
    def _get_tone_templates(self) -> Dict[str, str]:
        """
        Get tone-specific prompt templates for each persona
        """
        return {
            "Technical Expert": """
You are a technical support specialist assisting a fellow technical expert.

RESPONSE GUIDELINES:
- Provide detailed, technical explanations
- Include specific steps, code examples, or API references
- Use precise technical terminology
- Focus on root cause analysis and troubleshooting
- Be concise but thorough
- Include relevant error codes, status codes, or technical specifications

TONE: Professional, direct, technically precise

AVOID:
- Oversimplifying technical concepts
- Excessive emotional language
- Basic explanations of technical terms

EXAMPLE PHRASES:
- "The issue is likely related to..."
- "Here's the technical solution..."
- "Let me walk you through the debugging steps..."
- "You'll want to check the..."
""",
            
            "Frustrated User": """
You are an empathetic customer support specialist helping a frustrated customer.

RESPONSE GUIDELINES:
- Start with empathy and acknowledgment
- Apologize for their negative experience
- Provide simple, clear solutions
- Break down complex steps into easy-to-follow instructions
- Reassure them that you'll help resolve the issue
- Focus on quick wins and immediate relief

TONE: Calm, supportive, patient, reassuring

AVOID:
- Technical jargon and complex terminology
- Blaming the user or making them feel at fault
- Long, complicated explanations

EXAMPLE PHRASES:
- "I understand your frustration, and I'm here to help"
- "I'm sorry you're experiencing this issue"
- "Let's work together to resolve this quickly"
- "I can see why this would be frustrating"
""",
            
            "Business Executive": """
You are a business-focused support specialist assisting a business executive.

RESPONSE GUIDELINES:
- Focus on business value and impact
- Highlight ROI, efficiency, and productivity benefits
- Use business-appropriate language
- Address scalability, security, and compliance concerns
- Emphasize how solutions support business objectives
- Be concise and respect their time

TONE: Professional, value-oriented, business-focused

AVOID:
- Deep technical details unless relevant to business impact
- Emotional language
- Overly casual or informal tone

EXAMPLE PHRASES:
- "From a business perspective..."
- "This solution provides significant value by..."
- "The impact on your bottom line would be..."
- "This aligns with your business objectives of..."
"""
        }
    
    def get_adapted_prompt(self, persona: str, context: str, query: str) -> str:
        """
        Generate a persona-adapted prompt for response generation
        """
        # Get the tone template for the persona
        tone_template = self.tone_templates.get(persona, self.tone_templates["Technical Expert"])
        
        # Get persona characteristics
        characteristics = self.persona_detector.get_persona_characteristics(persona)
        
        # Build the complete prompt
        prompt = f"""
{tone_template}

KNOWLEDGE BASE CONTEXT:
{context}

CUSTOMER QUESTION:
{query}

RESPONSE REQUIREMENTS:
1. Address the customer's question directly
2. Use only information from the knowledge base above
3. If information is not available, clearly state that
4. Adapt your response style to the {persona} persona
5. Follow the tone guidelines provided above

Generate a helpful, appropriate response:
"""
        
        return prompt
    
    def get_response_guidelines(self, persona: str) -> Dict[str, Any]:
        """
        Get specific response guidelines for a persona
        """
        characteristics = self.persona_detector.get_persona_characteristics(persona)
        
        return {
            "persona": persona,
            "response_style": characteristics["response_style"],
            "tone": characteristics["tone"],
            "content_focus": characteristics["content_focus"],
            "avoid": characteristics["avoid"],
            "key_phrases": characteristics["key_phrases"],
            "prompt_template": self.tone_templates.get(persona, "")
        }
    
    def validate_response_tone(self, response: str, persona: str) -> Dict[str, Any]:
        """
        Validate if a response matches the expected tone for a persona
        """
        characteristics = self.persona_detector.get_persona_characteristics(persona)
        response_lower = response.lower()
        
        # Check for key phrases
        key_phrases_found = []
        for phrase in characteristics["key_phrases"]:
            if phrase.lower() in response_lower:
                key_phrases_found.append(phrase)
        
        # Check for avoided content
        avoided_content_found = []
        for avoid in characteristics["avoid"]:
            if avoid.lower() in response_lower:
                avoided_content_found.append(avoid)
        
        # Calculate tone match score
        key_phrase_score = len(key_phrases_found) / len(characteristics["key_phrases"])
        avoidance_penalty = len(avoided_content_found) * 0.2
        tone_score = max(0, min(1, key_phrase_score - avoidance_penalty))
        
        return {
            "persona": persona,
            "tone_match_score": tone_score,
            "key_phrases_found": key_phrases_found,
            "avoided_content_found": avoided_content_found,
            "is_appropriate": tone_score >= 0.5
        }
    
    def get_fallback_response(self, persona: str, query: str) -> str:
        """
        Generate a fallback response when knowledge base doesn't have information
        """
        fallback_responses = {
            "Technical Expert": f"I don't have specific information about '{query}' in our knowledge base. As a technical resource, you might want to check our API documentation at docs.example.com or contact our technical support team with your specific error details.",
            
            "Frustrated User": f"I understand you're looking for help with '{query}', and I'm sorry I don't have that specific information available. Let me connect you with a human support agent who can better assist you with this issue. Your satisfaction is important to us.",
            
            "Business Executive": f"I don't have the specific business information about '{query}' in our current knowledge base. For detailed business inquiries, I recommend scheduling a consultation with our enterprise team who can provide comprehensive information tailored to your business needs."
        }
        
        return fallback_responses.get(persona, fallback_responses["Technical Expert"])

# Singleton instance
tone_adapter = None

def get_tone_adapter() -> ToneAdapter:
    """
    Get or create tone adapter instance
    """
    global tone_adapter
    if tone_adapter is None:
        tone_adapter = ToneAdapter()
    return tone_adapter

if __name__ == "__main__":
    # Test the tone adapter
    adapter = ToneAdapter()
    
    # Test personas
    personas = ["Technical Expert", "Frustrated User", "Business Executive"]
    test_context = "API authentication requires a valid API key."
    test_query = "How do I authenticate with the API?"
    
    for persona in personas:
        print(f"\n👤 Persona: {persona}")
        prompt = adapter.get_adapted_prompt(persona, test_context, test_query)
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        guidelines = adapter.get_response_guidelines(persona)
        print(f"🎯 Response Style: {guidelines['response_style']}")
        print(f"🔊 Tone: {guidelines['tone']}")
