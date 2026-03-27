pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  environment {
    APP_NAME     = 'demo-nginx'
    BACKEND_APP_NAME = 'backend'
    NAMESPACE    = 'demo'
    DOCKERHUB_REPO = 'novikva/demo-nginx'
    DOCKERHUB_BACKEND_REPO = 'novikva/demo-backend'
    KUBECONFIG   = '/var/lib/jenkins/.kube/config'
    IMAGE_TAG = "${BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
    FULL_IMAGE   = "${DOCKERHUB_REPO}:${IMAGE_TAG}"
    FULL_BACKEND_IMAGE = "${DOCKERHUB_BACKEND_REPO}:${IMAGE_TAG}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Inspect') {
      steps {
        sh '''
          set -eux
          pwd
          ls -la
        '''
      }
    }

    stage('Build image') {
      steps {
        sh '''
          set -eux
          docker build -t ${FULL_IMAGE} .
          docker tag ${FULL_IMAGE} ${DOCKERHUB_REPO}:latest
          docker build -t ${FULL_BACKEND_IMAGE} ./backend
          docker tag ${FULL_BACKEND_IMAGE} ${DOCKERHUB_BACKEND_REPO}:latest
        '''
      }
    }

    stage('Push image') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh '''
            set -eux
            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
            docker push ${FULL_IMAGE}
            docker push ${DOCKERHUB_REPO}:latest
            docker push ${FULL_BACKEND_IMAGE}
            docker push ${DOCKERHUB_BACKEND_REPO}:latest
          '''
        }
      }
    }

    stage('Ensure namespace/resources') {
      steps {
        sh '''
          set -eux
          export KUBECONFIG=${KUBECONFIG}
          kubectl apply -f k8s/service.yaml
          kubectl apply -f k8s/postgres.yaml
          kubectl apply -f k8s/redis.yaml
          kubectl apply -f k8s/backend.yaml

          if ! kubectl get deployment ${APP_NAME} -n ${NAMESPACE} >/dev/null 2>&1; then
            kubectl apply -f k8s/deployment.yaml
          fi
        '''
      }
    }

    stage('Deploy image') {
      steps {
        sh '''
          set -eux
          export KUBECONFIG=${KUBECONFIG}

          kubectl set image deployment/${APP_NAME} \
            nginx=${FULL_IMAGE} \
            -n ${NAMESPACE}

          kubectl set image deployment/${BACKEND_APP_NAME} \
            backend=${FULL_BACKEND_IMAGE} \
            -n ${NAMESPACE}

          kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=180s
          kubectl rollout status deployment/${BACKEND_APP_NAME} -n ${NAMESPACE} --timeout=180s
        '''
      }
    }

    stage('Health check') {
      steps {
        sh '''
          set -eux
          curl -f http://127.0.0.1/
        '''
      }
    }
  }

  post {
    success {
      echo "Deploy OK: ${FULL_IMAGE}"
    }

    failure {
      script {
        sh '''
          set +e
          export KUBECONFIG=${KUBECONFIG}
          kubectl rollout undo deployment/${APP_NAME} -n ${NAMESPACE}
          kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=180s || true
        '''
      }
      echo 'Deploy FAILED, rollback attempted'
    }

    always {
      sh '''
        set +e
        docker image prune -f
      '''
    }
  }
}
