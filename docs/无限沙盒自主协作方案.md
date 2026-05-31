# 无限沙盒自主协作方案

> **核心理念：** 不考虑token成本，无限沙盒，24小时自主联动，质量不塌方  
> **适用场景：** 追求极致速度，预算充足，2人团队+AI沙盒协作  
> **基于：** 6个AI专家从6种范式的深度探索

---

## 🎯 三个可落地方案（渐进式升级）

### 方案1：轻量级任务市场 ⭐⭐⭐⭐⭐

**定位：** 最小可行方案，今天2小时搭起来，立即可用

**核心思想：**
- GitHub Issues作为任务市场
- Python脚本每5分钟扫描，自动拉起/回收沙盒
- 沙盒自主认领任务，完成后自动触发下游
- 24小时无人值守运转

**为什么推荐：**
- ✅ 今天2小时就能搭起来
- ✅ 无需PostgreSQL、无需Go服务
- ✅ 只要GitHub + Python脚本 + Claude Code
- ✅ 完美适合2人团队起步

**技术栈：**
- GitHub Issues + Labels（任务队列）
- Python脚本（spawn_manager.py）
- GitHub Actions（CI/CD）
- Git分支（产物传递）
- Claude Code（AI沙盒）

---

### 方案2：中央编排器+DAG调度 ⭐⭐⭐⭐

**定位：** Week 2升级方案，适合任务依赖复杂的场景

**何时升级：**
- Week 2开始（阶段2+3，任务依赖变复杂）
- 已有PostgreSQL（MQTT服务用）
- 需要更强的质量保障

**新增能力：**
1. 复杂依赖管理（PostgreSQL存储任务DAG）
2. 接口契约锁定（Day 0定义所有接口）
3. 每日集成验收（17:00自动部署到测试设备）
4. 实时监控（Grafana仪表板）

**升级成本：** 1天（Day 7晚上或Day 8上午）

---

### 方案3：对抗式质量保障 ⭐⭐⭐

**定位：** 质量要求极高时的终极方案

**何时考虑：**
- Week 3发现质量问题频繁
- CI失败率>20%
- 需要极致质量保障

**对抗机制：**
- 生成沙盒 vs 审查沙盒 vs 测试沙盒 vs 红队沙盒
- 不同AI模型防止合谋
- 三层门禁（审查≥80分 + 测试覆盖率≥70% + 红队破坏性测试）

**搭建成本：** 3-5天（较高，不推荐2人团队）

---

## 📊 方案对比

| 维度 | 方案1 | 方案2 | 方案3 |
|------|-------|-------|-------|
| **搭建时间** | 2小时 | 1天 | 3-5天 |
| **复杂度** | 低 | 中 | 高 |
| **自主程度** | 高 | 极高 | 极高 |
| **质量保障** | 两层 | 三层 | 五层 |
| **适合阶段** | Week 1 | Week 2-3 | 质量要求极高 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 方案1详细实施指南

### 搭建步骤（2小时）

#### Step 1：创建GitHub仓库（15分钟）
```bash
# 已有仓库，添加Project看板
gh project create --title "AI沙盒任务看板" --owner YOUR_USERNAME
```

#### Step 2：创建17个Issues（30分钟）
```python
# scripts/create_issues.py
from github import Github

g = Github("YOUR_GITHUB_TOKEN")
repo = g.get_repo("YOUR_USERNAME/cell_proxy_ip")

issues = [
    # 阶段0：基础设施
    {"title": "T0.1 服务器环境配置", "labels": ["P0", "阶段0"], "deps": []},
    {"title": "T0.2 GitHub Actions Runner配置", "labels": ["P0", "阶段0"], "deps": []},
    {"title": "T0.3 PostgreSQL数据库搭建", "labels": ["P0", "阶段0"], "deps": []},
    {"title": "T0.4 MQTT调度服务核心", "labels": ["P0", "阶段0"], "deps": []},
    
    # 阶段1：MQTT核心
    {"title": "T1.1 设备端MQTT客户端", "labels": ["P0", "阶段1"], "deps": []},
    {"title": "T1.2 设备状态格式定义", "labels": ["P0", "阶段1"], "deps": ["T1.1"]},
    {"title": "T1.3 命令框架", "labels": ["P0", "阶段1"], "deps": ["T0.4", "T1.1"]},
    {"title": "T1.4 核心命令实现", "labels": ["P0", "阶段1"], "deps": ["T1.3"]},
    {"title": "T1.5 MQTT管理工具", "labels": ["P1", "阶段1"], "deps": ["T0.2"]},
    
    # 阶段2：双网卡切换
    {"title": "T2.0 双网卡路由验证", "labels": ["P0", "阶段2"], "deps": ["T1.1"]},
    {"title": "T2.1 路由配置脚本", "labels": ["P0", "阶段2"], "deps": ["T2.0"]},
    {"title": "T2.2 网络健康检测", "labels": ["P0", "阶段2"], "deps": ["T2.1"]},
    {"title": "T2.3 心跳服务", "labels": ["P0", "阶段2"], "deps": ["T2.2"]},
    {"title": "T2.4 自动故障切换", "labels": ["P0", "阶段2"], "deps": ["T2.1", "T2.3"]},
    {"title": "T2.5 路由优化", "labels": ["P1", "阶段2"], "deps": ["T2.4"]},
    
    # 阶段3：SIM卡管理
    {"title": "T3.1 SIM卡状态查询", "labels": ["P0", "阶段3"], "deps": ["T1.1"]},
    {"title": "T3.2 SIM卡切换命令", "labels": ["P0", "阶段3"], "deps": ["T3.1", "T1.4"]},
]

for issue in issues:
    labels = issue["labels"]
    if issue["deps"]:
        labels.append(f"blocked-by-{','.join(issue['deps'])}")
    
    body = f"""
## 任务描述
{issue['title']}

## 依赖任务
{', '.join(issue['deps']) if issue['deps'] else '无'}

## 验收标准
- [ ] 代码提交到feature分支
- [ ] 单元测试通过（覆盖率≥60%）
- [ ] CI编译通过
- [ ] 产物路径已记录
"""
    
    repo.create_issue(
        title=issue["title"],
        body=body,
        labels=labels
    )
    print(f"✅ 创建Issue: {issue['title']}")
```

#### Step 3：编写调度脚本（45分钟）
```python
# scripts/spawn_manager.py
import time
import os
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "YOUR_USERNAME/cell_proxy_ip"
MAX_SANDBOXES = 8
CHECK_INTERVAL = 300  # 5分钟

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def get_pending_tasks():
    """获取所有pending任务（无blocked-by标签）"""
    issues = repo.get_issues(state="open", labels=["P0"])
    pending = []
    for issue in issues:
        labels = [l.name for l in issue.labels]
        # 检查是否有blocked-by标签
        has_blocker = any(l.startswith("blocked-by-") for l in labels)
        # 检查是否已被认领
        in_progress = "in-progress" in labels
        
        if not has_blocker and not in_progress:
            pending.append(issue)
    return pending

def get_active_sandboxes():
    """获取所有活跃沙盒（通过in-progress标签）"""
    issues = repo.get_issues(state="open", labels=["in-progress"])
    return list(issues)

def spawn_sandbox(task_issue):
    """拉起新沙盒处理任务"""
    sandbox_id = f"sandbox-{int(time.time())}"
    
    # 标记任务为in-progress
    task_issue.add_to_labels("in-progress")
    task_issue.create_comment(f"🤖 {sandbox_id} 已认领此任务，开始工作...")
    
    print(f"🚀 拉起沙盒 {sandbox_id} 处理任务 {task_issue.title}")
    
    # TODO: 实际启动沙盒的代码
    # 可以通过subprocess调用claude-code CLI
    # 或者通过API创建新的Claude会话
    
    return sandbox_id

def check_completed_tasks():
    """检查已完成任务，解锁下游任务"""
    # 查找最近关闭的任务（最近1小时）
    import datetime
    since = datetime.datetime.now() - datetime.timedelta(hours=1)
    completed = repo.get_issues(state="closed", since=since)
    
    for completed_task in completed:
        # 提取任务ID（如 "T0.4"）
        task_id = completed_task.title.split()[0]
        
        # 查找所有被此任务阻塞的任务
        all_open = repo.get_issues(state="open")
        for issue in all_open:
            labels = [l.name for l in issue.labels]
            blocker_label = f"blocked-by-{task_id}"
            
            if blocker_label in labels:
                # 移除阻塞标签
                issue.remove_from_labels(blocker_label)
                issue.create_comment(
                    f"✅ 依赖任务 {task_id} 已完成，此任务已解锁，可以开始工作"
                )
                print(f"🔓 解锁任务 {issue.title}")

def main():
    print("🎯 AI沙盒调度器启动...")
    print(f"📊 最大并发沙盒数: {MAX_SANDBOXES}")
    print(f"⏱️  检查间隔: {CHECK_INTERVAL}秒")
    
    while True:
        try:
            print(f"\n{'='*60}")
            print(f"🔍 开始新一轮检查... {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 检查已完成任务，解锁下游
            check_completed_tasks()
            
            # 获取待处理任务和活跃沙盒
            pending_tasks = get_pending_tasks()
            active_sandboxes = get_active_sandboxes()
            
            print(f"📊 待处理任务: {len(pending_tasks)}")
            print(f"🤖 活跃沙盒: {len(active_sandboxes)}/{MAX_SANDBOXES}")
            
            # 如果任务积压且沙盒未满，拉起新沙盒
            if len(pending_tasks) > 0 and len(active_sandboxes) < MAX_SANDBOXES:
                tasks_to_spawn = min(
                    len(pending_tasks),
                    MAX_SANDBOXES - len(active_sandboxes)
                )
                
                print(f"🚀 准备拉起 {tasks_to_spawn} 个新沙盒...")
                
                for i in range(tasks_to_spawn):
                    spawn_sandbox(pending_tasks[i])
                    time.sleep(2)  # 避免并发冲突
            else:
                print("✅ 当前无需拉起新沙盒")
            
            # 等待下一次检查
            print(f"⏳ 等待 {CHECK_INTERVAL} 秒后进行下一次检查...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 收到退出信号，调度器停止")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            print("⏳ 60秒后重试...")
            time.sleep(60)

if __name__ == "__main__":
    main()
```

#### Step 4：配置CI/CD（30分钟）
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  pull_request:
    branches: [dev, main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      
      - name: Install dependencies
        run: |
          cd mqtt-dispatcher
          go mod download
      
      - name: Run linter
        run: |
          go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
          golangci-lint run ./...
      
      - name: Run unit tests
        run: |
          go test -v -coverprofile=coverage.out ./...
          go tool cover -func=coverage.out
      
      - name: Check coverage
        run: |
          coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "测试覆盖率: $coverage%"
          if (( $(echo "$coverage < 60" | bc -l) )); then
            echo "❌ 测试覆盖率 $coverage% < 60%"
            exit 1
          fi
          echo "✅ 测试覆盖率 $coverage% >= 60%"
      
      - name: Build for RV1103
        run: |
          GOOS=linux GOARCH=arm64 go build -o mqtt-dispatcher-arm64 ./cmd/dispatcher
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: mqtt-dispatcher-arm64
          path: mqtt-dispatcher-arm64
```

#### Step 5：启动调度器（10分钟）
```bash
# 安装依赖
pip install PyGithub

# 设置环境变量
export GITHUB_TOKEN="your_github_token"

# 创建日志目录
mkdir -p logs

# 启动调度器（后台运行）
nohup python scripts/spawn_manager.py > logs/spawn_manager.log 2>&1 &

# 查看日志
tail -f logs/spawn_manager.log
```

---

## 📋 24小时运转示例

### Day 1 完整流程

**09:00 - 人类启动**
- 创建17个Issues，标记依赖关系
- 启动spawn_manager.py调度器
- 调度器检测到4个无依赖任务（T0.1-T0.4）

**09:05 - 首批沙盒拉起**
- 拉起4个沙盒（Sandbox-1到4）
- 各自认领任务，开始工作

**10:30 - 第一个任务完成**
- Sandbox-1完成T0.4（MQTT调度服务）
- 提交PR，CI自动运行
- 测试通过，自动合并到dev分支
- 在Issue中评论产物路径，关闭Issue

**10:35 - 自动解锁下游**
- 调度器检测到T0.4完成
- 自动移除T1.3的"blocked-by-T0.4"标签
- T1.3变为pending状态

**10:40 - 沙盒接力**
- Sandbox-1空闲，调度器分配T1.3
- Sandbox-1 git merge feature/T0.4，开始开发命令框架

**12:00 - 任务积压**
- 待处理任务增加到6个
- 调度器检测到积压，拉起Sandbox-5和6

**18:00 - 人类下班**
- 调度器继续运行
- 沙盒继续工作

**23:00 - 夜间完成**
- Sandbox-2完成T0.2
- CI通过，自动合并
- 触发下游任务T1.5进入pending

**次日09:00 - 人类上班**
- 查看进度：昨晚完成3个任务
- 当前4个任务进行中
- 整体进度符合预期

---

## 🎯 推荐路径

### Week 1（Day 1-7）：方案1
- 2小时搭建，立即可用
- 重点跑通MQTT核心功能
- 验证AI沙盒协作模式

### Week 2（Day 8-14）：升级到方案2
- 1天升级，平滑过渡
- 应对复杂任务依赖
- 加强质量保障

### Week 3（Day 15-20）：按需考虑方案3
- 仅在质量问题频繁时考虑
- 搭建成本高，谨慎评估

---

## 💡 关键成功因素

### 1. 接口先行
- Day 0定义所有模块接口
- 锁定接口，沙盒只能实现
- 避免集成时接口不匹配

### 2. 渐进集成
- 每完成3个任务触发小集成
- 避免积累到最后才发现问题
- 快速反馈，快速修复

### 3. 质量门禁
- 单元测试覆盖率≥60%
- CI自动检查，失败拒绝合并
- 每日集成验收

### 4. 人工抽查
- 每天早会Review昨晚产出
- 每完成5个P0任务暂停Review
- 避免方向性错误累积

---

## 🚀 立即开始

**今天下午（2小时）：**
1. ✅ 创建GitHub Project看板
2. ✅ 创建17个Issues
3. ✅ 编写spawn_manager.py
4. ✅ 配置GitHub Actions
5. ✅ 启动调度器

**明天会议：**
- 展示给技术同事
- 确认技术方案
- 开始Day 1开发

**祝你成功！** 🎉
