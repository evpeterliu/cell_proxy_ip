# Luckfox程序上传 - 手动操作指南

## 问题：COM14被占用

当前无法通过远程自动上传，因为COM14串口被占用（访问被拒绝）。

## 解决方案

### 步骤1：找到并关闭占用COM14的程序

**可能占用COM14的程序：**
- PuTTY
- 串口调试助手
- Arduino IDE
- 其他串口终端软件

**查找方法：**
```powershell
# 打开PowerShell管理员
Get-Process | Where-Object {$_.MainWindowTitle -like '*COM14*'}
```

**或者直接关闭所有可疑程序：**
- 检查任务栏和系统托盘
- 关闭所有串口相关软件
- 重启计算机（最彻底的方法）

### 步骤2：运行上传脚本

**文件已准备好在：**
- `E:\claude\hello_evfwt.b64` - 程序文件（base64编码）
- `E:\claude\upload_serial.py` - Python上传脚本
- `E:\claude\upload_hello.ps1` - PowerShell上传脚本

**方法A：使用Python脚本（推荐）**
```powershell
cd E:\claude
python upload_serial.py
```

**方法B：使用PowerShell脚本**
```powershell
cd E:\claude
powershell -ExecutionPolicy Bypass -File upload_hello.ps1
```

### 步骤3：等待上传完成

- 上传时间：约5-8分钟
- 会显示进度百分比
- 完成后会自动测试程序并输出 "hello, evfwt"

## 如果还是无法访问COM14

### 检查设备管理器
1. Win+X → 设备管理器
2. 展开"端口(COM和LPT)"
3. 找到"USB-Enhanced-SERIAL CH343 (COM14)"
4. 右键 → 禁用设备 → 启用设备

### 检查端口权限
```powershell
# 以管理员身份运行PowerShell
$port = new-Object System.IO.Ports.SerialPort COM14,115200,None,8,one
$port.Open()
# 如果成功打开，说明权限没问题
$port.Close()
```

## 替代方案：使用minicom/screen（如果有WSL）

```bash
# 在WSL中
sudo apt install minicom
sudo minicom -D /dev/ttyUSB0 -b 115200

# 手动登录后粘贴base64内容（需要分段）
```

## 验证上传是否成功

程序上传成功后，Luckfox设备上会显示：
```
hello, evfwt
Program running successfully on Luckfox!
```

文件位置：`/root/hello_evfwt`

## 测试完整版程序

完整版程序（luckfox_network）在GitHub仓库中。

---

**当前状态：**
- ✅ frps服务运行正常
- ✅ frpc隧道连接成功
- ✅ Go程序已编译完成
- ✅ 上传脚本已准备好
- ❌ COM14串口被占用

**下一步：** 请在Windows上关闭占用COM14的程序，然后运行上传脚本。
