#!/usr/bin/env python3
"""
Media Optimizer - Test Script
测试 AI 自媒体运营系统
"""

import os
import sys
from datetime import datetime

# 添加脚本路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from content_generator import ContentGenerator
from auto_publisher import AutoPublisher
from data_analytics import DataAnalytics

def test_content_generation():
    """测试内容生成"""
    print("=" * 60)
    print("🧪 测试 1: 内容生成")
    print("=" * 60)
    print()
    
    generator = ContentGenerator()
    
    # 测试扫描知识库
    print("📂 测试：扫描 Obsidian 知识库")
    materials = generator.scan_obsidian(limit=3)
    print(f"✅ 找到 {len(materials)} 个素材")
    for i, material in enumerate(materials, 1):
        print(f"   {i}. [{material['project']}] {material['file']}")
    print()
    
    # 测试生成内容
    if materials:
        print("✍️  测试：生成内容卡片")
        material = materials[0]
        content_card = generator.generate_from_note(material['path'], 'tutorial')
        
        if content_card:
            print(f"✅ 内容卡片已生成")
            print(f"   ID: {content_card['id']}")
            print(f"   标题: {content_card['title']}")
            print(f"   类型: {content_card['type']}")
            print()
            
            # 测试平台适配
            print("🔄 测试：平台适配")
            for platform in ['twitter', 'zhihu', 'xiaohongshu']:
                generator.adapt_for_platform(content_card, platform)
            
            print(f"✅ 已适配 {len(content_card['platforms'])} 个平台")
            print()
            
            # 保存到队列
            print("💾 测试：保存到内容队列")
            generator.save_to_queue(content_card)
            print()
    
    return True

def test_auto_publisher():
    """测试自动发布"""
    print("=" * 60)
    print("🧪 测试 2: 自动发布")
    print("=" * 60)
    print()
    
    publisher = AutoPublisher()
    
    # 测试检查 browser 连接
    print("🔗 测试：检查 Browser 连接")
    connected = publisher.check_browser_connection()
    print()
    
    # 测试模拟发布
    print("📤 测试：模拟发布到 X.com")
    test_content = "这是一条测试推文！用 Media Optimizer 自动发布 🚀 #独立开发 #AI"
    result = publisher.publish_to_twitter(test_content)
    print(f"   结果: {'成功' if result['success'] else '失败'}")
    print(f"   URL: {result.get('url', 'N/A')}")
    print()
    
    return True

def test_data_analytics():
    """测试数据分析"""
    print("=" * 60)
    print("🧪 测试 3: 数据分析")
    print("=" * 60)
    print()
    
    analytics = DataAnalytics()
    
    # 测试数据收集
    print("📊 测试：收集平台数据")
    for platform in ['twitter', 'zhihu', 'xiaohongshu']:
        data = analytics.collect_data(platform)
        print(f"   {platform}: {data}")
    print()
    
    # 测试生成每日报告
    print("📅 测试：生成每日报告")
    analytics.generate_daily_report()
    print()
    
    # 测试爆款分析
    print("🔥 测试：爆款分析")
    analytics.analyze_viral_content()
    print()
    
    return True

def main():
    """主测试函数"""
    print()
    print("🚀 Media Optimizer - 系统测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # 测试 1: 内容生成
    try:
        results['content_generation'] = test_content_generation()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['content_generation'] = False
    
    # 测试 2: 自动发布
    try:
        results['auto_publisher'] = test_auto_publisher()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['auto_publisher'] = False
    
    # 测试 3: 数据分析
    try:
        results['data_analytics'] = test_data_analytics()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['data_analytics'] = False
    
    # 打印测试总结
    print()
    print("=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print()
    
    for test, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test}: {status}")
    
    print()
    passed = sum(results.values())
    total = len(results)
    print(f"总计: {passed}/{total} 通过")
    print()
    
    if passed == total:
        print("🎉 所有测试通过！系统已就绪。")
    else:
        print("⚠️  部分测试失败，请检查错误。")
    
    print()
    print("=" * 60)
    print()

if __name__ == '__main__':
    main()
