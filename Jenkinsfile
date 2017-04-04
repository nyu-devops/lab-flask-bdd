#!groovy

node('node') {
    currentBuild.result = "SUCCESS"
    try {
       stage 'Checkout'
           gotClone=true
           timeout(time: 60, unit: 'SECONDS') {
                   deleteDir()
                   checkout scm                      // checks out the git repo that contains this Jenkinsfile
           }
       stage 'Test'
            print "Executing build script for" $JOB_NAME
            sh '''
            if [ ! -d "venv" ]; then
                virtualenv venv
            fi
            . venv/bin/activate
            pip install -q -r requirements.txt
            if [ ! -d "reports" ]; then
                mkdir reports
            fi
            nosetests --with-xunit --xunit-file=./reports/unittests.xml
            '''
            step([$class: 'XUnitBuilder',
                thresholds: [[$class: 'FailedThreshold', unstableThreshold: '1']],
                tools: [[$class: 'JUnitType', pattern: 'reports/unittests.xml']]])
    }
    catch (err) {
        currentBuild.result = "FAILURE"
        throw err
    }

}
