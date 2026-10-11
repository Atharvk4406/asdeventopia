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
                echo '=== Stage 3: Running PyTest inside Docker ==='

                echo '--- Building test image ---'
                bat "docker build -t ${IMAGE_NAME}:test ."

                echo '--- Running PyTest inside Linux Docker container ---'
                bat "docker run --rm ${IMAGE_NAME}:test python -m pytest tests/ --doctest-modules -v"
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
                echo '=== Stage 5: Deploying to AWS EC2 using Ansible ==='

                bat '''
                wsl.exe -d Ubuntu -u atharv -- bash -lc "cd '/mnt/d/ASD MIni project' && ansible-playbook -i ansible/inventory ansible/deploy.yml"
                '''

                echo 'Ansible deployment and health check completed.'
            }
        }
    }

    post {
        always {
            echo '=== ASDD CI/CD Pipeline Execution Completed ==='
        }

        success {
            echo 'Pipeline Succeeded! Application deployed to AWS EC2.'
        }

        failure {
            echo 'Pipeline Failed! Please check Jenkins logs.'
        }
    }
}