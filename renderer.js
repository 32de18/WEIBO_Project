// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.

const exec = require('child_process').exec
const { dialog } = require('electron').remote
const ipc = require('electron').ipcRenderer
var iconv = require('iconv-lite')
iconv.skipDecodeWarning = true  // 关掉警告

var showMessage = document.getElementById('showMessage')
console.log = (message) => {
    while (message.slice(-1) == '\n' || message.slice(-1) == '\r')
        message = message.slice(0, -1)
    showMessage.value = showMessage.value + message + '\n'
}

function CheckChinesePrint() {
    var cmdStr = 'python D:/Users/huoji/Desktop/test.py'
    var workerProcess
    workerProcess = exec(cmdStr, { encoding: 'binary' })

    workerProcess.stdout.on('data', function (data) {
        console.log(iconv.decode(data, 'cp936'))
    })
    workerProcess.stderr.on('data', function (data) {
        console.log(iconv.decode(data, 'cp936'))
    })

    workerProcess.on('close', function (code) {
        workerProcess.kill()
    })
}

/**
 * 加载原始数据 时间经过格式化以及按时间从小到大排序
 */
var originalDatapath = ''  // 原始数据路径
function LoadOriginalData() {
    originalDatapath = ''

    dialog.showOpenDialog({
        properties: ['openFile'],
        filters: [
            { name: 'Files', extensions: ['csv', 'txt'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    }).then(result => {
        if (!result.canceled && result.filePaths != null && result.filePaths != '') {
            originalDatapath = result.filePaths[0]

            var readline = require('readline')
            var fs = require('fs')

            var objReadline = readline.createInterface({
                input: fs.createReadStream(originalDatapath)
            })

            var stT = '20991231', edT = '19990101'
            objReadline.on('line', (line) => {
                res = line.split(',')
                curTime = res[0]
                if (curTime > edT)
                    edT = curTime
                if (curTime < stT)
                    stT = curTime
            })

            objReadline.on('close', () => {
                document.getElementById('InputStartTime').value = stT.slice(0, 4) + '-' + stT.slice(4, 6) + '-' + stT.slice(-2)
                document.getElementById('InputEndTime').value = edT.slice(0, 4) + '-' + edT.slice(4, 6) + '-' + edT.slice(-2)
                dialog.showMessageBox({ type: 'info', title: '消息', message: '数据加载成功！' })
            })
        }
    }).catch(err => {
        dialog.showErrorBox('', err)
    })
}

/**
 * 选择时间
 */
var selStTime = '', selEdTime = ''
function SelectTime() {
    var startTime = document.getElementById('InputStartTime').value.split('-').join('')
    var endTime = document.getElementById('InputEndTime').value.split('-').join('')
    if (startTime > endTime) {
        dialog.showErrorBox('', '起始时间大于结束时间!')
        document.getElementById('InputStartTime').value = '2017-01-01'
        document.getElementById('InputEndTime').value = '2017-04-20'
        return
    }
    selStTime = startTime
    selEdTime = endTime

    dialog.showMessageBox({ type: 'info', title: '消息', message: '开始时间：' + selStTime + '\n结束时间：' + selEdTime })
}

/**
 * 一键处理
 */
var hotspots_filepath = 'D:/WorkData/WEIBO_Project/py3.6+/data/hotspots_file_test.csv'
var correlation_filepath = 'D:/WorkData/WEIBO_Project/py3.6+/data/correlation_file_test.csv'
function OnceProcess() {
    // 判断程序是否正在运行

    // 文件路径检查
    if (!CheckFilepath(originalDatapath)) {
        dialog.showErrorBox('', '文件路径错误!')
        return
    }

    // 检查是否选择了时间
    if (selStTime == '' || selEdTime == '') {
        dialog.showErrorBox('', '请选择并确定时间窗口!')
        return
    }

    var cmdStr = 'python -i ./py3.6+/main.py'
    var workerProcess
    workerProcess = exec(cmdStr, { encoding: 'binary' })

    workerProcess.stdin.write(originalDatapath + '\n')
    workerProcess.stdin.write(selStTime + '\n')
    workerProcess.stdin.write(selEdTime + '\n')
    workerProcess.stdin.write(hotspots_filepath + '\n')
    workerProcess.stdin.write(correlation_filepath + '\n')


    workerProcess.stdout.on('data', function (data) {
        data = iconv.decode(data, 'cp936')
        console.log(data)
        if (data == 'CODE_0') {
            dialog.showMessageBox({ type: 'info', title: '消息', message: '数据处理完成！' })
        }
    })
    workerProcess.stderr.on('data', function (data) {
        console.log(iconv.decode(data, 'cp936'))
    })
    workerProcess.on('close', function (code) {
        workerProcess.kill()
    })
}

/**
 * 文件路径检查
 * 判断此路径是否存在文件
 */
async function CheckFilepath(filepath) {
    if (filepath == null || filepath == '')
        return false

    var fs = require('fs')

    // 检查当前目录中是否存在该文件，以及该文件是否可读。
    await fs.access(filepath, fs.constants.F_OK | fs.constants.R_OK, (err) => {
        if (err) {
            console.error(
                `${filepath} ${err.code === 'ENOENT' ? '不存在' : '存在但不可读'}`)
            return false
        } else {
            console.log(`${filepath} 存在，且它是可读的`)
            return true
        }
    })
}

/**
 * 加载处理结果数据
 */
function ReadResultData(code) {
    dialog.showOpenDialog({
        properties: ['openFile'],
        filters: [
            { name: 'Files', extensions: ['csv', 'txt', 'ffss'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    }).then(result => {
        if (!result.canceled && result.filePaths != null && result.filePaths != '') {
            if (code == 1)
                ipc.send('read_result_data', result.filePaths[0])  // 将数据加载到全局变量里
            if (code == 2)
                ipc.send('read_result_data_2', result.filePaths[0])  // 将数据加载到全局变量里
        }
    }).catch(err => {
        dialog.showErrorBox('', err)
    })
}

ipc.on('load_data_completed', () => {
    dialog.showMessageBox({ type: 'info', title: '消息', message: '数据加载成功！' })
})