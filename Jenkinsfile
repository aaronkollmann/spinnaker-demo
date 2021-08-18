pipeline {
    agent { 'dockerfile' }
    stages {
        stage('build') {
            steps {
                sh 'docker build .'
            }
        }
    }
}
