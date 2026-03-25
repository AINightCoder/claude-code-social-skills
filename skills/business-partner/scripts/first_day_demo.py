#!/usr/bin/env python3
"""
Business Partner - First Day Demo
第一天演示：创建任务、分配任务、监督执行
"""

import sys
import os
from datetime import datetime

# 添加脚本路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from task_manager import TaskManager

def print_header(title):
    """打印标题"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()

def print_section(title):
    """打印章节"""
    print()
    print(f"## {title}")
    print("-" * 70)

def main():
    """第一天演示"""
    print_header("Business Partner - Day 1")

    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("🎯 目标: 90天内赚到第一笔钱")
    print()

    # Step 1: 创建今日任务
    print_section("Step 1: Spark 分配今日任务")

    manager = TaskManager()

    tasks = [
        {
            'title': '选定赚钱方向（从4个候选中选1个）',
            'priority': 'P0',
            'hours': 1,
            'description': '评估：AI语音助手 / Media Optimizer / 咨询 / 其他'
        },
        {
            'title': '制定MVP计划（核心功能≤3个）',
            'priority': 'P0',
            'hours': 1.5,
            'description': '明确技术栈、开发时间、验收标准'
        },
        {
            'title': '搭建项目骨架',
            'priority': 'P1',
            'hours': 2,
            'description': '初始化Git仓库、配置开发环境'
        }
    ]

    for task_info in tasks:
        task = manager.create_task(**task_info)
        # 设定截止时间（今日23:59）
        manager.assign_deadline(task['id'])

    print()
    print("✅ 已创建 3 个任务，截止时间：今日 23:59")

    # Step 2: 显示任务列表
    print_section("Step 2: 任务清单")

    manager.list_tasks()

    # Step 3: 开始第一个任务
    print_section("Step 3: 开始执行（模拟）")

    print("💡 提示：使用以下命令管理任务")
    print()
    print("开始任务:")
    print("  python task_manager.py start task_20260208200001")
    print()
    print("完成任务:")
    print("  python task_manager.py complete task_20260208200001 --hours 1.2 --notes '选定方向：AI语音助手'")
    print()
    print("查看进度:")
    print("  python task_manager.py list")
    print()

    # Step 4: 21:00提醒
    print_section("Step 4: 21:00 工作提醒（模拟）")

    print("⏰ Spark 主动提醒：")
    print()
    print("  夜码人，副业时间到了！")
    print()
    print("  📋 今日任务：")
    print("  1. [P0] 选定赚钱方向 ← 现在开始")
    print("  2. [P0] 制定MVP计划")
    print("  3. [P1] 搭建项目骨架")
    print()
    print("  💻 专注工作，我23:30来检查！")
    print()

    # Step 5: 23:30验收
    print_section("Step 5: 23:30 验收成果（模拟）")

    print("✅ 假设所有任务已完成，Spark验收：")
    print()
    manager.get_daily_summary()
    print()

    # Step 6: 明日计划
    print_section("Step 6: 明日任务预览")

    print("📝 明日任务（Spark会自动分配）：")
    print()
    print("1. [P0] MVP功能1：用户注册/登录（预估3小时）")
    print("2. [P0] MVP功能2：核心业务逻辑（预估4小时）")
    print("3. [P1] 编写技术文档（预估2小时）")
    print()

    # 总结
    print_section("✅ Day 1 完成")

    print("🎉 恭喜夜码人，第一天完美收官！")
    print()
    print("📈 今日成果：")
    print("  ✅ 选定赚钱方向")
    print("  ✅ 制定MVP计划")
    print("  ✅ 搭建项目骨架")
    print()
    print("🚀 明天继续加油！")
    print()
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
