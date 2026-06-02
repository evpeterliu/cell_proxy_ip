# Luckfox Pico - NET终端连接配置

## 设备信息

- **设备型号：** Luckfox Pico (瑞芯微 RV1106)
- **系统：** Linux luckfox 5.10.160 (armv7l)
- **主机名：** luckfox
- **串口：** COM14 (USB-Enhanced-SERIAL CH343)
- **波特率：** 115200

## 网络配置

| 项目 | 值 |
|------|-----|
| IP地址 | 192.168.2.112 |
| 子网掩码 | 255.255.0.0 (/16) |
| 网关 | 192.168.2.1 |
| MAC地址 | 32:93:65:12:90:0C |

## 登录信息

- **用户名：** root
- **密码：** luckfox

## 使用方法

### 通过串口执行命令

使用 `scripts/luckfox_serial.ps1` 脚本：

```powershell
# 在Windows上执行
cd E:\claude
powershell -ExecutionPolicy Bypass -File luckfox_serial.ps1 "uname -a"
```

### 常用命令示例

```powershell
# 查看系统信息
.\luckfox_serial.ps1 "uname -a"

# 查看网络配置
.\luckfox_serial.ps1 "ifconfig"

# 查看磁盘使用
.\luckfox_serial.ps1 "df -h"

# 查看进程
.\luckfox_serial.ps1 "ps aux"

# 查看内存
.\luckfox_serial.ps1 "free -m"
```

## 文件传输

### 通过网络传输（推荐）

由于设备有IP地址 192.168.2.112，可以使用scp/sftp：

```bash
# 上传文件到Luckfox
scp file.txt root@192.168.2.112:/root/

# 下载文件
scp root@192.168.2.112:/root/file.txt ./
```

### 通过串口传输（小文件）

使用base64编码通过串口传输：

```powershell
# 编码文件并通过串口发送
$content = [Convert]::ToBase64String([IO.File]::ReadAllBytes("file.bin"))
.\luckfox_serial.ps1 "echo $content | base64 -d > /root/file.bin"
```

---

**创建时间：** 2026-06-02  
**串口：** COM14 @ 115200  
**IP：** 192.168.2.112
