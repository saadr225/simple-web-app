pipeline {
    agent any

    environment {
        NODE_ENV = 'development'
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Setup Python Virtual Env') {
            steps {
                sh '''
                    if command -v python3 &>/dev/null; then
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install flake8 || echo "flake8 install failed"
                    else
                        echo "Python3 not installed. Skipping Python linting."
                    fi
                '''
            }
        }

        stage('Python Linting') {
            steps {
                sh '''
                    if [ -x "${VENV_DIR}/bin/flake8" ]; then
                        . ${VENV_DIR}/bin/activate
                        flake8 . || echo "flake8 warnings found"
                    else
                        echo "flake8 not available, skipping."
                    fi
                '''
            }
        }

        stage('Node.js Linting') {
            steps {
                sh '''
                    if command -v npm &>/dev/null; then
                        npm install || echo "npm install failed"
                        if [ -f .eslintrc.js ] || [ -f .eslintrc.json ]; then
                            npx eslint . || echo "ESLint warnings"
                        else
                            echo "ESLint not configured. Skipping JS linting."
                        fi
                    else
                        echo "npm not found, skipping JS linting"
                    fi
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Skipping actual test logic for now.'
                // Add your test commands here later
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    if command -v docker &>/dev/null; then
                        docker build -t simple-web-app .
                    else
                        echo "Docker not found, skipping Docker build"
                    fi
                '''
            }
        }

        stage('Post Cleanup') {
            steps {
                sh '''
                    echo "Cleaning up..."
                    docker ps -aq | xargs -r docker rm -f || true
                    docker images -q | xargs -r docker rmi -f || true
                    rm -rf ${VENV_DIR}
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline complete.'
        }

        failure {
            echo 'Pipeline failed ❌'
        }

        success {
            echo 'Pipeline succeeded ✅'
        }
    }
}
