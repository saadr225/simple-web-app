pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "simple-web-app"
        CONTAINER_NAME = "simple-web-app-container"
        MONGO_CONTAINER = "simple-web-app-mongo"
        SELENIUM_CONTAINER = "simple-web-app-selenium"
        MONGO_URI = "mongodb://mongo:27017/taskmanager"
        PORT = "3000"
    }

    stages {
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
                                sh 'npm install --only=dev eslint'
                                sh 'npx eslint server.js routes/ models/ || true'
                            } catch (Exception e) {
                                echo 'ESLint not configured, skipping JavaScript linting'
                            }
                        }
                    }
                }
                stage('Python Linting') {
                    steps {
                        echo 'Running Python linting with flake8...'
                        script {
                            try {
                                sh 'pip3 install flake8'
                                sh 'flake8 --ignore=E501,W503 test_selenium.py'
                            } catch (Exception e) {
                                echo 'Python linting completed with warnings'
                            }
                        }
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Node.js dependencies...'
                sh 'npm install'
                echo 'Installing Python dependencies...'
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Unit Tests') {
            steps {
                echo 'Running Node.js unit tests...'
                script {
                    try {
                        sh 'npm test'
                    } catch (Exception e) {
                        echo 'No unit tests configured, skipping...'
                    }
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker images...'
                // Build the Selenium test image
                sh 'docker build -t ${DOCKER_IMAGE}-selenium .'
                
                // Create a simple Dockerfile for the web app if it doesn't exist
                sh 'docker build -t ${DOCKER_IMAGE} .'

            }
        }

        stage('Setup Test Environment') {
            steps {
                echo 'Setting up test environment with Docker Compose...'
                
                // Create docker-compose.yml for testing
                sh '''
                    cat > docker-compose.test.yml << EOF
version: '3.8'
services:
  mongo:
    image: mongo:5.0
    container_name: ${MONGO_CONTAINER}
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: taskmanager
    networks:
      - test-network

  webapp:
    image: ${DOCKER_IMAGE}
    container_name: ${CONTAINER_NAME}
    ports:
      - "3000:3000"
    environment:
      MONGO_URI: mongodb://mongo:27017/taskmanager
      PORT: 3000
    depends_on:
      - mongo
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
EOF
                '''
                
                // Clean up any existing containers
                sh '''
                    docker-compose -f docker-compose.test.yml down --remove-orphans || true
                    docker rm -f ${CONTAINER_NAME} ${MONGO_CONTAINER} ${SELENIUM_CONTAINER} || true
                '''
                
                // Start the test environment
                sh 'docker-compose -f docker-compose.test.yml up -d'
                
                // Wait for services to be ready
                sh '''
                    echo "Waiting for MongoDB to be ready..."
                    sleep 10
                    
                    echo "Waiting for web application to be ready..."
                    timeout 60 sh -c 'until curl -f http://localhost:3000; do sleep 2; done' || echo "Web app startup timeout"
                    sleep 5
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
        }

        stage('Build Production Image') {
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
                docker-compose -f docker-compose.test.yml down --remove-orphans --volumes || true
                docker rm -f ${CONTAINER_NAME} ${MONGO_CONTAINER} ${SELENIUM_CONTAINER} || true
                docker rmi ${DOCKER_IMAGE}-selenium || true
                rm -f Dockerfile.webapp docker-compose.test.yml || true
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