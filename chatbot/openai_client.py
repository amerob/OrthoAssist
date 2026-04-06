import openai
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI API client for chatbot functionality"""
    
    def __init__(self):
        """Initialize OpenAI client with configuration"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please check your .env file.")
        
        # Initialize OpenAI client (new v1.0+ syntax)
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE
        self.system_prompt = Config.SYSTEM_PROMPT
        
        logger.info("OpenAI client initialized successfully")
    
    def get_chat_response(self, messages, analysis_context=None):
        """
        Get response from OpenAI GPT model
        
        Args:
            messages (list): List of chat messages
            analysis_context (dict): Current X-ray analysis results
            
        Returns:
            str: AI response or error message
        """
        try:
            # Prepare system message with context
            system_message = self._prepare_system_message(analysis_context)
            
            # Prepare full message list
            full_messages = [{"role": "system", "content": system_message}] + messages
            
            # Call OpenAI API (new v1.0+ syntax)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract and return response
            ai_response = response.choices[0].message.content.strip()
            logger.info("Successfully generated AI response")
            return ai_response
            
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return "I'm currently experiencing high demand. Please try again in a moment."
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm having trouble connecting to my knowledge base. Please try again."
            
        except openai.BadRequestError as e:
            logger.error(f"Invalid request to OpenAI: {e}")
            return "There was an issue with your request. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI client: {e}")
            return "I encountered an unexpected error. Please try again."
    
    def _prepare_system_message(self, analysis_context):
        """
        Prepare system message with analysis context
        
        Args:
            analysis_context (dict): Current analysis results
            
        Returns:
            str: Enhanced system prompt with context
        """
        base_prompt = self.system_prompt
        
        if analysis_context:
            context_info = "\n\nCurrent X-ray Analysis Context:\n"
            
            if 'organ_type' in analysis_context:
                context_info += f"- Detected Organ/Bone: {analysis_context['organ_type']}\n"
            
            if 'fracture_status' in analysis_context:
                context_info += f"- Fracture Status: {analysis_context['fracture_status']}\n"
            
            if 'confidence' in analysis_context:
                context_info += f"- Detection Confidence: {analysis_context['confidence']:.2f}\n"
            
            if 'detections' in analysis_context and analysis_context['detections']:
                context_info += f"- Number of Fractures Detected: {len(analysis_context['detections'])}\n"
                for i, detection in enumerate(analysis_context['detections'], 1):
                    context_info += f"  {i}. {detection.get('label', 'Fracture')} (Confidence: {detection.get('confidence', 0):.2f})\n"
            
            context_info += "\nUse this information to provide relevant, contextual responses about the user's specific X-ray analysis."
            
            return base_prompt + context_info
        
        return base_prompt
    
    def validate_api_key(self):
        """
        Validate OpenAI API key
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            # Test API key with a simple request (new v1.0+ syntax)
            self.client.models.list()
            logger.info("OpenAI API key validation successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {e}")
            return False