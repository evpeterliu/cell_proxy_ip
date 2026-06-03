# 服务器访问指南

**文档更新时间：** 2026-06-03

---

## 🔑 SSH访问信息

### 主服务器（中转服务器）

**服务器地址：** `203.3.113.133`  
**用户名：** `root`  
**认证方式：** SSH密钥  
**密钥位置：** `~/.ssh/server_key`  
**工作目录：** `/root/`

**连接命令：**
```bash
ssh -i ~/.ssh/server_key root@203.3.113.133
```

**用途：**
- frp服务管理（frps运行在此）
- 执行SOCKS5端口检测脚本
- 日志查看和诊断

---

### SOCKS5代理服务器

**域名：** `codex.adusun.com`  
**IP地址：** `154.92.2.59`  
**SSH访问：** 待配置（当前无直接SSH权限）  
**用途：** SOCKS5代理服务（端口21880-21896）

---

## 🔧 SOCKS5服务信息

### 代理配置

**服务器：** codex.adusun.com (154.92.2.59)  
**端口范围：** 21880-21896（共17个端口）  
**协议：** SOCKS5  
**认证：** 用户名密码  
- 用户名：`ppp`
- 密码：`ppp`

**连接格式：**
```
socks5://ppp:ppp@154.92.2.59:21883
```

### 设备映射

每个端口对应一台net终端设备（RV1103 + EC600M）：

| 端口 | 设备序列号 | SIM卡号 |
|------|-----------|---------|
| 21880 | GWOB2E8520D5D22 | 639304148539 |
| 21881 | GWUF6AE1E818E9E | 639090775532 |
| 21882 | GWU0EAAD409B83D | 639120518497 |
| 21883 | GWUC2D4C44638A3 | 639096134226 |
| ... | ... | ... |

**完整映射表：** 见 `socks5-monitoring/reports/latest_device_mapping.md`

---

## 📊 监控和检测

### 快速检测脚本

**位置：** `socks5-monitoring/scripts/quick_socks5_check.py`

**从中转服务器执行：**
```bash
# 1. SSH登录中转服务器
ssh -i ~/.ssh/server_key root@203.3.113.133

# 2. 执行检测（检测所有端口）
for port in {21880..21896}; do 
    echo -n "端口 $port: "
    ip=$(timeout 5 curl -x socks5://ppp:ppp@codex.adusun.com:$port -s https://ip.sb 2>/dev/null)
    if [ -n "$ip" ]; then 
        echo "✅ $ip"
    else 
        echo "❌ 不可用"
    fi
    sleep 0.5
done
```

**从云端执行（通过SSH隧道）：**
```bash
ssh -i ~/.ssh/server_key root@203.3.113.133 'bash -s' < socks5-monitoring/scripts/check_all_ports.sh
```

---

## 🗂️ 文件组织结构

```
cell_proxy_ip/
├── socks5-monitoring/           # SOCKS5监控相关
│   ├── reports/                 # 检测报告（按日期命名）
│   │   ├── 2026-06-03_device_mapping.md
│   │   ├── 2026-06-03_status.md
│   │   └── latest_device_mapping.md -> 最新报告的软链接
│   └── scripts/                 # 检测脚本
│       ├── quick_socks5_check.py
│       └── quick_ip.py
├── docs/
│   └── server-access/           # 本文件所在目录
│       └── README.md            # 服务器访问指南
├── archive/                     # 历史归档
│   └── socks5-old-reports/      # 旧的检测报告
└── scripts/                     # 其他通用脚本
```

---

## 🚀 常用操作

### 1. 检测所有SOCKS5端口状态

```bash
ssh -i ~/.ssh/server_key root@203.3.113.133 'for port in {21880..21896}; do timeout 5 curl -x socks5://ppp:ppp@codex.adusun.com:$port -s https://ip.sb && echo "✅ $port" || echo "❌ $port"; done'
```

### 2. 测试单个端口

```bash
curl -x socks5://ppp:ppp@154.92.2.59:21883 https://ip.sb
```

### 3. 查看frps状态

```bash
ssh -i ~/.ssh/server_key root@203.3.113.133 'ps aux | grep frps'
```

### 4. 查看frps日志

```bash
ssh -i ~/.ssh/server_key root@203.3.113.133 'tail -100 /root/frp_0.52.3_linux_amd64/frps.log'
```

---

## 📝 报告规范

### 文件命名规范

**检测报告：** `YYYY-MM-DD_report_type.md`

示例：
- `2026-06-03_device_mapping.md` - 设备映射报告
- `2026-06-03_status.md` - 端口状态报告
- `2026-06-03_analysis.md` - 分析报告

### 报告内容要求

1. **时间戳：** 明确的检测时间
2. **在线率：** 可用/总数，百分比
3. **设备映射：** 端口→设备序列号→SIM卡
4. **出口IP：** 每个在线端口的当前出口IP
5. **离线设备：** 列出需要处理的离线设备
6. **趋势对比：** 与上次检测对比

---

## 🔐 安全注意事项

1. **密钥管理：** 
   - SSH私钥保存在 `~/.ssh/server_key`
   - 权限必须为 `600`
   - 不要提交到Git仓库

2. **密码保护：**
   - SOCKS5密码（ppp:ppp）仅用于测试
   - 生产环境需更改为强密码

3. **访问日志：**
   - 所有SSH会话被记录
   - 定期审查访问日志

---

## 📞 故障排查

### 无法SSH连接

1. 检查密钥权限：`chmod 600 ~/.ssh/server_key`
2. 验证服务器IP：`ping 203.3.113.133`
3. 检查SSH服务：联系运维团队

### SOCKS5端口不通

1. 确认服务器可访问：`ping codex.adusun.com`
2. 检查端口映射：查看frps配置
3. 查看设备状态：通过MQTT平台确认设备在线
4. 检查SIM卡：信号强度、网络注册状态

### 无法获取出口IP

1. 检查SOCKS5认证：确认用户名密码正确
2. 测试网络连通：`curl https://ip.sb`
3. 查看设备日志：SSH到具体设备检查

---

## 📚 相关文档

- [SOCKS5监控报告](../../socks5-monitoring/reports/)
- [项目需求文档](../../01-requirements/)
- [技术方案文档](../../02-technical/)
- [运维手册](../../04-operations/)

---

**维护者：** 运维团队  
**最后更新：** 2026-06-03  
**文档版本：** v1.0
