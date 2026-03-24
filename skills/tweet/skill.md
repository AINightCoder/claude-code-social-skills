---
name: tweet
version: 1.0.0
description: |
  通过 Chrome DevTools MCP 发布 Twitter 推文。
  自动检测内容长度，超过 280 weighted chars 时自动拆分为 thread。
  用户输入 /tweet 后跟内容即可发布。
allowed-tools:
  - Bash
  - Read
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__type_text
  - mcp__chrome-devtools__press_key
tags:
  - twitter
  - social-media
dependencies:
  - python>=3.10
---

# Tweet Skill

通过 Chrome DevTools 浏览器自动化发布 Twitter 推文。

## 触发

```
/tweet <content>
```

content 可以是：
- 单条推文内容
- 长文本（自动拆分为 thread）
- 用 `---` 手动分隔的多条推文

## 流程

### Step 0: 确保 Chrome 调试模式可用

参见 `.claude/skills/_shared/chrome-setup.md`

### Step 1: 解析与拆分

**如果内容包含 `---` 分隔符**，按分隔符拆分，每段作为一条推文。

**否则**，调用拆分脚本：

```bash
python ~/.claude/skills/tweet/scripts/tweet_split.py --file /tmp/tweet_input.txt
```

先将用户输入的内容写入临时文件 `/tmp/tweet_input.txt`，然后调用脚本。

脚本返回 JSON：
```json
{
  "count": 3,
  "tweets": [
    { "index": 0, "content": "第一条", "weight": 120 },
    { "index": 1, "content": "第二条", "weight": 200 },
    { "index": 2, "content": "第三条", "weight": 150 }
  ]
}
```

**校验**：如果任何一条的 weight > 280，报错并提示用户修改。

### Step 2: 发布第一条推文

```
1. navigate_page(url: "https://x.com/compose/post")
2. take_snapshot → 找到输入框（textbox "Post text"）的 uid
3. click(uid) → 聚焦输入框
4. type_text(text: 第一条内容)
5. take_snapshot → 找到 Post/Reply 按钮的 uid
6. click(uid) → 发布
```

### Step 3: 获取推文 URL

发布后需要获取新推文的 URL：

```
1. 等待页面更新（take_snapshot）
2. 检查是否有弹窗（见 Step 5）
3. 在 snapshot 中查找刚发布的推文
   - 查找包含推文内容的 article 元素
   - 在该 article 内找到时间链接（格式: https://x.com/{username}/status/{id}）
4. 记录该 URL
```

**备选方案**：如果从页面 DOM 提取失败，使用以下方式：
```
- 观察浏览器当前 URL 是否已跳转到新推文页面
- 如果仍失败，take_screenshot 截图查看页面状态辅助判断
```

### Step 4: 发布后续推文（Thread）

如果有多条推文，对每条后续推文重复：

```
1. navigate_page(url: 上一条推文的 URL)
2. take_snapshot → 找到回复输入框（textbox "Post text", description 含 "Post your reply"）的 uid
3. click(uid) → 聚焦回复框
4. type_text(text: 当前推文内容)
5. take_snapshot → 找到 Reply 按钮（非 disabled 的 button "Reply"）的 uid
6. click(uid) → 发布回复
7. take_snapshot → 提取新回复的 URL（从新出现的 article 中找 status 链接）
8. 记录 URL 到 published 列表
```

### Step 5: 弹窗处理

每次点击 Post/Reply 后，take_snapshot 检查是否出现弹窗：

**Premium 推广弹窗**：
- 特征：snapshot 中出现 `"Want more people to see your reply?"` 或 `"Upgrade to Premium"` 文本
- 处理：找到 `button "Maybe later"` 或 `button "Close"` 的 uid，click 关闭

**其他弹窗**：
- 如果出现未知弹窗，take_screenshot 截图，尝试找到关闭按钮

### Step 6: 错误恢复

维护发布状态：

```
published: [{ index: 0, url: "..." }, { index: 1, url: "..." }]
failed: [{ index: 2, error: "..." }]
pending: [{ index: 3, content: "..." }]
```

**失败重试逻辑**：
1. 如果某条发布失败，记录错误
2. 从失败的那条开始重试，最多重试 3 次
3. 重试时使用上一条成功发布的 URL 作为回复目标
4. 如果 3 次都失败，输出已成功的 URL 列表和失败信息，让用户决定

### Step 7: 输出结果

发布完成后，输出：

```
发布完成！共 N 条推文。

1. https://x.com/AINightCoder/status/xxx （首条）
2. https://x.com/AINightCoder/status/xxx
3. https://x.com/AINightCoder/status/xxx
...
```

## 关键注意事项

### 元素定位

- 输入框：查找 `textbox "Post text"` 类型的元素
- 发布按钮：在 compose 页面是 `button "Post"`，在回复场景是 `button "Reply"`
- 按钮必须不含 `disabled` 属性才能点击
- 如果 snapshot 中有多个同名元素，优先选择带 `focusable` 或 `focused` 属性的

### 发布节奏

- 每条推文发布后，等待 snapshot 确认成功再继续下一条
- 不要在未确认上一条成功前发布下一条

### 字符编码

- type_text 直接输入中文内容，Chrome DevTools 会正确处理
- 不需要额外编码转换
