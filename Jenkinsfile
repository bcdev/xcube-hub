pipeline {
  agent any
  stages {
    stage('install') {
      steps {
        sh '''wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda;
export PATH="$HOME/miniconda/bin:$PATH";
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
