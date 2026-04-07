# OrthoAssist AI — Clinical Fracture Analysis System

> **For Research & Educational Use Only.**
> All AI-generated findings must be reviewed by a licensed radiologist or orthopedic specialist before any clinical application.

---

## Overview

OrthoAssist AI is an advanced orthopedic fracture analysis web application that combines state-of-the-art computer vision models with a conversational AI assistant. It enables rapid, preliminary screening of X-ray images for bone classification and fracture detection.

**Key capabilities:**
- Automated bone/organ classification using a ResNet50 ONNX model
- Fracture detection with bounding boxes using YOLOv8
- Context-aware AI clinical assistant powered by GPT-3.5 Turbo
- Professional medical-grade interface for research and education

---

## Demo

<p align="center">
  <img src="https://raw.githubusercontent.com/amerob/orthoassist/main/assets/ortho1.png" width="900"/>
</p>

### AI Clinical Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/amerob/orthoassist/main/assets/ortho2.png" width="900"/>
</p>

| Upload & Analysis | Diagnostic Report |
|---|---|
| Drag-and-drop X-ray → set confidence threshold → Run Analysis | Side-by-side original vs. annotated, detection table with severity |

---

## Features

### Imaging & Detection
- **Drag-and-drop upload** — supports JPEG, PNG, BMP up to 16 MB
- **Organ Classification** — ResNet50 ONNX identifies: Elbow, Finger, Forearm, Humerus, Shoulder, Wrist
- **Fracture Detection** — YOLOv8 localizes fractures with confidence scores and bounding boxes
- **Adjustable confidence threshold** — slider from 0–100% for detection sensitivity
- **Side-by-side image comparison** — original vs. AI-annotated with lightbox zoom
- **Detection table** — lists all findings with confidence bars and severity ratings (High / Moderate / Low)

### AI Clinical Assistant
- **Context-aware chat** — GPT-3.5 Turbo answers questions about the uploaded X-ray results
- **Medical disclaimers** — clearly communicates educational-only scope
- **Chat history** — retains up to 20 messages per session, with clear/reset option
- **Dynamic welcome message** — summarizes detected findings on chat open

### Interface
- Professional dark clinical UI — built for radiological reading environments
- Responsive layout — desktop sidebar, stacked on mobile
- Print-ready report — hides UI chrome, prints the diagnostic section cleanly
- Session clock, model status badge, system health indicator

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.9, Flask 3.1.1 |
| **Organ Classifier** | ResNet50 (ONNX Runtime 1.22.0) |
| **Fracture Detector** | YOLOv8 (Ultralytics 8.3.14) |
| **Deep Learning** | PyTorch 2.7.0 + TorchVision 0.22.0 |
| **Image Processing** | OpenCV 4.11.0, Pillow 11.2.1 |
| **AI Assistant** | OpenAI GPT-3.5 Turbo |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Icons** | Font Awesome 6.4.0 |
| **Deployment** | Docker (Python 3.9-slim) |

---

## Project Structure

```
chat_app/
├── app.py                      # Flask routes & prediction pipeline
├── config.py                   # API keys, model paths, system prompts
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker containerization
├── chatbot/
│   ├── chat_handler.py         # Session management & chat orchestration
│   └── openai_client.py        # OpenAI GPT integration
├── model/
│   ├── resnet50_fracture.onnx  # Organ classifier (~94 MB)
│   └── yolo_fracture_detection.pt  # Fracture detector (~5 MB)
├── static/
│   ├── css/
│   │   ├── styles.css          # Main clinical design system
│   │   └── chat.css            # Chat panel styles
│   ├── js/
│   │   ├── main.js             # Upload, slider, loading logic
│   │   └── chat.js             # Chat interface class
│   └── upload/                 # Uploaded & annotated image outputs
└── templates/
    └── index.html              # Single-page Jinja2 template
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/amerob/OrthoAssistAI.git
cd orthoassist/chat_app

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...

# 5. Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

### Docker

```bash
docker build -t orthoassist .
docker run -p 5000:5000 -e OPENAI_API_KEY=sk-... orthoassist
```

---

## API Endpoints

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing page |
| `/` | POST | Upload X-ray and run analysis |
| `/chat` | POST | Send chat message, receive AI reply |
| `/chat/history` | GET | Retrieve session chat history |
| `/chat/welcome` | GET | Get context-aware welcome message |
| `/chat/clear` | POST | Clear chat history |
| `/chat/status` | GET | Check AI assistant availability |

---

## Configuration (`config.py`)

| Parameter | Default | Description |
|---|---|---|
| `OPENAI_MODEL` | `gpt-3.5-turbo` | Language model for chat |
| `MAX_TOKENS` | `500` | Max tokens per AI response |
| `MAX_CONTENT_LENGTH` | `16 MB` | Upload size limit |
| `CONFIDENCE_DEFAULT` | `0.3` | Default detection threshold |
| `ORGAN_CLASSES` | 6 classes | Elbow, Finger, Forearm, Humerus, Shoulder, Wrist |

---

## Models

### ResNet50 (Organ Classification)
- Format: ONNX
- Input: 224×224 RGB image, normalized
- Output: 6-class softmax (bone type)
- Size: ~94 MB

### YOLOv8 (Fracture Detection)
- Framework: Ultralytics YOLOv8
- Task: Object detection (fracture localization)
- Output: Bounding boxes + confidence scores
- Size: ~5 MB

---

## Medical Disclaimer

> This application is developed for **research and educational purposes only**.
> It is **not a medical device** and has **not been approved** by any regulatory authority (FDA, CE, etc.).
> All outputs are preliminary AI inferences and must be validated by a licensed medical professional before any clinical use.
> Do not make clinical decisions based solely on this system's output.

---

## License

This project is released under the [MIT License](LICENSE).

---

## Author

**Amer Obaidat**
- Built for medical AI research and educational demonstrations
- Combines classical deep learning (ResNet50, YOLOv8) with LLM-powered clinical assistance

---

## Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [ONNX Runtime](https://onnxruntime.ai/)
- [OpenAI API](https://platform.openai.com/)
- [Flask](https://flask.palletsprojects.com/)
