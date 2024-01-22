pipeline {
  agent any
  stages {
    stage('version') {
      steps {
        sh """
        python3 --version
        python3 -m venv .venv
        . .venv/bin/activate
        pip3 install -r requirements.txt
        python3 bot/__main__.py
        """
      }
    }
  }
}