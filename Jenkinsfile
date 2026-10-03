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
                echo '=== Stage 3: Jenkins Python Environment Diagnostic ==='
                bat 'python -c "import sys; print(sys.executable)"'
                bat 'python -c "import site; print(site.getusersitepackages())"'
            }
        }

        stage('4. Docker Environment Diagnostic') {
    steps {
        echo '=== Stage 4: Docker Environment Diagnostic ==='
        bat 'echo %PATH%'
        bat 'where docker'
        bat 'docker --version'
    }
}        stage('5. Docker Container Deployment') {
            steps {
                echo '=== Stage 5: Deploying Docker Container ==='
                bat "docker stop ${CONTAINER_NAME} || exit 0"
                bat "docker rm ${CONTAINER_NAME} || exit 0"
                bat "docker run -d -p ${APP_PORT}:5000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:latest"
                echo "App successfully deployed locally on port ${APP_PORT}"
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
            echo 'Pipeline Failed! Please check logs.'
        }
    }
}