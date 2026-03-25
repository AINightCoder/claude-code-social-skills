#!/usr/bin/env python3
"""
Business Partner - Task Manager
任务管理：创建、分配、追踪、验收任务
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = SKILL_DIR / "workspace"
TASKS_DIR = WORKSPACE_DIR / "tasks"
GOALS_DIR = WORKSPACE_DIR / "goals"

class TaskManager:
    """任务管理器"""

    PRIORITY_LEVELS = {
        'P0': '今天必须完成',
        'P1': '本周完成',
        'P2': '本月完成'
    }

    def __init__(self):
        self.tasks_file = TASKS_DIR / "daily_tasks.json"
        self.history_file = TASKS_DIR / "task_history.json"
        self._load_tasks()

    def _load_tasks(self):
        """加载任务数据"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
        else:
            self.tasks = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'tasks': []
            }

        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def _save_tasks(self):
        """保存任务数据"""
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def create_task(self, title, priority='P1', estimate_hours=2, description=''):
        """创建新任务

        Args:
            title: 任务标题
            priority: 优先级 (P0/P1/P2)
            estimate_hours: 预估工时
            description: 任务描述
        """
        task = {
            'id': f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'title': title,
            'priority': priority,
            'estimate_hours': estimate_hours,
            'description': description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'assigned_to': '夜码人',
            'deadline': None,
            'started_at': None,
            'completed_at': None,
            'actual_hours': None,
            'notes': []
        }

        self.tasks['tasks'].append(task)
        self._save_tasks()

        print(f"✅ 任务已创建: [{task['id']}] {task['title']}")
        return task

    def assign_deadline(self, task_id, deadline_hours=None):
        """设定任务截止时间

        Args:
            task_id: 任务ID
            deadline_hours: 截止时间（小时），默认为今日23:59
        """
        task = self._find_task(task_id)
        if not task:
            print(f"❌ 任务不存在: {task_id}")
            return

        if deadline_hours:
            deadline = datetime.now() + timedelta(hours=deadline_hours)
        else:
            # 默认今日23:59
            deadline = datetime.now().replace(hour=23, minute=59, second=59)

        task['deadline'] = deadline.isoformat()
        self._save_tasks()

        print(f"✅ 截止时间已设定: {task['title']} -> {deadline.strftime('%H:%M')}")

    def start_task(self, task_id):
        """开始任务"""
        task = self._find_task(task_id)
        if not task:
            print(f"❌ 任务不存在: {task_id}")
            return

        task['status'] = 'in_progress'
        task['started_at'] = datetime.now().isoformat()
        self._save_tasks()

        print(f"▶️  任务开始: {task['title']}")

    def complete_task(self, task_id, actual_hours=None, notes=''):
        """完成任务"""
        task = self._find_task(task_id)
        if not task:
            print(f"❌ 任务不存在: {task_id}")
            return

        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()
        task['actual_hours'] = actual_hours

        if notes:
            task['notes'].append({
                'time': datetime.now().isoformat(),
                'content': notes
            })

        self._save_tasks()

        print(f"✅ 任务完成: {task['title']}")

        # 移入历史记录
        self._archive_task(task)

    def add_note(self, task_id, note):
        """添加任务备注"""
        task = self._find_task(task_id)
        if not task:
            print(f"❌ 任务不存在: {task_id}")
            return

        task['notes'].append({
            'time': datetime.now().isoformat(),
            'content': note
        })
        self._save_tasks()

        print(f"📝 备注已添加: {task['title']}")

    def _find_task(self, task_id):
        """查找任务"""
        for task in self.tasks['tasks']:
            if task['id'] == task_id:
                return task
        return None

    def _archive_task(self, task):
        """归档已完成任务"""
        # 添加到历史
        self.history.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'task': task
        })

        # 从当前任务列表移除
        self.tasks['tasks'] = [t for t in self.tasks['tasks'] if t['id'] != task['id']]
        self._save_tasks()

    def list_tasks(self, status=None, priority=None):
        """列出任务"""
        tasks = self.tasks['tasks']

        if status:
            tasks = [t for t in tasks if t['status'] == status]

        if priority:
            tasks = [t for t in tasks if t['priority'] == priority]

        # 按优先级排序
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
        tasks.sort(key=lambda t: priority_order.get(t['priority'], 3))

        if not tasks:
            print("📋 暂无任务")
            return

        print(f"📋 任务列表 ({len(tasks)}个)")
        print()

        for i, task in enumerate(tasks, 1):
            status_icon = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }.get(task['status'], '❓')

            print(f"{i}. {status_icon} [{task['priority']}] {task['title']}")
            print(f"   预估: {task['estimate_hours']}h")

            if task['deadline']:
                deadline = datetime.fromisoformat(task['deadline'])
                print(f"   截止: {deadline.strftime('%H:%M')}")

            if task['status'] == 'in_progress' and task['started_at']:
                started = datetime.fromisoformat(task['started_at'])
                elapsed = (datetime.now() - started).total_seconds() / 3600
                print(f"   已用: {elapsed:.1f}h")

            print()

    def get_daily_summary(self):
        """获取每日总结"""
        tasks = self.tasks['tasks']

        total = len(tasks)
        completed = len([t for t in tasks if t['status'] == 'completed'])
        in_progress = len([t for t in tasks if t['status'] == 'in_progress'])
        pending = len([t for t in tasks if t['status'] == 'pending'])

        total_estimate = sum(t['estimate_hours'] for t in tasks)
        completed_actual = sum(t['actual_hours'] or 0 for t in tasks if t['status'] == 'completed')

        print("📊 今日任务总结")
        print("=" * 60)
        print(f"总任务数: {total}")
        print(f"✅ 已完成: {completed}")
        print(f"🔄 进行中: {in_progress}")
        print(f"⏳ 待开始: {pending}")
        print()
        print(f"预估总工时: {total_estimate}h")
        print(f"实际已用: {completed_actual:.1f}h")
        print("=" * 60)

        # 检查逾期任务
        now = datetime.now()
        overdue = [t for t in tasks if t['deadline'] and datetime.fromisoformat(t['deadline']) < now and t['status'] != 'completed']

        if overdue:
            print()
            print("⚠️  逾期任务:")
            for task in overdue:
                deadline = datetime.fromisoformat(task['deadline'])
                print(f"   - {task['title']} (截止: {deadline.strftime('%H:%M')})")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python task_manager.py create <标题> [--priority P0|P1|P2] [--hours N]")
        print("  python task_manager.py list [--status pending|in_progress|completed]")
        print("  python task_manager.py start <task_id>")
        print("  python task_manager.py complete <task_id> [--hours N] [--notes 备注]")
        print("  python task_manager.py summary")
        sys.exit(1)

    manager = TaskManager()
    command = sys.argv[1]

    if command == 'create':
        if len(sys.argv) < 3:
            print("❌ 请提供任务标题")
            sys.exit(1)

        title = sys.argv[2]
        priority = '--priority' in sys.argv and sys.argv[sys.argv.index('--priority') + 1] or 'P1'
        hours = '--hours' in sys.argv and int(sys.argv[sys.argv.index('--hours') + 1]) or 2

        task = manager.create_task(title, priority, hours)
        print(f"\n任务ID: {task['id']}")
        print(f"使用此ID来 start/complete 任务")

    elif command == 'list':
        status = '--status' in sys.argv and sys.argv[sys.argv.index('--status') + 1] or None
        manager.list_tasks(status=status)

    elif command == 'start':
        if len(sys.argv) < 3:
            print("❌ 请提供任务ID")
            sys.exit(1)

        manager.start_task(sys.argv[2])

    elif command == 'complete':
        if len(sys.argv) < 3:
            print("❌ 请提供任务ID")
            sys.exit(1)

        hours = '--hours' in sys.argv and int(sys.argv[sys.argv.index('--hours') + 1]) or None
        notes = '--notes' in sys.argv and sys.argv[sys.argv.index('--notes') + 1] or ''

        manager.complete_task(sys.argv[2], hours, notes)

    elif command == 'summary':
        manager.get_daily_summary()

    else:
        print(f"❌ 未知命令: {command}")

if __name__ == '__main__':
    main()
