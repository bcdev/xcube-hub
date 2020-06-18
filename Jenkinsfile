pipeline {
  agent any
  stages {
    stage('install') {
      steps {
        sh '''conda info;
conda install -n base -c conda-forge mamba;
mamba env create;
source activate xcube_geodb;
pip install .'''
      }
    }

    stage('test') {
      steps {
        sh '''source activate xcube_geodb && pytest'''
      }
    }

  }
  environment {
    TT = '0'
  }
}
