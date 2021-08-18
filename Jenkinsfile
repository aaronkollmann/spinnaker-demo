pipeline {
    agent { 'docker' }
    stages {
        stage('build') {
            steps {
                sh 'docker build .'
            }
        }
    }
}
