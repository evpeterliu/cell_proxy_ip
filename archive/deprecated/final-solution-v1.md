# net终端方案一：最终实施方案（Superpower版）

> **项目：** RV1103 + EC600M 双卡net终端  
> **方案：** 分阶段实现（第一阶段：中转模式 + 远程管理）  
> **交付时间：** 30天  
> **文档版本：** v2.0 Final

---

## 🎯 执行摘要

### 核心目标

**解决当前最大痛点：** 手机卡断网后无法远程排查问题

**交付物：**
1. 稳定的IP代理服务（通过中转服务器）
2. 多通道远程访问能力（MQTT + frpc + RJ45）
3. 自动故障诊断系统
4. 完善的远程管理功能
5. OTA升级能力（为未来扩展做准备）

**成功标准：**
- ✅ 30天内部署到菲律宾10台设备
- ✅ 设备在线率 >95%
- ✅ 故障排查时间 <30分钟
- ✅ 远程管理成功率 >90%

---

## 📋 目录

1. [系统架构设计](#系统架构设计)
2. [核心功能详解](#核心功能详解)
3. [技术实现方案](#技术实现方案)
4. [30天开发计划](#30天开发计划)
5. [部署方案](#部署方案)
6. [监控和运维](#监控和运维)
7. [风险控制](#风险控制)
8. [成本分析](#成本分析)
9. [后期扩展路径](#后期扩展路径)

---

## 🏗️ 系统架构设计

### 整体架构图

```
                        互联网用户
                            │
                            │ SOCKS5代理请求
                            ▼
              ┌─────────────────────────┐
              │   香港中转服务器         │
              │   (Hetzner/Vultr)       │
              │                         │
              │  ┌──────────────────┐  │
              │  │ Nginx (1080)     │  │
              │  │ 负载均衡+限流     │  │
              │  └──────────────────┘  │
              │           │             │
              │  ┌────────▼─────────┐  │
              │  │ gost SOCKS5      │  │
              │  │ (代理服务)       │  │
              │  └──────────────────┘  │
              │           │             │
              │  ┌────────▼─────────┐  │
              │  │ frps (7000)      │  │
              │  │ (反向代理服务器)  │  │
              │  └──────────────────┘  │
              └─────────────────────────┘
                            │
                            │ frp隧道
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ net终端-001   │   │ net终端-002   │   │ net终端-N     │
│ (菲律宾)      │   │ (菲律宾)      │   │ (其他国家)    │
│               │   │               │   │               │
│ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │
│ │网络监控   │ │   │ │网络监控   │ │   │ │网络监控   │ │
│ │服务       │ │   │ │服务       │ │   │ │服务       │ │
│ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │
│ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │
│ │frpc客户端 │ │   │ │frpc客户端 │ │   │ │frpc客户端 │ │
│ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │
│ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │
│ │MQTT客户端 │ │   │ │MQTT客户端 │ │   │ │MQTT客户端 │ │
│ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │
│               │   │               │   │               │
│ ┌─────┬─────┐ │   │ ┌─────┬─────┐ │   │ ┌─────┬─────┐ │
│ │SIM1 │SIM2 │ │   │ │SIM1 │SIM2 │ │   │ │SIM1 │SIM2 │ │
│ │Globe│Smart│ │   │ │Globe│Smart│ │   │ │运营商│    │ │
│ └─────┴─────┘ │   │ └─────┴─────┘ │   │ └─────┴─────┘ │
│               │   │               │   │               │
│ ┌───────────┐ │   │ ┌───────────┐ │   │ ┌───────────┐ │
│ │RJ45 (备用)│ │   │ │RJ45 (备用)│ │   │ │RJ45 (备用)│ │
│ └───────────┘ │   │ └───────────┘ │   │ └───────────┘ │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   MQTT服务器 (菲律宾)    │
              │   (设备管理和监控)       │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   监控面板 (Grafana)     │
              │   (运维人员访问)         │
              └─────────────────────────┘
```

### 网络层次设计

**三层网络架构：**

```
┌─────────────────────────────────────────────────────────┐
│ 第1层：主网络（手机卡4G/5G）                             │
│ - 用途：代理流量出口                                     │
│ - 优先级：最高                                           │
│ - 接口：usb0 (EC600M 4G模块)                            │
│ - 路由：默认路由，metric 100                             │
└─────────────────────────────────────────────────────────┘
                            │
                            │ 故障时自动切换
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 第2层：备用网络（RJ45有线）                              │
│ - 用途：故障时的管理通道                                 │
│ - 优先级：中                                             │
│ - 接口：eth0                                            │
│ - 路由：策略路由，仅SSH流量                              │
└─────────────────────────────────────────────────────────┘
                            │
                            │ 双通道并行
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 第3层：管理通道（MQTT）                                  │
│ - 用途：设备管理和监控                                   │
│ - 优先级：最高（独立通道）                               │
│ - 协议：MQTT over TCP                                   │
│ - 特点：可通过任意网络连接                               │
└─────────────────────────────────────────────────────────┘
```

### 数据流向

**正常情况（手机卡在线）：**
```
用户 → 中转服务器 → frp隧道 → net终端(手机卡) → 目标网站
                                    │
                                    └→ MQTT → 监控系统
```

**故障情况（手机卡断网）：**
```
运维人员 → MQTT命令 → net终端(RJ45) → 执行诊断
                                    │
                                    └→ 上报结果 → 监控系统
```

---

## 🎯 核心功能详解

### 功能1：双网卡智能路由

**目标：** 手机卡和RJ45共存，自动切换

**实现原理：**

```bash
# 策略路由配置
# 1. 主路由表（手机卡）
ip route add default via <4G网关> dev usb0 metric 100

# 2. 备用路由表（RJ45）
ip route add default via <RJ45网关> dev eth0 table 200

# 3. 策略路由规则
# SSH流量可以走RJ45
ip rule add from <RJ45网段> table 200
ip rule add to <RJ45网段> table 200

# 4. 故障切换
# 当手机卡断网时，修改默认路由
ip route del default via <4G网关> dev usb0
ip route add default via <RJ45网关> dev eth0 metric 50
```

**关键特性：**
- ✅ 两个网络可以同时工作
- ✅ 手机卡故障时自动切换到RJ45
- ✅ 手机卡恢复后自动切回
- ✅ SSH始终可以通过RJ45访问

---

### 功能2：心跳检测和自动切换

**目标：** 实时监控网络状态，自动处理故障

**检测机制：**

```python
# 多层次检测
def check_network_health():
    """
    返回：{
        'cellular': True/False,
        'rj45': True/False,
        'frpc': True/False,
        'reason': '故障原因'
    }
    """
    
    # 第1层：ICMP检测（最快）
    cellular_ping = ping("8.8.8.8", interface="usb0", count=3, timeout=5)
    
    # 第2层：HTTP检测（更可靠）
    if cellular_ping:
        cellular_http = http_get("http://www.google.com", timeout=10)
    
    # 第3层：frpc连接检测
    frpc_status = check_frpc_connection()
    
    # 第4层：SIM卡状态检测
    sim_status = check_sim_card_status()
    
    return {
        'cellular': cellular_ping and cellular_http,
        'rj45': ping("网关", interface="eth0"),
        'frpc': frpc_status,
        'sim': sim_status
    }
```

**自动切换逻辑：**

```python
def auto_failover():
    """自动故障切换"""
    
    health = check_network_health()
    
    if not health['cellular']:
        logger.warning("手机卡网络故障")
        
        # 尝试1：重启4G模块
        restart_modem()
        sleep(30)
        
        # 尝试2：切换SIM卡
        if not check_network_health()['cellular']:
            switch_sim_card()
            sleep(30)
        
        # 尝试3：切换到RJ45
        if not check_network_health()['cellular']:
            switch_to_rj45()
            send_alert("手机卡断网，已切换到RJ45")
    
    # 检测恢复
    if health['cellular'] and current_route == 'rj45':
        switch_to_cellular()
        send_alert("手机卡已恢复，切回主网络")
```

**检测频率：**
- 正常情况：每30秒检测一次
- 故障情况：每10秒检测一次
- 恢复后：每60秒检测一次

---

### 功能3：MQTT远程管理

**目标：** 通过MQTT实现设备的远程控制和监控

**MQTT主题设计：**

```
# 设备上报主题
device/{device_id}/status          # 设备状态（每30秒）
device/{device_id}/heartbeat       # 心跳（每10秒）
device/{device_id}/alert           # 告警
device/{device_id}/log             # 日志

# 命令下发主题
device/{device_id}/command         # 远程命令
device/{device_id}/config          # 配置更新
device/{device_id}/ota             # OTA升级

# 响应主题
device/{device_id}/response        # 命令执行结果
```

**支持的远程命令：**

| 命令 | 参数 | 功能 | 执行时间 |
|------|------|------|---------|
| `check_status` | - | 检查设备状态 | 5秒 |
| `check_sim` | sim_slot | 检查SIM卡状态 | 5秒 |
| `switch_sim` | target_sim | 切换SIM卡 | 20秒 |
| `restart_modem` | - | 重启4G模块 | 30秒 |
| `restart_network` | - | 重启网络服务 | 10秒 |
| `restart_frpc` | - | 重启frpc | 5秒 |
| `reboot` | - | 重启设备 | 60秒 |
| `collect_logs` | time_range | 收集日志 | 30秒 |
| `update_config` | config_json | 更新配置 | 5秒 |
| `run_diagnostic` | - | 运行完整诊断 | 60秒 |

**命令示例：**

```json
// 切换SIM卡命令
{
  "command": "switch_sim",
  "params": {
    "target_sim": 2
  },
  "request_id": "req-12345",
  "timestamp": "2026-05-31T10:30:00Z"
}

// 设备响应
{
  "command": "switch_sim",
  "status": "success",
  "result": {
    "old_sim": 1,
    "new_sim": 2,
    "carrier": "Smart",
    "signal": -72,
    "network_type": "4G"
  },
  "request_id": "req-12345",
  "timestamp": "2026-05-31T10:30:25Z"
}
```

---

### 功能4：自动故障诊断

**目标：** 自动识别故障原因，减少人工排查时间

**诊断流程：**

```
1. 检测网络连通性
   ├─ ping 8.8.8.8 (检测互联网)
   ├─ ping 中转服务器 (检测隧道)
   └─ ping 网关 (检测本地网络)

2. 检测SIM卡状态
   ├─ AT命令查询信号强度
   ├─ 查询运营商信息
   ├─ 查询流量使用情况
   └─ 检查SIM卡是否锁定

3. 检测系统资源
   ├─ CPU使用率
   ├─ 内存使用率
   ├─ 磁盘空间
   └─ 系统温度

4. 检测服务状态
   ├─ frpc进程状态
   ├─ MQTT连接状态
   ├─ 网络监控服务状态
   └─ 系统日志错误

5. 生成诊断报告
   └─ 上报到MQTT和监控系统
```

**诊断报告示例：**

```json
{
  "device_id": "net-001",
  "timestamp": "2026-05-31T10:30:00Z",
  "diagnosis": {
    "network": {
      "cellular": {
        "status": "offline",
        "reason": "No signal",
        "last_online": "2026-05-31T08:00:00Z"
      },
      "rj45": {
        "status": "online",
        "ip": "192.168.1.100",
        "gateway": "192.168.1.1"
      },
      "internet": {
        "status": "online",
        "via": "rj45"
      }
    },
    "sim_cards": {
      "sim1": {
        "status": "online",
        "carrier": "Globe",
        "signal_dbm": -75,
        "signal_quality": "good",
        "network_type": "4G",
        "data_used_gb": 2.3,
        "data_remaining_gb": 7.7
      },
      "sim2": {
        "status": "offline",
        "carrier": "Smart",
        "error": "No signal",
        "last_online": "2026-05-30T08:00:00Z"
      },
      "current_sim": 1
    },
    "system": {
      "cpu_usage": 25,
      "memory_usage": 45,
      "disk_usage": 30,
      "temperature": 45,
      "uptime_hours": 72
    },
    "services": {
      "frpc": {
        "status": "disconnected",
        "reason": "Network unreachable",
        "last_connected": "2026-05-31T08:00:00Z"
      },
      "mqtt": {
        "status": "connected",
        "via": "rj45"
      },
      "network_monitor": {
        "status": "running"
      }
    },
    "recommendation": [
      "手机卡网络故障，已切换到RJ45",
      "建议检查SIM1信号覆盖",
      "建议切换到SIM2测试"
    ]
  }
}
```

---

### 功能5：OTA升级

**目标：** 远程升级设备固件，无需现场操作

**升级流程：**

```
1. 准备阶段
   ├─ 构建升级包（.swu格式）
   ├─ 上传到文件服务器
   └─ 生成升级任务

2. 下发升级命令
   ├─ 通过MQTT推送升级通知
   ├─ 设备检查升级包版本
   └─ 设备下载升级包

3. 升级执行
   ├─ 验证升级包签名
   ├─ 备份当前系统
   ├─ 安装新系统
   └─ 重启设备

4. 升级验证
   ├─ 设备启动后自检
   ├─ 上报新版本号
   └─ 如果失败，自动回滚

5. 灰度发布
   ├─ 先升级10%设备
   ├─ 观察24小时
   ├─ 逐步扩大范围
   └─ 最终全量升级
```

**升级包结构：**

```
upgrade.swu
├── sw-description (升级描述文件)
├── rootfs.img (根文件系统镜像)
├── kernel.img (内核镜像，可选)
├── scripts/
│   ├── pre-install.sh (安装前脚本)
│   └── post-install.sh (安装后脚本)
└── signature (数字签名)
```

**回滚机制：**
- 双分区设计（A/B分区）
- 升级失败自动回滚到旧版本
- 保留配置文件和数据

---

## 💻 技术实现方案

### 技术栈选型

**设备端（RV1103）：**

| 组件 | 技术选型 | 版本 | 理由 |
|------|---------|------|------|
| 操作系统 | Ubuntu 22.04 ARM64 | LTS | 稳定，软件包丰富 |
| 隧道客户端 | tiny-frpc | latest | 轻量，已验证 |
| MQTT客户端 | paho-mqtt (Python) | 1.6+ | 成熟，易用 |
| 网络监控 | Python 3.11 | 3.11+ | 灵活，开发快 |
| OTA升级 | swupdate | 2023.05+ | 嵌入式标准 |
| 进程管理 | systemd | 系统自带 | 可靠 |
| 日志管理 | rsyslog + logrotate | 系统自带 | 标准方案 |

**服务器端（香港中转）：**

| 组件 | 技术选型 | 版本 | 理由 |
|------|---------|------|------|
| 反向代理 | Nginx | 1.24+ | 高性能 |
| 隧道服务器 | frps | 0.52+ | 成熟稳定 |
| 代理服务 | gost | 3.0+ | 支持SOCKS5 |
| MQTT服务器 | Mosquitto | 2.0+ | 轻量，可靠 |
| 监控 | Prometheus + Grafana | latest | 业界标准 |
| 数据库 | PostgreSQL | 15+ | 可靠 |
| 缓存 | Redis | 7+ | 高性能 |

---

### 核心代码实现

#### 1. 网络监控服务

```python
#!/usr/bin/env python3
# network_monitor.py

import time
import subprocess
import json
import paho.mqtt.client as mqtt
from datetime import datetime

class NetworkMonitor:
    def __init__(self):
        self.device_id = self.get_device_id()
        self.mqtt_client = self.init_mqtt()
        self.current_route = "cellular"
        self.failure_count = 0
        
    def get_device_id(self):
        """获取设备ID"""
        # 从配置文件或MAC地址生成
        return "net-001"
    
    def init_mqtt(self):
        """初始化MQTT连接"""
        client = mqtt.Client(client_id=self.device_id)
        client.on_connect = self.on_mqtt_connect
        client.on_message = self.on_mqtt_message
        client.connect("mqtt.example.com", 1883, 60)
        return client
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        print(f"Connected to MQTT with result code {rc}")
        # 订阅命令主题
        client.subscribe(f"device/{self.device_id}/command")
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT消息回调"""
        try:
            command = json.loads(msg.payload)
            self.handle_command(command)
        except Exception as e:
            print(f"Error handling command: {e}")
    
    def ping(self, host, interface=None, count=3, timeout=5):
        """Ping检测"""
        cmd = ["ping", "-c", str(count), "-W", str(timeout)]
        if interface:
            cmd.extend(["-I", interface])
        cmd.append(host)
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout+2)
            return result.returncode == 0
        except:
            return False
    
    def check_network_health(self):
        """检查网络健康状态"""
        cellular_ok = self.ping("8.8.8.8", interface="usb0")
        rj45_ok = self.ping("192.168.1.1", interface="eth0")
        frpc_ok = self.check_frpc_status()
        
        return {
            "cellular": cellular_ok,
            "rj45": rj45_ok,
            "frpc": frpc_ok,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_frpc_status(self):
        """检查frpc连接状态"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "frpc"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "active"
        except:
            return False
