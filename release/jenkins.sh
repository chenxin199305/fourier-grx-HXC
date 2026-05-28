pipeline {
    agent {
        label "Grx2204"
    }
    stages {
        stage('CodePrepare') {
            steps {
                dir('fourier-grx') {
                    git branch: '$COMPILE_BRANCH', credentialsId: 'gitlabCert', url: 'git@gitlab.fftaicorp.com:mini/fourier-grx.git'
                }
                dir('fourier-grx/fourier-core') {
                    git branch: '$COMPILE_BRANCH', credentialsId: 'gitlabCert', url: 'git@gitlab.fftaicorp.com:mini/fourier-core.git'
                }
            }
        }
        stage('ClearSpace') {
            steps {
                sh '''
                echo $(whoami)
                '''
            }
        }
        stage('BuildAll') {
            steps {
                sh '''
                echo "####################"

                echo "Prepare Conda Environment"

                __conda_setup="$('/home/fftai-2204/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
                if [ $? -eq 0 ]; then
                    eval "$__conda_setup"
                else
                    if [ -f "/home/fftai-2204/miniconda3/etc/profile.d/conda.sh" ]; then
                        . "/home/fftai-2204/miniconda3/etc/profile.d/conda.sh"
                    else
                        export PATH="/home/fftai-2204/miniconda3/bin:$PATH"
                    fi
                fi
                unset __conda_setup

                echo "####################"

                conda env list

                echo "####################"

                conda activate fourier-grx-gitlab

                echo "####################"

                echo $PWD
                cd fourier-grx

                cd fourier-core
                pip install -e .

                cd ..
                pip install -e .

                echo "####################"

                echo "Start Build"

                make blaze

                echo "Build Finished"

                echo "####################"

                echo "Start Package"

                mkdir -p dist/jenkins
                rm -rf dist/jenkins/*

                GET_VERSION = $(shell \
                (pip show fourier-grx 2>/dev/null | grep Version | awk '{print $$2}') || \
                echo "0.0.1" \
                )

                echo "Version: $GET_VERSION"

                cp dist/fourier-grx.deb dist/jenkins/fourier-grx-$GET_VERSION-$BUILD_NUMBER-$BUILD_TIMESTAMP.deb

                echo "Package Finished"

                echo "####################"
                '''
            }
        }
        stage('Package') {
            steps {
                archiveArtifacts artifacts: 'fourier-grx/dist/jenkins/fourier-grx-*.deb', followSymlinks: false
            }
        }
    }
}