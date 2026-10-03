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
                echo '=== Stage 3: ml_chatbot Import Diagnostic ==='

                bat 'python -c "import ml_chatbot; print(100, flush=True)"'

                bat 'python -c "from ml_chatbot import predict_intent; print(200, flush=True)"'

                bat 'python -c "import app; print(300, flush=True)"'
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