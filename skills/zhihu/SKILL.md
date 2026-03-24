---
name: zhihu
version: 1.1.0
description: |
  通过 Chrome DevTools MCP 发布知乎文章或评论。
  Publish articles or comments on Zhihu (知乎) via browser automation.
  支持 Markdown 语法输入，可指定话题。
  用户输入 /zhihu 后跟标题和正文即可发布，使用 --comment 可评论指定文章。
  触发关键词：zhihu, 知乎, 发知乎, 知乎文章, post to zhihu, 知乎评论
allowed-tools:
  - Bash
  - Read
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__type_text
  - mcp__chrome-devtools__press_key
  - mcp__chrome-devtools__evaluate_script
tags:
  - zhihu
  - social-media
---

# Zhihu Skill

通过 Chrome DevTools 浏览器自动化发布知乎文章。

## 触发

```
/zhihu [--topic <话题>] <标题>
---
正文内容（支持 Markdown）
```

或从文件读取（文件第一行为标题，其余为正文）：
```
/zhihu --file <文件路径>
```

## 流程

### Step 0: 确保 Chrome 调试模式可用

参见 `.claude/skills/_shared/chrome-setup.md`

### Step 1: 解析输入

**参数解析**：
- `--topic <话题>`：可选，发布时添加的话题标签
- `--file <路径>`：从文件读取，第一行为标题，其余为正文
- 直接输入时：用 `---` 分隔标题和正文

**示例**：
```
/zhihu --topic AI 我用 Claude Code 做了一次产品诊断
---
作为一个独立开发者，我一直在...
```

### Step 2: 导航到写文章页面

```
navigate_page(url: "https://zhuanlan.zhihu.com/write", timeout: 30000)
```

知乎写文章页面加载较慢，设置 30 秒超时。

加载完成后 take_snapshot，确认看到：
- 标题输入框（`textbox multiline`，无 label，placeholder "请输入标题"）
- 正文输入框（`textbox multiline`，description 含 "请输入正文"）

### Step 3: 输入标题

```
1. take_snapshot → 找到标题输入框
   - 特征：第一个 textbox multiline，value 为空，紧跟在工具栏按钮之后
   - 通常是 snapshot 中第一个没有 description 的 textbox multiline
2. click(uid) → 聚焦标题框
3. type_text(text: 标题内容)
```

**注意**：标题最多 100 个字。

### Step 4: 输入正文

```
1. take_snapshot → 找到正文输入框
   - 特征：第二个 textbox multiline，description 含 "请输入正文"
2. click(uid) → 聚焦正文框
3. type_text(text: 正文内容)
```

**Markdown 支持**：知乎编辑器默认开启 Markdown 语法输入，直接输入 Markdown 格式文本即可自动渲染。

**列表预处理**：知乎编辑器的 Markdown 实时渲染会将 `1.` 和 `- ` 转换为富文本列表元素，同时保留原始文本，导致序号重复（如 `2. 1. 内容`、`· - 内容`）。

输入正文前必须预处理列表：
- 有序列表 `1. xxx` → 改为 `1、xxx`（用中文顿号代替英文点号）
- 无序列表 `- xxx` → 改为 `· xxx` 或直接去掉符号

```
预处理示例：
Markdown 原文：              知乎输入：
1. 第一项                    1、第一项
2. 第二项           →        2、第二项
3. 第三项                    3、第三项
- 无序项                     · 无序项
```

可用正则替换：`^(\d+)\. ` → `$1、`，`^- ` → `· `

### Step 5: 添加话题（可选）

输入内容后，页面底部的"发布设置"区域会出现话题选项。

```
1. evaluate_script 滚动到页面底部：
   window.scrollTo(0, document.body.scrollHeight)
2. take_snapshot → 找到 button "添加话题"
3. click(uid) → 打开话题输入
4. take_snapshot → 找到话题搜索输入框
5. type_text(text: 话题关键词)
6. take_snapshot → 等待搜索结果出现
7. click 第一个匹配的话题
```

### Step 6: 发布

```
1. take_snapshot → 找到 button "发布"（确认不是 disabled）
2. click(uid) → 发布文章
```

**发布后可能的情况**：
- 页面跳转到已发布的文章页面
- 或弹出发布成功提示

### Step 7: 获取文章 URL

知乎文章 ID 在编辑时就已经生成（URL 会从 `/write` 变为 `/p/{article_id}/edit`）。

**方案 A**（优先）：在 Step 4 输入内容后，从浏览器 URL 中提取文章 ID：
```javascript
() => {
  const match = window.location.pathname.match(/\/p\/(\d+)\/edit/);
  return match ? {
    id: match[1],
    url: 'https://zhuanlan.zhihu.com/p/' + match[1]
  } : { error: 'no article id found' };
}
```

**方案 B**：发布后检查页面是否跳转，从新 URL 提取。

### Step 8: 输出结果

```
发布成功！

https://zhuanlan.zhihu.com/p/xxx
```

## 关键注意事项

### 元素定位

- **标题框**：第一个 `textbox multiline`（无 description），在工具栏按钮组之后
- **正文框**：第二个 `textbox multiline`，description 含 "请输入正文"
- **发布按钮**：`button "发布"`，标题和正文都有内容时可用
- **添加话题**：`button "添加话题"`，在"发布设置"区域内，需要滚动到底部才可见
- **发布设置**：`button "发布设置"`，在底部状态栏

### 知乎编辑器特性

- 支持 Markdown 语法（底部显示 "Markdown 语法输入中"）
- 自动保存草稿（输入即保存）
- 编辑 URL 自动变为 `/p/{id}/edit`
- 标题最多 100 字
- 正文无字数限制

### 登录态

知乎写文章需要登录。如果导航到 `/write` 后跳转到登录页（URL 包含 `/signin`），需要提示用户先在 Chrome 调试窗口中手动登录知乎。

### 错误处理

- 登录过期：导航到 `/write` 后 URL 包含 `/signin`，提示用户在 Chrome 调试窗口中登录
- 发布失败：如果 "发布" 按钮点击后仍显示编辑页，take_screenshot 检查是否有错误提示
- 评论焦点丢失：如果 type_text 输入到搜索框而非评论框，重新 click 评论框 uid 后再输入

### 与其他 Skill 的差异

| 维度 | Twitter | 即刻 | 知乎 |
|------|---------|------|------|
| 内容类型 | 短文本 | 短文本 | 长文章 |
| 标题 | 无 | 无 | 有（必填） |
| 编辑器 | 纯文本 | 纯文本 | 富文本/Markdown |
| 字数限制 | 280 weighted | 无 | 无 |
| URL 获取 | DOM 提取 | API 查询 | 编辑 URL 提取 |
| 话题 | #hashtag 内嵌 | 圈子选择器 | 话题搜索添加 |

---

## 评论功能

### 触发

```
/zhihu --comment <文章URL> <评论内容>
```

文章 URL 格式：`https://zhuanlan.zhihu.com/p/<article_id>`

### 流程

#### Step 1: 导航到文章页

```
navigate_page(url: 文章URL)
```

#### Step 2: 找到评论输入框并输入

```
1. take_snapshot → 找到评论输入框
   - 特征：textbox multiline，description 为 "理性发言，友善互动"
2. click(uid) → 聚焦评论框（点击后会展开评论工具栏，出现表情、发布按钮等）
3. type_text(text: 评论内容)
```

**关键陷阱**：知乎页面顶部有搜索框 `combobox "搜索"`，type_text 可能误输入到搜索框。必须确保 take_snapshot 中评论框显示 `focusable focused` 状态后再输入。

#### Step 3: 发送评论

```
1. take_snapshot → 找到 button "发布"（在评论工具栏中，非 disabled）
2. click(uid) → 发送评论
```

**注意**：
- **不要用 Ctrl+Enter**，这会触发搜索框而不是发送评论
- 必须点击评论框展开后出现的 `button "发布"`
- 如果 button "发布" 是 disabled 状态，说明评论框未正确输入内容

#### Step 4: 确认成功

```
take_screenshot → 确认评论出现在评论列表中
```

### 评论注意事项

- 评论框 description 是 "理性发言，友善互动"
- 点击评论框后会展开工具栏（表情、发布按钮）
- **焦点陷阱**：搜索框可能抢占焦点，确认评论框 focused 后再输入
- 发送用 click "发布" 按钮，**不要用键盘快捷键**
