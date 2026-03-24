"""生成小红书/抖音文字卡片图片 (1080x1440, 3:4 深色风格)"""

import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 卡片尺寸
WIDTH, HEIGHT = 1080, 1440

# 颜色
BG_COLOR = (30, 30, 35)
TITLE_COLOR = (255, 255, 255)
CONTENT_COLOR = (220, 220, 225)
ACCENT_COLOR = (100, 140, 255)

# 字体 - 优先微软雅黑，回退到系统字体
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
]


def find_font(bold=False):
    """查找可用字体"""
    if bold:
        candidates = ["C:/Windows/Fonts/msyhbd.ttc"] + FONT_CANDIDATES
    else:
        candidates = FONT_CANDIDATES
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def generate_card(title: str, content: str, output: str):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_path = find_font()
    font_bold_path = find_font(bold=True)

    title_font = ImageFont.truetype(font_bold_path or font_path, 52) if font_path else ImageFont.load_default()
    content_font = ImageFont.truetype(font_path, 38) if font_path else ImageFont.load_default()

    margin_x = 80
    y = 120

    # 顶部装饰线
    draw.rectangle([margin_x, y, margin_x + 60, y + 4], fill=ACCENT_COLOR)
    y += 40

    # 标题
    title_lines = textwrap.wrap(title, width=18)
    for line in title_lines[:2]:
        draw.text((margin_x, y), line, font=title_font, fill=TITLE_COLOR)
        y += 70
    y += 30

    # 分隔线
    draw.rectangle([margin_x, y, WIDTH - margin_x, y + 1], fill=(80, 80, 90))
    y += 40

    # 正文
    max_content_y = HEIGHT - 120
    content_lines = textwrap.wrap(content, width=24)
    for line in content_lines:
        if y + 55 > max_content_y:
            draw.text((margin_x, y), "...", font=content_font, fill=CONTENT_COLOR)
            break
        draw.text((margin_x, y), line, font=content_font, fill=CONTENT_COLOR)
        y += 55

    # 底部装饰
    draw.rectangle([margin_x, HEIGHT - 80, margin_x + 40, HEIGHT - 76], fill=ACCENT_COLOR)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG")
    print(f"Card saved: {output}")


def main():
    parser = argparse.ArgumentParser(description="生成文字卡片图片")
    parser.add_argument("--title", required=True, help="卡片标题")
    parser.add_argument("--content", required=True, help="卡片正文")
    parser.add_argument("--output", default="/tmp/xhs_card.png", help="输出路径")
    args = parser.parse_args()
    generate_card(args.title, args.content, args.output)


if __name__ == "__main__":
    main()
