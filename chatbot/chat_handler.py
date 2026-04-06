from flask import session
from .openai_client import OpenAIClient
from config import Config
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles chat logic, session management, and context integration"""
    
    def __init__(self):
        """Initialize chat handler with OpenAI client"""
        self.openai_client = OpenAIClient()
        self.max_history = Config.MAX_CHAT_HISTORY
        self.chat_key = Config.CHAT_SESSION_KEY
        self.analysis_key = Config.ANALYSIS_SESSION_KEY
    
    def process_message(self, user_message):
        """
        Process user message and generate AI response
        
        Args:
            user_message (str): User's chat message
            
        Returns:
            dict: Response containing AI message and status
        """
        try:
            # Validate input
            if not user_message or not user_message.strip():
                return {
                    'success': False,
                    'message': 'Please enter a message.',
                    'error': 'empty_message'
                }
            
            user_message = user_message.strip()
            
            # Get current analysis context
            analysis_context = self.get_analysis_context()
            
            # Add user message to history
            self.add_message_to_history('user', user_message)
            
            # Get chat history for OpenAI
            chat_messages = self.get_chat_messages_for_api()
            
            # Generate AI response
            ai_response = self.openai_client.get_chat_response(
                messages=chat_messages,
                analysis_context=analysis_context
            )
            
            # Add AI response to history
            self.add_message_to_history('assistant', ai_response)
            
            # Return successful response
            return {
                'success': True,
                'message': ai_response,
                'timestamp': datetime.now().strftime('%H:%M')
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                'success': False,
                'message': 'Sorry, I encountered an error. Please try again.',
                'error': str(e)
            }
    
    def get_chat_history(self):
        """
        Get formatted chat history for display
        
        Returns:
            list: List of chat messages with metadata
        """
        if self.chat_key not in session:
            return []
        
        return session[self.chat_key]
    
    def add_message_to_history(self, role, content):
        """
        Add message to chat history
        
        Args:
            role (str): 'user' or 'assistant'
            content (str): Message content
        """
        if self.chat_key not in session:
            session[self.chat_key] = []
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime('%H:%M')
        }
        
        session[self.chat_key].append(message)
        
        # Limit history size
        if len(session[self.chat_key]) > self.max_history * 2:  # *2 for user + assistant pairs
            session[self.chat_key] = session[self.chat_key][-self.max_history:]
        
        # Mark session as modified
        session.modified = True
    
    def get_chat_messages_for_api(self):
        """
        Get chat messages in OpenAI API format
        
        Returns:
            list: Messages formatted for OpenAI API
        """
        if self.chat_key not in session:
            return []
        
        # Convert to OpenAI format (remove timestamp)
        api_messages = []
        for msg in session[self.chat_key]:
            api_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        return api_messages
    
    def set_analysis_context(self, organ_type, fracture_status, confidence, detections=None):
        """
        Set current analysis results for chat context
        
        Args:
            organ_type (str): Detected organ/bone type
            fracture_status (str): Fracture detection status
            confidence (float): Detection confidence
            detections (list): List of fracture detections
        """
        session[self.analysis_key] = {
            'organ_type': organ_type,
            'fracture_status': fracture_status,
            'confidence': confidence,
            'detections': detections or [],
            'timestamp': datetime.now().isoformat()
        }
        session.modified = True
        
        logger.info(f"Analysis context set: {organ_type}, {fracture_status}")
    
    def get_analysis_context(self):
        """
        Get current analysis context
        
        Returns:
            dict: Current analysis results or None
        """
        return session.get(self.analysis_key)
    
    def has_analysis_context(self):
        """
        Check if analysis context exists
        
        Returns:
            bool: True if analysis context exists
        """
        return self.analysis_key in session and session[self.analysis_key] is not None
    
    def clear_chat_history(self):
        """Clear chat history from session"""
        if self.chat_key in session:
            del session[self.chat_key]
            session.modified = True
        logger.info("Chat history cleared")
    
    def clear_analysis_context(self):
        """Clear analysis context from session"""
        if self.analysis_key in session:
            del session[self.analysis_key]
            session.modified = True
        logger.info("Analysis context cleared")
    
    def get_welcome_message(self):
        """
        Generate context-aware welcome message
        
        Returns:
            dict: Welcome message with metadata
        """
        analysis = self.get_analysis_context()
        
        if analysis:
            organ = analysis.get('organ_type', 'bone structure')
            status = analysis.get('fracture_status', 'analysis')
            
            welcome_text = f"""👋 Hi! I'm your AI medical assistant. I can see you've just analyzed an X-ray of your {organ.lower()}. 
            
The analysis shows: {status}

I'm here to help you understand:
• What these results mean
• Information about {organ.lower()} anatomy
• General fracture healing and care
• Any questions about the analysis

What would you like to know about your X-ray results?

{Config.MEDICAL_DISCLAIMER}"""
        else:
            welcome_text = f"""👋 Hello! I'm your AI medical assistant for OrthoScan AI.

I can help you understand:
• X-ray analysis results
• Bone and fracture information  
• General orthopedic knowledge
• Recovery and care guidance

Please upload and analyze an X-ray first, then I'll be able to discuss your specific results!

{Config.MEDICAL_DISCLAIMER}"""
        
        return {
            'role': 'assistant',
            'content': welcome_text,
            'timestamp': datetime.now().strftime('%H:%M'),
            'is_welcome': True
        }
    
    def validate_setup(self):
        """
        Validate chatbot setup
        
        Returns:
            dict: Validation results
        """
        try:
            # Check OpenAI API key
            api_valid = self.openai_client.validate_api_key()
            
            return {
                'valid': api_valid,
                'openai_connected': api_valid,
                'message': 'Chatbot ready!' if api_valid else 'OpenAI API key invalid'
            }
        except Exception as e:
            logger.error(f"Chatbot validation error: {e}")
            return {
                'valid': False,
                'openai_connected': False,
                'message': f'Setup error: {str(e)}'
            }