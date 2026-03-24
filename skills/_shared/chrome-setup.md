# 确保 Chrome 调试模式可用

在使用任何 Chrome DevTools 工具之前，必须先确认 Chrome 调试端口就绪。

## 检测

```bash
curl -s http://127.0.0.1:9222/json/version
```

- **有 JSON 返回**：调试端口正常，继续下一步
- **连接拒绝或无输出**：需要启动 Chrome 调试模式，进入恢复流程

## 恢复流程

Chrome 的 `--remote-debugging-port` 只对第一个启动的 Chrome 实例生效。如果已有 Chrome 在运行，新启动的命令只会在已有实例中打开新窗口，调试端口参数被静默忽略。

### 1. 关闭所有 Chrome

按当前操作系统选择对应命令：

**Windows（PowerShell / CMD）**
```powershell
taskkill /F /IM chrome.exe
```

**macOS**
```bash
pkill -f "Google Chrome"
```

**Linux**
```bash
pkill chrome
```

### 2. 等待进程退出（3-5 秒）

```bash
sleep 3
```

必要时再手动检查是否还有残留 Chrome 进程。

### 3. 用独立 user-data-dir 启动

必须使用单独的浏览器 profile，避免污染日常浏览器环境，也保证调试端口稳定。

**Windows（PowerShell）**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\chrome-debug"
```

**Windows（Git Bash / bash）**
```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="$USERPROFILE/chrome-debug" &
```

**macOS**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug" &
```

**Linux**
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug" &
```

如果系统里安装的是 `chromium`，把 `google-chrome` 替换为实际可执行文件名即可。

### 4. 验证端口就绪

```bash
sleep 5 && curl -s http://127.0.0.1:9222/json/version
```

返回 JSON 即表示调试端口可用。

## 注意事项

- 独立 `user-data-dir` 是干净 profile，没有任何网站的登录态。如果目标网站需要登录，需要用户在弹出的 Chrome 中先手动登录。
- 只要后续继续使用同一个 `user-data-dir`（例如 Windows 的 `$env:USERPROFILE\chrome-debug`，macOS / Linux 的 `$HOME/chrome-debug`），登录态通常会保留。
- 如果仍然失败，先确认没有残留 Chrome 进程，再重试启动命令。
