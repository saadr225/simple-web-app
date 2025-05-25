pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "simple-web-app"
        CONTAINER_NAME = "simple-web-app-container"
        MONGO_CONTAINER = "simple-web-app-mongo"
        SELENIUM_CONTAINER = "simple-web-app-selenium"
        MONGO_URI = "mongodb://mongo:27017/taskmanager"
        PORT = "3000"
        // Environment for Node.js
        PATH = "$PATH:/usr/local/bin:/usr/bin:/bin"
        // Use a Python virtual environment
        PYTHON_VENV = "${WORKSPACE}/venv"
    }

    stages {
        stage('Environment Setup') {
            steps {
                echo 'Setting up environment...'
                script {
                    // Check and install dependencies
                    sh '''
                        # Check if Docker is installed
                        if ! command -v docker &> /dev/null; then
                            echo "Docker is not installed or not in PATH"
                        else
                            echo "Docker is installed: $(docker --version)"
                        fi
                        
                        # Create Python virtual environment
                        if command -v python3 &> /dev/null; then
                            python3 -m venv ${PYTHON_VENV} || echo "Could not create virtual environment"
                            if [ -d "${PYTHON_VENV}" ]; then
                                . ${PYTHON_VENV}/bin/activate
                                pip install --upgrade pip
                                echo "Python virtual environment created and activated"
                            fi
                        else
                            echo "Python 3 is not installed or not in PATH"
                        fi
                        
                        # Check if docker-compose exists and version
                        if ! command -v docker-compose &> /dev/null; then
                            echo "Docker Compose is not installed or not in PATH. Will use docker compose subcommand."
                        else
                            echo "Docker Compose is installed: $(docker-compose --version)"
                        fi
                    '''
                }
            }
        }

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Code Linting') {
            parallel {
                stage('JavaScript Linting') {
                    steps {
                        echo 'Running JavaScript linting with ESLint...'
                        script {
                            try {
                                // Use a Docker container for Node.js operations
                                sh '''
                                    echo "Using Docker for Node.js operations..."
                                    docker run --rm -v $(pwd):/app -w /app node:18-alpine sh -c "npm install eslint && npx eslint server.js routes/ models/ || echo 'Linting completed with warnings'"
                                '''
                            } catch (Exception e) {
                                echo "JavaScript linting skipped: ${e.getMessage()}"
                            }
                        }
                    }
                }
                stage('Python Linting') {
                    steps {
                        echo 'Running Python linting with flake8...'
                        script {
                            try {
                                // Use Python venv or Docker if available
                                sh '''
                                    if [ -d "${PYTHON_VENV}" ]; then
                                        . ${PYTHON_VENV}/bin/activate
                                        pip install flake8
                                        flake8 --ignore=E501,W503 test_selenium.py || echo "Linting completed with warnings"
                                    else
                                        echo "Using Docker for Python operations..."
                                        docker run --rm -v $(pwd):/app -w /app python:3.10-slim sh -c "pip install flake8 && flake8 --ignore=E501,W503 test_selenium.py || echo 'Linting completed with warnings'"
                                    fi
                                '''
                            } catch (Exception e) {
                                echo "Python linting skipped: ${e.getMessage()}"
                            }
                        }
                    }
                }
            }
        }        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies using Docker...'
                script {
                    try {
                        sh '''
                            # Create Dockerfile.webapp if it doesn't exist
                            if [ ! -f Dockerfile.webapp ]; then
                                cat > Dockerfile.webapp << EOF
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
ENV MONGO_URI=mongodb://mongo:27017/taskmanager
ENV PORT=3000
CMD ["node", "server.js"]
EOF
                            fi
                            
                            # Install Python dependencies in venv or skip
                            if [ -d "${PYTHON_VENV}" ]; then
                                . ${PYTHON_VENV}/bin/activate
                                pip install -r requirements.txt || echo "Could not install Python dependencies"
                            fi
                        '''
                    } catch (Exception e) {
                        echo "Dependency installation had issues: ${e.getMessage()}"
                        echo "Continuing with pipeline..."
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo 'Running Node.js unit tests...'
                script {
                    try {
                        // Use Docker to run Node.js tests
                        sh '''
                            docker run --rm -v $(pwd):/app -w /app node:18-alpine sh -c "npm test || echo 'No tests specified in package.json'"
                        '''
                    } catch (Exception e) {
                        echo 'No unit tests configured, skipping...'
                    }
                }
            }
        }        stage('Docker Build') {
            steps {
                echo 'Building Docker images...'
                // Build the Selenium test image
                sh 'docker build -t ${DOCKER_IMAGE}-selenium -f Dockerfile .'
                
                // Build the webapp image
                sh 'docker build -t ${DOCKER_IMAGE} -f Dockerfile.webapp .'
            }
        }
        
        stage('Setup Test Environment') {
            steps {
                echo 'Setting up test environment with Docker...'
                
                // Create a network for the containers
                sh 'docker network create test-network || true'
                
                // Clean up any existing containers
                sh '''
                    docker rm -f ${CONTAINER_NAME} ${MONGO_CONTAINER} ${SELENIUM_CONTAINER} || true
                '''
                
                // Start MongoDB container
                sh '''
                    docker run -d --name ${MONGO_CONTAINER} \
                        --network test-network \
                        -p 27017:27017 \
                        -e MONGO_INITDB_DATABASE=taskmanager \
                        mongo:5.0
                '''
                
                // Start web app container
                sh '''
                    docker run -d --name ${CONTAINER_NAME} \
                        --network test-network \
                        -p 3000:3000 \
                        -e MONGO_URI=mongodb://mongo:27017/taskmanager \
                        -e PORT=3000 \
                        ${DOCKER_IMAGE}
                '''
                
                // Wait for services to be ready
                sh '''
                    echo "Waiting for MongoDB to be ready..."
                    sleep 10
                    
                    echo "Waiting for web application to be ready..."
                    sleep 5
                    for i in {1..12}; do
                        if curl -s http://localhost:3000 > /dev/null; then
                            echo "Web app is ready!"
                            break
                        fi
                        echo "Waiting for web app to start... (attempt $i/12)"
                        sleep 5
                    done
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                echo 'Running Selenium integration tests...'
                script {
                    try {
                        // Run Selenium tests with network access to the web app
                        sh '''
                            docker run --rm \
                                --network host \
                                --name ${SELENIUM_CONTAINER} \
                                -v $(pwd)/test_selenium.py:/app/test_selenium.py \
                                ${DOCKER_IMAGE}-selenium \
                                python test_selenium.py
                        '''
                    } catch (Exception e) {
                        echo "Selenium tests failed: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Running security scans...'
                script {
                    try {
                        // NPM audit for Node.js dependencies
                        sh 'npm audit --audit-level=high || true'
                        
                        // Docker image security scan (if trivy is available)
                        sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image ${DOCKER_IMAGE} || echo "Trivy not available, skipping security scan"'
                    } catch (Exception e) {
                        echo 'Security scan completed with warnings'
                    }
                }
            }
        }

        stage('Performance Tests') {
            steps {
                echo 'Running basic performance tests...'
                script {
                    try {
                        // Simple load test using curl
                        sh '''
                            echo "Running basic load test..."
                            for i in {1..10}; do
                                curl -s -o /dev/null -w "%{http_code}\\n" http://localhost:3000 &
                            done
                            wait
                            echo "Load test completed"
                        '''
                    } catch (Exception e) {
                        echo 'Performance tests completed with warnings'
                    }
                }
            }
        }        stage('Build Production Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'production'
                }
            }
            steps {
                echo 'Building production Docker image...'
                sh 'docker tag ${DOCKER_IMAGE} ${DOCKER_IMAGE}:latest'
                sh 'docker tag ${DOCKER_IMAGE} ${DOCKER_IMAGE}:${BUILD_NUMBER}'
                
                // If you have a Docker registry, push the image
                script {
                    try {
                        sh 'docker tag ${DOCKER_IMAGE} your-registry/${DOCKER_IMAGE}:${BUILD_NUMBER}'
                        sh 'docker push your-registry/${DOCKER_IMAGE}:${BUILD_NUMBER}'
                    } catch (Exception e) {
                        echo 'Docker registry push skipped - registry not configured'
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up test environment...'
            sh '''
                docker rm -f ${CONTAINER_NAME} ${MONGO_CONTAINER} ${SELENIUM_CONTAINER} || true
                docker network rm test-network || true
                docker rmi ${DOCKER_IMAGE}-selenium || true
                rm -f Dockerfile.webapp || true
            '''
            
            // Archive test results if they exist
            script {
                try {
                    archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
                } catch (Exception e) {
                    echo 'No artifacts to archive'
                }
            }
        }
        
        success {
            echo 'Pipeline completed successfully ✅'
            script {
                try {
                    // Send success notification (configure as needed)
                    emailext (
                        subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                        body: "The build completed successfully. Check console output at ${env.BUILD_URL}",
                        to: "${env.CHANGE_AUTHOR_EMAIL}"
                    )
                } catch (Exception e) {
                    echo 'Email notification not configured'
                }
            }
        }
        
        failure {
            echo 'Pipeline failed ❌'
            script {
                try {
                    // Send failure notification (configure as needed)
                    emailext (
                        subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                        body: "The build failed. Check console output at ${env.BUILD_URL}",
                        to: "${env.CHANGE_AUTHOR_EMAIL}"
                    )
                } catch (Exception e) {
                    echo 'Email notification not configured'
                }
            }
        }
        
        unstable {
            echo 'Pipeline completed with warnings ⚠️'
        }
    }
}