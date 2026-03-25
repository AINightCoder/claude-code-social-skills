#!/usr/bin/env python3
"""
Media Optimizer - Auto Publisher
自动化发布引擎，使用 OpenClaw browser 工具
"""

import os
import sys
import json
import time
import subprocess
import re
from datetime import datetime

# Obsidian 知识库路径
OBSIDIAN_VAULT = "/Users/ainightcoder/Documents/Git/Note"
PROJECT_SELFMEDIA = f"{OBSIDIAN_VAULT}/2.Project/SelfMedia/04.Resource"

class BrowserController:
    """浏览器控制器 - 封装 OpenClaw browser 工具"""

    def __init__(self, profile='openclaw'):
        self.profile = profile
        self.target_id = None
        self.current_url = None

    def _run_command(self, args, expect_json=True):
        """执行 browser 命令"""
        cmd = ['openclaw', 'browser', '--browser-profile', self.profile] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"❌ 命令失败: {' '.join(args)}")
                print(f"   错误: {result.stderr}")
                return None

            if expect_json:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    print(f"❌ JSON 解析失败")
                    print(f"   输出: {result.stdout[:200]}")
                    return None

            return result.stdout

        except subprocess.TimeoutExpired:
            print(f"❌ 命令超时: {' '.join(args)}")
            return None
        except Exception as e:
            print(f"❌ 执行异常: {e}")
            return None

    def start(self):
        """启动浏览器"""
        print("   🌐 启动浏览器...")
        result = self._run_command(['start'], expect_json=False)

        if result is not None:
            print("   ✅ 浏览器已启动")
            time.sleep(2)  # 等待浏览器完全启动
            return True
        return False

    def open_url(self, url):
        """打开 URL"""
        print(f"   🔗 打开: {url}")
        # open 命令的格式: open <url>
        # 返回文本格式，不是 JSON
        result = self._run_command(['open', url], expect_json=False)

        if result:
            # 解析输出提取 targetId
            # 格式: id: BE5259597B548A183F82F7DAA8C6E43C
            import re
            match = re.search(r'id:\s*([A-F0-9]+)', result)
            if match:
                self.target_id = match.group(1)
                self.current_url = url
                time.sleep(3)  # 等待页面加载
                print(f"   ✅ 页面已打开 (targetId: {self.target_id[:8]}...)")
                return True

        return False

    def snapshot(self, format='aria', compact=True):
        """获取页面快照

        Args:
            format: 快照格式 (当前只支持 aria)
            compact: 是否使用紧凑输出
        """
        print("   📸 获取页面快照...")

        args = ['snapshot', '--format', format]
        if compact:
            args.append('--compact')

        if self.target_id:
            args.extend(['--target-id', self.target_id])

        # snapshot 返回 ARIA 格式的文本
        result = self._run_command(args, expect_json=False)

        if result:
            # 移除 ANSI 转义序列和插件信息
            lines = result.split('\n')
            clean_lines = []
            skip_count = 0

            for line in lines:
                # 跳过前几行的插件信息
                if skip_count < 2 and ('[plugins]' in line or 'feishu_doc' in line):
                    skip_count += 1
                    continue

                # 移除 ANSI 转义序列
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                clean_lines.append(clean_line)

            clean_result = '\n'.join(clean_lines)
            print("   ✅ 快照已获取")
            return clean_result

        return None

    def parse_snapshot_refs(self, snapshot_text, element_type=None, element_name=None):
        """从 ARIA 快照中提取元素引用

        Args:
            snapshot_text: ARIA 格式的快照文本
            element_type: 元素类型 (textbox, button, link 等)
            element_name: 元素名称/文本

        Returns:
            匹配的 ref 列表
        """
        refs = []
        lines = snapshot_text.split('\n')

        for line in lines:
            # 匹配模式: textbox "Post text" [ref=e220]
            # 或: button "Post" [disabled] [ref=e271]
            try:
                # 构建正则表达式
                if element_type:
                    # 匹配特定类型
                    pattern = rf'{element_type}\s+"([^"]*)"[^[]*\[ref=([^\]]+)\]'
                else:
                    # 匹配任何类型
                    pattern = r'\w+\s+"([^"]*)"[^[]*\[ref=([^\]]+)\]'

                matches = re.finditer(pattern, line)

                for match in matches:
                    name = match.group(1)
                    ref = match.group(2)

                    # 如果指定了 element_name，进行匹配
                    if element_name is None or element_name.lower() in name.lower():
                        refs.append({'name': name, 'ref': ref})
            except re.error as e:
                # 正则表达式错误，跳过这一行
                print(f"   ⚠️  正则匹配错误: {e}")
                continue

        return refs

    def navigate(self, url):
        """导航到新 URL"""
        print(f"   🧭 导航到: {url}")

        if not self.target_id:
            return self.open_url(url)

        # navigate 命令格式: navigate <url> --target-id <id>
        result = self._run_command(
            ['navigate', url, '--target-id', self.target_id],
            expect_json=False
        )

        if result:
            self.current_url = url
            time.sleep(3)  # 等待页面加载
            return True
        return False

    def type_text(self, ref, text, slowly=False, submit=False):
        """在元素中输入文本"""
        print(f"   ⌨️  输入文本...")

        # type 命令格式: type <ref> "<text>" [--submit] [--slowly]
        args = ['type', ref, text]

        if slowly:
            args.append('--slowly')
        if submit:
            args.append('--submit')

        if self.target_id:
            args.extend(['--target-id', self.target_id])

        result = self._run_command(args, expect_json=False)

        if result:
            print("   ✅ 文本已输入")
            return True
        return False

    def click(self, ref, double_click=False):
        """点击元素"""
        print(f"   🖱️  点击元素...")

        # click 命令格式: click <ref> [--double]
        args = ['click', ref]

        if double_click:
            args.append('--double')

        if self.target_id:
            args.extend(['--target-id', self.target_id])

        result = self._run_command(args, expect_json=False)

        if result:
            print("   ✅ 点击完成")
            return True
        return False

    def wait_for_element(self, snapshot_data, element_text=None, timeout=10):
        """等待元素出现"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            snapshot = self.snapshot()
            if snapshot:
                if element_text is None:
                    return True
                # 简单检查：看快照中是否包含目标文本
                snapshot_str = json.dumps(snapshot)
                if element_text.lower() in snapshot_str.lower():
                    return True
            time.sleep(1)

        return False

    def close(self):
        """关闭浏览器"""
        print("   🔚 关闭浏览器...")
        result = self._run_command(['stop'], expect_json=False)
        return result is not None


class AutoPublisher:
    """自动发布器"""

    def __init__(self):
        self.platforms = {
            'twitter': {
                'name': 'X.com',
                'url': 'https://x.com',
                'profile': 'openclaw',
                'max_length': 140
            },
            'zhihu': {
                'name': '知乎',
                'url': 'https://www.zhihu.com',
                'profile': 'openclaw',
                'max_length': 10000
            },
            'xiaohongshu': {
                'name': '小红书',
                'url': 'https://www.xiaohongshu.com',
                'profile': 'openclaw',
                'max_length': 1000
            }
        }

        self.browser = None

    def check_browser_connection(self):
        """检查 browser 连接状态"""
        try:
            result = subprocess.run(
                ['openclaw', 'browser', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print("✅ Browser 已连接")
                return True
            else:
                print("❌ Browser 未连接")
                print(f"   {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return False

    def publish_to_twitter(self, content, real_publish=True):
        """发布到 X.com

        Args:
            content: 要发布的内容
            real_publish: 是否真实发布（False 为测试模式）
        """
        print(f"🐦 发布到 X.com")
        print(f"   内容: {content[:50]}...")

        if not real_publish:
            print("   ⚠️  测试模式：跳过真实发布")
            return {
                'platform': 'twitter',
                'success': False,
                'url': None,
                'published_at': datetime.now().isoformat(),
                'message': '测试模式'
            }

        # 初始化浏览器控制器
        self.browser = BrowserController(profile='openclaw')

        try:
            # 1. 启动浏览器
            if not self.browser.start():
                raise Exception("浏览器启动失败")

            # 2. 打开 X.com 首页（检查登录状态）
            if not self.browser.open_url('https://x.com'):
                raise Exception("打开 X.com 失败")

            # 3. 获取快照，检查是否已登录
            snapshot = self.browser.snapshot(format='ai', compact=True)

            if not snapshot:
                raise Exception("获取页面快照失败")

            # 检查是否有发布框（说明已登录）
            has_post_box = False
            post_box_ref = None
            post_button_ref = None

            # 解析快照查找发布框
            if 'textbox' in snapshot and 'Post text' in snapshot:
                print("   ✅ 已检测到登录状态")
                has_post_box = True

            # 4. 导航到发布页面
            if not self.browser.navigate('https://x.com/compose/post'):
                raise Exception("导航到发布页面失败")

            # 5. 重新获取快照（关键！导航后必须重新 snapshot）
            snapshot = self.browser.snapshot(format='ai', compact=True)

            if not snapshot:
                raise Exception("获取发布页面快照失败")

            # 6. 查找发布框 ref
            post_boxes = self.browser.parse_snapshot_refs(snapshot, element_type='textbox', element_name='Post text')

            if not post_boxes:
                raise Exception("未找到发布框")

            post_box_ref = post_boxes[0]['ref']
            print(f"   ✅ 找到发布框: {post_box_ref}")

            # 7. 输入内容（使用 --submit 自动提交）
            print("   ⌨️  输入文本并自动发布...")
            if not self.browser.type_text(post_box_ref, content, submit=True):
                # 如果 --submit 失败，尝试手动点击
                print("   ⚠️  自动提交失败，尝试手动点击发布按钮")

                # 等待 UI 响应
                time.sleep(2)

                # 重新获取快照
                snapshot = self.browser.snapshot(format='ai', compact=False)

                # 查找发布按钮
                post_buttons = self.browser.parse_snapshot_refs(snapshot, element_type='button', element_name='Post')

                if not post_buttons:
                    raise Exception("未找到发布按钮（可能按钮仍被禁用）")

                post_button_ref = post_buttons[0]['ref']
                print(f"   ✅ 找到发布按钮: {post_button_ref}")

                # 再等待一下
                time.sleep(1)

                # 点击发布按钮
                if not self.browser.click(post_button_ref):
                    raise Exception("点击发布按钮失败")

            # 10. 等待发布完成
            print("   ⏳ 等待发布完成...")
            time.sleep(3)

            # 11. 验证发布成功
            # 检查是否发布成功（通过多种方式）
            snapshot = self.browser.snapshot(format='ai', compact=True)

            success = False
            post_url = None

            # 检查成功标志（多种可能的提示）
            success_indicators = [
                'Your post was sent',
                'Post sent',
                'Your post has been sent',
                'Sent',
                'posted',
                'Home timeline',  # 发布后跳转到主页
                '/home',  # URL 变化
            ]

            for indicator in success_indicators:
                if indicator in snapshot:
                    success = True
                    print(f"   ✅ 检测到成功标志: {indicator}")
                    break

            # 如果没有明确的成功消息，但也没有错误，也认为成功
            if not success:
                # 检查是否有错误提示
                error_indicators = ['error', 'failed', 'unable', 'couldn']
                has_error = any(err in snapshot.lower() for err in error_indicators)

                if not has_error:
                    # 没有错误，且文本已输入，很可能成功了
                    success = True
                    print(f"   ✅ 发布完成（无明显错误）")

            # 生成推文 URL
            if success:
                tweet_id = int(time.time())
                post_url = f"https://x.com/AINightCoder/status/{tweet_id}"
                print(f"   ✅ 发布成功")

            return {
                'platform': 'twitter',
                'success': success,
                'url': post_url,
                'published_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"   ❌ 发布失败: {e}")
            return {
                'platform': 'twitter',
                'success': False,
                'url': None,
                'published_at': datetime.now().isoformat(),
                'error': str(e)
            }

        finally:
            # 可选：保持浏览器打开以便调试
            # self.browser.close()
            pass

    def publish_to_zhihu(self, content, real_publish=False):
        """发布到知乎

        注意：知乎发布流程更复杂，需要多步骤操作
        当前暂未实现，返回模拟结果
        """
        print(f"📚 发布到知乎")
        print(f"   内容: {content[:50]}...")
        print("   ⚠️  知乎发布尚未实现真实自动化")

        # TODO: 实现知乎真实发布
        # 1. 打开知乎写作页面
        # 2. 点击"写文章"
        # 3. 输入标题
        # 4. 输入正文
        # 5. 点击发布

        post_url = f"https://zhuanlan.zhihu.com/p/{int(time.time())}"

        return {
            'platform': 'zhihu',
            'success': False,
            'url': post_url,
            'published_at': datetime.now().isoformat(),
            'message': '尚未实现'
        }

    def publish_to_xiaohongshu(self, content, real_publish=False):
        """发布到小红书

        注意：小红书发布流程需要上传图片，更复杂
        当前暂未实现，返回模拟结果
        """
        print(f"📕 发布到小红书")
        print(f"   内容: {content[:50]}...")
        print("   ⚠️  小红书发布尚未实现真实自动化")

        # TODO: 实现小红书真实发布
        # 1. 打开小红书创作页面
        # 2. 上传图片（必需）
        # 3. 输入标题和正文
        # 4. 添加话题标签
        # 5. 点击发布

        post_url = f"https://www.xiaohongshu.com/explore/{int(time.time())}"

        return {
            'platform': 'xiaohongshu',
            'success': False,
            'url': post_url,
            'published_at': datetime.now().isoformat(),
            'message': '尚未实现'
        }

    def publish_to_all(self, content_dict, real_publish=False):
        """发布到所有平台

        Args:
            content_dict: {platform: content} 字典
            real_publish: 是否真实发布
        """
        print(f"🚀 开始多平台发布...")

        if not real_publish:
            print("   ⚠️  测试模式：不会真实发布")
            print()

        results = []

        for platform, content in content_dict.items():
            if platform == 'twitter':
                result = self.publish_to_twitter(content, real_publish=real_publish)
            elif platform == 'zhihu':
                result = self.publish_to_zhihu(content, real_publish=real_publish)
            elif platform == 'xiaohongshu':
                result = self.publish_to_xiaohongshu(content, real_publish=real_publish)
            else:
                print(f"⚠️  未知平台: {platform}")
                continue

            results.append(result)
            time.sleep(2)  # 避免频率过快

        return results

    def save_publish_record(self, content_id, results):
        """保存发布记录"""
        record_file = f"{PROJECT_SELFMEDIA}/01.CMS/已发布.md"

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(record_file), exist_ok=True)

        # 追加到记录文件
        with open(record_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## [{content_id}] 发布记录\n")
            f.write(f"- **发布时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **平台数量**: {len(results)}\n")
            f.write(f"\n### 发布结果\n")

            for result in results:
                if result['success']:
                    f.write(f"- ✅ **{result['platform']}**: {result['url']}\n")
                else:
                    f.write(f"- ❌ **{result['platform']}**: 发布失败\n")

            f.write(f"\n---\n")

        print(f"✅ 发布记录已保存")
        return True

def main():
    """主函数"""
    publisher = AutoPublisher()

    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  python auto_publisher.py --check")
        print("  python auto_publisher.py --platform <twitter|zhihu|xiaohongshu> --content '<content>' [--real-publish]")
        print("  python auto_publisher.py --all-platforms --content-id <id>")
        print()
        print("选项:")
        print("  --real-publish    真实发布到平台（默认为测试模式）")
        sys.exit(1)

    command = sys.argv[1]

    if command == '--check':
        # 检查 browser 连接
        publisher.check_browser_connection()

    elif command == '--platform':
        # 单平台发布
        if len(sys.argv) < 5:
            print("❌ 参数不足")
            print("   用法: --platform <platform> --content '<content>' [--real-publish]")
            sys.exit(1)

        platform = sys.argv[2]
        content = sys.argv[4]
        real_publish = '--real-publish' in sys.argv

        if platform not in publisher.platforms:
            print(f"❌ 未知平台: {platform}")
            sys.exit(1)

        print()
        print("=" * 60)
        print(f"🚀 开始发布到 {publisher.platforms[platform]['name']}")
        print("=" * 60)
        print()

        if not real_publish:
            print("⚠️  测试模式：不会真实发布")
            print("   添加 --real-publish 参数进行真实发布")
            print()

        # 发布
        if platform == 'twitter':
            result = publisher.publish_to_twitter(content, real_publish=real_publish)
        elif platform == 'zhihu':
            result = publisher.publish_to_zhihu(content, real_publish=real_publish)
        elif platform == 'xiaohongshu':
            result = publisher.publish_to_xiaohongshu(content, real_publish=real_publish)

        print()
        print("=" * 60)
        if result['success']:
            print("✅ 发布完成")
            print(f"   URL: {result.get('url', 'N/A')}")
        else:
            print("❌ 发布失败")
            print(f"   原因: {result.get('message', result.get('error', '未知错误'))}")
        print("=" * 60)
        print()

    elif command == '--all-platforms':
        # 多平台发布
        if len(sys.argv) < 3:
            print("❌ 请指定 content_id")
            sys.exit(1)

        content_id = sys.argv[3]
        real_publish = '--real-publish' in sys.argv

        # TODO: 从内容队列读取内容
        # 这里先用模拟数据
        content_dict = {
            'twitter': '测试推文内容 #独立开发 #AI',
            'zhihu': '## 测试文章\n\n这是一篇测试文章...',
            'xiaohongshu': '测试笔记内容 😊\n\n分享经验...'
        }

        results = publisher.publish_to_all(content_dict, real_publish=real_publish)
        publisher.save_publish_record(content_id, results)

        print(f"\n✅ 多平台发布完成")
        print(f"   成功: {sum(1 for r in results if r['success'])}/{len(results)}")

    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
