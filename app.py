import os
import cv2
import numpy as np
from flask import Flask, request, render_template, session, url_for, jsonify
from PIL import Image
import onnxruntime as ort
from torchvision import transforms
from ultralytics import YOLO
import time
from werkzeug.utils import secure_filename
import logging

# Import our custom modules
from config import Config
from chatbot import ChatHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Configuration
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Load models
try:
    session_organ = ort.InferenceSession(Config.MODEL_PATH_ORGAN)
    model_fracture = YOLO(Config.MODEL_PATH_FRACTURE)
    logger.info("AI models loaded successfully")
except Exception as e:
    logger.error(f"Error loading models: {e}")
    raise

# Initialize chat handler
try:
    chat_handler = ChatHandler()
    logger.info("Chat handler initialized successfully")
except Exception as e:
    logger.error(f"Error initializing chat handler: {e}")
    chat_handler = None

# Image transformations
transform_224 = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


import traceback

def predict_organ(image_path):
    """Classify organ using ONNX model"""
    try:
        image = Image.open(image_path).convert('RGB')
        image = transform_224(image).unsqueeze(0).numpy()
        inputs = {session_organ.get_inputs()[0].name: image}
        outputs = session_organ.run(None, inputs)
        predicted_organ = Config.CLASS_NAMES_ORGAN[np.argmax(outputs[0])]
        logger.info(f"Organ classification: {predicted_organ}")
        return predicted_organ
    except Exception as e:
        logger.error(f"Error in organ prediction: {e}\n{traceback.format_exc()}")
        return "Unknown"


def process_fracture(image_path, confidence):
    """Process fracture detection with given confidence threshold"""
    try:
        img = cv2.imread(image_path)
        results = model_fracture.predict(img, conf=confidence, verbose=False)[0]

        annotated_img = img.copy()
        fracture_found = False
        detections = []

        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = box.conf[0].item()
                cls_id = box.cls[0].item()
                label = model_fracture.names.get(int(cls_id), "Fracture")

                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(annotated_img, f"{label} {conf:.2f}",
                            (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)
                detections.append({'confidence': conf, 'label': label})
                fracture_found = True

        # Save annotated image with timestamp
        annotated_dir = os.path.join(os.path.dirname(image_path), "annotated")
        os.makedirs(annotated_dir, exist_ok=True)
        timestamp = str(int(time.time()))
        annotated_filename = f"{timestamp}_{os.path.basename(image_path)}"
        annotated_path = os.path.join(annotated_dir, annotated_filename)
        cv2.imwrite(annotated_path, annotated_img)

        fracture_status = "Fracture(s) detected" if fracture_found else "No fracture detected"
        logger.info(f"Fracture detection: {fracture_status}, {len(detections)} detections")

        return {
            'status': fracture_status,
            'image_path': annotated_path,
            'detections': detections
        }
    except Exception as e:
        logger.error(f"Error in fracture detection: {e}\n{traceback.format_exc()}")
        return {
            'status': 'Error in fracture detection',
            'image_path': image_path,
            'detections': []
        }


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for X-ray analysis"""
    current_file = session.get('current_file')
    confidence = float(request.form.get('confidence', 0.3)) if request.method == 'POST' else 0.3

    if request.method == 'POST':
        logger.info("POST request received")
        logger.info(f"Request files: {list(request.files.keys())}")
        logger.info(f"Request form: {dict(request.form)}")
        
        try:
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                logger.info(f"File object: {file}")
                logger.info(f"File filename: {file.filename}")
                logger.info(f"File content type: {getattr(file, 'content_type', 'unknown')}")
                
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    session['current_file'] = filename
                    current_file = filename
                    logger.info(f"File uploaded successfully: {filename} to {filepath}")
                else:
                    logger.warning("Empty filename received or no file object")
            else:
                logger.info("No 'file' key in request.files")
                logger.info("Using existing file from session")

            # Process analysis if file exists
            if current_file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_file)
                logger.info(f"Starting analysis for: {filepath}")
                
                # Check if file exists
                if not os.path.exists(filepath):
                    logger.error(f"File not found: {filepath}")
                    return render_template('index.html', 
                                         error="File not found. Please upload again.",
                                         confidence=confidence, 
                                         chat_available=chat_handler is not None)
                
                # Perform AI analysis
                logger.info("Starting organ prediction...")
                organ_type = predict_organ(filepath)
                logger.info(f"Organ prediction complete: {organ_type}")
                
                logger.info("Starting fracture detection...")
                result = process_fracture(filepath, confidence)
                logger.info(f"Fracture detection complete: {result['status']}")

                # Update chat context with analysis results
                if chat_handler:
                    chat_handler.set_analysis_context(
                        organ_type=organ_type,
                        fracture_status=result['status'],
                        confidence=confidence,
                        detections=result['detections']
                    )
                    logger.info("Chat context updated with analysis results")

                logger.info("Rendering results template...")
                return render_template('index.html',
                                       uploaded_file=current_file,
                                       prediction_organ=organ_type,
                                       prediction_fracture=result['status'],
                                       image_path=url_for('static', filename=f'upload/{current_file}'),
                                       annotated_image_path=url_for('static',
                                                                    filename=f'upload/annotated/{os.path.basename(result["image_path"])}'),
                                       confidence=confidence,
                                       detections=result['detections'],
                                       chat_available=chat_handler is not None)
            else:
                logger.warning("No current file to analyze")
                return render_template('index.html', 
                                     error="Please select a file first.",
                                     confidence=confidence, 
                                     chat_available=chat_handler is not None)
        
        except Exception as e:
            logger.error(f"Error in POST processing: {str(e)}", exc_info=True)
            return render_template('index.html', 
                                 error=f"Analysis failed: {str(e)}",
                                 confidence=confidence, 
                                 chat_available=chat_handler is not None)

    return render_template('index.html', confidence=confidence, chat_available=chat_handler is not None)


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    if not chat_handler:
        return jsonify({
            'success': False,
            'message': 'Chat service is not available.',
            'error': 'chat_unavailable'
        })

    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Please enter a message.',
                'error': 'empty_message'
            })

        # Process message with chat handler
        response = chat_handler.process_message(user_message)
        logger.info(f"Chat message processed: {response['success']}")
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in chat route: {e}")
        return jsonify({
            'success': False,
            'message': 'Sorry, I encountered an error. Please try again.',
            'error': str(e)
        })


@app.route('/chat/history')
def chat_history():
    """Get chat history"""
    if not chat_handler:
        return jsonify({'success': False, 'error': 'chat_unavailable'})

    try:
        history = chat_handler.get_chat_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/chat/welcome')
def chat_welcome():
    """Get welcome message"""
    if not chat_handler:
        return jsonify({'success': False, 'error': 'chat_unavailable'})

    try:
        welcome = chat_handler.get_welcome_message()
        return jsonify({
            'success': True,
            'message': welcome['content'],
            'timestamp': welcome['timestamp']
        })
    except Exception as e:
        logger.error(f"Error getting welcome message: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    if not chat_handler:
        return jsonify({'success': False, 'error': 'chat_unavailable'})

    try:
        chat_handler.clear_chat_history()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error clearing chat: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/chat/status')
def chat_status():
    """Get chat system status"""
    if not chat_handler:
        return jsonify({
            'available': False,
            'message': 'Chat service not initialized'
        })

    try:
        status = chat_handler.validate_setup()
        return jsonify({
            'available': status['valid'],
            'openai_connected': status['openai_connected'],
            'message': status['message']
        })
    except Exception as e:
        logger.error(f"Error checking chat status: {e}")
        return jsonify({
            'available': False,
            'message': f'Status check failed: {str(e)}'
        })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'message': 'File size must be less than 16MB'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again.'
    }), 500


if __name__ == '__main__':
    # Validate setup before starting
    if chat_handler:
        status = chat_handler.validate_setup()
        if status['valid']:
            logger.info("✅ OrthoScan AI with Chat is ready!")
        else:
            logger.warning(f"⚠️ Chat may not work properly: {status['message']}")
    else:
        logger.warning("⚠️ Chat handler initialization failed - running without chat")
    
    app.run(debug=True)