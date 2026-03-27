pipeline {
  agent any

  environment {
    DOCKER_IMAGE = "novikva/demo-nginx"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build') {
      steps { sh 'docker build -t $DOCKER_IMAGE:latest .' }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh '''
          echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
          docker push $DOCKER_IMAGE:latest
          '''
        }
      }
    }

    stage('Deploy') {
      steps {
        sh '''
        kubectl apply -f k8s/deployment.yaml
        kubectl apply -f k8s/service.yaml
        kubectl rollout restart deployment demo-nginx -n demo
        '''
      }
    }
  }
}
