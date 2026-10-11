
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

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Environment & Dependencies') {
            steps {
                bat '''
@echo off
python --version
if errorlevel 1 exit /b 1

docker --version
if errorlevel 1 exit /b 1

docker info
if errorlevel 1 exit /b 1
'''
            }
        }

        stage('Automated Unit Testing') {
            steps {
                bat '''
@echo off
docker build -t ai-event-management-app:test .
if errorlevel 1 exit /b 1

docker run --rm ai-event-management-app:test python -m pytest tests/ --doctest-modules -v
if errorlevel 1 exit /b 1
'''
            }
        }

        stage('Docker Container Build') {
            steps {
                bat '''
@echo off
docker build -t ai-event-management-app:latest .
if errorlevel 1 exit /b 1
'''
            }
        }

        stage('Docker Container Deployment') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'aws-ec2-ssh',
                        keyFileVariable: 'EC2_SSH_KEY',
                        usernameVariable: 'EC2_SSH_USER'
                    )
                ]) {
                    script {
                        writeFile(
                            file: 'deploy-ec2.sh',
                            text: '''#!/bin/bash
set -Eeuo pipefail

APP_DIR="/home/ubuntu/asdd-app"
ENV_FILE="/home/ubuntu/eventopia.env"
CONTAINER="ai-event-management-container"
IMAGE="ai-event-management-app"

echo "Starting Eventopia deployment..."

# Preserve the existing environment file.
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Environment file not found."
    exit 1
fi

cd "$APP_DIR"

echo "Fetching latest application code..."
git fetch origin main
git reset --hard origin/main

echo "Building Docker image on EC2..."
docker build -t "$IMAGE:latest" .

echo "Replacing the existing application container..."
docker rm -f "$CONTAINER" 2>/dev/null || true

docker run -d \
    --name "$CONTAINER" \
    --restart unless-stopped \
    --network host \
    --env-file "$ENV_FILE" \
    "$IMAGE:latest"

echo "Checking application health..."

for attempt in $(seq 1 12); do
    if curl --fail --silent http://127.0.0.1:5000/health; then
        echo
        echo "Deployment and health check successful."
        exit 0
    fi

    echo "Health check attempt $attempt/12 failed."
    sleep 5
done

echo "ERROR: Application health check failed."
docker logs --tail 100 "$CONTAINER" || true
exit 1
'''
                        )

                        bat '''
@echo off
setlocal

set "SSH_KEY_COPY=%WORKSPACE%@tmp\\ssh-deploy-%BUILD_NUMBER%.pem"
set "SSH_RESULT=1"

if not exist "%WORKSPACE%@tmp" mkdir "%WORKSPACE%@tmp"
if errorlevel 1 goto cleanup

echo Copying SSH key to a restricted temporary file...
copy /Y "%EC2_SSH_KEY%" "%SSH_KEY_COPY%" >nul
if errorlevel 1 goto cleanup

echo Restricting SSH key permissions...
icacls "%SSH_KEY_COPY%" /inheritance:r
if errorlevel 1 goto cleanup

icacls "%SSH_KEY_COPY%" /grant:r "*S-1-5-18:F"
if errorlevel 1 goto cleanup

icacls "%SSH_KEY_COPY%" /remove:g "BUILTIN\\Users" "Authenticated Users" "Everyone" >nul 2>&1

echo Connecting to EC2 and deploying Eventopia...

ssh -i "%SSH_KEY_COPY%" ^
    -o BatchMode=yes ^
    -o ConnectTimeout=15 ^
    -o StrictHostKeyChecking=yes ^
    -o "UserKnownHostsFile=C:/ProgramData/Jenkins/.ssh/known_hosts" ^
    -o GlobalKnownHostsFile=NUL ^
    "%EC2_SSH_USER%@%EC2_HOST%" "bash -s" < deploy-ec2.sh

set "SSH_RESULT=%ERRORLEVEL%"

:cleanup
if exist "%SSH_KEY_COPY%" del /F "%SSH_KEY_COPY%" >nul 2>&1

if "%SSH_RESULT%"=="0" (
    echo EC2 deployment completed successfully.
) else (
    echo EC2 deployment failed. Check the console output.
)

exit /b %SSH_RESULT%
'''
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'All five pipeline stages completed successfully.'
            echo 'Health endpoint: http://65.0.138.207:5000/health'
        }

        failure {
            echo 'Pipeline failed. Review the first error in Console Output.'
        }

        always {
            echo 'Eventopia CI/CD pipeline finished.'
        }
    }
}
