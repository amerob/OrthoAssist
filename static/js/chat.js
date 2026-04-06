// Chat functionality for OrthoScan AI
class ChatInterface {
    constructor() {
        this.chatContainer = null;
        this.chatMessages = null;
        this.chatInput = null;
        this.sendButton = null;
        this.typingIndicator = null;
        this.isExpanded = false;
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupChat());
        } else {
            this.setupChat();
        }
    }
    
    setupChat() {
        this.chatContainer = document.getElementById('chatBody') || document.getElementById('chatContainer');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        if (!this.chatContainer) {
            console.log('Chat elements not found - chat not available yet');
            return;
        }
        
        this.bindEvents();
        this.loadChatHistory();
        
        console.log('Chat interface initialized');
    }
    
    bindEvents() {
        // Chat toggle — header or dedicated button
        const chatHeader = document.getElementById('chatHeader');
        if (chatHeader) {
            chatHeader.addEventListener('click', () => this.toggleChat());
        }
        const chatToggleBtn = document.getElementById('chatToggleBtn');
        if (chatToggleBtn) {
            chatToggleBtn.addEventListener('click', (e) => { e.stopPropagation(); this.toggleChat(); });
        }
        
        // Send message events
        if (this.sendButton) {
            this.sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
        
        if (this.chatInput) {
            // Send on Enter, new line on Shift+Enter
            this.chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                } else if (e.key === 'Enter' && e.shiftKey) {
                    // Allow new line
                    return;
                }
            });
            
            // Auto-resize textarea
            this.chatInput.addEventListener('input', () => {
                this.autoResizeTextarea();
                this.updateSendButton();
            });
        }
        
        // Auto-expand chat if analysis results are present
        if (document.querySelector('.results-section')) {
            setTimeout(() => {
                this.expandChat();
            }, 1000);
        }
    }
    
    toggleChat() {
        if (this.isExpanded) {
            this.collapseChat();
        } else {
            this.expandChat();
        }
    }
    
    expandChat() {
        const body = document.getElementById('chatBody') || this.chatContainer;
        if (!body) return;
        body.classList.add('open', 'expanded');
        const chevron = document.getElementById('chatChevron');
        if (chevron) chevron.style.transform = 'rotate(180deg)';
        this.isExpanded = true;
        setTimeout(() => {
            this.scrollToBottom();
            if (this.chatInput) this.chatInput.focus();
        }, 350);
        if (this.chatMessages && this.chatMessages.children.length === 0) {
            this.loadWelcomeMessage();
        }
    }

    collapseChat() {
        const body = document.getElementById('chatBody') || this.chatContainer;
        if (!body) return;
        body.classList.remove('open', 'expanded');
        const chevron = document.getElementById('chatChevron');
        if (chevron) chevron.style.transform = '';
        this.isExpanded = false;
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message to UI
        this.addMessage('user', message);
        
        // Clear input
        this.chatInput.value = '';
        this.autoResizeTextarea();
        this.updateSendButton();
        
        // Show typing indicator
        this.showTyping();
        
        try {
            // Send to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            if (data.success) {
                // Add AI response
                this.addMessage('assistant', data.message, data.timestamp);
            } else {
                // Show error
                this.addMessage('assistant', data.message || 'Sorry, I encountered an error. Please try again.');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addMessage('assistant', 'I\'m having trouble connecting. Please check your internet connection and try again.');
        }
    }
    
    addMessage(role, content, timestamp = null) {
        if (!this.chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message message-${role}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = this.formatMessage(content);
        
        const timeDiv = document.createElement('span');
        timeDiv.className = 'message-timestamp';
        timeDiv.textContent = timestamp || this.getCurrentTime();
        
        messageDiv.appendChild(bubble);
        messageDiv.appendChild(timeDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Convert line breaks to <br> tags
        content = content.replace(/\n/g, '<br>');
        
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert markdown-style bold text
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        return content;
    }
    
    showTyping() {
        if (!this.typingIndicator) return;
        
        this.isTyping = true;
        this.typingIndicator.classList.add('show');
        this.updateSendButton();
        this.scrollToBottom();
    }
    
    hideTyping() {
        if (!this.typingIndicator) return;
        
        this.isTyping = false;
        this.typingIndicator.classList.remove('show');
        this.updateSendButton();
    }
    
    updateSendButton() {
        if (!this.sendButton || !this.chatInput) return;
        
        const hasText = this.chatInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isTyping;
    }
    
    autoResizeTextarea() {
        if (!this.chatInput) return;
        
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 100) + 'px';
    }
    
    scrollToBottom() {
        if (!this.chatMessages) return;
        
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    getCurrentTime() {
        return new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch('/chat/history');
            const data = await response.json();
            
            if (data.success && data.history) {
                data.history.forEach(msg => {
                    this.addMessage(msg.role, msg.content, msg.timestamp);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async loadWelcomeMessage() {
        try {
            const response = await fetch('/chat/welcome');
            const data = await response.json();
            
            if (data.success && data.message) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message message-assistant welcome-message';
                
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble';
                bubble.innerHTML = this.formatMessage(data.message);
                
                const timeDiv = document.createElement('span');
                timeDiv.className = 'message-timestamp';
                timeDiv.textContent = data.timestamp || this.getCurrentTime();
                
                messageDiv.appendChild(bubble);
                messageDiv.appendChild(timeDiv);
                
                if (this.chatMessages) {
                    this.chatMessages.appendChild(messageDiv);
                    this.scrollToBottom();
                }
            }
        } catch (error) {
            console.error('Error loading welcome message:', error);
        }
    }
    
    // Public method to refresh chat when new analysis is available
    refreshForNewAnalysis() {
        if (this.chatMessages) {
            // Clear existing messages
            this.chatMessages.innerHTML = '';
        }
        
        // Load new welcome message with updated context
        this.loadWelcomeMessage();
        
        // Auto-expand if not already expanded
        if (!this.isExpanded) {
            setTimeout(() => {
                this.expandChat();
            }, 500);
        }
    }
    
    // Clear chat history
    async clearHistory() {
        try {
            await fetch('/chat/clear', { method: 'POST' });
            if (this.chatMessages) {
                this.chatMessages.innerHTML = '';
            }
            this.loadWelcomeMessage();
        } catch (error) {
            console.error('Error clearing chat history:', error);
        }
    }
}

// Initialize chat when page loads
let chatInterface;

document.addEventListener('DOMContentLoaded', () => {
    chatInterface = new ChatInterface();
});

// Make chat interface available globally
window.chatInterface = chatInterface;

// Auto-refresh chat when new analysis results are available
document.addEventListener('analysisComplete', () => {
    if (window.chatInterface) {
        window.chatInterface.refreshForNewAnalysis();
    }
});