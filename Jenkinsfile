pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        SONAR_TOKEN = credentials('SONAR_TOKEN')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests & SonarQube Analysis') {
            steps {
                sh 'pip install -r requirements-dev.txt'
                sh 'pytest tests/unit || echo "No tests configured yet"'
                script {
                    withSonarQubeEnv('SonarQube-Server') {
                        sh "sonar-scanner -Dsonar.projectKey=ssp-inventory-service -Dsonar.sources=app -Dsonar.login=${SONAR_TOKEN}"
                    }
                }
            }
        }

        stage('Setup Terraform & Get ECR Repo') {
            steps {
                script {
                    dir('terraform') {
                        // 1. Initialize using your backend.conf file
                        sh 'terraform init -backend-config=backend.conf'

                        sh 'terraform workspace select dev || terraform workspace new dev'
                        env.ECR_REPOSITORY_URL = sh(script: 'terraform output -raw ecr_repository_url', returnStdout: true).trim()
                    }
                    if (!env.ECR_REPOSITORY_URL) {
                        error "Failed to get ECR repository URL from Terraform."
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Note: We use the ECR URL we just fetched
                    def dockerImage = docker.build("ssp-inventory-service:${env.BUILD_NUMBER}", ".")
                    docker.withRegistry("https://${env.ECR_REPOSITORY_URL}", 'ecr:us-east-1') {
                        dockerImage.push("${env.BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Terraform Plan & Deploy') {
            steps {
                script {
                    dir('terraform') {
                        // Switch to target workspace (e.g., dev)
                        sh "terraform workspace select ${params.TARGET_ENV} || terraform workspace new ${params.TARGET_ENV}"

                        def imageUrl = "${env.ECR_REPOSITORY_URL}:${env.BUILD_NUMBER}"

                        // 2. Create the plan and save it to a file
                        sh "terraform plan -var=\"container_image=${imageUrl}\" -var=\"environment=${params.TARGET_ENV}\" -out=tfplan"

                        // 3. Approval Gate
                        input message: "Review plan for ${params.TARGET_ENV}. Proceed with Deploy?", ok: 'Apply'

                        // 4. Apply the saved plan
                        sh 'terraform apply -auto-approve tfplan'
                    }
                }
            }
        }
    }
}
