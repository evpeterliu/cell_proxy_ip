# FRP内网穿透部署文档

> 通过公网服务器实现内网Windows环境的远程访问

**部署日期：** 2026-06-01  
**服务器IP：** 203.3.113.133  
**用途：** 远程访问内网Windows开发环境

---

## 📋 系统架构

```
┌─────────────────────────────────────────────────┐
│          公网服务器（Ubuntu 24.04）              │
│          IP: 203.3.113.133                      │
│                                                 │
│  FRP服务端（frps）                               │
│  ├─ 控制端口: 7000                               │
│  ├─ Dashboard: 7500                             │
│  └─ SSH穿透: 6022 → 内网Windows:22               │
└─────────────────────────────────────────────────┘
                    ↑
                    │ frp tunnel
                    │
┌─────────────────────────────────────────────────┐
│          内网Windows PC                          │
│                                                 │
│  FRP客户端（frpc）                               │
│  ├─ SSH Server: localhost:22                    │
│  └─ 连接到: 203.3.113.133:7000                  │
└─────────────────────────────────────────────────┘
```

---

## 🚀 服务端部署步骤

### 1. 环境信息

**服务器配置：**
- 系统：Ubuntu 24.04.2 LTS
- CPU：Intel Xeon Platinum 8566C
- 内存：3.6GB
- 磁盘：40GB

**软件版本：**
- FRP版本：v0.52.3

### 2. 安装FRP服务端

#### 自动安装脚本

**脚本位置：** `/root/setup_frp_complete.sh`

**一键安装命令：**
```bash
cd /root
chmod +x setup_frp_complete.sh
./setup_frp_complete.sh
```

**脚本功能：**
- ✅ 自动下载FRP v0.52.3
- ✅ 解压到 `/root/frp_0.52.3_linux_amd64/`
- ✅ 创建配置文件 `frps.ini`
- ✅ 配置防火墙规则
- ✅ 创建systemd服务
- ✅ 自动启动并设置开机自启

### 3. 服务端配置

**配置文件：** `/root/frp_0.52.3_linux_amd64/frps.ini`

```ini
[common]
bind_port = 7000                              # FRP服务端口
dashboard_port = 7500                         # Web管理界面端口
dashboard_user = admin                        # Dashboard用户名
dashboard_pwd = ec800m_dashboard_2024         # Dashboard密码
token = ec800m_dev_secure_2024                # 客户端认证Token
allow_ports = 6000-6100                       # 允许的端口范围
log_file = /root/frp_0.52.3_linux_amd64/frps.log
log_level = info
log_max_days = 7                              # 日志保留7天
```

### 4. 端口说明

| 端口 | 用途 | 协议 | 说明 |
|------|------|------|------|
| 7000 | FRP控制端口 | TCP | 客户端连接到此端口 |
| 7500 | Web Dashboard | HTTP | 管理界面 |
| 6022 | SSH穿透端口 | TCP | 映射到内网Windows SSH |
| 6000-6100 | 可用端口范围 | TCP | 未来扩展使用 |

### 5. 防火墙配置

**开放端口：**
```bash
# Ubuntu使用ufw
ufw allow 7000/tcp
ufw allow 7500/tcp
ufw allow 6022/tcp
ufw reload
```

### 6. systemd服务配置

**服务文件：** `/etc/systemd/system/frps.service`

```ini
[Unit]
Description=FRP Server Service
After=network.target

[Service]
Type=simple
User=root
Restart=on-failure
RestartSec=5s
ExecStart=/root/frp_0.52.3_linux_amd64/frps -c /root/frp_0.52.3_linux_amd64/frps.ini
ExecReload=/bin/kill -s HUP $MAINPID

[Install]
WantedBy=multi-user.target
```

**服务管理命令：**
```bash
# 启动服务
systemctl start frps

# 停止服务
systemctl stop frps

# 重启服务
systemctl restart frps

# 查看状态
systemctl status frps

# 开机自启
systemctl enable frps

# 查看日志
journalctl -u frps -f
```

---

## 💻 客户端配置（Windows）

### 1. 下载FRP客户端

**下载地址：**
```
https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_windows_amd64.zip
```

### 2. 客户端配置文件

**文件名：** `frpc.ini`（放在Windows的frp解压目录）

```ini
[common]
server_addr = 203.3.113.133         # 服务器IP
server_port = 7000                   # 服务器端口
token = ec800m_dev_secure_2024       # 认证Token（与服务端一致）

[ssh]
type = tcp
local_ip = 127.0.0.1                 # 本地SSH服务IP
local_port = 22                      # 本地SSH端口
remote_port = 6022                   # 映射到服务器的6022端口
```

### 3. 启动客户端

**命令行启动：**
```cmd
cd C:\frp_0.52.3_windows_amd64
frpc.exe -c frpc.ini
```

**后台运行（使用nssm）：**
```cmd
# 安装nssm
nssm install frpc "C:\frp_0.52.3_windows_amd64\frpc.exe" "-c" "C:\frp_0.52.3_windows_amd64\frpc.ini"

# 启动服务
nssm start frpc
```

### 4. Windows SSH服务配置

**安装OpenSSH Server：**
```powershell
# 管理员PowerShell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动服务
Start-Service sshd

# 设置开机自启
Set-Service -Name sshd -StartupType 'Automatic'

# 配置防火墙
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

---

## 🔗 连接测试

### 1. 测试FRP连接

**从任意外网位置SSH连接：**
```bash
ssh -p 6022 <Windows用户名>@203.3.113.133
```

**示例：**
```bash
ssh -p 6022 claude_dev@203.3.113.133
```

### 2. 验证连接状态

**服务器端查看：**
```bash
# 查看连接日志
tail -f /root/frp_0.52.3_linux_amd64/frps.log

# 查看连接状态
netstat -an | grep 7000 | grep ESTABLISHED

# 查看6022端口
netstat -tuln | grep 6022
```

**客户端查看：**
```cmd
# 查看frpc日志
# 日志会显示连接状态
```

### 3. Web Dashboard访问

**访问地址：**
```
http://203.3.113.133:7500
```

**登录信息：**
- 用户名：`admin`
- 密码：`ec800m_dashboard_2024`

---

## 📊 运行状态

### 当前运行信息

**服务状态：**
```bash
root@ecm-3ab4# ps aux | grep frps
root  71249  0.0  0.4 728328 18580 ?  Sl  Jun01  0:31 ./frps -c frps.ini
```

**启动时间：** 2026-06-01  
**运行时长：** 持续运行中  
**客户端连接：** 正常（日志显示持续有连接）

**监听端口：**
```
tcp6  0  0 :::6022   :::*  LISTEN
tcp6  0  0 :::7000   :::*  LISTEN
tcp6  0  0 :::7500   :::*  LISTEN
```

---

## 🛠️ 维护和故障排查

### 常用命令

**查看服务状态：**
```bash
systemctl status frps
```

**查看实时日志：**
```bash
tail -f /root/frp_0.52.3_linux_amd64/frps.log
```

**重启服务：**
```bash
systemctl restart frps
```

**检查端口占用：**
```bash
netstat -tuln | grep -E "7000|7500|6022"
```

### 常见问题

#### 1. 客户端连接失败

**检查步骤：**
- 确认服务端frps服务正常运行
- 确认防火墙7000端口已开放
- 确认token配置一致
- 检查服务器日志：`tail -f /root/frp_0.52.3_linux_amd64/frps.log`

#### 2. SSH连接失败

**检查步骤：**
- 确认客户端frpc正常运行
- 确认Windows SSH服务已启动
- 确认6022端口映射正常
- 测试本地SSH：`ssh localhost -p 22`（在Windows上）

#### 3. Dashboard无法访问

**检查步骤：**
- 确认7500端口已开放
- 确认dashboard配置正确
- 浏览器访问：`http://203.3.113.133:7500`

---

## 📁 重要文件位置

**服务器端：**
```
/root/frp_0.52.3_linux_amd64/          # FRP安装目录
├── frps                               # 服务端可执行文件
├── frps.ini                           # 配置文件
└── frps.log                           # 日志文件

/root/setup_frp_complete.sh            # 自动安装脚本
/etc/systemd/system/frps.service       # systemd服务文件
```

**Windows客户端：**
```
C:\frp_0.52.3_windows_amd64\           # FRP客户端目录
├── frpc.exe                           # 客户端可执行文件
└── frpc.ini                           # 配置文件
```

---

## 🔐 安全建议

1. **修改默认密码**
   - 定期更换Dashboard密码
   - 使用强密码策略

2. **Token安全**
   - Token是客户端认证凭证，不要泄露
   - 建议定期更换

3. **防火墙配置**
   - 只开放必要端口
   - 限制SSH登录IP（可选）

4. **日志监控**
   - 定期查看连接日志
   - 发现异常及时处理

5. **备份配置**
   - 定期备份配置文件
   - 记录重要配置信息

---

## 📝 更新日志

| 日期 | 操作 | 说明 |
|------|------|------|
| 2026-06-01 | 初始部署 | 完成FRP服务端和客户端配置 |
| 2026-06-02 | 文档整理 | 创建完整的部署文档 |

---

## 🔗 相关链接

- **FRP官方仓库：** https://github.com/fatedier/frp
- **FRP文档：** https://gofrp.org/zh-cn/
- **服务器SSH：** `ssh root@203.3.113.133`
- **Windows SSH穿透：** `ssh -p 6022 <用户名>@203.3.113.133`
- **Dashboard：** http://203.3.113.133:7500

---

**文档维护：** 请在每次重要配置变更后更新此文档