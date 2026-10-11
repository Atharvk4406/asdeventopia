```groovy
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'ai-event-management-app'
        CONTAINER_NAME = 'ai-event-management-container'
        APP_PORT = '5000'
        EC2_HOST = '65.0.138.207'
        EC2_USER = 'ubuntu'
        SSH_CREDENTIAL_ID = 'aws-ec2-ssh'
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
                bat "docker build -t ${IMAGE_NAME}:test ."
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
                echo '=== Stage 5: Deploying to AWS EC2 using SSH ==='

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${SSH_CREDENTIAL_ID}",
                        keyFileVariable: 'EC2_SSH_KEY',
                        usernameVariable: 'EC2_SSH_USER'
                    )
                ]) {
                    script {
                        def deployScript = '''
set -eu

cd /home/ubuntu/asdd-app

echo "Checking deployment prerequisites..."
test -f /home/ubuntu/eventopia.env
command -v docker

echo "Fetching latest application code..."
git fetch origin main
git reset --hard origin/main

echo "Building the application image..."
docker build -t ai-event-management-app:latest .

echo "Replacing the application container..."
docker rm -f ai-event-management-container || true

docker run -d \
  --name ai-event-management-container \
  --network host \
  --env-file /home/ubuntu/eventopia.env \
  --restart unless-stopped \
  ai-event-management-app:latest

echo "Waiting for the health endpoint..."
for attempt in $(seq 1 12); do
    if curl --fail --silent http://127.0.0.1:5000/health; then
        echo
        echo "Deployment health check passed."
        exit 0
    fi
    sleep 5
done

echo "Health check failed."
docker logs --tail 80 ai-event-management-container || true
exit 1
'''

                        writeFile(
                            file: 'deploy-ec2.sh',
                            text: deployScript.replace('\r', '')
                        )

                        bat """
@echo off
ssh -i "%EC2_SSH_KEY%" -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes %EC2_SSH_USER%@${EC2_HOST} "bash -s" < deploy-ec2.sh
if errorlevel 1 exit /b 1
"""
                    }
                }

                echo 'AWS deployment and health check completed.'
            }
        }
    }

    post {
        always {
            echo '=== ASDD CI/CD Pipeline Execution Completed ==='
        }

        success {
            echo 'Pipeline Succeeded! Application deployment health check passed.'
        }

        failure {
            echo 'Pipeline Failed! Please check Jenkins logs.'
        }
    }
}
```