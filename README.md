# Claude Code Social Skills

通过 Claude Code Skills 自动化社交媒体内容发布与优化。

## 支持平台

| 平台 | 命令 | 功能 | 特点 |
|------|------|------|------|
| Twitter/X | `/tweet` | 推文/Thread | 自动拆分 280 字符限制 |
| 即刻 | `/jike` | 动态 | 支持圈子选择 |
| 小红书 | `/xhs` | 图文笔记 | 自动生成文字卡片 |
| 知乎 | `/zhihu` | 文章 | 支持 Markdown |
| 抖音 | `/douyin` | 图文 | 支持多图/自动生成卡片 |
| **内容评估** | `/media-eval` | 评估+优化 | 分层评估+多平台改写 |
| **自动运营** | `/media-optimizer` | 编排调度 | 自动生成→评估→多平台同时发布 |

## 前置要求

- [Claude Code CLI](https://github.com/anthropics/claude-code)
- [Chrome DevTools MCP](https://github.com/anthropics/mcp-server-chrome) 已配置
- Python 3.10+
- Pillow（用于生成文字卡片图片）

## 安装

### 1. Clone 仓库

```bash
git clone https://github.com/AINightCoder/claude-code-social-skills.git
cd claude-code-social-skills
```

### 2. 复制 Skills 到 Claude Code 目录

**Linux / macOS:**
```bash
cp -r skills/* ~/.claude/skills/
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse -Force skills\* $env:USERPROFILE\.claude\skills\
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 配置 Chrome 调试模式

所有 Skills 依赖 Chrome DevTools MCP，需要先启动 Chrome 调试模式。

### Windows

```powershell
# 关闭所有 Chrome 进程
taskkill /F /IM chrome.exe

# 启动调试模式（使用独立 profile）
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\chrome-debug"
```

### macOS

```bash
# 关闭所有 Chrome 进程
pkill -f "Google Chrome"

# 启动调试模式
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug"
```

### Linux

```bash
# 关闭所有 Chrome 进程
pkill chrome

# 启动调试模式
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug"
```

### 验证调试端口

```bash
curl http://127.0.0.1:9222/json/version
```

返回 JSON 表示调试端口正常。

> **注意**: 独立 `user-data-dir` 是干净的浏览器 profile，没有登录态。首次使用需要在弹出的 Chrome 中手动登录各平台。

## 使用方法

### /media-eval - 内容评估与优化

发布前先用 AI 资深编辑评估内容质量，自动改写为各平台版本。

```
/media-eval 你的内容文本
```

**指定目标平台：**
```
/media-eval --platform xhs,tweet 你的内容文本
```

**从文件评估：**
```
/media-eval path/to/article.md
```

**从 URL 评估：**
```
/media-eval https://example.com/article
```

**评估输出：**
- 分层评估报告：内容本质层（叙事/观点/共鸣/可读性）+ 平台包装层（算法/调性/互动）
- 总分（1-100）+ 各维度评分 + 具体到句子的改写建议
- 针对每个目标平台的优化改写版本（不是截断，是调性重写）

> 推荐工作流：`/media-eval` 评估优化 → `/tweet` `/xhs` `/zhihu` 等发布

---

### /media-optimizer - 自媒体自动化运营

全自动编排系统：内容生成 → `/media-eval` 评估 → 五平台同时发布。

```
"生成今日内容"        # AI 扫描知识库+热点，生成内容
"发布到所有平台"      # 自动评估+改写+五平台同时发布
"查看数据报告"        # 各平台数据汇总分析
```

**核心流程：**
```
内容生成 → /media-eval 评估（评分>=75直接发，<75自动优化最多2次）
         → 同时调用 /tweet /jike /xhs /zhihu /douyin 发布
```

**热点响应：** 检测到相关热点时，评估一次无论评分直接发布五平台，追速度。

> media-optimizer 是编排层，评估委托 `/media-eval`，发布委托各平台 skill。

---

### /tweet - 发布 Twitter 推文

```
/tweet 这是一条推文内容
```

**长文本自动拆分为 Thread:**
```
/tweet 这是一段很长的内容，超过 280 字符会自动拆分为多条推文，形成 Thread...
```

**手动分隔多条推文:**
```
/tweet 第一条推文
---
第二条推文
---
第三条推文
```

### /jike - 发布即刻动态

```
/jike 今天学到了一个新技能！
```

**指定圈子:**
```
/jike --topic 程序员 分享一个技术心得...
```

### /xhs - 发布小红书笔记

```
/xhs --title "我的第一篇笔记" 这是笔记正文内容...
```

**指定话题标签:**
```
/xhs --title "技术分享" --tags "编程,Python" 这是一篇关于 Python 的笔记...
```

**使用自定义图片:**
```
/xhs --title "旅行日记" --images "photo1.jpg,photo2.jpg" 今天去了...
```

> 未指定图片时，自动生成高级风格文字卡片（支持 Emoji、渐变背景、5 套配色方案）。

**指定卡片配色方案：**
```
/xhs --title "技术分享" --scheme midnight 内容...
```

可选配色：`midnight`（深靛蓝）、`forest`（墨绿）、`ember`（酒红暖橙）、`ocean`（深海蓝）、`lavender`（薰衣草紫），不指定则随机。

### /zhihu - 发布知乎文章

```
/zhihu 我用 Claude Code 做了一次产品诊断
---
作为一个独立开发者，我一直在寻找提升效率的工具...

（支持 Markdown 语法）
```

**指定话题:**
```
/zhihu --topic AI 我的 AI 开发之旅
---
正文内容...
```

### /douyin - 发布抖音图文

```
/douyin 今天分享一个超好用的小技巧！
```

**使用自定义图片:**
```
/douyin --images photo1.jpg photo2.jpg 今天分享...
```

**上传整个目录的图片:**
```
/douyin --dir ./photos 今天的旅行记录
```

> 未指定图片时，自动生成文字卡片。

## 常见问题

### Q: 提示"Chrome 调试端口不可用"

确保 Chrome 是以 `--remote-debugging-port=9222` 参数启动的。如果已有 Chrome 在运行，需要先关闭所有实例再重新启动。

### Q: 发布时提示需要登录

使用独立 `user-data-dir` 启动的 Chrome 是干净的 profile，需要手动登录各平台。在调试窗口中登录后，登录态会保留。

### Q: 小红书/抖音上传图片失败

检查图片格式（支持 jpg/jpeg/png/webp）和大小（建议单张 < 10MB）。图片比例推荐 3:4 竖图。

### Q: Twitter 发布失败

可能是 rate limit。等待几分钟后重试。如果内容包含敏感词，也可能被平台拦截。

### Q: 即刻动态获取 URL 失败

即刻动态的 URL 需要通过 API 获取，确保登录态有效。如果获取失败，可以在即刻 App 中查看已发布的动态。

## 项目结构

```
claude-code-social-skills/
├── README.md
├── requirements.txt
└── skills/
    ├── media-evaluator/
    │   └── SKILL.md          # 内容评估与优化（纯 prompt，无依赖）
    ├── media-optimizer/
    │   ├── SKILL.md          # 自动化运营编排（委托 media-eval + 各平台 skill）
    │   ├── scripts/          # 内容生成、数据分析等脚本
    │   └── templates/        # 内容模板
    ├── tweet/
    │   ├── SKILL.md
    │   └── scripts/tweet_split.py
    ├── jike/
    │   └── SKILL.md
    ├── xhs/
    │   └── SKILL.md
    ├── zhihu/
    │   └── SKILL.md
    ├── douyin/
    │   └── SKILL.md
    └── _shared/
        ├── chrome-setup.md
        └── scripts/
            └── xhs_text_card.py  # 文字卡片生成（渐变背景/5套配色/Emoji支持）
```

## License

MIT