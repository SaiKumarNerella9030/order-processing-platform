pipeline {
  agent any

  environment {
    KUBECONFIG_PATH = "${WORKSPACE}/kubeconfig"
  }

  stages {
    stage('Checkout Code') {
      steps {
        git credentialsId: 'Gitcreds', url: 'https://github.com/SaiKumarNerella9030/order-processing-platform.git', branch: 'main'
      }
    }

    stage('Init Kube Config') {
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-creds', variable: 'KUBECONFIG_FILE')]) {
          sh """
            cp $KUBECONFIG_FILE ${KUBECONFIG_PATH}
            export KUBECONFIG=${KUBECONFIG_PATH}
            kubectl version --short
          """
        }
      }
    }

    stage('Create Namespaces') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          kubectl apply -f manifests/namespaces/
        '''
      }
    }

    stage('Apply Prometheus RBAC') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          kubectl apply -f monitoring/prometheus/rbac/
        '''
      }
    }

    stage('Install Prometheus via Helm') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          helm upgrade --install prometheus monitoring/prometheus/chart/ -n monitoring
        '''
      }
    }

    stage('Apply Grafana RBAC') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          kubectl apply -f monitoring/grafana/rbac/
        '''
      }
    }

    stage('Install Grafana via Helm') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          helm upgrade --install grafana monitoring/grafana/chart/ -n monitoring
        '''
      }
    }

    stage('Apply ServiceMonitors') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          kubectl apply -f monitoring/servicemonitors/
        '''
      }
    }

    stage('Build and Push Microservices') {
      steps {
        sh '''
          chmod +x build_and_push.sh
          ./build_and_push.sh
        '''
      }
    }

    stage('Deploy Microservices via Helm') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          chmod +x deploy_microservices.sh
          ./deploy_microservices.sh
        '''
      }
    }

    stage('Health Check') {
      steps {
        sh '''
          export KUBECONFIG=${KUBECONFIG_PATH}
          chmod +x health_check.sh
          ./health_check.sh
        '''
      }
    }
  }

  post {
    failure {
      echo '❌ Deployment failed. Please check logs.'
    }
    success {
      echo '✅ Deployment succeeded.'
    }
  }
}
