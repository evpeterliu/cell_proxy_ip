# EC600M网络自动重连方案

> **文档版本：** v1.0  
> **创建日期：** 2026-06-01  
> **适用设备：** RV1103 + EC600M模块

---

## 📋 目录

1. [方案概述](#方案概述)
2. [AT命令详解](#at命令详解)
3. [初始化流程](#初始化流程)
4. [自动重连机制](#自动重连机制)
5. [代码实现](#代码实现)
6. [常见问题](#常见问题)

---

## 📖 方案概述

### 核心目标

- ✅ 模块开机自动拨号上网
- ✅ 网络断开自动重连
- ✅ 支持双SIM卡自动切换
- ✅ 异常情况自动恢复

### 技术方案

**使用AT+QNETDEVCTL命令实现：**
- `AT+QNETDEVCTL?` - 查询模块联网状态
- `AT+QNETDEVCTL=3,1,1` - 启用ECM模式并自动拨号

---

## 🔧 AT命令详解

### 1. AT+QNETDEVCTL? - 查询联网状态

**命令语法：**
```bash
AT+QNETDEVCTL?
```

**返回值：**
```bash
+QNETDEVCTL: <mode>,<status>,<enable>

OK
```

**参数说明：**
- **mode**: 网络设备模式（1-11）
  - `1` = QMI模式
  - `3` = ECM模式（Ethernet Control Model）
  - 其他值：1-11范围内的其他模式

- **status**: 连接状态（0-3）
  - `0` = 未连接
  - `1` = 已连接
  - `2-3` = 其他状态

- **enable**: 是否启用自动拨号（0或1）
  - `0` = 不自动拨号
  - `1` = 自动拨号

**使用示例：**
```bash
# 查询当前状态
AT+QNETDEVCTL?

# 可能的返回：
+QNETDEVCTL: 3,1,1  # ECM模式，已连接，自动拨号已启用
OK
```

---

### 2. AT+QNETDEVCTL=3,1,1 - 启用拨号上网

**命令语法：**
```bash
AT+QNETDEVCTL=<mode>,<status>,<enable>
```

**参数详解：**

**参数1 - mode（网络设备模式）：**
- `1` = QMI模式
- `3` = ECM模式（推荐用于Linux）
- 其他值：1-11范围内的其他模式

**参数2 - status（操作类型）：**
- `0` = 禁用
- `1` = 启用/连接
- `2-3` = 其他状态

**参数3 - enable（自动拨号）：**
- `0` = 不自动拨号（需要手动拨号）
- `1` = 自动拨号（推荐）

**使用示例：**
```bash
# 启用ECM模式并自动拨号
AT+QNETDEVCTL=3,1,1

# 返回：
OK

# 禁用网络设备
AT+QNETDEVCTL=3,0,0

# 返回：
OK
```

**重要说明：**
- 此命令打开模块拨号上网功能
- 设置 `enable=1` 后，模块会自动拨号
- 网络断开后会自动重连（如果enable=1）
- 需要先配置好USB网络模式和APN

---

### 3. 相关AT命令

**配置USB网络模式：**
```bash
# 查询当前模式
AT+QCFG="usbnet"

# 设置为ECM模式
AT+QCFG="usbnet",1

# 设置为QMI模式
AT+QCFG="usbnet",0

# 注意：设置后需要重启模块生效
AT+CFUN=1,1
```

**配置APN：**
```bash
# 通用APN
AT+CGDCONT=1,"IP","internet"

# 菲律宾Globe运营商
AT+CGDCONT=1,"IP","internet.globe.com.ph"

# 菲律宾Smart运营商
AT+CGDCONT=1,"IP","smartlte"
```

**启用自动附着网络：**
```bash
AT+CGATT=1
```

**查询IP地址：**
```bash
AT+CGPADDR=1

# 返回：
+CGPADDR: 1,"10.123.45.67"
OK
```

---

## 🚀 初始化流程

### 完整的初始化脚本

**创建 `/usr/bin/ec600m_init.sh`：**

```bash
#!/bin/bash

# EC600M模块初始化脚本
# 用途：配置模块并启用自动拨号

SERIAL_PORT="/dev/ttyUSB2"
INTERFACE="usb0"
LOG_FILE="/var/log/ec600m_init.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 发送AT命令
send_at() {
    local cmd=$1
    local timeout=${2:-2}
    
    log "发送AT命令: $cmd"
    echo -e "${cmd}\r" > $SERIAL_PORT
    sleep $timeout
}

# 检查命令响应
check_response() {
    local cmd=$1
    local expected=$2
    
    send_at "$cmd" 1
    
    # 读取响应（简化版，实际应该用更可靠的方法）
    response=$(timeout 2 cat $SERIAL_PORT 2>/dev/null)
    
    if echo "$response" | grep -q "$expected"; then
        log "✓ $cmd 成功"
        return 0
    else
        log "✗ $cmd 失败: $response"
        return 1
    fi
}

# 主流程
main() {
    log "========================================="
    log "开始初始化EC600M模块"
    log "========================================="
    
    # 步骤1：检查模块是否就绪
    log "步骤1：检查模块就绪状态..."
    send_at "AT"
    
    # 步骤2：配置USB网络模式为ECM
    log "步骤2：配置USB网络模式为ECM..."
    send_at "AT+QCFG=\"usbnet\",1"
    
    # 步骤3：重启模块使配置生效
    log "步骤3：重启模块..."
    send_at "AT+CFUN=1,1"
    log "等待模块重启（30秒）..."
    sleep 30
    
    # 步骤4：配置APN
    log "步骤4：配置APN..."
    send_at "AT+CGDCONT=1,\"IP\",\"internet\""
    
    # 步骤5：启用自动附着网络
    log "步骤5：启用自动附着网络..."
    send_at "AT+CGATT=1"
    
    # 步骤6：启用网络设备并自动拨号
    log "步骤6：启用网络设备并自动拨号..."
    send_at "AT+QNETDEVCTL=3,1,1" 5
    
    # 步骤7：查询联网状态
    log "步骤7：查询联网状态..."
    send_at "AT+QNETDEVCTL?"
    
    # 步骤8：查询IP地址
    log "步骤8：查询IP地址..."
    send_at "AT+CGPADDR=1"
    
    # 步骤9：配置Linux网络接口
    log "步骤9：配置网络接口..."
    
    # 等待接口出现
    for i in {1..10}; do
        if ifconfig -a | grep -q $INTERFACE; then
            log "✓ 网络接口 $INTERFACE 已出现"
            break
        fi
        log "等待网络接口出现... ($i/10)"
        sleep 2
    done
    
    # 启用接口
    log "启用网络接口..."
    ifconfig $INTERFACE up
    sleep 2
    
    # 获取IP地址
    log "获取IP地址..."
    udhcpc -i $INTERFACE -q
    sleep 3
    
    # 步骤10：验证网络连接
    log "步骤10：验证网络连接..."
    if ping -c 3 -W 5 8.8.8.8 > /dev/null 2>&1; then
        log "========================================="
        log "✓ 初始化成功！网络连接正常！"
        log "========================================="
        
        # 显示网络信息
        log "网络接口信息："
        ifconfig $INTERFACE | tee -a $LOG_FILE
        
        exit 0
    else
        log "========================================="
        log "✗ 初始化失败！网络连接异常！"
        log "========================================="
        exit 1
    fi
}

# 执行主流程
main
```

**设置权限并执行：**
```bash
chmod +x /usr/bin/ec600m_init.sh
/usr/bin/ec600m_init.sh
```

---

## 🔄 自动重连机制

### 方案1：使用AT命令自动重连（推荐）

**原理：**
- `AT+QNETDEVCTL=3,1,1` 的第三个参数 `enable=1` 表示启用自动拨号
- 模块会自动检测网络断开并重新拨号
- 无需额外的监控脚本

**优点：**
- ✅ 简单可靠
- ✅ 模块内部实现，响应快
- ✅ 无需额外代码

**缺点：**
- ⚠️ 无法自定义重连策略
- ⚠️ 无法记录详细日志

---

### 方案2：脚本监控和重连（更灵活）

**创建 `/usr/bin/network_monitor.sh`：**

```bash
#!/bin/bash

# 网络监控和自动重连脚本

# 配置参数
CHECK_INTERVAL=30  # 检查间隔（秒）
MAX_RETRY=3        # 最大重试次数
INTERFACE="usb0"   # 网络接口名称
SERIAL_PORT="/dev/ttyUSB2"
LOG_FILE="/var/log/network_monitor.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 发送AT命令
send_at() {
    echo -e "${1}\r" > $SERIAL_PORT
    sleep ${2:-2}
}

# 检查网络连接
check_network() {
    # 方法1：ping测试
    if ping -c 3 -W 5 8.8.8.8 > /dev/null 2>&1; then
        return 0
    fi
    
    # 方法2：检查接口状态
    if ! ifconfig $INTERFACE 2>/dev/null | grep -q "inet "; then
        return 1
    fi
    
    return 1
}

# 查询模块联网状态
check_module_status() {
    log "查询模块联网状态..."
    send_at "AT+QNETDEVCTL?" 1
    
    # 简化版响应检查
    # 实际应该读取串口响应并解析
    return 0
}

# 重新拨号
reconnect() {
    local retry_count=0
    
    log "========================================="
    log "开始重连流程..."
    log "========================================="
    
    while [ $retry_count -lt $MAX_RETRY ]; do
        retry_count=$((retry_count + 1))
        log "重连尝试 $retry_count/$MAX_RETRY"
        
        # 步骤1：禁用网络设备
        log "禁用网络设备..."
        send_at "AT+QNETDEVCTL=3,0,0" 2
        
        # 步骤2：重新启用并拨号
        log "重新启用并拨号..."
        send_at "AT+QNETDEVCTL=3,1,1" 5
        
        # 步骤3：重新配置网络接口
        log "重新配置网络接口..."
        ifconfig $INTERFACE down 2>/dev/null
        sleep 1
        ifconfig $INTERFACE up 2>/dev/null
        sleep 2
        
        # 步骤4：获取IP地址
        log "获取IP地址..."
        udhcpc -i $INTERFACE -q 2>/dev/null
        sleep 3
        
        # 步骤5：检查是否成功
        if check_network; then
            log "========================================="
            log "✓ 重连成功！"
            log "========================================="
            return 0
        fi
        
        log "✗ 重连失败，等待后重试..."
        sleep 10
    done
    
    log "========================================="
    log "✗ 重连失败，已达到最大重试次数"
    log "========================================="
    return 1
}

# 主循环
main() {
    log "========================================="
    log "网络监控服务启动"
    log "检查间隔: ${CHECK_INTERVAL}秒"
    log "========================================="
    
    while true; do
        if ! check_network; then
            log "⚠ 网络连接断开，开始重连..."
            
            # 先检查模块状态
            check_module_status
            
            # 尝试重连
            if reconnect; then
                log "✓ 网络已恢复"
            else
                log "✗ 网络恢复失败，将在下次检查时重试"
            fi
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# 启动主循环
main
```

**设置开机自启动：**

创建 `/etc/systemd/system/network-monitor.service`：

```ini
[Unit]
Description=EC600M Network Monitor and Auto Reconnect Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/network_monitor.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**启用服务：**
```bash
chmod +x /usr/bin/network_monitor.sh
systemctl daemon-reload
systemctl enable network-monitor
systemctl start network-monitor

# 查看服务状态
systemctl status network-monitor

# 查看日志
journalctl -u network-monitor -f
```

---

### 方案3：Python实现（最强大）

**创建 `/usr/bin/network_manager.py`：**

```python
#!/usr/bin/env python3
"""
EC600M网络管理器
功能：监控网络状态，自动重连
"""

import serial
import time
import subprocess
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='/var/log/network_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EC600MNetworkManager:
    def __init__(self):
        self.serial_port = '/dev/ttyUSB2'
        self.baud_rate = 115200
        self.interface = 'usb0'
        self.check_interval = 30
        self.max_retry = 3
        
    def send_at_command(self, command, timeout=5):
        """发送AT命令并获取响应"""
        try:
            with serial.Serial(self.serial_port, self.baud_rate, timeout=timeout) as ser:
                # 清空缓冲区
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                
                # 发送命令
                ser.write(f"{command}\r\n".encode())
                time.sleep(0.5)
                
                # 读取响应
                response = ""
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if ser.in_waiting > 0:
                        response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                        time.sleep(0.1)
                    else:
                        if response and ("OK" in response or "ERROR" in response):
                            break
                        time.sleep(0.1)
                
                logging.info(f"AT命令: {command} -> {response.strip()}")
                return response
        except Exception as e:
            logging.error(f"发送AT命令失败: {e}")
            return None
    
    def check_module_status(self):
        """查询模块联网状态"""
        response = self.send_at_command("AT+QNETDEVCTL?")
        if response and "+QNETDEVCTL" in response:
            logging.info(f"模块状态: {response.strip()}")
            return True
        return False
    
    def check_network(self):
        """检查网络连接"""
        # 方法1：ping测试
        try:
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '5', '8.8.8.8'],
                capture_output=True,
                timeout=20
            )
            if result.returncode == 0:
                return True
        except Exception as e:
            logging.error(f"Ping测试失败: {e}")
        
        # 方法2：检查接口IP
        try:
            result = subprocess.run(
                ['ifconfig', self.interface],
                capture_output=True,
                text=True
            )
            if 'inet ' in result.stdout:
                return True
        except Exception as e:
            logging.error(f"接口检查失败: {e}")
        
        return False
    
    def disable_network(self):
        """禁用网络设备"""
        logging.info("禁用网络设备...")
        self.send_at_command("AT+QNETDEVCTL=3,0,0")
        time.sleep(2)
    
    def enable_network(self):
        """启用网络设备并拨号"""
        logging.info("启用网络设备并拨号...")
        self.send_at_command("AT+QNETDEVCTL=3,1,1")
        time.sleep(5)
    
    def configure_interface(self):
        """配置网络接口"""
        logging.info("配置网络接口...")
        
        # 关闭接口
        subprocess.run(['ifconfig', self.interface, 'down'], 
                      stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # 启用接口
        subprocess.run(['ifconfig', self.interface, 'up'],
                      stderr=subprocess.DEVNULL)
        time.sleep(2)
        
        # 获取IP地址
        subprocess.run(['udhcpc', '-i', self.interface, '-q'],
                      stderr=subprocess.DEVNULL)
        time.sleep(3)
    
    def reconnect(self):
        """重新连接网络"""
        logging.info("=" * 50)
        logging.info("开始重连流程...")
        logging.info("=" * 50)
        
        for attempt in range(1, self.max_retry + 1):
            logging.info(f"重连尝试 {attempt}/{self.max_retry}")
            
            # 禁用网络
            self.disable_network()
            
            # 启用网络
            self.enable_network()
            
            # 配置接口
            self.configure_interface()
            
            # 检查连接
            if self.check_network():
                logging.info("=" * 50)
                logging.info("✓ 重连成功！")
                logging.info("=" * 50)
                return True
            
            logging.warning(f"✗ 重连失败，等待后重试...")
            time.sleep(10)
        
        logging.error("=" * 50)
        logging.error("✗ 重连失败，已达到最大重试次数")
        logging.error("=" * 50)
        return False
    
    def run(self):
        """主循环"""
        logging.info("=" * 50)
        logging.info("EC600M网络管理服务启动")
        logging.info(f"检查间隔: {self.check_interval}秒")
        logging.info("=" * 50)
        
        while True:
            try:
                if not self.check_network():
                    logging.warning("⚠ 网络连接断开，开始重连...")
                    
                    # 检查模块状态
                    self.check_module_status()
                    
                    # 尝试重连
                    if self.reconnect():
                        logging.info("✓ 网络已恢复")
                    else:
                        logging.error("✗ 网络恢复失败")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logging.info("服务停止")
                break
            except Exception as e:
                logging.error(f"主循环异常: {e}")
                time.sleep(10)

if __name__ == "__main__":
    manager = EC600MNetworkManager()
    manager.run()
```

**安装依赖：**
```bash
pip3 install pyserial
```

**设置权限并测试：**
```bash
chmod +x /usr/bin/network_manager.py
python3 /usr/bin/network_manager.py
```

---

## ❓ 常见问题

### 问题1：AT+QNETDEVCTL返回ERROR

**可能原因：**
- USB网络模式未正确配置
- 模块不支持该命令
- 参数错误

**解决方案：**
```bash
# 1. 查询当前USB网络模式
AT+QCFG="usbnet"

# 2. 设置为ECM模式
AT+QCFG="usbnet",1

# 3. 重启模块
AT+CFUN=1,1

# 4. 等待30秒后再执行
AT+QNETDEVCTL=3,1,1
```

---

### 问题2：执行命令后无法获取IP

**解决方案：**
```bash
# 1. 检查网络接口是否出现
ifconfig -a

# 2. 手动启用接口
ifconfig usb0 up

# 3. 使用dhclient获取IP
dhclient usb0

# 4. 或者使用udhcpc
udhcpc -i usb0

# 5. 检查IP地址
ifconfig usb0
```

---

### 问题3：网络经常断开

**解决方案：**
1. 使用自动重连脚本
2. 检查信号强度：`AT+CSQ`
3. 检查SIM卡状态：`AT+CPIN?`
4. 启用自动附着：`AT+CGATT=1`
5. 检查APN配置是否正确

---

### 问题4：模块重启后配置丢失

**解决方案：**
```bash
# 将初始化脚本设置为开机自启动

# 方法1：使用systemd
cat > /etc/systemd/system/ec600m-init.service << EOF
[Unit]
Description=EC600M Initialization Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/ec600m_init.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ec600m-init
systemctl start ec600m-init

# 方法2：使用rc.local
echo "/usr/bin/ec600m_init.sh &" >> /etc/rc.local
chmod +x /etc/rc.local
```

---

### 问题5：如何查看详细日志

**查看初始化日志：**
```bash
cat /var/log/ec600m_init.log
```

**查看监控日志：**
```bash
cat /var/log/network_monitor.log

# 或者实时查看
tail -f /var/log/network_monitor.log
```

**查看systemd服务日志：**
```bash
journalctl -u network-monitor -f
```

---

## 📊 推荐方案

### 最佳实践

**初始化阶段：**
1. ✅ 使用 `ec600m_init.sh` 脚本初始化模块
2. ✅ 配置为开机自启动
3. ✅ 启用 `AT+QNETDEVCTL=3,1,1` 自动拨号

**运行阶段：**
1. ✅ 使用Python脚本 `network_manager.py` 监控网络
2. ✅ 配置为systemd服务
3. ✅ 定期查看日志

**优先级：**
- 🔴 **P0**：基础拨号功能（AT+QNETDEVCTL=3,1,1）
- 🔴 **P0**：自动重连机制
- 🟡 **P1**：网络状态监控
- 🟢 **P2**：详细日志和统计

---

## 📚 参考资料

1. [Quectel TCP/IP Application Note](https://www.scribd.com/document/847058744/quectel-ec200ueg800geg91xueg915g-series-tcpip-application-note-v1-3)
2. [Quectel Forums - AT+QNETDEVCTL Discussion](https://forums.quectel.com/t/eg800g-q-at-qnetdevctl/29597)
3. [Quectel Linux USB Driver](https://github.com/bacnh85/Quectel_Linux_USB_Driver)
4. [ECM Mode Setup Guide](https://forums.quectel.com/t/reliably-setting-up-apn-for-eg915-in-ecm-mode-with-at-commands/43804)
5. [OpenWrt QMI Dialing](https://www.openwrt.pro/post-546.html)

---

**文档结束**

> 如有疑问，请联系技术负责人
