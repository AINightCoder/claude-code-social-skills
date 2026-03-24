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

1. 关闭所有 Chrome：
   ```bash
   taskkill //F //IM chrome.exe
   ```
2. 等待进程退出（3-5 秒）：
   ```bash
   sleep 3 && tasklist | grep -i chrome || echo "no chrome running"
   ```
3. 用独立 user-data-dir 启动：
   ```bash
   "/c/Program Files/Google/Chrome/Application/chrome.exe" \
     --remote-debugging-port=9222 \
     --user-data-dir="C:/Users/Administrator/chrome-debug" &
   ```
4. 验证端口就绪：
   ```bash
   sleep 5 && curl -s http://127.0.0.1:9222/json/version | head -c 100
   ```

## 注意事项

- 独立 user-data-dir（`C:/Users/Administrator/chrome-debug`）是干净 profile，没有任何网站的登录态。如果目标网站需要登录，需要用户在弹出的 Chrome 中先手动登录。
- 如果仍然失败，检查是否有杀不掉的残留进程（`Access is denied`），提示用户手动关闭后重试。
