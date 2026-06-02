# Windows远程访问配置指南

本文档记录通过FRP内网穿透实现远程访问Windows开发环境的完整配置过程。

## 📋 目录

- [架构概览](#架构概览)
- [环境信息](#环境信息)
- [服务端配置](#服务端配置)
- [客户端配置](#客户端配置)
- [SSH密钥配置](#ssh密钥配置)
- [连接测试](#连接测试)
- [故障排查](#故障排查)
- [自动化脚本](#自动化脚本)

---

## 架构概览

```
┌─────────────────┐      FRP隧道      ┌─────────────────┐
│   远程访问端    │ ◄─────────────► │   云服务器      │
│   (任意位置)    │    SSH:22        │  203.3.113.133  │
└─────────────────┘    TCP:6022       └─────────────────┘
                                              ▲
                                              │ FRP Client
                                              │ (内网穿透)
                                              │
                                      ┌───────┴──────────┐
                                      │  Windows PC      │
                                      │  DESKTOP-VI8GQ54 │
                                      │  (内网环境)      │
                                      └──────────────────┘
```

**工作流程：**
1. Windows电脑通过frpc连接到云服务器的7000端口（FRP控制端口）
2. frps在云服务器上监听6022端口，映射到Windows的22端口（SSH）
3. 远程端通过SSH连接云服务器的6022端口，实现访问Windows

**当前临时方案（因天翼云安全组限制）：**
- 外网 → 云服务器22端口（SSH）
- SSH隧道转发 → 本地16022端口 → 云服务器本地6022端口 → Windows SSH

---

## 环境信息

### 云服务器
- **IP地址：** 203.3.113.133（公网），10.0.0.8（内网）
- **操作系统：** Ubuntu 24.04.2 LTS
- **云服务商：** 天翼云
- **FRP版本：** v0.52.3
- **开放端口：** 22 (SSH), 7000 (FRP控制), 7500 (FRP Dashboard), 6022 (SSH穿透 - 需配置)

### Windows PC
- **主机名：** DESKTOP-VI8GQ54
- **用户：** administrator
- **密码：** ew666888
- **FRP客户端：** C:\frp_0.52.3_windows_amd64\
- **SSH服务：** OpenSSH Server (Windows内置)
- **开发环境：** Qt, LLVM-MinGW, MDK, MounRiver等

---

## 服务端配置

### 1. FRP服务端安装

```bash
# 连接到服务器
ssh -i ~/.ssh/server_key root@203.3.113.133

# 进入frp目录
cd /root/frp_0.52.3_linux_amd64
```

### 2. 服务端配置文件

**文件路径：** `/root/frp_0.52.3_linux_amd64/frps.toml`

```toml
bindAddr = "0.0.0.0"
bindPort = 7000

transport.tcpMux = true

webServer.addr = "0.0.0.0"
webServer.port = 7500
webServer.user = "admin"
webServer.password = "ec800m_dashboard_2024"

auth.token = "ec800m_dev_secure_2024"

allowPorts = [
  { start = 6000, end = 6100 }
]

log.to = "/root/frp_0.52.3_linux_amd64/frps.log"
log.level = "info"
log.maxDays = 7
```

**配置说明：**
- `bindAddr`: 绑定到所有IPv4地址（包括公网IP）
- `bindPort`: FRP控制端口
- `webServer`: Dashboard访问地址和认证信息
- `auth.token`: 客户端连接认证令牌
- `allowPorts`: 允许映射的端口范围

### 3. 启动FRP服务端

```bash
# 启动frps（后台运行）
cd /root/frp_0.52.3_linux_amd64
nohup ./frps -c frps.toml > /dev/null 2>&1 &

# 检查进程
ps aux | grep frps | grep -v grep

# 检查端口监听
netstat -tlnp | grep frps
# 应该看到：
# tcp6  0  0 :::7000   :::*  LISTEN  <pid>/./frps
# tcp6  0  0 :::6022   :::*  LISTEN  <pid>/./frps
# tcp6  0  0 :::7500   :::*  LISTEN  <pid>/./frps

# 查看日志
tail -f /root/frp_0.52.3_linux_amd64/frps.log
```

### 4. 配置开机自启（可选）

```bash
# 创建systemd服务文件
cat > /etc/systemd/system/frps.service << 'EOF'
[Unit]
Description=FRP Server Service
After=network.target

[Service]
Type=simple
User=root
Restart=on-failure
RestartSec=5s
ExecStart=/root/frp_0.52.3_linux_amd64/frps -c /root/frp_0.52.3_linux_amd64/frps.toml

[Install]
WantedBy=multi-user.target
EOF

# 重载systemd配置
systemctl daemon-reload

# 启动并启用服务
systemctl enable frps
systemctl start frps

# 检查状态
systemctl status frps
```

---

## 客户端配置

### 1. Windows OpenSSH Server安装

以**管理员身份**打开PowerShell：

```powershell
# 安装OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 启动SSH服务
Start-Service sshd

# 设置开机自启
Set-Service -Name sshd -StartupType 'Automatic'

# 配置防火墙规则
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# 检查服务状态
Get-Service sshd
# 应该显示 Status: Running

# 测试本地SSH
ssh localhost
```

### 2. FRP客户端配置

**文件路径：** `C:\frp_0.52.3_windows_amd64\frpc.ini`

```ini
[common]
server_addr = 203.3.113.133
server_port = 7000
token = ec800m_dev_secure_2024

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6022
```

**配置说明：**
- `server_addr`: FRP服务端公网IP
- `server_port`: FRP服务端控制端口
- `token`: 与服务端配置一致的认证令牌
- `local_port`: Windows本地SSH端口（22）
- `remote_port`: 映射到服务器的端口（6022）

### 3. 启动FRP客户端

```cmd
# 进入frp目录
cd C:\frp_0.52.3_windows_amd64

# 启动frpc
.\frpc.exe -c frpc.ini
```

**成功日志示例：**
```
2026/06/02 16:06:26 [I] [root.go:139] start frpc service for config file [frpc.ini]
2026/06/02 16:06:28 [I] [service.go:299] [8e6660963e76bcbb] login to server success
2026/06/02 16:06:28 [I] [proxy_manager.go:156] [8e6660963e76bcbb] proxy added: [ssh]
2026/06/02 16:06:28 [I] [control.go:173] [8e6660963e76bcbb] [ssh] start proxy success
```

### 4. 配置Windows服务（开机自启）

使用NSSM（Non-Sucking Service Manager）将frpc注册为Windows服务：

```powershell
# 下载NSSM (https://nssm.cc/download)
# 解压到 C:\nssm\

# 安装frpc服务
C:\nssm\nssm.exe install frpc "C:\frp_0.52.3_windows_amd64\frpc.exe" "-c" "C:\frp_0.52.3_windows_amd64\frpc.ini"

# 启动服务
Start-Service frpc

# 检查状态
Get-Service frpc
```

---

## SSH密钥配置

### 1. 生成SSH密钥对

在远程访问端（Linux/Mac）生成密钥：

```bash
ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa_windows -N "" -C "claude@workspace"
```

**生成的密钥对：**
- 私钥：`~/.ssh/id_rsa_windows`
- 公钥：`~/.ssh/id_rsa_windows.pub`

**本项目密钥位置：**
```
cell_proxy_ip/
└── .ssh/
    ├── id_rsa_windows      # 私钥（用于连接）
    └── id_rsa_windows.pub  # 公钥（配置到Windows）
```

### 2. 配置Windows authorized_keys

以**管理员身份**在Windows PowerShell执行：

```powershell
# 创建.ssh目录
mkdir C:\Users\Administrator\.ssh -ErrorAction SilentlyContinue

# 添加公钥（替换为实际的公钥内容）
Set-Content -Path C:\Users\Administrator\.ssh\authorized_keys -Value "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCaOmqeiPMu5LSwxGDITrDYFWxLZi5KJT4i7GqBXz9N07p0yawTrGbulrG7XA91T2R5hd06N2MpLI0YZvay/T66eetIQRqPOnwY+D6lCCNTN1BGwQckt1y52LJctoSvbdDp0229UlWCJeRK8XcuQvv6YwurOYTpONkdNd3SeIEqGMuM6f48Ol9s9kHhlpHPmrNuHLvBg0EJRqbroB0gTfjN/Ze71RHwaAcgOJtHWK6OVe/6J/2op/Sq4JBHbHtavo6Oj8VctaS5cbiO6fXfpv2nCclejYrhqMgq8mFXWcVpbZOhefhMet0v8eptbSgw9WZ+QWY0bvp9MYMjkvAVA0sF claude@workspace"

# 设置正确的权限（重要！）
icacls C:\Users\Administrator\.ssh\authorized_keys /inheritance:r
icacls C:\Users\Administrator\.ssh\authorized_keys /grant "Administrators:F"
icacls C:\Users\Administrator\.ssh\authorized_keys /grant "SYSTEM:F"

# 验证配置
type C:\Users\Administrator\.ssh\authorized_keys
```

### 3. 获取项目中的公钥

```bash
# 从GitHub克隆项目后
cd cell_proxy_ip
cat .ssh/id_rsa_windows.pub

# 或直接从GitHub查看
# https://github.com/evpeterliu/cell_proxy_ip/blob/main/.ssh/id_rsa_windows.pub
```

---

## 连接测试

### 方式1：直接连接（需要安全组配置）

**理论上的连接方式（天翼云安全组6022端口开放后）：**

```bash
# 使用密钥连接
ssh -i .ssh/id_rsa_windows -p 6022 administrator@203.3.113.133

# 使用密码连接
ssh -p 6022 administrator@203.3.113.133
# 密码: ew666888
```

### 方式2：SSH隧道转发（当前使用方式）

**由于天翼云安全组6022端口无法从外网访问，使用SSH隧道作为临时方案：**

```bash
# 步骤1：建立SSH隧道（后台运行）
ssh -i ~/.ssh/server_key -f -N -L 16022:127.0.0.1:6022 root@203.3.113.133

# 步骤2：通过本地端口连接Windows
ssh -i .ssh/id_rsa_windows -p 16022 administrator@localhost

# 或者合并为一条命令（使用ProxyJump）
ssh -i .ssh/id_rsa_windows -p 6022 \
    -o ProxyJump=root@203.3.113.133 \
    administrator@localhost
```

**工作原理：**
```
本地16022端口 → SSH隧道 → 服务器22端口 → 服务器本地6022端口 → FRP隧道 → Windows 22端口
```

### 测试连接

```bash
# 测试基本连接
ssh -i .ssh/id_rsa_windows -p 16022 administrator@localhost 'hostname'
# 输出: DESKTOP-VI8GQ54

# 查看系统信息
ssh -i .ssh/id_rsa_windows -p 16022 administrator@localhost 'systeminfo | findstr /C:"OS Name" /C:"OS Version"'

# 列出目录
ssh -i .ssh/id_rsa_windows -p 16022 administrator@localhost 'dir C:\'

# 检查frpc状态
ssh -i .ssh/id_rsa_windows -p 16022 administrator@localhost 'tasklist | findstr frpc'
```

---

## 故障排查

### 问题1：外网无法连接6022端口

**症状：**
```bash
$ ssh -p 6022 administrator@203.3.113.133
ssh: connect to host 203.3.113.133 port 6022: Connection refused
```

**诊断步骤：**

```bash
# 1. 检查服务器内部是否能连接
ssh -i ~/.ssh/server_key root@203.3.113.133
telnet 127.0.0.1 6022
# 如果能看到 "SSH-2.0-OpenSSH_for_Windows" → FRP隧道正常

# 2. 检查frps端口监听
netstat -tlnp | grep 6022
# 应该看到：tcp6  0  0 :::6022  :::*  LISTEN

# 3. 检查frps日志
tail -50 /root/frp_0.52.3_linux_amd64/frps.log | grep -E "client login|new proxy|error"
```

**解决方案：**

1. **检查天翼云安全组配置**
   - 登录天翼云控制台
   - 找到服务器实例
   - 安全组 → 入站规则
   - 添加：协议=TCP，端口=6022，来源=0.0.0.0/0
   - 保存并确认规则已绑定到服务器

2. **检查服务器防火墙**
   ```bash
   # Ubuntu UFW
   ufw status
   ufw allow 6022/tcp
   ```

3. **使用SSH隧道临时方案**（见"连接测试 - 方式2"）

### 问题2：Windows SSH服务未启动

**症状：**
- frpc显示连接成功
- 服务器内部telnet 6022能连上，但立即断开
- 没有看到SSH banner

**解决方案：**

```powershell
# 检查SSH服务状态
Get-Service sshd

# 启动服务
Start-Service sshd

# 检查22端口监听
netstat -an | findstr :22

# 测试本地SSH
ssh localhost
```

### 问题3：frpc连接失败

**症状：**
```
[E] login to server failed: xxx
```

**解决方案：**

```bash
# 1. 检查服务端frps是否运行
ssh -i ~/.ssh/server_key root@203.3.113.133
ps aux | grep frps
netstat -tlnp | grep 7000

# 2. 检查token是否一致
# frps.toml: auth.token = "ec800m_dev_secure_2024"
# frpc.ini:  token = ec800m_dev_secure_2024

# 3. 检查网络连通性
# Windows上测试:
telnet 203.3.113.133 7000

# 4. 查看frps日志
tail -50 /root/frp_0.52.3_linux_amd64/frps.log
```

### 问题4：SSH密钥认证失败

**症状：**
```
Permission denied (publickey,password,keyboard-interactive).
```

**解决方案：**

```powershell
# 1. 检查authorized_keys文件
type C:\Users\Administrator\.ssh\authorized_keys

# 2. 检查文件权限
icacls C:\Users\Administrator\.ssh\authorized_keys
# 应该只有Administrators和SYSTEM有权限

# 3. 重新设置权限
icacls C:\Users\Administrator\.ssh\authorized_keys /inheritance:r
icacls C:\Users\Administrator\.ssh\authorized_keys /grant "Administrators:F"
icacls C:\Users\Administrator\.ssh\authorized_keys /grant "SYSTEM:F"

# 4. 检查公钥格式
# 公钥应该是一行，以 "ssh-rsa " 开头
# 不能有换行或额外空格

# 5. 重启SSH服务
Restart-Service sshd
```

### 问题5：中文乱码

**症状：**
SSH命令返回的中文显示为乱码

**解决方案：**

```bash
# 方法1：使用chcp命令切换代码页
ssh ... 'chcp 65001 && dir C:\'

# 方法2：设置环境变量
ssh ... 'set LC_ALL=zh_CN.UTF-8 && dir C:\'

# 方法3：在客户端设置字符集
export LC_ALL=en_US.UTF-8
ssh ...
```

---

## 自动化脚本

### 一键连接脚本

创建 `connect-windows.sh`：

```bash
#!/bin/bash
# Windows远程连接脚本

# 配置参数
SERVER_IP="203.3.113.133"
SERVER_USER="root"
SERVER_KEY="$HOME/.ssh/server_key"
WINDOWS_KEY="$(dirname "$0")/.ssh/id_rsa_windows"
WINDOWS_USER="administrator"
LOCAL_PORT=16022
REMOTE_PORT=6022

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Windows远程连接脚本 ===${NC}"

# 检查密钥文件
if [ ! -f "$WINDOWS_KEY" ]; then
    echo -e "${RED}错误: Windows SSH密钥不存在: $WINDOWS_KEY${NC}"
    exit 1
fi

# 检查SSH隧道是否已建立
TUNNEL_PID=$(ps aux | grep "ssh.*$LOCAL_PORT:127.0.0.1:$REMOTE_PORT" | grep -v grep | awk '{print $2}')

if [ -z "$TUNNEL_PID" ]; then
    echo -e "${YELLOW}建立SSH隧道...${NC}"
    ssh -i "$SERVER_KEY" -f -N -L $LOCAL_PORT:127.0.0.1:$REMOTE_PORT $SERVER_USER@$SERVER_IP
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SSH隧道已建立${NC}"
        sleep 2
    else
        echo -e "${RED}✗ SSH隧道建立失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ SSH隧道已存在 (PID: $TUNNEL_PID)${NC}"
fi

# 连接到Windows
echo -e "${YELLOW}连接到Windows...${NC}"
ssh -i "$WINDOWS_KEY" -p $LOCAL_PORT -o StrictHostKeyChecking=no $WINDOWS_USER@localhost "$@"

# 如果指定了 --close-tunnel 参数，关闭隧道
if [[ "$1" == "--close-tunnel" ]]; then
    if [ -n "$TUNNEL_PID" ]; then
        echo -e "${YELLOW}关闭SSH隧道...${NC}"
        kill $TUNNEL_PID
        echo -e "${GREEN}✓ SSH隧道已关闭${NC}"
    fi
fi
```

**使用方式：**

```bash
# 赋予执行权限
chmod +x connect-windows.sh

# 连接Windows（进入交互式shell）
./connect-windows.sh

# 执行单条命令
./connect-windows.sh 'hostname'
./connect-windows.sh 'dir C:\'

# 连接后关闭隧道
./connect-windows.sh --close-tunnel
```

### 健康检查脚本

创建 `check-frp-status.sh`：

```bash
#!/bin/bash
# FRP服务健康检查脚本

SERVER_IP="203.3.113.133"
SERVER_KEY="$HOME/.ssh/server_key"

echo "=== FRP服务状态检查 ==="
echo ""

# 检查服务端
echo "【服务端状态】"
ssh -i "$SERVER_KEY" root@$SERVER_IP << 'REMOTE_SCRIPT'
# 检查frps进程
if ps aux | grep frps | grep -v grep > /dev/null; then
    echo "✓ frps进程运行中"
    ps aux | grep frps | grep -v grep | awk '{print "  PID:", $2, "CPU:", $3"%", "MEM:", $4"%"}'
else
    echo "✗ frps进程未运行"
fi

# 检查端口监听
echo ""
echo "端口监听状态:"
netstat -tlnp 2>/dev/null | grep frps | awk '{print "  " $4, "->", $7}'

# 检查最近日志
echo ""
echo "最近5条日志:"
tail -5 /root/frp_0.52.3_linux_amd64/frps.log | sed 's/^/  /'
REMOTE_SCRIPT

echo ""
echo "【客户端连接测试】"
# 测试内部6022端口
ssh -i "$SERVER_KEY" root@$SERVER_IP "timeout 2 telnet 127.0.0.1 6022 2>&1 | head -3" && \
    echo "✓ Windows SSH隧道正常" || \
    echo "✗ Windows SSH隧道异常"

echo ""
echo "=== 检查完成 ==="
```

**使用方式：**

```bash
chmod +x check-frp-status.sh
./check-frp-status.sh
```

---

## 安全建议

### 1. 修改默认密码

```powershell
# Windows上修改administrator密码
net user administrator NEW_STRONG_PASSWORD
```

### 2. 限制SSH访问来源

如果知道固定的访问IP，在天翼云安全组中限制来源IP：

```
协议: TCP
端口: 6022
来源: YOUR_IP_ADDRESS/32  # 替换为你的公网IP
```

### 3. 定期更新SSH密钥

```bash
# 生成新密钥
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_windows -C "windows-access-$(date +%Y%m%d)"

# 配置到Windows
# ... (重复"SSH密钥配置"步骤)

# 删除旧密钥
rm ~/.ssh/id_rsa_windows*
```

### 4. 启用FRP加密

在 `frps.toml` 和 `frpc.ini` 中启用TLS：

```toml
# frps.toml
transport.tls.enable = true
transport.tls.certFile = "/path/to/cert.pem"
transport.tls.keyFile = "/path/to/key.pem"
```

```ini
# frpc.ini
[common]
tls_enable = true
```

### 5. 配置fail2ban（服务器端）

```bash
# 安装fail2ban
apt-get install fail2ban

# 配置SSH保护
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 22,6022
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

# 启动服务
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 附录

### A. 常用命令速查

```bash
# 服务端命令
ssh -i ~/.ssh/server_key root@203.3.113.133

# 启动/停止frps
cd /root/frp_0.52.3_linux_amd64
./frps -c frps.toml                    # 前台运行
nohup ./frps -c frps.toml &            # 后台运行
killall frps                            # 停止

# 查看frps状态
ps aux | grep frps
netstat -tlnp | grep frps
tail -f /root/frp_0.52.3_linux_amd64/frps.log

# 客户端命令（Windows）
cd C:\frp_0.52.3_windows_amd64
.\frpc.exe -c frpc.ini                 # 启动frpc
tasklist | findstr frpc                # 查看进程
taskkill /F /IM frpc.exe               # 停止进程

# SSH连接（当前方式）
ssh -i ~/.ssh/server_key -f -N -L 16022:127.0.0.1:6022 root@203.3.113.133
ssh -i .ssh/id_rsa_windows -p 16022 administrator@localhost
```

### B. 端口说明

| 端口  | 协议 | 用途                | 位置       | 状态       |
|-------|------|---------------------|------------|------------|
| 22    | TCP  | SSH服务             | Windows PC | ✓ 正常     |
| 22    | TCP  | SSH服务             | 云服务器   | ✓ 正常     |
| 6022  | TCP  | SSH穿透端口         | 云服务器   | ✓ 内部正常 |
| 7000  | TCP  | FRP控制端口         | 云服务器   | ✓ 正常     |
| 7500  | TCP  | FRP Dashboard       | 云服务器   | ✓ 正常     |
| 16022 | TCP  | 本地SSH隧道转发端口 | 本地       | ✓ 正常     |

### C. 配置文件路径汇总

```
服务端：
/root/frp_0.52.3_linux_amd64/
├── frps                    # 服务端可执行文件
├── frps.toml               # 服务端配置（TOML格式）
└── frps.log                # 服务端日志

客户端（Windows）：
C:\frp_0.52.3_windows_amd64\
├── frpc.exe                # 客户端可执行文件
└── frpc.ini                # 客户端配置（INI格式）

C:\Users\Administrator\.ssh\
└── authorized_keys         # SSH公钥

SSH密钥：
cell_proxy_ip/.ssh/
├── id_rsa_windows          # 私钥
└── id_rsa_windows.pub      # 公钥
```

### D. 相关文档

- [FRP官方文档](https://github.com/fatedier/frp)
- [OpenSSH for Windows](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- [SSH密钥配置](https://www.ssh.com/academy/ssh/keygen)

---

## 更新日志

| 日期       | 版本  | 说明                                       |
|------------|-------|-------------------------------------------|
| 2026-06-02 | 1.0.0 | 初始版本，完整配置Windows远程访问         |

---

**维护者：** claude@workspace  
**最后更新：** 2026-06-02  
**项目地址：** https://github.com/evpeterliu/cell_proxy_ip
