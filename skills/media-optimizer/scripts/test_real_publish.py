#!/usr/bin/env python3
"""
Media Optimizer - Real Publish Test
测试真实的自动发布功能
"""

import os
import sys
from datetime import datetime

# 添加脚本路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from auto_publisher import AutoPublisher

def test_twitter_publish():
    """测试 X.com 真实发布"""
    print("=" * 60)
    print("🧪 测试: X.com 真实发布")
    print("=" * 60)
    print()

    publisher = AutoPublisher()

    # 测试内容
    test_content = f"""这是 Media Optimizer 的真实发布测试！🚀

测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✨ 功能亮点:
- 完全自动化浏览器控制
- 遵循 snapshot → act 标准流程
- 使用 openclaw profile 实现零人工干预

#独立开发 #AI #自动化 #OpenClaw"""

    print("📝 测试内容:")
    print(test_content)
    print()

    # 执行真实发布
    result = publisher.publish_to_twitter(test_content, real_publish=True)

    print()
    print("=" * 60)
    print("📊 发布结果")
    print("=" * 60)
    print()

    if result['success']:
        print("✅ 发布成功！")
        print(f"   平台: {result['platform']}")
        print(f"   URL: {result['url']}")
        print(f"   时间: {result['published_at']}")
    else:
        print("❌ 发布失败")
        print(f"   错误: {result.get('error', result.get('message', '未知错误'))}")

    print()
    return result['success']

def main():
    """主函数"""
    print()
    print("🚀 Media Optimizer - 真实发布测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("⚠️  警告: 这将真实发布到您的 X.com 账号！")
    print()

    # 确认
    response = input("确认要继续吗？(yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("❌ 测试已取消")
        return

    print()

    # 运行测试
    success = test_twitter_publish()

    print()
    if success:
        print("🎉 测试完成！请检查您的 X.com 账号确认发布。")
    else:
        print("⚠️  测试失败，请检查错误信息。")

    print()

if __name__ == '__main__':
    main()
