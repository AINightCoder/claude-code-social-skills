"""生成小红书/抖音文字卡片图片 (1080x1440, 3:4 高级风格，支持 Emoji)"""

import argparse
import random
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

# 卡片尺寸
WIDTH, HEIGHT = 1080, 1440

# ── 配色方案 ──────────────────────────────────────────────
# 每套方案: (bg_top, bg_bottom, title_color, content_color, accent_color)
COLOR_SCHEMES = {
    "midnight": {
        "bg_top": (15, 23, 42),       # 深靛蓝
        "bg_bottom": (30, 41, 59),     # 略亮靛蓝
        "title": (248, 250, 252),
        "content": (203, 213, 225),
        "accent": (99, 102, 241),      # 靛紫
        "accent2": (139, 92, 246),     # 紫色
    },
    "forest": {
        "bg_top": (13, 27, 23),        # 深墨绿
        "bg_bottom": (22, 40, 35),
        "title": (236, 253, 245),
        "content": (187, 227, 210),
        "accent": (52, 211, 153),      # 翡翠绿
        "accent2": (16, 185, 129),
    },
    "ember": {
        "bg_top": (35, 15, 15),        # 深酒红
        "bg_bottom": (50, 25, 20),
        "title": (255, 241, 235),
        "content": (225, 200, 190),
        "accent": (251, 146, 60),      # 暖橙
        "accent2": (245, 101, 101),    # 珊瑚红
    },
    "ocean": {
        "bg_top": (10, 25, 47),        # 深海蓝
        "bg_bottom": (17, 40, 65),
        "title": (224, 242, 254),
        "content": (186, 220, 245),
        "accent": (56, 189, 248),      # 天蓝
        "accent2": (14, 165, 233),
    },
    "lavender": {
        "bg_top": (30, 20, 45),        # 深薰衣草紫
        "bg_bottom": (45, 30, 60),
        "title": (245, 240, 255),
        "content": (210, 200, 230),
        "accent": (196, 167, 255),     # 淡紫
        "accent2": (232, 121, 249),    # 粉紫
    },
}

# ── 字体 ──────────────────────────────────────────────────
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
    "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
]
EMOJI_FONT_PATH = "C:/Windows/Fonts/seguiemj.ttf"

# emoji 正则 - 覆盖 keycap 序列、组合 emoji、ZWJ 序列等
EMOJI_RE = re.compile(
    "(?:"
    # keycap 序列: 数字/符号 + VS16 + 组合键帽
    "[0-9#*]\uFE0F?\u20E3"
    "|"
    # ZWJ 序列 (家庭、职业等组合 emoji)
    "(?:["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002B50\U00002B55"
    "\U000023E9-\U000023FA"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "\U000020E3"
    "\U00002702-\U000027B0"
    "\U0001F004\U0001F0CF"
    "\U0001F170-\U0001F251"
    "][\uFE0E\uFE0F]?"
    "(?:\u200D["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000027BF"
    "][\uFE0E\uFE0F]?)*"
    ")"
    ")+",
    flags=re.UNICODE,
)


def _find_font(bold=False):
    if bold:
        candidates = ["C:/Windows/Fonts/msyhbd.ttc"] + FONT_CANDIDATES
    else:
        candidates = FONT_CANDIDATES
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def _load_font(size, bold=False):
    path = _find_font(bold)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _load_emoji_font(size):
    if Path(EMOJI_FONT_PATH).exists():
        return ImageFont.truetype(EMOJI_FONT_PATH, size)
    return None


def _draw_gradient(img, color_top, color_bottom):
    """绘制垂直线性渐变背景"""
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _tokenize(text):
    """将文本拆分为 (内容, 是否emoji) 的 token 列表"""
    tokens = []
    last_end = 0
    for m in EMOJI_RE.finditer(text):
        if m.start() > last_end:
            tokens.append((text[last_end:m.start()], False))
        tokens.append((m.group(), True))
        last_end = m.end()
    if last_end < len(text):
        tokens.append((text[last_end:], False))
    return tokens


def _emoji_aware_wrap(text, width):
    """emoji 感知的文本换行，每个 emoji 算 2 个字符宽度"""
    tokens = _tokenize(text)
    lines = []
    current_line = ""
    current_width = 0

    for token_text, is_emoji in tokens:
        if is_emoji:
            token_width = 2  # emoji 算 2 字符宽
            if current_width + token_width > width and current_line:
                lines.append(current_line)
                current_line = token_text
                current_width = token_width
            else:
                current_line += token_text
                current_width += token_width
        else:
            # 逐字符处理普通文本
            for char in token_text:
                # 中文/全角字符算 2 宽度，其他算 1
                cw = 2 if ord(char) > 0x7F else 1
                if current_width + cw > width and current_line:
                    lines.append(current_line)
                    current_line = char
                    current_width = cw
                else:
                    current_line += char
                    current_width += cw

    if current_line:
        lines.append(current_line)
    return lines


def _draw_text_with_emoji(draw, img, x, y, text, text_font, emoji_font, fill):
    """绘制含 emoji 的混排文本，返回绘制后的 x 坐标"""
    if emoji_font is None:
        draw.text((x, y), text, font=text_font, fill=fill)
        return

    parts = EMOJI_RE.split(text)
    emojis = EMOJI_RE.findall(text)

    cursor_x = x
    for i, part in enumerate(parts):
        if part:
            draw.text((cursor_x, y), part, font=text_font, fill=fill)
            bbox = text_font.getbbox(part)
            cursor_x += bbox[2] - bbox[0]
        if i < len(emojis):
            # 绘制 emoji (使用 embedded_color 保留彩色)
            draw.text((cursor_x, y), emojis[i], font=emoji_font,
                       embedded_color=True)
            bbox = emoji_font.getbbox(emojis[i])
            cursor_x += bbox[2] - bbox[0]


def _draw_decoration(draw, scheme, margin_x):
    """绘制装饰元素：顶部和底部的渐变色块"""
    accent = scheme["accent"]
    accent2 = scheme["accent2"]

    # 顶部装饰 - 渐变色条
    bar_width = 80
    bar_height = 5
    y_top = 100
    for bx in range(bar_width):
        ratio = bx / bar_width
        r = int(accent[0] + (accent2[0] - accent[0]) * ratio)
        g = int(accent[1] + (accent2[1] - accent[1]) * ratio)
        b = int(accent[2] + (accent2[2] - accent[2]) * ratio)
        draw.line([(margin_x + bx, y_top), (margin_x + bx, y_top + bar_height)],
                  fill=(r, g, b))

    # 底部装饰 - 渐变色条
    y_bot = HEIGHT - 80
    for bx in range(50):
        ratio = bx / 50
        r = int(accent2[0] + (accent[0] - accent2[0]) * ratio)
        g = int(accent2[1] + (accent[1] - accent2[1]) * ratio)
        b = int(accent2[2] + (accent[2] - accent2[2]) * ratio)
        draw.line([(margin_x + bx, y_bot), (margin_x + bx, y_bot + 4)],
                  fill=(r, g, b))


def generate_card(title: str, content: str, output: str,
                  scheme_name: Optional[str] = None):
    # 选择配色
    if scheme_name and scheme_name in COLOR_SCHEMES:
        scheme = COLOR_SCHEMES[scheme_name]
    else:
        scheme = random.choice(list(COLOR_SCHEMES.values()))

    img = Image.new("RGB", (WIDTH, HEIGHT), scheme["bg_top"])

    # 渐变背景
    _draw_gradient(img, scheme["bg_top"], scheme["bg_bottom"])

    draw = ImageDraw.Draw(img)

    # 字体
    title_font = _load_font(76, bold=True)
    content_font = _load_font(38)
    emoji_font_title = _load_emoji_font(72)
    emoji_font_content = _load_emoji_font(36)

    margin_x = 80
    y = 100

    # 装饰元素
    _draw_decoration(draw, scheme, margin_x)
    y += 40

    # ── 标题 ──
    title_lines = _emoji_aware_wrap(title, width=18)  # 大字体每行更少字
    title_line_height = 95
    for line in title_lines[:3]:  # 最多3行标题
        _draw_text_with_emoji(draw, img, margin_x, y, line,
                              title_font, emoji_font_title, scheme["title"])
        y += title_line_height
    y += 25

    # 分隔线 - 渐变
    sep_y = y
    accent = scheme["accent"]
    accent2 = scheme["accent2"]
    line_len = WIDTH - 2 * margin_x
    for sx in range(line_len):
        ratio = sx / line_len
        r = int(accent[0] + (accent2[0] - accent[0]) * ratio)
        g = int(accent[1] + (accent2[1] - accent[1]) * ratio)
        b = int(accent[2] + (accent2[2] - accent[2]) * ratio)
        draw.point((margin_x + sx, sep_y), fill=(r, g, b))
        draw.point((margin_x + sx, sep_y + 1), fill=(r, g, b, 128))
    y += 45

    # ── 正文 ──
    max_content_y = HEIGHT - 120
    content_lines = _emoji_aware_wrap(content, width=38)
    content_line_height = 58
    for line in content_lines:
        if y + content_line_height > max_content_y:
            draw.text((margin_x, y), "...", font=content_font,
                      fill=scheme["content"])
            break
        _draw_text_with_emoji(draw, img, margin_x, y, line,
                              content_font, emoji_font_content,
                              scheme["content"])
        y += content_line_height

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG")
    print(f"Card saved: {output}")


def main():
    parser = argparse.ArgumentParser(description="生成文字卡片图片")
    parser.add_argument("--title", required=True, help="卡片标题")
    parser.add_argument("--content", required=True, help="卡片正文")
    parser.add_argument("--output", default="/tmp/xhs_card.png", help="输出路径")
    parser.add_argument("--scheme", default=None,
                        choices=list(COLOR_SCHEMES.keys()),
                        help="配色方案 (默认随机)")
    args = parser.parse_args()
    generate_card(args.title, args.content, args.output, args.scheme)


if __name__ == "__main__":
    main()
