pipeline {
    agent {
    // Equivalent to "docker build -f Dockerfile.build --build-arg version=1.0.2 ./build/
        dockerfile {
            filename 'Dockerfile'
            dir '.'
            label 'aaronkollmann/teamspeak3-bot'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'echo test'
            }
        }
    }
}
