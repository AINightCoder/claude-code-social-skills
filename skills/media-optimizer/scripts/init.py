#!/usr/bin/env python3
"""
Media Optimizer - Initialization Script
初始化 AI 自媒体运营系统
"""

import os
import sys
from datetime import datetime

# Obsidian 知识库路径
OBSIDIAN_VAULT = "/Users/ainightcoder/Documents/Git/Note"
PROJECT_SELFMEDIA = f"{OBSIDIAN_VAULT}/2.Project/SelfMedia/04.Resource"

def init_directories():
    """初始化目录结构"""
    print("📁 创建目录结构...")
    
    directories = [
        f"{PROJECT_SELFMEDIA}/01.CMS",
        f"{PROJECT_SELFMEDIA}/02.Platforms",
        f"{PROJECT_SELFMEDIA}/03.Automation",
        f"{PROJECT_SELFMEDIA}/04.Analytics",
        f"{PROJECT_SELFMEDIA}/05.Templates",
        f"{PROJECT_SELFMEDIA}/06.CRM",
        f"{PROJECT_SELFMEDIA}/07.Monetization"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print(f"\n✅ 目录结构创建完成\n")

def init_cms_files():
    """初始化 CMS 文件"""
    print("📝 初始化 CMS 文件...")
    
    # 素材库
    with open(f"{PROJECT_SELFMEDIA}/01.CMS/素材库.md", 'w', encoding='utf-8') as f:
        f.write("# 素材库\n\n")
        f.write("## 来源分类\n\n")
        f.write("### 知识库笔记\n")
        f.write("- [ ] 笔记1\n")
        f.write("- [ ] 笔记2\n\n")
        f.write("### 热点话题\n")
        f.write("- [ ] 热点1\n")
        f.write("- [ ] 热点2\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 01.CMS/素材库.md")
    
    # 内容队列
    with open(f"{PROJECT_SELFMEDIA}/01.CMS/内容队列.md", 'w', encoding='utf-8') as f:
        f.write("# 内容队列\n\n")
        f.write("## 待发布\n\n")
        f.write("暂无待发布内容\n\n")
        f.write("---\n")
        f.write("## 已完成\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 01.CMS/内容队列.md")
    
    # 已发布
    with open(f"{PROJECT_SELFMEDIA}/01.CMS/已发布.md", 'w', encoding='utf-8') as f:
        f.write("# 已发布内容\n\n")
        f.write("## 发布记录\n\n")
        f.write("暂无发布记录\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 01.CMS/已发布.md")
    
    # 草稿箱
    with open(f"{PROJECT_SELFMEDIA}/01.CMS/草稿箱.md", 'w', encoding='utf-8') as f:
        f.write("# 草稿箱\n\n")
        f.write("## 草稿列表\n\n")
        f.write("暂无草稿\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 01.CMS/草稿箱.md")
    
    print(f"\n✅ CMS 文件初始化完成\n")

def init_analytics_files():
    """初始化数据分析文件"""
    print("📊 初始化数据分析文件...")
    
    # 每日数据
    with open(f"{PROJECT_SELFMEDIA}/04.Analytics/每日数据.md", 'w', encoding='utf-8') as f:
        f.write("# 每日数据\n\n")
        f.write("## 数据记录\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 04.Analytics/每日数据.md")
    
    # 每周报告
    with open(f"{PROJECT_SELFMEDIA}/04.Analytics/每周报告.md", 'w', encoding='utf-8') as f:
        f.write("# 每周报告\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 04.Analytics/每周报告.md")
    
    # 爆款分析
    with open(f"{PROJECT_SELFMEDIA}/04.Analytics/爆款分析.md", 'w', encoding='utf-8') as f:
        f.write("# 爆款内容分析\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 04.Analytics/爆款分析.md")
    
    # A/B测试
    with open(f"{PROJECT_SELFMEDIA}/04.Analytics/A_B测试.md", 'w', encoding='utf-8') as f:
        f.write("# A/B 测试\n\n")
        f.write("## 测试计划\n\n")
        f.write("---\n")
        f.write(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"   ✅ 04.Analytics/A_B测试.md")
    
    print(f"\n✅ 数据分析文件初始化完成\n")

def print_summary():
    """打印初始化摘要"""
    print("=" * 60)
    print("🎉 Media Optimizer 初始化完成！")
    print("=" * 60)
    print()
    print("📁 项目目录:")
    print(f"   {PROJECT_SELFMEDIA}")
    print()
    print("🚀 下一步:")
    print("   1. 配置平台账号 (02.Platforms/)")
    print("   2. 生成内容 (scripts/content_generator.py)")
    print("   3. 自动发布 (scripts/auto_publisher.py)")
    print("   4. 查看数据 (scripts/data_analytics.py)")
    print()
    print("📖 文档:")
    print("   ~/.claude/skills/media-optimizer/SKILL.md")
    print()
    print("=" * 60)

def main():
    """主函数"""
    print()
    print("🚀 Media Optimizer - 初始化")
    print()
    
    # 初始化目录
    init_directories()
    
    # 初始化 CMS 文件
    init_cms_files()
    
    # 初始化数据分析文件
    init_analytics_files()
    
    # 打印摘要
    print_summary()
    
    print("✅ 系统已就绪！\n")

if __name__ == '__main__':
    main()
