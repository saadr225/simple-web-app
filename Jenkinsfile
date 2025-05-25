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

        stage('Python & JS Linting') {
            parallel {
                stage('Python Linting') {
                    steps {
                        sh '''
                            python3 -m venv ${VENV_DIR}
                            . ${VENV_DIR}/bin/activate
                            pip install --upgrade pip flake8
                            flake8 . || echo "flake8 warnings found"
                        '''
                    }
                }
                stage('Node.js Linting') {
                    steps {
                        sh '''
                            if command -v npm &>/dev/null; then
                                npm install
                                if [ -f .eslintrc.js ] || [ -f .eslintrc.json ]; then
                                    npx eslint . || echo "ESLint warnings"
                                else
                                    echo "ESLint not configured. Skipping JS linting."
                                fi
                            fi
                        '''
                    }
                }
            }
        }

        stage('Build Web App Docker Image') {
            steps {
                sh 'docker build -f Dockerfile.webapp -t webapp-image .'
            }
        }

        stage('Run Web App Container') {
            steps {
                sh 'docker run -d -p 3000:3000 --name webapp-test webapp-image'
            }
        }

        stage('Wait for Web App') {
            steps {
                sh '''
                    echo "Waiting for app to start..."
                    sleep 10
                    curl -f http://localhost:3000 || (echo "Web app not responding" && exit 1)
                '''
            }
        }

        stage('Run Selenium Test Container') {
            steps {
                sh '''
                    docker build -t selenium-test -f Dockerfile .
                    docker run --rm --network host -e APP_URL=http://localhost:3000 selenium-test

                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    docker rm -f webapp-test || true
                    docker rmi -f webapp-image selenium-test || true
                    rm -rf ${VENV_DIR}
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline complete.'
        }
        success {
            echo 'Pipeline succeeded ✅'
        }
        failure {
            echo 'Pipeline failed ❌'
        }
    }
}
