"""
OrthoScan AI Chatbot Module

This module provides OpenAI-powered chatbot functionality for medical 
X-ray analysis discussion and educational support.
"""

from .openai_client import OpenAIClient
from .chat_handler import ChatHandler

__version__ = "1.0.0"
__author__ = "OrthoScan AI Team"

__all__ = ['OpenAIClient', 'ChatHandler']