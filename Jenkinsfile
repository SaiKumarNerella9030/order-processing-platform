pipeline {
    agent any

    environment {
        KUBECONFIG_PATH = '/var/lib/jenkins/.kube/config'
    }

    options {
        skipDefaultCheckout()
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Init Kube Config') {
            steps {
                withCredentials([string(credentialsId: 'kubeconfig-b64', variable: 'KUBE_CONFIG_B64')]) {
                    sh '''
                        mkdir -p $(dirname $KUBECONFIG_PATH)
                        echo "$KUBE_CONFIG_B64" | base64 -d > $KUBECONFIG_PATH
                        chmod 600 $KUBECONFIG_PATH
                        echo "✅ Kubeconfig decoded and stored."
                        kubectl version --short
                    '''
                }
            }
        }

        stage('Create Namespaces') {
            steps {
                sh '''
                    kubectl create namespace devopsify --dry-run=client -o yaml | kubectl apply -f -
                    echo "✅ Namespace created/applied."
                '''
            }
        }

        stage('Apply Prometheus RBAC') {
            steps {
                sh 'kubectl apply -f monitoring/prometheus/rbac.yaml -n devopsify'
            }
        }

        stage('Install Prometheus via Helm') {
            steps {
                sh '''
                    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
                    helm repo update
                    helm upgrade --install prometheus prometheus-community/prometheus \
                        --namespace devopsify \
                        -f monitoring/prometheus/values.yaml
                '''
            }
        }

        stage('Apply Grafana RBAC') {
            steps {
                sh 'kubectl apply -f monitoring/grafana/rbac.yaml -n devopsify'
            }
        }

        stage('Install Grafana via Helm') {
            steps {
                sh '''
                    helm repo add grafana https://grafana.github.io/helm-charts
                    helm repo update
                    helm upgrade --install grafana grafana/grafana \
                        --namespace devopsify \
                        -f monitoring/grafana/values.yaml
                '''
            }
        }

        stage('Apply ServiceMonitors') {
            steps {
                sh 'kubectl apply -f monitoring/servicemonitors/ -n devopsify'
            }
        }

        stage('Verify Monitoring Stack') {
            steps {
                sh 'kubectl get pods -n devopsify'
            }
        }

        stage('Build and Push Microservices') {
            steps {
                sh './scripts/build_and_push_all.sh'
            }
        }

        stage('Deploy Microservices via Helm') {
            steps {
                sh './scripts/deploy_all_services.sh'
            }
        }

        stage('Health Check') {
            steps {
                sh './scripts/health_check.sh'
            }
        }
    }

    post {
        failure {
            echo ' Deployment failed. Please check logs.'
        }
        success {
            echo ' Deployment succeeded.'
        }
    }
}
