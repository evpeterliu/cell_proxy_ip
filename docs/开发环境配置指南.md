# 开发环境配置指南

> **适用对象：** 开发人员  
> **前置条件：** 熟悉Linux基础命令  
> **预计时间：** 1-2小时

---

## 📋 目录

1. [服务器端环境配置](#服务器端环境配置)
2. [设备端环境配置](#设备端环境配置)
3. [开发工具配置](#开发工具配置)
4. [常见问题排查](#常见问题排查)

---

## 🖥️ 服务器端环境配置

### 1. 香港中转服务器

**推荐配置：**
- CPU: 4核
- 内存: 8GB
- 硬盘: 100GB SSD
- 带宽: 100Mbps
- 系统: Ubuntu 22.04 LTS

#### 1.1 基础环境安装

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim htop net-tools

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### 1.2 防火墙配置

```bash
# 安装UFW
sudo apt install -y ufw

# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 1080/tcp  # SOCKS5
sudo ufw allow 7000/tcp  # frps

# 启用防火墙
sudo ufw enable
sudo ufw status
```

#### 1.3 创建项目目录

```bash
# 创建项目目录
sudo mkdir -p /opt/net-terminal
cd /opt/net-terminal

# 创建子目录
mkdir -p {config,data,logs}

# 设置权限
sudo chown -R $USER:$USER /opt/net-terminal
```

---

### 2. 菲律宾MQTT服务器

**推荐配置：**
- CPU: 2核
- 内存: 4GB
- 硬盘: 50GB SSD
- 带宽: 50Mbps
- 系统: Ubuntu 22.04 LTS

#### 2.1 安装Mosquitto MQTT

```bash
# 安装Mosquitto
sudo apt install -y mosquitto mosquitto-clients

# 创建配置文件
sudo tee /etc/mosquitto/conf.d/default.conf << 'EOF'
# 监听端口
listener 1883

# 允许匿名连接（生产环境需要改为false）
allow_anonymous false

# 密码文件
password_file /etc/mosquitto/passwd

# 日志配置
log_dest file /var/log/mosquitto/mosquitto.log
log_type all

# 持久化
persistence true
persistence_location /var/lib/mosquitto/
EOF

# 创建MQTT用户
sudo mosquitto_passwd -c /etc/mosquitto/passwd admin
# 输入密码：your_secure_password

# 重启Mosquitto
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

# 验证
mosquitto_sub -h localhost -t test -u admin -P your_secure_password
```

#### 2.2 安装PostgreSQL

```bash
# 安装PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql << 'EOF'
CREATE DATABASE net_terminal;
CREATE USER net_admin WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE net_terminal TO net_admin;
\q
EOF

# 验证
psql -h localhost -U net_admin -d net_terminal -c "SELECT version();"
```

#### 2.3 初始化数据库表

```bash
# 创建初始化脚本
cat > /tmp/init_db.sql << 'EOF'
-- 设备表
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'offline',
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 设备状态表（时序数据）
CREATE TABLE IF NOT EXISTS device_status (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    network_type VARCHAR(20),
    sim_slot INTEGER,
    signal_dbm INTEGER,
    cpu_usage INTEGER,
    memory_usage INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 命令表
CREATE TABLE IF NOT EXISTS commands (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    command VARCHAR(50) NOT NULL,
    params JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_device_status_device_id ON device_status(device_id);
CREATE INDEX idx_device_status_timestamp ON device_status(timestamp);
CREATE INDEX idx_commands_device_id ON commands(device_id);
CREATE INDEX idx_commands_status ON commands(status);
EOF

# 执行初始化
psql -h localhost -U net_admin -d net_terminal -f /tmp/init_db.sql
```

---

## 📱 设备端环境配置

### 1. RV1103设备准备

**硬件要求：**
- RV1103开发板
- EC600M 4G模块（USB接口）
- 两张SIM卡（Globe/Smart）
- 网线（RJ45）
- 电源适配器

#### 1.1 系统安装

```bash
# 烧录Ubuntu 22.04 ARM64镜像到SD卡
# 使用balenaEtcher或dd命令

# 首次启动后，更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y python3 python3-pip git vim
```

#### 1.2 配置网络

```bash
# 查看网络接口
ip addr

# 配置静态IP（可选）
sudo tee /etc/netplan/01-netcfg.yaml << 'EOF'
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
EOF

sudo netplan apply
```

#### 1.3 安装Python依赖

```bash
# 安装pip包
pip3 install paho-mqtt pyserial psutil requests

# 验证安装
python3 -c "import paho.mqtt.client as mqtt; print('MQTT OK')"
```

#### 1.4 安装frpc

```bash
# 下载frpc（ARM64版本）
wget https://github.com/fatedier/frp/releases/download/v0.52.0/frp_0.52.0_linux_arm64.tar.gz

# 解压
tar -xzf frp_0.52.0_linux_arm64.tar.gz
cd frp_0.52.0_linux_arm64

# 复制到系统目录
sudo cp frpc /usr/local/bin/
sudo chmod +x /usr/local/bin/frpc

# 创建配置目录
sudo mkdir -p /etc/frp

# 验证
frpc --version
```

#### 1.5 配置EC600M模块

```bash
# 安装USB串口驱动
sudo apt install -y usb-modeswitch

# 查看USB设备
lsusb

# 查看串口设备
ls /dev/ttyUSB*

# 测试AT命令
sudo apt install -y minicom
sudo minicom -D /dev/ttyUSB2

# 在minicom中输入：
AT
AT+CSQ  # 查询信号强度
AT+COPS?  # 查询运营商
```

---

## 🛠️ 开发工具配置

### 1. Go开发环境

```bash
# 安装Go 1.21
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz

# 配置环境变量
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
source ~/.bashrc

# 验证
go version

# 配置Go代理（国内）
go env -w GOPROXY=https://goproxy.cn,direct
```

### 2. Python开发环境

```bash
# 安装Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# 创建虚拟环境
python3.11 -m venv ~/venv/net-terminal
source ~/venv/net-terminal/bin/activate

# 安装开发工具
pip install black flake8 pytest
```

### 3. VS Code远程开发

```bash
# 在本地安装VS Code
# 安装Remote-SSH插件

# 配置SSH连接
# ~/.ssh/config
Host net-server
    HostName your_server_ip
    User your_username
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

---

## 🔍 常见问题排查

### 1. Docker无法启动

```bash
# 检查Docker服务状态
sudo systemctl status docker

# 查看日志
sudo journalctl -u docker -n 50

# 重启Docker
sudo systemctl restart docker
```

### 2. MQTT连接失败

```bash
# 检查Mosquitto状态
sudo systemctl status mosquitto

# 查看日志
sudo tail -f /var/log/mosquitto/mosquitto.log

# 测试连接
mosquitto_sub -h localhost -t test -u admin -P password -v
```

### 3. PostgreSQL连接失败

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 查看日志
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# 检查监听端口
sudo netstat -tulpn | grep 5432

# 修改监听地址（如果需要远程连接）
sudo vim /etc/postgresql/14/main/postgresql.conf
# 修改：listen_addresses = '*'

sudo vim /etc/postgresql/14/main/pg_hba.conf
# 添加：host all all 0.0.0.0/0 md5

sudo systemctl restart postgresql
```

### 4. frpc连接失败

```bash
# 检查frpc配置
cat /etc/frp/frpc.toml

# 手动启动测试
frpc -c /etc/frp/frpc.toml

# 检查网络连通性
ping frps_server_ip
telnet frps_server_ip 7000
```

### 5. EC600M模块无法识别

```bash
# 检查USB设备
lsusb | grep Quectel

# 检查内核日志
dmesg | grep ttyUSB

# 重新加载USB驱动
sudo modprobe -r option
sudo modprobe option

# 检查串口权限
sudo usermod -aG dialout $USER
# 重新登录生效
```

---

## ✅ 环境验证清单

### 服务器端

- [ ] Docker和Docker Compose已安装
- [ ] 防火墙规则已配置
- [ ] Mosquitto MQTT正常运行
- [ ] PostgreSQL数据库已初始化
- [ ] frps服务正常运行
- [ ] 能通过MQTT客户端连接

### 设备端

- [ ] Ubuntu系统已安装
- [ ] Python环境已配置
- [ ] frpc已安装
- [ ] EC600M模块能识别
- [ ] 能通过AT命令查询信号
- [ ] 网络接口正常

---

## 📚 参考资料

- [Docker官方文档](https://docs.docker.com/)
- [Mosquitto文档](https://mosquitto.org/documentation/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)
- [frp文档](https://github.com/fatedier/frp)
- [EC600M AT命令手册](https://www.quectel.com/)

---

**环境配置指南完成！** 🚀
