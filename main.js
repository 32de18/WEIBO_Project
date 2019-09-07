// Modules to control application life and create native browser window
const { app, BrowserWindow, Menu } = require('electron')
const path = require('path')

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    // width: screenWidth,
    // height: screenHight,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      // 取消跨域限制
      webSecurity: false,
      nodeIntegration: true,
    },
    show: false,
    icon: './weizhi.ico'
  })

  // 自动最大化
  mainWindow.maximize()
  mainWindow.show()

  // and load the index.html of the app.
  mainWindow.loadFile('index.html')

  // Open the DevTools.
  // mainWindow.webContents.openDevTools()

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })

  createMenu()
}

// 取消菜单栏
function createMenu() {
  // darwin 表示 macOS 针对 macOS 设置
  if (process.platform === 'darwin') {
    const template = [{
      label: '微知系统',
      submenu: [
        {
          role: 'about'
        },
        {
          role: 'quit'
        }
      ]
    }]
    let menu = Menu.buildFromTemplate(template)
    Menu.setApplicationMenu(menu)
  } else {
    // win 及 linux 系统
    Menu.setApplicationMenu(null)
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) createWindow()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
const ipc = require('electron').ipcMain

let sub_3dlabel_win;
ipc.on('sub_3dlabel', () => {
  sub_3dlabel_win = new BrowserWindow({
    width: 800,
    height: 700,
    frame: true,
    parent: mainWindow, //win是主窗口
    icon: './weizhi.ico'

  })
  sub_3dlabel_win.loadURL(path.join('file:', __dirname, 'sub_3dlabel.html')) //new.html是新开窗口的渲染进程
  sub_3dlabel_win.on('closed', () => { sub_3dlabel_win = null })
})