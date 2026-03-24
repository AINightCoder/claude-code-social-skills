---
name: douyin
version: 1.1.0
description: |
  通过 Chrome DevTools MCP 发布抖音图文或评论。
  Publish image posts or comments on Douyin (抖音/TikTok China) via browser automation.
  支持多张图片上传，可指定话题。
  用户输入 /douyin 后跟图片路径和描述文本即可发布，使用 --comment 可评论指定作品。
  触发关键词：douyin, 抖音, 发抖音, 抖音图文, post to douyin, TikTok
allowed-tools:
  - Bash
  - Read
  - Glob
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__type_text
  - mcp__chrome-devtools__press_key
  - mcp__chrome-devtools__upload_file
  - mcp__chrome-devtools__evaluate_script
tags:
  - douyin
  - social-media
---

# Douyin Skill

通过 Chrome DevTools 浏览器自动化发布抖音图文。

## 触发

```
/douyin <描述文本>
/douyin --images <图片路径1> [图片路径2...] <描述文本>
/douyin --dir <图片目录> <描述文本>
```

- 不指定 `--images` 时，自动将描述文本生成为文字卡片图片（1080x1440，3:4 比例）
- `--images`：指定一张或多张图片路径（空格分隔），跳过文字卡片生成
- `--dir`：指定图片目录，自动上传目录下所有 jpg/jpeg/png/webp 图片
- 描述文本中可用 `#话题` 格式内嵌话题

## 流程

### Step 0: 确保 Chrome 调试模式可用

参见 `.claude/skills/_shared/chrome-setup.md`

### Step 1: 解析输入

**参数解析**：
- 提取 `--images` 后的图片路径列表（如果有）
- 或 `--dir` 后的目录路径（用 Glob 查找 `*.{jpg,jpeg,png,webp}`）
- 剩余文本作为描述内容
- 标题：截取描述文本前 20 字

**图片校验**（仅当提供了 `--images` 或 `--dir` 时）：
- 格式：jpg、jpeg、png、webp（不支持 gif）
- 大小：单张不超过 50MB
- 数量：最多 35 张
- 比例：推荐 3:4 或 4:3

### Step 1.5: 生成文字卡片图片（未提供 --images 时）

如果用户未提供 `--images` 或 `--dir`，自动将描述文本生成为文字卡片图片。

复用 `scripts/xhs_text_card.py`（与小红书 Skill 共享），生成 1080x1440 (3:4) 深色风格卡片：

```bash
python ~/.claude/skills/_shared/scripts/xhs_text_card.py \
  --title "标题（前20字）" \
  --content "完整描述文本" \
  --output /tmp/douyin_card.png
```

生成后将 `/tmp/douyin_card.png` 作为上传图片。

### Step 2: 导航到图文上传页面

```
navigate_page(url: "https://creator.douyin.com/creator-micro/content/upload?default-tab=3", timeout: 30000)
```

加载完成后 take_snapshot，确认看到：
- "发布图文" tab 已激活
- 上传按钮（`button "上传图文"`）
- 文件选择器（`button "选择文件"`）

**登录检查**：如果页面跳转到登录页，提示用户先在 Chrome 调试窗口中登录抖音创作者中心。

### Step 3: 上传图片

**上传第一张图片**：
```
1. take_snapshot → 找到文件选择器（button "选择文件"）
2. upload_file(uid, filePath: 第一张图片路径)
3. 等待上传完成，页面自动跳转到编辑页
```

**上传更多图片**（如果有多张）：
```
对每张后续图片：
1. take_snapshot → 找到 button "继续添加"
2. click(uid) → 打开文件选择器
3. take_snapshot → 找到新的 button "选择文件"
4. upload_file(uid, filePath: 图片路径)
5. 等待上传完成
```

### Step 4: 填写标题

```
1. take_snapshot → 找到标题输入框（textbox "添加作品标题"）
2. click(uid) → 聚焦
3. type_text(text: 标题内容)
```

**标题规则**：
- 最多 20 个字
- 如果用户未单独指定标题，截取描述文本前 20 字作为标题

### Step 5: 填写描述

```
1. take_snapshot → 找到描述输入区域
   - 特征：generic 元素，内含 "添加作品描述..." placeholder
2. click(uid) → 聚焦
3. type_text(text: 描述内容)
```

**描述规则**：
- 最多 1000 字
- 话题用 `#话题名 ` 格式（# 后跟话题名，空格结束）
- @好友用 `@用户名 ` 格式

### Step 6: 发布

```
1. take_snapshot → 找到 button "发布"
2. click(uid) → 发布作品
```

### Step 7: 获取作品 URL

发布后页面可能跳转到作品管理页。获取作品 URL 的方式：

**方案 A**：发布后检查页面 URL 变化
```javascript
() => { return window.location.href; }
```

**方案 B**：如果无法从 URL 获取，提示用户在抖音 App 中查看

### Step 8: 输出结果

```
发布成功！已上传 N 张图片。

抖音图文已发布，请在抖音 App 中查看。
```

## 关键注意事项

### 元素定位

- **上传页文件选择器**：`button "选择文件"`（在上传页面）
- **标题框**：`textbox "添加作品标题"`
- **描述框**：`generic` 元素，placeholder "添加作品描述..."
- **继续添加**：`button "继续添加"`（上传图片后出现）
- **发布按钮**：`button "发布"`
- **话题入口**：`#添加话题` 文本

### 页面跳转

上传图片后页面 URL 会自动变化：
- 上传页：`/content/upload?default-tab=3`
- 编辑页：`/content/post/image?...`

### 弹窗处理

首次使用可能弹出"新增共创中心"提示，需要点击 `button "我知道了"` 关闭。

### 登录态

抖音创作者中心需要登录。支持扫码登录和手机验证码登录。如果是干净 profile 需要用户先手动登录。

### 错误处理

- 登录过期：页面跳转到登录页，提示用户在 Chrome 调试窗口中登录抖音创作者中心
- 上传失败：如果上传后页面未跳转到编辑页，take_screenshot 检查状态，重试 upload_file
- 弹窗干扰：首次使用可能弹出"新增共创中心"提示，点击 `button "我知道了"` 关闭
- 评论输入框未激活：如果点击占位文本后未出现 combobox，尝试 take_screenshot 后再次点击

### 与其他 Skill 的差异

| 维度 | Twitter | 即刻 | 知乎 | 抖音图文 |
|------|---------|------|------|---------|
| 内容类型 | 短文本 | 短文本 | 长文章 | 图文 |
| 图片 | 可选 | 可选 | 可选 | 必须 |
| 标题 | 无 | 无 | 有(100字) | 有(20字) |
| 描述 | 280 chars | 无限 | 无限 | 1000字 |
| URL 获取 | DOM | API | 编辑URL | 待定 |

---

## 评论功能

### 触发

```
/douyin --comment <作品URL> <评论内容>
```

作品 URL 格式：`https://www.douyin.com/note/<note_id>` 或 `https://www.douyin.com/video/<video_id>`

### 流程

#### Step 1: 导航到作品页

```
navigate_page(url: 作品URL)
```

如果不知道作品 URL，可从个人主页获取：
```
1. navigate_page(url: "https://www.douyin.com/user/self")
2. take_snapshot → 找到目标作品的 link 元素（含 /note/ 或 /video/ 的 URL）
3. 提取作品 URL，用 navigate_page 直接导航
```

**注意**：不要从个人主页点击作品（会打开错误的推荐视频弹窗），必须用 navigate_page 直接导航到作品 URL。

#### Step 2: 激活评论输入框

抖音评论输入框默认不可见，需要先激活：

```
1. take_snapshot → 找到 "留下你的精彩评论吧" 文本元素
2. click(uid) → 点击该文本激活输入框
3. take_snapshot → 确认出现 combobox 元素（description 含 "留下你的精彩评论吧"，focusable）
```

**关键**：点击 "留下你的精彩评论吧" 后，会出现一个 `combobox` 元素，这才是真正的输入框。

#### Step 3: 输入评论

```
1. click(combobox uid) → 确保聚焦
2. type_text(text: 评论内容)
```

#### Step 4: 发送评论

```
press_key(key: "Enter") → 发送评论
```

**注意**：抖音评论用 Enter 键发送（不是点击按钮）。

#### Step 5: 确认成功

```
take_screenshot → 确认评论出现在评论列表中（评论数从 0 变为 1）
```

### 评论注意事项

- 评论输入框是 `combobox` 类型（不是 textbox），需要先点击占位文本激活
- **不要从个人主页点击作品卡片**，会触发推荐视频弹窗而非目标作品；直接用 navigate_page 导航到 `/note/<id>` URL
- 评论用 **Enter 键**发送，不需要找发送按钮
- 右侧评论面板的 "评论(N)" tab 需要先被激活才能看到评论列表
- 抖音可能弹出下载客户端提示，可忽略
