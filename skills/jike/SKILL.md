---
name: jike
version: 1.0.0
description: |
  通过 Chrome DevTools MCP 发布即刻动态。
  支持指定圈子（默认选择推荐的第一个圈子）。
  用户输入 /jike 后跟内容即可发布。
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
  - jike
  - social-media
---

# Jike Skill

通过 Chrome DevTools 浏览器自动化发布即刻动态。

## 触发

```
/jike <content>
/jike --topic <圈子名> <content>
```

- 不指定 `--topic` 时，默认选择推荐列表中的第一个圈子
- 指定 `--topic` 时，在圈子搜索框中输入关键词并选择匹配项

## 流程

### Step 0: 确保 Chrome 调试模式可用

参见 `.claude/skills/_shared/chrome-setup.md`

### Step 1: 导航到即刻首页

```
navigate_page(url: "https://web.okjike.com/following")
```

等待页面加载完成后 take_snapshot，确认看到发布输入框。

### Step 2: 输入内容

```
1. take_snapshot → 找到输入框（textbox, multiline, 无 label 或 placeholder 为"分享你的想法..."）
   - 输入框特征：紧跟在用户头像链接之后的 textbox multiline 元素
2. click(uid) → 聚焦输入框
3. type_text(text: 动态内容)
```

### Step 3: 选择圈子

输入内容后，页面会自动推荐圈子列表。

**默认行为（不指定 --topic）**：
```
1. take_snapshot → 查找推荐的圈子列表
   - 圈子推荐项是 generic 元素，内含 StaticText（如 "JitHub程序员"、"工程师的日常" 等）
   - 它们出现在 textbox "未选择圈子" 之后
2. click 第一个推荐圈子的 uid
```

**指定圈子（--topic <名称>）**：
```
1. take_snapshot → 找到圈子搜索框（textbox "未选择圈子"）
2. click(uid) → 聚焦圈子搜索框
3. type_text(text: 圈子关键词)
4. take_snapshot → 等待搜索结果出现
5. click 匹配的圈子项
```

### Step 4: 发布

```
1. take_snapshot → 找到 button "发送"（确认不是 disabled 状态）
2. click(uid) → 发布
```

### Step 5: 获取动态 URL

即刻的动态在 DOM 中没有直接的链接，需要通过 API 获取。

发布后使用 evaluate_script 调用即刻 API：

```javascript
async () => {
  const token = localStorage.getItem('JK_ACCESS_TOKEN');
  const res = await fetch('https://api.ruguoapp.com/1.0/personalUpdate/single', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-jike-access-token': token
    },
    body: JSON.stringify({
      limit: 5,
      username: '<USER_ID>'
    })
  });
  const data = await res.json();
  if (data.success && data.data) {
    // 跳过置顶帖，取第一条非置顶的动态
    const post = data.data.find(p => !(p.pinned && p.pinned.personalUpdate));
    if (post) {
      return {
        id: post.id,
        content: post.content.substring(0, 50),
        topic: post.topic ? post.topic.content : null,
        url: 'https://web.okjike.com/originalPost/' + post.id
      };
    }
  }
  return { error: 'failed to get post' };
}
```

**注意**：API 返回的列表中置顶帖排在最前面，必须跳过置顶帖才能拿到刚发的动态。

**获取 USER_ID**：从页面中提取，通常在导航栏的个人主页链接中：
- 查找 snapshot 中 link 的 url 包含 `/u/` 的元素
- 提取 UUID 部分（如 `2653db93-ee4a-4839-b03c-605b74ca3e0d`）

### Step 6: 输出结果

```
发布成功！

https://web.okjike.com/originalPost/xxx
```

## 关键注意事项

### 元素定位

- **输入框**：页面顶部的 `textbox multiline`，无明确 label，在用户头像链接之后
- **圈子搜索框**：`textbox "未选择圈子"`
- **圈子推荐项**：`generic` 元素，内含 `StaticText`（圈子名称），在圈子搜索框之后出现
- **发送按钮**：`button "发送"`，有内容时不含 `disabled`

### 与 Twitter Skill 的差异

| 维度 | Twitter | 即刻 |
|------|---------|------|
| 发布入口 | navigate 到 compose 页面 | 首页顶部直接输入 |
| 字数限制 | 280 weighted chars | 无限制 |
| Thread | 支持（回复自己） | 不支持（单条动态） |
| 话题/圈子 | #hashtag 内嵌文本 | 独立选择器 |
| 获取 URL | 从 DOM 提取 | 通过 API 查询 |

### 发布节奏

- 确认输入框聚焦后再输入内容
- 确认圈子选择完成后再点击发送
- 发送后等待 snapshot 确认动态出现在 timeline 中
