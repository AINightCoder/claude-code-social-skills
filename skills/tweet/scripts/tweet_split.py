"""将长文本拆分为多条推文，确保每条不超过 280 weighted chars。

Twitter 字符权重规则：
- ASCII 字符 = 1
- CJK / emoji / 其他非 ASCII = 2
- URL 统一算 23（t.co 短链）
"""

import argparse
import json
import re
import sys


def char_weight(ch: str) -> int:
    cp = ord(ch)
    if cp <= 0x7F:
        return 1
    return 2


URL_PATTERN = re.compile(r"https?://\S+")
MAX_WEIGHT = 280


def text_weight(text: str) -> int:
    """计算一段文本的 Twitter 加权字符数。"""
    urls = URL_PATTERN.findall(text)
    clean = text
    for url in urls:
        clean = clean.replace(url, "", 1)
    w = sum(char_weight(ch) for ch in clean)
    w += len(urls) * 23
    return w


def split_tweets(text: str) -> list[str]:
    """将文本拆分为多条推文，每条不超过 280 加权字符。"""
    if text_weight(text) <= MAX_WEIGHT:
        return [text]

    # 按段落 → 句子 → 硬切 三级拆分
    paragraphs = re.split(r"\n{2,}", text.strip())
    tweets = []
    current = ""

    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para
        if text_weight(candidate) <= MAX_WEIGHT:
            current = candidate
        else:
            # 当前段落放不下，先保存已有内容
            if current:
                tweets.append(current.strip())
                current = ""

            # 尝试按句子拆分这个段落
            if text_weight(para) <= MAX_WEIGHT:
                current = para
            else:
                sentences = re.split(r"(?<=[。！？.!?\n])\s*", para)
                for sent in sentences:
                    if not sent.strip():
                        continue
                    candidate = (current + " " + sent).strip() if current else sent
                    if text_weight(candidate) <= MAX_WEIGHT:
                        current = candidate
                    else:
                        if current:
                            tweets.append(current.strip())
                        # 句子本身超长，硬切
                        if text_weight(sent) > MAX_WEIGHT:
                            tweets.extend(_hard_split(sent))
                            current = ""
                        else:
                            current = sent

    if current.strip():
        tweets.append(current.strip())

    return tweets


def _hard_split(text: str) -> list[str]:
    """按字符硬切，确保每段不超过 MAX_WEIGHT。"""
    parts = []
    current = ""
    for ch in text:
        if text_weight(current + ch) > MAX_WEIGHT:
            parts.append(current)
            current = ch
        else:
            current += ch
    if current:
        parts.append(current)
    return parts


def main():
    parser = argparse.ArgumentParser(description="拆分推文")
    parser.add_argument("--file", required=True, help="输入文件路径")
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {args.file}"}))
        sys.exit(1)

    tweets = split_tweets(text)
    result = {
        "count": len(tweets),
        "tweets": [
            {"index": i, "content": t, "weight": text_weight(t)}
            for i, t in enumerate(tweets)
        ],
    }
    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
