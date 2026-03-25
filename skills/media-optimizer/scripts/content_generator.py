#!/usr/bin/env python3
"""
Media Optimizer - Content Generator
AI 驱动的内容生成引擎
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# Obsidian 知识库路径
OBSIDIAN_VAULT = "/Users/ainightcoder/Documents/Git/Note"
PROJECT_SELFMEDIA = f"{OBSIDIAN_VAULT}/2.Project/SelfMedia/04.Resource"

class ContentGenerator:
    """内容生成器"""

    # 隐私保护规则
    PRIVACY_RULES = {
        'forbidden_names': ['高健'],
        'preferred_name': '夜码人',
        'forbidden_companies': ['沈阳美嘉信息科技股份有限公司'],
        'forbidden_locations': ['辽宁省沈阳市', '沈阳', '东北大学'],
        'safe_locations': ['中国'],
    }

    def __init__(self):
        self.content_types = {
            'tutorial': '教程类',
            'opinion': '观点类',
            'news': '资讯类',
            'tools': '工具类',
            'story': '故事类'
        }

    def check_privacy(self, content):
        """隐私检查 - 确保不泄露敏感信息

        Returns: (is_safe, violations)
            is_safe: bool - 是否通过隐私检查
            violations: list - 违规项列表
        """
        violations = []

        # 检查禁用姓名
        for name in self.PRIVACY_RULES['forbidden_names']:
            if name in content:
                violations.append(f"包含禁用姓名: {name}")

        # 检查禁用公司
        for company in self.PRIVACY_RULES['forbidden_companies']:
            if company in content:
                violations.append(f"包含禁用公司: {company}")

        # 检查禁用地点
        for location in self.PRIVACY_RULES['forbidden_locations']:
            if location in content:
                violations.append(f"包含禁用地点: {location}")

        # 检查是否使用了首选称呼
        if self.PRIVACY_RULES['preferred_name'] not in content and '我' in content:
            # 如果内容用"我"自称，应该包含首选称呼
            violations.append(f"应使用首选称呼: {self.PRIVACY_RULES['preferred_name']}")

        is_safe = len(violations) == 0
        return is_safe, violations

    def apply_privacy_fix(self, content):
        """自动应用隐私修复 - 替换敏感信息"""
        fixed_content = content

        # 替换禁用姓名
        for name in self.PRIVACY_RULES['forbidden_names']:
            fixed_content = fixed_content.replace(name, self.PRIVACY_RULES['preferred_name'])

        # 替换禁用地点
        for location in self.PRIVACY_RULES['forbidden_locations']:
            fixed_content = fixed_content.replace(location, '中国')

        # 替换禁用公司
        for company in self.PRIVACY_RULES['forbidden_companies']:
            fixed_content = fixed_content.replace(company, '某科技公司')

        return fixed_content
        
    def scan_obsidian(self, limit=10):
        """扫描 Obsidian 知识库获取素材"""
        print(f"🔍 扫描知识库: {OBSIDIAN_VAULT}")
        
        # 扫描项目目录
        project_dir = f"{OBSIDIAN_VAULT}/2.Project"
        materials = []
        
        for project in os.listdir(project_dir):
            project_path = f"{project_dir}/{project}"
            if os.path.isdir(project_path):
                # 查找 README 和主要笔记
                for file in os.listdir(project_path):
                    if file.endswith('.md') and not file.startswith('.'):
                        materials.append({
                            'project': project,
                            'file': file,
                            'path': f"{project_path}/{file}"
                        })
                        
        print(f"✅ 找到 {len(materials)} 个素材")
        return materials[:limit]
    
    def generate_from_note(self, note_path, content_type='opinion'):
        """从笔记生成内容"""
        print(f"📝 读取笔记: {note_path}")
        
        if not os.path.exists(note_path):
            print(f"❌ 文件不存在: {note_path}")
            return None
            
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取标题和正文
        lines = content.split('\n')
        title = lines[0].replace('#', '').strip()
        body = '\n'.join(lines[1:])
        
        # 生成内容卡片
        content_card = {
            'id': f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'title': title,
            'type': content_type,
            'source': note_path,
            'created_at': datetime.now().isoformat(),
            'platforms': {}
        }
        
        print(f"✅ 内容卡片已生成: {title}")
        return content_card
    
    def adapt_for_platform(self, content_card, platform):
        """为特定平台适配内容"""
        title = content_card['title']
        
        if platform == 'twitter':
            # X.com: 140字以内
            adapted = f"""
{title[:100]}...

作为独立开发者，分享我的实战经验✨

#独立开发 #AI #自动化
"""
            content_card['platforms']['twitter'] = adapted.strip()
            
        elif platform == 'zhihu':
            # 知乎: 深度长文
            adapted = f"""
# {title}

## 摘要
作为独立开发者，我在实践中总结的经验...

## 正文
（展开详细内容）

## 总结
（核心观点）
"""
            content_card['platforms']['zhihu'] = adapted.strip()
            
        elif platform == 'xiaohongshu':
            # 小红书: 种草风格
            adapted = f"""
{title} 😱

姐妹们！作为独立开发者，今天分享一个超实用的经验...

【核心要点】
✨ 要点1
✨ 要点2
✨ 要点3

【效果】
真的很有用！

#独立开发 #程序员 #干货分享
"""
            content_card['platforms']['xiaohongshu'] = adapted.strip()
        
        print(f"✅ 已适配 {platform} 平台")
        return content_card
    
    def save_to_queue(self, content_card):
        """保存到内容队列"""
        queue_file = f"{PROJECT_SELFMEDIA}/01.CMS/内容队列.md"
        
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        
        # 追加到队列文件
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## [{content_card['id']}] {content_card['title']}\n")
            f.write(f"- **类型**: {content_card['type']}\n")
            f.write(f"- **创建时间**: {content_card['created_at']}\n")
            f.write(f"- **状态**: 待发布\n")
            f.write(f"- **平台**: {', '.join(content_card['platforms'].keys())}\n")
            f.write(f"\n### 内容摘要\n")
            f.write(f"...\n")
            f.write(f"\n---\n")
        
        print(f"✅ 已保存到内容队列")
        return True

def main():
    """主函数"""
    generator = ContentGenerator()
    
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  python content_generator.py --scan-obsidian")
        print("  python content_generator.py --generate <note_path>")
        print("  python content_generator.py --adapt <content_id> <platform>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--scan-obsidian':
        # 扫描知识库
        materials = generator.scan_obsidian(limit=5)
        for i, material in enumerate(materials, 1):
            print(f"{i}. [{material['project']}] {material['file']}")
    
    elif command == '--generate':
        # 从笔记生成内容
        if len(sys.argv) < 3:
            print("❌ 请指定笔记路径")
            sys.exit(1)
        
        note_path = sys.argv[2]
        content_card = generator.generate_from_note(note_path)
        
        if content_card:
            # 适配所有平台
            for platform in ['twitter', 'zhihu', 'xiaohongshu']:
                generator.adapt_for_platform(content_card, platform)
            
            # 保存到队列
            generator.save_to_queue(content_card)
            print(f"\n✅ 内容生成完成: {content_card['id']}")
    
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
