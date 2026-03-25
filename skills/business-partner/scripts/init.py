#!/usr/bin/env python3
"""
Business Partner - Initialization Script
初始化商业伙伴系统
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = SKILL_DIR / "workspace"
GOALS_DIR = WORKSPACE_DIR / "goals"
TASKS_DIR = WORKSPACE_DIR / "tasks"
REPORTS_DIR = WORKSPACE_DIR / "reports"
KPIS_DIR = WORKSPACE_DIR / "kpis"

def init_directories():
    """初始化目录结构"""
    print("📁 创建目录结构...")

    directories = [
        WORKSPACE_DIR,
        GOALS_DIR,
        TASKS_DIR,
        REPORTS_DIR,
        KPIS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory.relative_to(SKILL_DIR)}")

    print(f"\n✅ 目录结构创建完成\n")

def init_goal_file():
    """初始化目标文件"""
    print("🎯 创建90天冲刺目标...")

    goal_file = GOALS_DIR / "90_day_sprint.md"

    if not goal_file.exists():
        content = f"""# 90天冲刺目标

**开始时间**: {datetime.now().strftime('%Y-%m-%d')}
**结束时间**: {datetime.now().strftime('%Y-%m-%d')}（90天后）

---

## 🎯 大目标

**在90天内通过独立开发获得第一笔收入**

具体指标：
- ✅ 付费用户：5个
- ✅ 收入范围：$100-500
- ✅ 产品正式上线
- ✅ 100个注册用户

---

## 📊 里程碑

### Month 1: 方向 + MVP（Day 1-30）
- [ ] Week 1-2: 选定赚钱方向
- [ ] Week 3-4: 完成MVP核心功能

**KPI**:
- 选定1个方向
- MVP完成60%
- 技术栈确定

### Month 2: 完善 + 验证（Day 31-60）
- [ ] Week 5-8: 产品打磨
- [ ] 获取50个测试用户
- [ ] 优化核心流程

**KPI**:
- MVP完成100%
- 50个测试用户
- Beta版本上线

### Month 3: 上线 + 推广（Day 61-90）
- [ ] Week 9-12: 正式上线
- [ ] 市场推广
- [ ] 获取5个付费用户

**KPI**:
- 100个注册用户
- 5个付费用户
- 收入$100-500

---

## 💰 赚钱方向（待定）

**当前状态**: 未选定

**候选方向**：
1. AI语音助手（SaaS订阅）
2. Media Optimizer（工具/模板）
3. 独立开发咨询（知识变现）
4. _____（你来填）

**选定时间**: _____
**选定方向**: _____
**理由**: _____
---

## 📈 进度追踪

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

| 指标 | 目标 | 当前 | 进度 |
|------|------|------|------|
| 收入 | $100-500 | $0 | 0% |
| 付费用户 | 5 | 0 | 0% |
| 注册用户 | 100 | 0 | 0% |
| MVP进度 | 100% | 0% | 0% |

---

## 🚀 立即行动

**今天需要做**：
1. 评估4个赚钱方向
2. 选定1个方向
3. 制定MVP计划
4. 明确核心功能（≤3个）

**截止时间**: 今天23:00

---

**夜码人，90天倒计时开始！** ⏰
"""

        with open(goal_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"   ✅ workspace/goals/90_day_sprint.md")
    else:
        print(f"   ⚠️  目标文件已存在")

    print()

def init_kpi_tracker():
    """初始化KPI追踪文件"""
    print("📊 创建KPI追踪系统...")

    kpi_file = KPIS_DIR / "daily_kpis.md"

    if not kpi_file.exists():
        content = """# 每日KPI追踪

**开始日期**: _____
**当前日期**: _____
**冲刺天数**: Day 1 / 90

---

## 📊 核心KPI

### 收入指标
- 首笔收入时间: _____
- 当前月收入: $0
- 付费用户数: 0
- 客单价(ARPU): $0

### 产品指标
- MVP完成度: 0%
- 核心功能数: 0 / 3
- Bug修复数: 0
- 用户满意度: N/A

### 运营指标
- 自媒体粉丝: _____ / _____
- 内容发布数: 0
- 社区活跃度: N/A

### 个人效率
- 任务完成率: 0%
- 深度工作时长: 0h
- 代码提交数: 0
- 拖延次数: 0

---

## 📈 每日记录

### Day 1 (_____)
- 收入: $0
- 代码提交: _____
- 任务完成: _____ / _____
- 备注: _____

### Day 2 (_____)
- ...

---

## 🎯 趋势分析

**每周日更新**：

- Week 1 (Day 1-7): _____
- Week 2 (Day 8-14): _____
- ...

---

## 💡 经验教训

记录重要的决策、失败教训、成功经验：

---

"""
        with open(kpi_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"   ✅ workspace/kpis/daily_kpis.md")
    else:
        print(f"   ⚠️  KPI文件已存在")

    print()

def print_next_steps():
    """打印下一步行动"""
    print("=" * 60)
    print("🎉 Business Partner 系统初始化完成！")
    print("=" * 60)
    print()
    print("📋 下一步行动：")
    print()
    print("1. 🎯 设定90天目标")
    print("   编辑 workspace/goals/90_day_sprint.md")
    print()
    print("2. 💰 选定赚钱方向")
    print("   从4个候选方向中选1个")
    print()
    print("3. 📝 制定MVP计划")
    print("   明确核心功能（≤3个）")
    print()
    print("4. 🚀 开始第一天")
    print("   对Spark说：\"开始第一天\"")
    print()
    print("=" * 60)
    print("准备好了吗，夜码人？我们开始赚钱！💰")
    print("=" * 60)

def main():
    """主函数"""
    print()
    print("🚀 Business Partner - 初始化")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 初始化目录
    init_directories()

    # 初始化目标文件
    init_goal_file()

    # 初始化KPI系统
    init_kpi_tracker()

    # 打印下一步
    print_next_steps()

    print()

if __name__ == '__main__':
    main()
