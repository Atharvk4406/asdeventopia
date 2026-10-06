# 🎪 Eventopia — AI-Based Event Management System

An intelligent, full-stack college event & tech fest management portal powered by **Flask**, **MySQL**, **Google Gemini AI**, **Scikit-Learn NLP**, and modern DevOps tools.

---

## 🌟 Key Features

- **🤖 Dual-Engine AI Assistant**:
  - **Gemini AI Chatbot**: Natural language query interface powered by Google Gemini API to answer queries about upcoming events, schedules, venues, and pricing.
  - **RandomForest ML Intent Classifier**: Fallback intent prediction model built using TF-IDF Vectorizer and Scikit-Learn `RandomForestClassifier`.
- **🎫 Digital Ticket Generation & Verification**:
  - Automated QR code generation for user event registrations.
  - Verification & attendance scanning for event coordinators and staff.
- **🏛️ Department Tech Fests & Competitions**:
  - Full support for multi-category event hierarchies (Tech Fests, Competitions, Workshops, Hackathons).
  - Registration deadline management with automated notifications.
- **⏰ Smart Automated Reminders**:
  - Background daemon threads for 1-hour email reminders and deadline notifications.
- **📊 Admin Dashboard & Analytics**:
  - Real-time registration statistics, feedback rating calculation, and activity logs.
- **🔄 DevOps & CI/CD Pipeline**:
  - **Containerization**: Dockerfile for containerized deployment.
  - **CI/CD Automation**: Jenkinsfile pipeline for automated dependency setup, PyTest unit tests, Docker build & container lifecycle.
  - **Infrastructure as Code**: Terraform configuration for provisioning infrastructure.
  - **Configuration Management**: Ansible playbooks for server deployment.

---

## 🏗️ Project Architecture

```
ASD MINI PROJECT /
├── app.py                     # Main Flask Application & Core Routes
├── chatbot.py                 # Google Gemini AI Chatbot Module
├── ml_chatbot.py              # RandomForest ML Intent Classification Module
├── intents.json               # Intent definitions for ML classifier
├── templates/                 # Jinja2 HTML Templates
├── static/                    # Custom CSS, JS, Images & QR Tickets
│   ├── css/style.css
│   └── uploads/
├── tests/                     # Automated PyTest Test Suite
│   └── test_app.py
├── ansible/                   # Ansible Playbooks & Inventory
├── terraform/                 # Infrastructure Provisioning Scripts
├── Dockerfile                 # Container Build Configuration
├── Jenkinsfile                # CI/CD Pipeline Definition
└── requirements.txt           # Python Dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- MySQL Server (Database name: `eventhopia`)

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY="your_google_gemini_api_key"
NGROK_AUTHTOKEN="your_ngrok_authtoken"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Access the application at `http://localhost:5000`.

---

## 🧪 Testing & CI/CD

Run unit tests locally with PyTest:
```bash
pytest
```

---

## 🔌 API & Health Endpoints

- `GET /health`: Health check endpoint for container / Jenkins liveness checks.
- `GET /api/info`: System metadata and DevOps stack info.
- `POST /chatbot`: Chatbot query endpoint.
## DevOps Workflow

Eventopia follows an Agile and DevOps workflow using GitHub, PyTest, Docker, Jenkins, Terraform, and Ansible.

Jenkins Poll SCM test
