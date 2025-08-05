pipeline {
  agent any

  environment {
    KUBECONFIG_PATH = "${env.WORKSPACE}/.kube/config"
  }

  stages {

    stage('Checkout Code') {
      steps {
        checkout([$class: 'GitSCM',
                  branches: [[name: '*/main']],
                  userRemoteConfigs: [[url: 'https://github.com/SaiKumarNerella9030/order-processing-platform.git', credentialsId: 'Gitcreds']]
        ])
      }
    }

    stage('Init Kube Config') {
      steps {
        withCredentials([string(credentialsId: 'KUBE_CONFIG_B64', variable: 'KUBE_CONFIG_B64')]) {
          sh '''
            mkdir -p ~/.kube
            echo "$KUBE_CONFIG_B64" | base64 -d > ~/.kube/config
            chmod 600 ~/.kube/config
            echo ✅ Kubeconfig decoded and stored.
            echo 📦 K8s Client Version:
            kubectl version --client
          '''
        }
      }
    }

    stage('Create Namespaces') {
      steps {
        sh '''
          kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
          echo ✅ Namespace 'monitoring' created/applied.
        '''
      }
    }

    stage('Apply Prometheus RBAC') {
      steps {
        sh '''
          kubectl apply -f monitoring/prometheus/rbac/serviceaccount.yaml -n monitoring
          kubectl apply -f monitoring/prometheus/rbac/role.yaml -n monitoring
          kubectl apply -f monitoring/prometheus/rbac/rolebinding.yaml -n monitoring
          echo ✅ Prometheus RBAC applied.
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
            --set serviceAccounts.server.name=prometheus-sa \
            --set serviceAccounts.server.create=false
          echo ✅ Prometheus installed.
        '''
      }
    }

    stage('Apply Grafana RBAC') {
      steps {
        sh '''
          kubectl apply -f monitoring/grafana/rbac/serviceaccount.yaml -n monitoring
          kubectl apply -f monitoring/grafana/rbac/role.yaml -n monitoring
          kubectl apply -f monitoring/grafana/rbac/rolebinding.yaml -n monitoring
          echo ✅ Grafana RBAC applied.
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
            --set serviceAccount.name=grafana-sa \
            --set serviceAccount.create=false \
            --set adminPassword='admin'
          echo ✅ Grafana installed.
        '''
      }
    }

    stage('Apply ServiceMonitors') {
      steps {
        sh '''
          echo ⏳ Applying ServiceMonitors...
          kubectl apply -f monitoring/servicemonitors/ -n monitoring
          echo ✅ ServiceMonitors applied.
        '''
      }
    }

    stage('Verify Monitoring Stack') {
      steps {
        sh '''
          echo 🧪 Verifying Prometheus pods:
          kubectl get pods -n monitoring -l app=prometheus
          echo 🧪 Verifying Grafana pods:
          kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
        '''
      }
    }

    stage('Build and Push Microservices') {
      steps {
        echo "⛏️ Build and push microservices (not implemented here)"
        // You can add Docker build + push logic here
      }
    }

    stage('Deploy Microservices via Helm') {
      steps {
        echo "🚀 Deploying microservices via Helm (not implemented here)"
        // Add deployment logic if needed
      }
    }

    stage('Health Check') {
      steps {
        echo "🩺 Health check (optional)"
        // Add readiness probe or health curl calls here
      }
    }
  }

  post {
    failure {
      echo "❌ Deployment failed. Please check logs."
    }
  }
}
