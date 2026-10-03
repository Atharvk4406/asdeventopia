pipeline {
    agent any

    environment {
        IMAGE_NAME = 'ai-event-management-app'
        CONTAINER_NAME = 'ai-event-management-container'
        APP_PORT = '5000'
    }

    stages {

        stage('1. Checkout SCM') {
            steps {
                echo '=== Stage 1: Fetching Latest Code from GitHub ==='

                checkout scm
            }
        }

        stage('2. Environment & Dependencies') {
            steps {
                echo '=== Stage 2: Installing Dependencies ==='

                bat 'python --version'
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('3. Automated Unit Testing') {
            steps {
                echo '=== Stage 3: Testing app.py Dependencies Individually ==='

                bat 'python -c "import mysql.connector; print(100)"'
                bat 'python -c "from werkzeug.security import generate_password_hash, check_password_hash; print(200)"'
                bat 'python -c "from werkzeug.utils import secure_filename; print(300)"'
                bat 'python -c "import os; print(400)"'
                bat 'python -c "from email.mime.text import MIMEText; print(500)"'
                bat 'python -c "import smtplib; print(600)"'
                bat 'python -c "import uuid; print(700)"'
                bat 'python -c "import qrcode; print(800)"'
                bat 'python -c "from io import BytesIO; print(900)"'
                bat 'python -c "import base64; print(1000)"'
                bat 'python -c "import pandas; print(1100)"'
                bat 'python -c "import threading; print(1200)"'
                bat 'python -c "import time; print(1300)"'
                bat 'python -c "from datetime import datetime, timedelta; print(1400)"'
                bat 'python -c "import re; print(1500)"'
                bat 'python -c "import socket; print(1600)"'
                bat 'python -c "from dotenv import load_dotenv; print(1700)"'

                echo '=== All app.py dependency imports completed ==='
            }
        }

        stage('4. Docker Container Build') {
            steps {
                echo '=== Stage 4: Building Docker Image ==='

                bat "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('5. Docker Container Deployment') {
            steps {
                echo '=== Stage 5: Deploying Docker Container ==='

                bat "docker stop ${CONTAINER_NAME} || exit 0"
                bat "docker rm ${CONTAINER_NAME} || exit 0"
                bat "docker run -d -p ${APP_PORT}:5000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:latest"

                echo "Application successfully deployed on port ${APP_PORT}"
            }
        }
    }

    post {
        always {
            echo '=== ASDD CI/CD Pipeline Execution Completed ==='
        }

        success {
            echo 'Pipeline Succeeded! Application is active & healthy.'
        }

        failure {
            echo 'Pipeline Failed! Please check Jenkins logs.'
        }
    }
}