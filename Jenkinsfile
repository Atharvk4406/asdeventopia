
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        EC2_HOST = '65.0.138.207'
        EC2_SSH_USER = 'ubuntu'
        SSH_CREDENTIAL_ID = 'aws-ec2-ssh'
        APP_CONTAINER = 'ai-event-management-container'
        APP_IMAGE = 'ai-event-management-app'
        REMOTE_APP_DIR = '/home/ubuntu/asdd-app'
        KNOWN_HOSTS = 'C:/ProgramData/Jenkins/.ssh/known_hosts'
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
                bat "docker build -t ${APP_IMAGE}:test ."
                bat "docker run --rm ${APP_IMAGE}:test python -m pytest tests/ --doctest-modules -v"
            }
        }

        stage('4. Docker Container Build') {
            steps {
                echo '=== Stage 4: Building Docker Image ==='
                bat "docker build -t ${APP_IMAGE}:latest ."
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
                        writeFile file: 'deploy-ec2.sh', text: '''#!/bin/bash
set -eu

cd /home/ubuntu/asdd-app

if [ ! -f /home/ubuntu/eventopia.env ]; then
    echo "ERROR: Required environment file is missing."
    exit 1
fi

echo "Fetching latest application code..."
git fetch origin main
git reset --hard origin/main

echo "Building Docker image..."
docker build -t ai-event-management-app:latest .

echo "Replacing application container..."
docker rm -f ai-event-management-container || true

docker run -d \
    --name ai-event-management-container \
    --restart unless-stopped \
    --network host \
    --env-file /home/ubuntu/eventopia.env \
    ai-event-management-app:latest

echo "Waiting for application health endpoint..."
for attempt in $(seq 1 12); do
    if curl --fail --silent http://127.0.0.1:5000/health; then
        echo
        echo "Deployment health check passed."
        exit 0
    fi
    sleep 5
done

echo "ERROR: Application health check failed."
docker logs --tail 100 ai-event-management-container || true
exit 1
'''

                        bat '''
@echo off
ssh -i "%EC2_SSH_KEY%" -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes -o "UserKnownHostsFile=C:/ProgramData/Jenkins/.ssh/known_hosts" -o GlobalKnownHostsFile=NUL "%EC2_SSH_USER%@%EC2_HOST%" "bash -s" < deploy-ec2.sh
'''
                    }
                }
            }
        }
    }

    post {
        success {
            echo '=== SUCCESS: Eventopia CI/CD Pipeline Completed ==='
            echo 'All stages passed and the deployment health check succeeded.'
        }

        failure {
            echo '=== FAILURE: Eventopia CI/CD Pipeline Failed ==='
            echo 'Check the failed stage in Console Output.'
        }

        always {
            echo '=== ASDD CI/CD Pipeline Execution Completed ==='
        }
    }
}
