// Main application JavaScript for OrthoScan AI
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const fileText = document.getElementById('fileText');
    const uploadStatus = document.getElementById('uploadStatus');
    const confidenceSlider = document.getElementById('confidenceSlider');
    const confidenceValue = document.getElementById('confidenceValue');
    const form = document.getElementById('mainForm');
    const analyzeBtn = document.querySelector('.analyze-btn');

    // File upload handling
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }

    // Confidence slider handling
    if (confidenceSlider) {
        confidenceSlider.addEventListener('input', handleConfidenceChange);
        // Load saved confidence from session storage
        loadSavedConfidence();
    }

    // Form submission handling
    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }

    // Initialize loading overlay
    createLoadingOverlay();

    function handleFileSelection(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            if (!isValidImageFile(file)) {
                showAlert('Please select a valid image file (JPEG, PNG, or BMP).', 'error');
                fileInput.value = '';
                return;
            }

            // Validate file size (max 16MB)
            if (file.size > 16 * 1024 * 1024) {
                showAlert('File size must be less than 16MB.', 'error');
                fileInput.value = '';
                return;
            }

            // Update UI
            if (fileText) {
                fileText.textContent = file.name;
            }
            if (uploadStatus) {
                uploadStatus.textContent = `Selected: ${file.name}`;
                uploadStatus.style.color = '#27ae60';
            }

            // Show file preview
            showFilePreview(file);

            console.log('File selected:', file.name, 'Size:', formatFileSize(file.size));
        }
    }

    function handleConfidenceChange(e) {
        const value = parseFloat(e.target.value);
        if (confidenceValue) {
            confidenceValue.textContent = value.toFixed(2);
        }
        
        // Save to session storage
        sessionStorage.setItem('confidence', value);
        
        console.log('Confidence threshold updated:', value);
    }

    function handleFormSubmission(e) {
        const fileSelected = fileInput && fileInput.files && fileInput.files[0];
        
        if (!fileSelected) {
            e.preventDefault();
            showAlert('Please select an X-ray image first.', 'warning');
            return;
        }

        // Show loading overlay
        showLoadingOverlay();
        
        // Disable form elements
        setFormEnabled(false);
        
        console.log('Starting X-ray analysis...');
    }

    function isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp'];
        return validTypes.includes(file.type.toLowerCase());
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showFilePreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Remove existing preview
            const existingPreview = document.getElementById('filePreview');
            if (existingPreview) {
                existingPreview.remove();
            }

            // Create preview element
            const preview = document.createElement('div');
            preview.id = 'filePreview';
            preview.className = 'file-preview';
            preview.innerHTML = `
                <div class="preview-container">
                    <img src="${e.target.result}" alt="Preview" class="preview-image">
                    <div class="preview-info">
                        <p><strong>${file.name}</strong></p>
                        <p>Size: ${formatFileSize(file.size)}</p>
                    </div>
                </div>
            `;

            // Add preview after upload section
            const uploadSection = document.querySelector('.upload-section');
            if (uploadSection) {
                uploadSection.appendChild(preview);
            }
        };
        reader.readAsDataURL(file);
    }

    function loadSavedConfidence() {
        const savedConfidence = sessionStorage.getItem('confidence');
        if (savedConfidence && confidenceSlider && confidenceValue) {
            const value = parseFloat(savedConfidence);
            confidenceSlider.value = value;
            confidenceValue.textContent = value.toFixed(2);
        }
    }

    function createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <h3>Analyzing X-ray Image...</h3>
                <p>AI models are processing your image</p>
                <div class="loading-steps">
                    <div class="step active" id="step1">📤 Uploading image</div>
                    <div class="step" id="step2">🦴 Classifying organ</div>
                    <div class="step" id="step3">🔍 Detecting fractures</div>
                    <div class="step" id="step4">📋 Generating report</div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Add loading styles
        const style = document.createElement('style');
        style.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: none;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            }
            .loading-content {
                background: white;
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                max-width: 400px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            .loading-steps {
                margin-top: 20px;
                text-align: left;
            }
            .step {
                padding: 8px 0;
                color: #888;
                transition: color 0.3s ease;
            }
            .step.active {
                color: #3498db;
                font-weight: bold;
            }
            .step.completed {
                color: #27ae60;
            }
            .file-preview {
                margin-top: 20px;
                padding: 20px;
                border: 2px dashed #ddd;
                border-radius: 10px;
                background: #f9f9f9;
            }
            .preview-container {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .preview-image {
                width: 80px;
                height: 80px;
                object-fit: cover;
                border-radius: 8px;
                border: 2px solid #ddd;
            }
            .preview-info p {
                margin: 5px 0;
                font-size: 14px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    function showLoadingOverlay() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            
            // Simulate loading steps
            simulateLoadingSteps();
        }
    }

    function hideLoadingOverlay() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        setFormEnabled(true);
    }

    function simulateLoadingSteps() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        let currentStep = 0;

        const interval = setInterval(() => {
            if (currentStep > 0) {
                const prevStep = document.getElementById(steps[currentStep - 1]);
                if (prevStep) {
                    prevStep.classList.remove('active');
                    prevStep.classList.add('completed');
                }
            }

            if (currentStep < steps.length) {
                const step = document.getElementById(steps[currentStep]);
                if (step) {
                    step.classList.add('active');
                }
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 1000);
    }

    function setFormEnabled(enabled) {
        const elements = [fileInput, confidenceSlider, analyzeBtn];
        elements.forEach(element => {
            if (element) {
                element.disabled = !enabled;
            }
        });
    }

    function showAlert(message, type = 'info') {
        // Remove existing alert
        const existingAlert = document.querySelector('.alert-notification');
        if (existingAlert) {
            existingAlert.remove();
        }

        // Create alert
        const alert = document.createElement('div');
        alert.className = `alert-notification alert-${type}`;
        alert.innerHTML = `
            <div class="alert-content">
                <span class="alert-icon">${getAlertIcon(type)}</span>
                <span class="alert-message">${message}</span>
                <button class="alert-close">&times;</button>
            </div>
        `;

        // Add alert styles
        const style = document.createElement('style');
        style.textContent = `
            .alert-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                animation: slideInRight 0.3s ease;
            }
            .alert-info { background: #d1ecf1; border-left: 4px solid #bee5eb; color: #0c5460; }
            .alert-warning { background: #fff3cd; border-left: 4px solid #ffeaa7; color: #856404; }
            .alert-error { background: #f8d7da; border-left: 4px solid #f5c6cb; color: #721c24; }
            .alert-success { background: #d4edda; border-left: 4px solid #c3e6cb; color: #155724; }
            .alert-content {
                padding: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .alert-close {
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                margin-left: auto;
                opacity: 0.7;
            }
            .alert-close:hover { opacity: 1; }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        // Add to document
        document.body.appendChild(alert);

        // Close button functionality
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => alert.remove());
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    function getAlertIcon(type) {
        const icons = {
            info: 'ℹ️',
            warning: '⚠️',
            error: '❌',
            success: '✅'
        };
        return icons[type] || icons.info;
    }

    // Hide loading overlay when page finishes loading (in case of redirect)
    window.addEventListener('load', () => {
        hideLoadingOverlay();
        
        // Trigger analysis complete event if results are present
        if (document.querySelector('.results-section')) {
            setTimeout(() => {
                const event = new CustomEvent('analysisComplete');
                document.dispatchEvent(event);
            }, 500);
        }
    });

    // Handle browser back button
    window.addEventListener('beforeunload', () => {
        hideLoadingOverlay();
    });

    console.log('OrthoScan AI main script loaded successfully');
});