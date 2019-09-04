// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.
let cmdStr = 'python ./py3.6+/back-main.py'

const exec = require('child_process').exec

let workerProcess

function runExec() {
    console.log(cmdStr)
    var message = document.getElementById('message').value + '\n'
    workerProcess = exec(cmdStr)

    workerProcess.stdin.write(message)

    workerProcess.stdout.on('data', function (data) {
        console.log(data)
    })
    workerProcess.stderr.on('data', function (data) {
        console.log(data);
    })
    workerProcess.on('close', function (code) {
        console.log(code);
    })
}



