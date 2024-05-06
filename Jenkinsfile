pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'python:3.9.13-alpine3.16'
    }

    stages {
        stage('Cache Dependencies') {
            steps {
                script {
                    // Loading the dependency cache if present
                    def cachedDeps = cache(steps: [
                        // Copying the dependency cache to the working directory
                        load('/path/to/cache/key')
                    ])
                    // If the cache was found, use it, otherwise install the dependencies again
                    if (cachedDeps != null) {
                        echo 'Using cached dependencies'
                    } else {
                        echo 'Installing dependencies'
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Building a Docker image
                    docker.build DOCKER_IMAGE, '--file Dockerfile .'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Running tests inside a Docker container
                    docker.withRegistry('', '') {
                        docker.image(DOCKER_IMAGE).inside('-v $PWD:/usr/workspace') {
                            sh 'ls -la'
                            sh 'pytest -sv --alluredir=allure-results'
                        }
                    }
                }
            }
        }

    }

    post {
        always {
            // Maintain dependency cache for future builds
            cache(save: '/path/to/cache/key', paths: ['~/.cache/pip'])
        }
    }
}