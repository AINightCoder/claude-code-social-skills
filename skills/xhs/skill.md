---
name: xhs
version: 2.0.0
description: |
  通过 Chrome DevTools MCP 发布小红书笔记。
  自动将文字内容生成为卡片图片，解决小红书必须有图片的限制。
  支持指定标题、话题标签，也支持直接提供图片路径。
  用户输入 /xhs 后跟内容即可发布。
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
  - xiaohongshu
  - social-media
dependencies:
  - python>=3.10
  - Pillow
---

# XHS Skill

通过 Chrome DevTools 浏览器自动化发布小红书笔记。

## 触发

```
/xhs [--title "标题"] [--tags "标签1,标签2"] [--images "path1.jpg,path2.jpg"] <content>
```

- `--title`：笔记标题（必填，最多 20 字）。如果未指定，从内容中自动提取/生成
- `--tags`：话题标签，逗号分隔（可选）
- `--images`：图片路径，逗号分隔（可选）。如果未提供，自动生成文字卡片图
- `content`：笔记正文（最多 1000 字）

## 流程

### Step 0: 确保 Chrome 调试模式可用

参见 `.claude/skills/_shared/chrome-setup.md`

### Step 1: 解析参数

从用户输入中提取：
- **title**：如果用户指定了 `--title`，使用指定值。否则从正文内容中提取前 20 字或生成简短标题
- **content**：笔记正文，最多 1000 字
- **tags**：如果用户指定了 `--tags`，使用指定值
- **images**：如果用户指定了 `--images`，使用指定路径

### Step 2: 准备图片

**如果用户提供了 `--images`**：
- 验证图片文件存在
- 直接使用用户提供的图片路径

**如果未提供图片（默认）**：
- 调用文字卡片生成脚本：

```bash
python ~/.claude/skills/_shared/scripts/xhs_text_card.py \
  --title "标题" \
  --content "正文内容" \
  --output /tmp/xhs_card.png
```

- 脚本生成 1080x1440 (3:4) 深色风格文字卡片
- 使用生成的 `/tmp/xhs_card.png` 作为图片

### Step 3: 导航到小红书创作者中心

```
navigate_page(url: "https://creator.xiaohongshu.com/publish/publish", timeout: 30000)
```

加载完成后 take_snapshot，确认看到：
- 上传图片区域
- "发布笔记" 相关 UI

**登录检查**：如果页面跳转到登录页，提示用户先在 Chrome 调试窗口中登录小红书。

### Step 4: 上传图片

```
1. take_snapshot → 找到上传区域的文件选择器（input[type=file] 或 button "上传图片"/"拖拽或点击上传"）
2. upload_file(uid, filePath: 图片路径)
3. 等待上传完成（take_snapshot 确认缩略图出现）
```

**多张图片**：
```
对每张后续图片：
1. take_snapshot → 找到 "继续添加" 或 "+" 按钮
2. upload_file(uid, filePath: 图片路径)
3. 等待上传完成
```

### Step 5: 填写标题

```
1. take_snapshot → 找到标题输入框（textbox，placeholder 含"标题"）
2. click(uid) → 聚焦
3. type_text(text: 标题内容，最多 20 字)
```

### Step 6: 填写正文

```
1. take_snapshot → 找到正文编辑区域（textbox/generic，placeholder 含"正文"或"描述"）
2. click(uid) → 聚焦
3. type_text(text: 正文内容)
```

### Step 7: 添加话题标签（如果有）

```
1. take_snapshot → 查找 "#" 话题入口或 "添加话题" 按钮
2. click(uid) → 打开话题选择
3. 对每个标签：
   a. type_text(text: 标签名)
   b. take_snapshot → 找到匹配的话题建议
   c. click(uid) → 选择话题
```

### Step 8: 发布

```
1. take_snapshot → 找到 button "发布"（确认非 disabled）
2. click(uid) → 发布笔记
```

### Step 9: 确认发布成功

```
1. take_snapshot / take_screenshot → 确认页面跳转或出现发布成功提示
2. 如有可能，提取笔记 URL
```

### Step 10: 输出结果

```
发布成功！

标题：xxx
内容：xxx（前 50 字）
图片：自动生成文字卡片 / 用户提供 N 张
标签：#tag1 #tag2
```

## 关键注意事项

### 小红书平台限制

- **图片必填**：每条笔记至少 1 张图片，最多 18 张
- **标题必填**：最多 20 字
- **正文限制**：最多 1000 字
- **图片格式**：jpg、jpeg、png、webp
- **图片比例**：推荐 3:4（竖图）

### 元素定位

- **上传区域**：页面中的文件上传区域，可能是 input[type=file] 或拖拽区域
- **标题框**：textbox，placeholder 含 "标题"
- **正文框**：编辑区域，placeholder 含 "正文" 或 "描述"
- **发布按钮**：button "发布"
- 小红书的页面结构可能更新频繁，如果 snapshot 中找不到预期元素，先 take_screenshot 查看实际页面状态

### 登录态

小红书创作者中心需要登录。支持扫码登录。如果是干净 profile 需要用户先手动登录。

### 发布节奏

- 确认图片上传完成后再填写标题和正文
- 确认所有内容填写完毕后再点击发布
- 发布后等待确认成功再输出结果

### 与其他 Skill 的差异

| 维度 | Twitter | 即刻 | 知乎 | 抖音图文 | 小红书 |
|------|---------|------|------|---------|--------|
| 发布方式 | Chrome DevTools | Chrome DevTools | Chrome DevTools | Chrome DevTools | Chrome DevTools |
| 内容类型 | 短文本 | 短文本 | 长文章 | 图文 | 图文笔记 |
| 图片 | 可选 | 可选 | 可选 | 必须 | 必须（自动生成）|
| 标题 | 无 | 无 | 有(100字) | 有(20字) | 有(20字) |
| 正文限制 | 280 chars | 无限 | 无限 | 1000字 | 1000字 |

### 错误处理

- 登录过期：提示用户在 Chrome 调试窗口中重新登录
- 图片上传失败：重试一次，仍失败则提示用户检查图片格式和大小
- 发布失败：take_screenshot 截图，输出错误信息供排查
