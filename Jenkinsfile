// One parameterized Jenkins job for this repository.
// Defaults: offline Unit + read-only ParaBank Smoke. Live-bank final submits are excluded.
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 60, unit: 'MINUTES')
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
    }

    parameters {
        booleanParam(name: 'RUN_ALL', defaultValue: false,
            description: 'Run all CI-allowed groups: Unit + ParaBank Smoke + demo UI/API transfers. ProCredit logins only if ALLOW_PROCREDIT_LOGIN is also selected. Never live-bank negative transfers.')
        booleanParam(name: 'RUN_UNIT', defaultValue: true, description: 'Offline Unit tests')
        booleanParam(name: 'RUN_PARABANK_SMOKE', defaultValue: true, description: 'Demo Selenium login and Accounts Overview')
        booleanParam(name: 'RUN_PARABANK_UI', defaultValue: false, description: 'Demo Selenium internal funds transfer (changes demo balances)')
        booleanParam(name: 'RUN_PARABANK_API', defaultValue: false, description: 'Demo GET -> POST -> GET transfer (changes demo balances)')
        booleanParam(name: 'RUN_PROCREDIT_DESKTOP_LOGIN', defaultValue: false, description: 'Real ProCredit desktop OTP login; manual attended Windows agent only')
        booleanParam(name: 'RUN_PROCREDIT_MOBILE_LOGIN', defaultValue: false, description: 'Real ProCredit mobile-responsive OTP login; manual attended Windows agent only')
        booleanParam(name: 'ALLOW_PROCREDIT_LOGIN', defaultValue: false, description: 'Explicit approval to run selected ProCredit login(s). RUN_ALL includes both only when this is enabled.')
        string(name: 'PARABANK_URL', defaultValue: 'http://localhost:8081/parabank',
            description: 'Local ParaBank URL ON THE JENKINS AGENT (not on a different machine).')
        // Demo account IDs and transfer amount load from Secret file: parabank-ci-config.
        string(name: 'TERMUX_USER', defaultValue: 'u0_a321', description: 'Termux SSH login on your phone (for ProCredit OTP only)')
        string(name: 'TERMUX_KEY_PATH', defaultValue: 'C:\\ProgramData\\Jenkins\\.jenkins\\ssh\\termux_jenkins_v3', description: 'SSH private key path readable by Jenkins agent')
        string(name: 'OTP_LENGTH', defaultValue: '4', description: 'Actual SMS code length (use 4 or 6 to match your bank)')
        string(name: 'OTP_SENDER', defaultValue: 'ProCredit', description: 'SMS sender filter')
    }

    environment {
        PYTHONUNBUFFERED = '1'
        BROWSER = 'chrome'
        HEADLESS = 'true'
        PARABANK_API_TRANSFER_RUN = 'NO'
        PARABANK_API_ALLOW_PUBLIC = 'NO'
        PRO_CREDIT_RUN = '0'
        PRO_CREDIT_NEGATIVE_SUBMIT = 'NO'
        PRO_CREDIT_MOBILE_NEGATIVE_SUBMIT = 'NO'
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }

        // ParaBank demo account IDs live only in Jenkins Credentials, never in Git.
        // Secret file (ID: parabank-ci-config) contains:
        // PARABANK_FROM_ACCOUNT=<numeric demo sender>
        // PARABANK_TO_ACCOUNT=<numeric demo receiver>
        // PARABANK_TRANSFER_AMOUNT=1.00
        stage('Load ParaBank CI Config') {
            when { expression { return params.RUN_ALL || params.RUN_PARABANK_UI || params.RUN_PARABANK_API } }
            steps {
                withCredentials([file(credentialsId: 'parabank-ci-config', variable: 'PARABANK_CONFIG_FILE')]) {
                    script {
                        def config = [:]
                        def content = readFile(file: env.PARABANK_CONFIG_FILE, encoding: 'UTF-8')
                        content.replace("\uFEFF", '').split(/\r?\n/).each { row ->
                            def line = row.trim()
                            if (line && !line.startsWith('#')) {
                                def pair = line.split('=', 2)
                                if (pair.length == 2) {
                                    config[pair[0].trim()] = pair[1].trim()
                                }
                            }
                        }

                        env.PARABANK_FROM_ACCOUNT = config['PARABANK_FROM_ACCOUNT'] ?: ''
                        env.PARABANK_TO_ACCOUNT = config['PARABANK_TO_ACCOUNT'] ?: ''
                        env.PARABANK_TRANSFER_AMOUNT = config['PARABANK_TRANSFER_AMOUNT'] ?: '1.00'

                        // Do not echo account IDs or Secret file contents.
                        echo 'ParaBank CI configuration loaded from Jenkins Credentials.'
                    }
                }
            }
        }

        stage('Validate selected tests') {
            steps {
                script {
                    def doUnit = params.RUN_ALL || params.RUN_UNIT
                    def doSmoke = params.RUN_ALL || params.RUN_PARABANK_SMOKE
                    def doUi = params.RUN_ALL || params.RUN_PARABANK_UI
                    def doApi = params.RUN_ALL || params.RUN_PARABANK_API
                    def doDesktop = params.RUN_PROCREDIT_DESKTOP_LOGIN || (params.RUN_ALL && params.ALLOW_PROCREDIT_LOGIN)
                    def doMobile = params.RUN_PROCREDIT_MOBILE_LOGIN || (params.RUN_ALL && params.ALLOW_PROCREDIT_LOGIN)
                    def doBank = doDesktop || doMobile

                    if (!(doUnit || doSmoke || doUi || doApi || doBank)) {
                        error('No tests selected. Enable at least one RUN_* option.')
                    }
                    def url = params.PARABANK_URL.trim()
                    if ((doSmoke || doUi || doApi) && !(url ==~ /https?:\/\/.+/)) {
                        error('PARABANK_URL must start with http:// or https://')
                    }
                    if (doUi || doApi) {
                        // Refuse unknown/public websites for operations that change money balances.
                        if (!(url ==~ /https?:\/\/(localhost|127\.0\.0\.1)(:[0-9]+)?\/parabank\/?/)) {
                            error('Demo transfer stages require a local ParaBank instance (localhost/127.0.0.1).')
                        }
                        def fromId = (env.PARABANK_FROM_ACCOUNT ?: '').trim()
                        def toId = (env.PARABANK_TO_ACCOUNT ?: '').trim()
                        def amount = (env.PARABANK_TRANSFER_AMOUNT ?: '').trim()
                        if (!(fromId ==~ /[0-9]+/) || !(toId ==~ /[0-9]+/) || fromId == toId) {
                            error('Secret file parabank-ci-config must contain two different numeric PARABANK_FROM_ACCOUNT / PARABANK_TO_ACCOUNT values.')
                        }
                        if (!(amount ==~ /[0-9]+(\.[0-9]{1,2})?/) || !(amount ==~ /.*[1-9].*/)) {
                            error('TRANSFER_AMOUNT must be positive with no more than 2 decimal places.')
                        }
                    }
                    if (doBank) {
                        if (!params.ALLOW_PROCREDIT_LOGIN) {
                            error('To run ProCredit login tests explicitly enable ALLOW_PROCREDIT_LOGIN.')
                        }
                        if (isUnix()) {
                            error('ProCredit SMS + visible Chrome tests require an attended Windows Jenkins agent.')
                        }
                        if (!params.TERMUX_USER.trim() || !params.TERMUX_KEY_PATH.trim()) {
                            error('ProCredit requires TERMUX_USER and TERMUX_KEY_PATH on the Windows agent.')
                        }
                        if (!(params.OTP_LENGTH.trim() ==~ /[4-8]/)) {
                            error('OTP_LENGTH must be a single digit from 4 to 8.')
                        }
                    }
                    echo "Selected: Unit=${doUnit}, Smoke=${doSmoke}, ParaBank UI=${doUi}, ParaBank API=${doApi}, ProCredit desktop=${doDesktop}, ProCredit mobile=${doMobile}"
                    echo 'ProCredit negative-transfer final-submit tests are never run by this Jenkinsfile.'
                }
            }
        }

        stage('Install requirements') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -eu
                            python3 -m venv .venv
                            .venv/bin/python -m pip install -r requirements-ci.txt
                            mkdir -p reports
                        '''
                    } else {
                        bat '''
                            @echo off
                            python -m venv .venv
                            if errorlevel 1 exit /b 1
                            .venv\\Scripts\\python.exe -m pip install -r requirements-ci.txt
                            if errorlevel 1 exit /b 1
                            if not exist reports mkdir reports
                        '''
                    }
                }
            }
        }

        stage('Unit tests') {
            when { expression { return params.RUN_ALL || params.RUN_UNIT } }
            steps {
                script {
                    if (isUnix()) {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { sh '.venv/bin/python -m pytest unit_tests -v --alluredir=allure-results --junitxml=reports/unit.xml' }
                    } else {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { bat '.venv\\Scripts\\python.exe -m pytest unit_tests -v --alluredir=allure-results --junitxml=reports/unit.xml' }
                    }
                }
            }
        }

        stage('ParaBank Smoke') {
            when { expression { return params.RUN_ALL || params.RUN_PARABANK_SMOKE } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'parabank-demo-user', usernameVariable: 'PARABANK_USERNAME', passwordVariable: 'PARABANK_PASSWORD')]) {
                    withEnv(["PARABANK_BASE_URL=${params.PARABANK_URL.trim()}"]) {
                        script {
                            if (isUnix()) {
                                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { sh '.venv/bin/python -m pytest tests/test_smoke_transfer_funds.py -v --alluredir=allure-results --junitxml=reports/smoke.xml' }
                            } else {
                                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { bat '.venv\\Scripts\\python.exe -m pytest tests/test_smoke_transfer_funds.py -v --alluredir=allure-results --junitxml=reports/smoke.xml' }
                            }
                        }
                    }
                }
            }
        }

        stage('ParaBank UI Transfer') {
            when { expression { return params.RUN_ALL || params.RUN_PARABANK_UI } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'parabank-demo-user', usernameVariable: 'PARABANK_USERNAME', passwordVariable: 'PARABANK_PASSWORD')]) {
                    withEnv([
                        "PARABANK_BASE_URL=${params.PARABANK_URL.trim()}"
                    ]) {
                        script {
                            if (isUnix()) {
                                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { sh '.venv/bin/python -m pytest tests/test_transfer_funds.py -v --alluredir=allure-results --junitxml=reports/ui-transfer.xml' }
                            } else {
                                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { bat '.venv\\Scripts\\python.exe -m pytest tests/test_transfer_funds.py -v --alluredir=allure-results --junitxml=reports/ui-transfer.xml' }
                            }
                        }
                    }
                }
            }
        }

        stage('ParaBank API Transfer') {
            when { expression { return params.RUN_ALL || params.RUN_PARABANK_API } }
            steps {
                withEnv([
                    "PARABANK_BASE_URL=${params.PARABANK_URL.trim()}",
                    'PARABANK_API_TRANSFER_RUN=YES'
                ]) {
                    script {
                        if (isUnix()) {
                            catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { sh '.venv/bin/python -m pytest api_tests/test_parabank_api_transfer.py -v --alluredir=allure-results --junitxml=reports/api-transfer.xml' }
                        } else {
                            catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { bat '.venv\\Scripts\\python.exe -m pytest api_tests/test_parabank_api_transfer.py -v --alluredir=allure-results --junitxml=reports/api-transfer.xml' }
                        }
                    }
                }
            }
        }

        stage('ProCredit Desktop Login [manual]') {
            when { expression { return params.RUN_PROCREDIT_DESKTOP_LOGIN || (params.RUN_ALL && params.ALLOW_PROCREDIT_LOGIN) } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'procredit-bank-user', usernameVariable: 'PRO_CREDIT_USERNAME', passwordVariable: 'PRO_CREDIT_PASSWORD')]) {
                    withEnv([
                        'PRO_CREDIT_RUN=1', 'HEADLESS=false',
                        "TERMUX_SSH_USER=${params.TERMUX_USER.trim()}",
                        "TERMUX_SSH_KEY=${params.TERMUX_KEY_PATH.trim()}",
                        "PROCREDIT_OTP_LENGTH=${params.OTP_LENGTH.trim()}",
                        "PROCREDIT_SMS_SENDER=${params.OTP_SENDER.trim()}"
                    ]) {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { bat '.venv\\Scripts\\python.exe -m pytest tests/test_procredit_login.py -v --alluredir=allure-results --junitxml=reports/procredit-desktop.xml' }
                    }
                }
            }
        }

        stage('ProCredit Mobile Login [manual]') {
            when { expression { return params.RUN_PROCREDIT_MOBILE_LOGIN || (params.RUN_ALL && params.ALLOW_PROCREDIT_LOGIN) } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'procredit-bank-user', usernameVariable: 'PRO_CREDIT_USERNAME', passwordVariable: 'PRO_CREDIT_PASSWORD')]) {
                    withEnv([
                        'PRO_CREDIT_RUN=1', 'HEADLESS=false',
                        "TERMUX_SSH_USER=${params.TERMUX_USER.trim()}",
                        "TERMUX_SSH_KEY=${params.TERMUX_KEY_PATH.trim()}",
                        "PROCREDIT_OTP_LENGTH=${params.OTP_LENGTH.trim()}",
                        "PROCREDIT_SMS_SENDER=${params.OTP_SENDER.trim()}"
                    ]) {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') { bat '.venv\\Scripts\\python.exe -m pytest tests/test_procreditbank_mobile_login.py -v --alluredir=allure-results --junitxml=reports/procredit-mobile.xml' }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('reports')) {
                    junit allowEmptyResults: true, testResults: 'reports/*.xml'
                }
                def bankInSelection = params.RUN_PROCREDIT_DESKTOP_LOGIN || params.RUN_PROCREDIT_MOBILE_LOGIN || (params.RUN_ALL && params.ALLOW_PROCREDIT_LOGIN)
                if (bankInSelection) {
                    // These sessions can show real personal/financial information in HTML, Allure and PNG.
                    // Do not expose private bank artifacts in a shared Jenkins job.
                    archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
                    echo 'Private ProCredit HTML, screenshot and Allure output are NOT published by Jenkins.'
                } else {
                    archiveArtifacts artifacts: 'reports/*.xml,reports/html/**/*.html,reports/screenshots/**/*.png,allure-results/**', allowEmptyArchive: true
                    if (fileExists('allure-results')) {
                        allure includeProperties: false, results: [[path: 'allure-results']]
                    }
                }
            }
        }
    }
}
