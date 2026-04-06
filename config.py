import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-3.5-turbo'
    OPENAI_MAX_TOKENS = 500
    OPENAI_TEMPERATURE = 0.7
    
    # Flask Configuration
    SECRET_KEY = os.urandom(24)
    
    # Model Paths
    MODEL_PATH_ORGAN = os.getenv('MODEL_PATH_ORGAN', 'model/resnet50_fracture.onnx')
    MODEL_PATH_FRACTURE = os.getenv('MODEL_PATH_FRACTURE', 'model/yolo_fracture_detection.pt')
    
    # Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/upload')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Organ Classification
    CLASS_NAMES_ORGAN = ['Eblow', 'Finger', 'Forearm', 'Humerous', 'Shoulder', 'Wrist']
    
    # Chat Configuration
    MAX_CHAT_HISTORY = 20  # Maximum chat messages to keep in session
    CHAT_SESSION_KEY = 'chat_history'
    ANALYSIS_SESSION_KEY = 'analysis_results'
    
    # Medical Disclaimer
    MEDICAL_DISCLAIMER = """
    ⚠️ **Important Medical Disclaimer**: 
    This AI assistant is for educational purposes only and does not provide medical advice, 
    diagnosis, or treatment recommendations. Always consult with qualified healthcare 
    professionals for medical decisions. This analysis should not replace professional 
    medical consultation.
    """
    
    # System Prompt for OpenAI
    SYSTEM_PROMPT = """
    You are a knowledgeable medical AI assistant integrated with OrthoScan AI, 
    a fracture detection system. Your role is to help users understand X-ray 
    analysis results and provide educational information about fractures and bone health.
    
    Guidelines:
    - Explain medical concepts in simple, understandable terms
    - Provide educational information about fractures, bones, and X-ray interpretation
    - Help users understand their analysis results (organ classification and fracture detection)
    - Discuss general treatment approaches and recovery processes
    - Always emphasize the importance of consulting healthcare professionals
    - NEVER prescribe specific medications or dosages
    - NEVER provide definitive diagnoses - only explain what the AI analysis suggests
    - Always remind users that this is educational and not a substitute for professional medical advice
    
    Be helpful, empathetic, and professional while maintaining appropriate medical boundaries.
    """