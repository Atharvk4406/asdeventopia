
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

        stage('Local Docker Container Deployment') {
            steps {
                bat '''
@echo off
setlocal

echo Updating the local Eventopia container...

REM Build the latest local image.
docker build -t ai-event-management-app:latest .
if errorlevel 1 exit /b 1

REM Remove the old local container if it exists.
docker rm -f ai-event-management-container 2>nul

REM Start the updated local container.
docker run -d ^
    --name ai-event-management-container ^
    --restart unless-stopped ^
    -p 5000:5000 ^
    ai-event-management-app:latest

if errorlevel 1 exit /b 1

echo Waiting for the local application health endpoint...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok = $false; for ($i = 0; $i -lt 12; $i++) { try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { $ok = $true; break } } catch {}; Start-Sleep -Seconds 5 }; if (-not $ok) { docker logs --tail 100 ai-event-management-container; exit 1 }"

if errorlevel 1 exit /b 1

echo Local Docker deployment and health check successful.
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

echo "Starting Eventopia EC2 deployment..."

# Preserve the existing EC2 environment file.
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Environment file not found: $ENV_FILE"
    exit 1
fi

cd "$APP_DIR"

git config --global --add safe.directory "$APP_DIR"

echo "Fetching latest application code..."
git fetch origin main

echo "Updating application to origin/main..."
git reset --hard origin/main

echo "Building Docker image on EC2..."
docker build -t "$IMAGE:latest" .

echo "Removing the old EC2 container if present..."
docker rm -f "$CONTAINER" 2>/dev/null || true

echo "Starting the updated EC2 container..."
docker run -d \
    --name "$CONTAINER" \
    --restart unless-stopped \
    --network host \
    --env-file "$ENV_FILE" \
    "$IMAGE:latest"

echo "Waiting for the EC2 health endpoint..."

for attempt in $(seq 1 12); do
    if curl --fail --silent http://127.0.0.1:5000/health; then
        echo
        echo "EC2 deployment and health check successful."
        exit 0
    fi

    echo "Health check attempt $attempt/12 failed."
    sleep 5
done

echo "ERROR: EC2 application health check failed."
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

echo Copying SSH key to a temporary file...
copy /Y "%EC2_SSH_KEY%" "%SSH_KEY_COPY%" >nul
if errorlevel 1 goto cleanup

echo Restricting private key permissions...
icacls "%SSH_KEY_COPY%" /inheritance:r
if errorlevel 1 goto cleanup

icacls "%SSH_KEY_COPY%" /grant:r "*S-1-5-18:F"
if errorlevel 1 goto cleanup

icacls "%SSH_KEY_COPY%" /remove:g "BUILTIN\\Users" "Authenticated Users" "Everyone" >nul 2>&1

echo Connecting to EC2 and running deployment...

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
    echo EC2 deployment failed. Check the console output above.
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
            echo 'All six pipeline stages completed successfully.'
            echo 'Local health endpoint: http://localhost:5000/health'
            echo 'EC2 health endpoint: http://65.0.138.207:5000/health'
        }

        failure {
            echo 'Pipeline failed. Review the first error in Console Output.'
        }

        always {
            echo 'Eventopia CI/CD pipeline finished.'
        }
    }
}
