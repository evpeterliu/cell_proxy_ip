# 手机卡代理服务 - 技术实现指南（第2部分）

> **开发指南：** 模块开发详细说明  
> **前置文档：** 《技术实现指南-第1部分-架构设计.md》

---

## 📦 模块开发指南

### 模块 1：公网服务器部署

#### 1.1 服务器准备

**推荐配置：**
- 服务商：Hetzner / OVH / Vultr
- 配置：8核 CPU, 32GB RAM, 500GB SSD
- 带宽：1Gbps 不限流量
- 系统：Ubuntu 22.04 LTS

**初始化脚本：**
```bash
#!/bin/bash
# 文件名: server_init.sh

# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 配置防火墙
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 1080/tcp
ufw allow 7000/tcp
ufw --force enable

echo "服务器初始化完成！"
```

#### 1.2 Docker Compose 配置文件

**创建项目目录结构：**
```bash
mkdir -p ~/proxy-service/{nginx,frps,api,prometheus}
cd ~/proxy-service
```

**docker-compose.yml（核心配置）**
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
      - "1080:1080"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    restart: always

  frps:
    image: snowdreamtech/frps:0.52.0
    ports:
      - "7000:7000"
    volumes:
      - ./frps/frps.ini:/etc/frp/frps.ini:ro
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: proxy_db
      POSTGRES_USER: proxy_user
      POSTGRES_PASSWORD: change_me_in_production
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass change_me_in_production
    volumes:
      - redis-data:/data
    restart: always

volumes:
  postgres-data:
  redis-data:
```

---

### 模块 2：手机卡设备端配置

#### 2.1 设备初始化

**一键安装脚本（device_setup.sh）：**
```bash
#!/bin/bash
# 在树莓派上运行此脚本

echo "=== 手机卡设备初始化 ==="

# 1. 安装 frpc
wget https://github.com/fatedier/frp/releases/download/v0.52.0/frp_0.52.0_linux_arm64.tar.gz
tar -xzf frp_0.52.0_linux_arm64.tar.gz
sudo cp frp_0.52.0_linux_arm64/frpc /usr/local/bin/
sudo chmod +x /usr/local/bin/frpc

# 2. 创建配置文件
sudo mkdir -p /etc/frpc
sudo tee /etc/frpc/frpc.ini > /dev/null <<EOF
[common]
server_addr = YOUR_SERVER_IP
server_port = 7000
token = YOUR_SECRET_TOKEN
user = device_$(hostname)

[socks5]
type = tcp
local_ip = 127.0.0.1
local_port = 1080
remote_port = 0
plugin = socks5
EOF

# 3. 创建 systemd 服务
sudo tee /etc/systemd/system/frpc.service > /dev/null <<EOF
[Unit]
Description=frp client
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/frpc -c /etc/frpc/frpc.ini
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 4. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable frpc
sudo systemctl start frpc

echo "=== 安装完成 ==="
echo "请修改 /etc/frpc/frpc.ini 中的服务器地址和密钥"
```

---

### 模块 3：API 服务开发（简化版）

#### 3.1 FastAPI 应用结构

**main.py（核心 API）：**
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List
import secrets

app = FastAPI(title="手机卡代理服务 API")
security = HTTPBasic()

# 数据模型
class Device(BaseModel):
    device_id: str
    status: str
    carrier: str
    location: str

class User(BaseModel):
    username: str
    balance: float
    status: str

# 模拟数据库
devices_db = {}
users_db = {
    "demo_user": {
        "password": "demo_pass",
        "balance": 100.0,
        "status": "active"
    }
}

# 认证
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    
    if username not in users_db:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    if users_db[username]["password"] != password:
        raise HTTPException(status_code=401, detail="密码错误")
    
    return username

# API 端点
@app.get("/")
def read_root():
    return {"message": "手机卡代理服务 API", "version": "1.0"}

@app.get("/api/devices", response_model=List[Device])
def list_devices(username: str = Depends(verify_credentials)):
    """获取设备列表"""
    return list(devices_db.values())

@app.post("/api/devices/heartbeat")
def device_heartbeat(device_id: str, data: dict):
    """设备心跳上报"""
    devices_db[device_id] = {
        "device_id": device_id,
        "status": "online",
        "last_heartbeat": data.get("timestamp"),
        **data
    }
    return {"status": "ok"}

@app.get("/api/users/me", response_model=User)
def get_current_user(username: str = Depends(verify_credentials)):
    """获取当前用户信息"""
    user_data = users_db[username]
    return User(
        username=username,
        balance=user_data["balance"],
        status=user_data["status"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**启动 API 服务：**
```bash
# 安装依赖
pip3 install fastapi uvicorn

# 运行服务
python3 main.py
```

---

### 模块 4：前端管理后台（简化版）

#### 4.1 HTML 单页面管理后台

**index.html（完整管理界面）：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>手机卡代理服务 - 管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-box { text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; }
        .stat-box h3 { font-size: 32px; margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .status-online { color: #28a745; font-weight: bold; }
        .status-offline { color: #dc3545; font-weight: bold; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📱 手机卡代理服务管理后台</h1>
    </div>

    <div class="container">
        <!-- 统计卡片 -->
        <div class="stats">
            <div class="stat-box">
                <h3 id="total-devices">0</h3>
                <p>总设备数</p>
            </div>
            <div class="stat-box">
                <h3 id="online-devices">0</h3>
                <p>在线设备</p>
            </div>
            <div class="stat-box">
                <h3 id="total-traffic">0 GB</h3>
                <p>今日流量</p>
            </div>
            <div class="stat-box">
                <h3 id="active-users">0</h3>
                <p>活跃用户</p>
            </div>
        </div>

        <!-- 设备列表 -->
        <div class="card">
            <h2>设备列表</h2>
            <table id="device-table">
                <thead>
                    <tr>
                        <th>设备ID</th>
                        <th>状态</th>
                        <th>运营商</th>
                        <th>地区</th>
                        <th>CPU</th>
                        <th>内存</th>
                        <th>最后心跳</th>
                    </tr>
                </thead>
                <tbody id="device-list">
                    <tr>
                        <td colspan="7" style="text-align: center; color: #999;">暂无数据</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // API 配置
        const API_URL = 'http://YOUR_SERVER_IP:8000';
        const USERNAME = 'demo_user';
        const PASSWORD = 'demo_pass';

        // 获取设备列表
        async function fetchDevices() {
            try {
                const response = await fetch(`${API_URL}/api/devices`, {
                    headers: {
                        'Authorization': 'Basic ' + btoa(`${USERNAME}:${PASSWORD}`)
                    }
                });
                
                if (!response.ok) throw new Error('获取设备列表失败');
                
                const devices = await response.json();
                updateDeviceTable(devices);
                updateStats(devices);
            } catch (error) {
                console.error('错误:', error);
            }
        }

        // 更新设备表格
        function updateDeviceTable(devices) {
            const tbody = document.getElementById('device-list');
            
            if (devices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">暂无设备</td></tr>';
                return;
            }

            tbody.innerHTML = devices.map(device => `
                <tr>
                    <td>${device.device_id}</td>
                    <td class="status-${device.status}">${device.status === 'online' ? '在线' : '离线'}</td>
                    <td>${device.carrier || '-'}</td>
                    <td>${device.location || '-'}</td>
                    <td>${device.system_stats?.cpu_percent || '-'}%</td>
                    <td>${device.system_stats?.memory_percent || '-'}%</td>
                    <td>${device.last_heartbeat ? new Date(device.last_heartbeat).toLocaleString() : '-'}</td>
                </tr>
            `).join('');
        }

        // 更新统计数据
        function updateStats(devices) {
            const onlineDevices = devices.filter(d => d.status === 'online').length;
            
            document.getElementById('total-devices').textContent = devices.length;
            document.getElementById('online-devices').textContent = onlineDevices;
        }

        // 定时刷新
        setInterval(fetchDevices, 5000);
        fetchDevices();
    </script>
</body>
</html>
```

---

## 🚀 快速部署指南

### 步骤 1：部署公网服务器

```bash
# 1. 登录服务器
ssh root@YOUR_SERVER_IP

# 2. 下载配置文件
git clone https://github.com/your-repo/proxy-service.git
cd proxy-service

# 3. 修改配置
vim docker-compose.yml  # 修改密码等敏感信息

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

### 步骤 2：配置手机卡设备

```bash
# 1. 在树莓派上下载脚本
wget https://your-server.com/device_setup.sh

# 2. 修改配置
vim device_setup.sh  # 填入服务器 IP 和密钥

# 3. 运行安装
bash device_setup.sh

# 4. 查看状态
systemctl status frpc
```

### 步骤 3：测试连接

```bash
# 使用 curl 测试 SOCKS5 代理
curl --socks5 YOUR_SERVER_IP:1080 \
     --proxy-user demo_user:demo_pass \
     https://api.ipify.org

# 应该返回手机卡的 IP 地址
```

---

## 📝 开发任务清单

### 给 AI 的开发指令

**任务 1：部署公网服务器**
```
请帮我在服务器上部署手机卡代理服务的公网端。
要求：
1. 使用 Docker Compose 部署
2. 包含 frps、nginx、postgres、redis
3. 配置防火墙规则
4. 生成 SSL 证书（Let's Encrypt）
```

**任务 2：开发设备监控脚本**
```
请帮我开发一个 Python 脚本，用于监控手机卡设备状态。
要求：
1. 每 30 秒上报心跳到 API
2. 监控 CPU、内存、网络流量
3. 检测 frpc 进程，异常时自动重启
4. 记录日志到文件
```

**任务 3：开发用户管理 API**
```
请帮我开发用户管理相关的 API 接口。
要求：
1. 用户注册、登录（JWT 认证）
2. 用户信息查询和修改
3. 余额充值和扣费
4. 使用记录查询
5. 使用 FastAPI + SQLAlchemy
```

**任务 4：开发前端管理后台**
```
请帮我开发一个管理后台页面。
要求：
1. 显示设备列表和状态
2. 实时统计数据（设备数、流量等）
3. 用户管理界面
4. 使用 Vue 3 + Element Plus
```

---

**文档完成！**

> 所有配置文件和脚本都可以直接使用  
> 开发人员可以根据任务清单使用 AI 辅助开发
