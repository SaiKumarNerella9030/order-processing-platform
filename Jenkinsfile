pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        KUBE_CONFIG = credentials('kubeconfig-creds')
    }

    stages {
        stage('Init Kube Config') {
            steps {
                sh 'mkdir -p ~/.kube && echo "$KUBE_CONFIG" > ~/.kube/config'
            }
        }

        stage('Create Namespaces') {
            steps {
                sh '''
                kubectl create namespace devopsify --dry-run=client -o yaml | kubectl apply -f -
                kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
                '''
            }
        }

        stage('Apply Prometheus RBAC') {
            steps {
                sh '''
                kubectl apply -f monitoring/prometheus/rbac/serviceaccount.yaml
                kubectl apply -f monitoring/prometheus/rbac/role.yaml
                kubectl apply -f monitoring/prometheus/rbac/rolebinding.yaml
                '''
            }
        }

        stage('Install Prometheus via Helm') {
            steps {
                sh '''
                helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
                helm repo update
                helm upgrade --install prometheus prometheus-community/prometheus \
                    --namespace monitoring \
                    --values monitoring/prometheus/values.yaml \
                    --set serviceAccounts.server.name=prometheus-sa
                '''
            }
        }

        stage('Apply Grafana RBAC') {
            steps {
                sh '''
                kubectl apply -f monitoring/grafana/rbac/serviceaccount.yaml
                kubectl apply -f monitoring/grafana/rbac/clusterrole.yaml
                kubectl apply -f monitoring/grafana/rbac/clusterrolebinding.yaml
                '''
            }
        }

        stage('Install Grafana via Helm') {
            steps {
                sh '''
                helm repo add grafana https://grafana.github.io/helm-charts
                helm repo update
                helm upgrade --install grafana grafana/grafana \
                    --namespace monitoring \
                    --values monitoring/grafana/values.yaml \
                    --set serviceAccount.name=grafana-sa \
                    --set adminPassword='admin'
                '''
            }
        }

        stage('Apply ServiceMonitors') {
            steps {
                sh 'kubectl apply -f monitoring/servicemonitors/'
            }
        }

        stage('Verify Monitoring Stack') {
            steps {
                sh 'kubectl rollout status deployment/prometheus-server -n monitoring'
                sh 'kubectl rollout status deployment/grafana -n monitoring'
            }
        }

        stage('Build and Push Microservices') {
            steps {
                script {
                    def services = ['auth-service', 'user-service', 'payment-service', 'order-service', 'frontend-service']
                    services.each { svc ->
                        dir("services/${svc}") {
                            sh "./run_tests.sh || true"
                            sh "docker build -t mydockerhub/${svc}:${env.BUILD_NUMBER} ."
                            sh "echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"
                            sh "docker push mydockerhub/${svc}:${env.BUILD_NUMBER}"
                        }
                    }
                }
            }
        }

        stage('Deploy Microservices via Helm') {
            steps {
                script {
                    def services = ['auth-service', 'user-service', 'payment-service', 'order-service', 'frontend-service']
                    services.each { svc ->
                        dir("helm-charts/${svc}") {
                            sh "helm upgrade --install ${svc} . --namespace devopsify --set image.tag=${env.BUILD_NUMBER}"
                        }
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                sh 'python3 scripts/health_check.py'
            }
        }
    }

    post {
        success {
            echo " Full DevOps stack deployed successfully!"
        }
        failure {
            echo " Deployment failed. Please check logs."
        }
    }
}
