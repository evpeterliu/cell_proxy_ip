# Luckfox Go 程序部署指南

## 当前状态

✅ **已完成：**
- Go程序已编译完成（ARM32架构）
- 两个版本：
  - `luckfox_network` (2.6MB) - 完整版，包含网络测试
  - `hello_evfwt` (1.2MB) - 简化版，仅打印 "hello, evfwt"

## 方案：通过串口上传程序

由于SSH隧道临时断开，使用串口base64传输方式。

### 步骤1：获取编译好的程序

编译好的程序位置：
```
/workspace/cell_proxy_ip/luckfox_go/hello_evfwt
/workspace/cell_proxy_ip/luckfox_go/luckfox_network
```

Base64编码文件：
```
/workspace/cell_proxy_ip/luckfox_go/hello_evfwt.b64 (1.7MB)
/workspace/cell_proxy_ip/luckfox_go/luckfox_network.b64 (3.6MB)
```

### 步骤2：传输文件到Windows

**选项A：通过SSH隧道（推荐，需要先恢复隧道）**
```bash
scp -i ~/.ssh/id_rsa_windows -P 16022 \
  /workspace/cell_proxy_ip/luckfox_go/hello_evfwt.b64 \
  administrator@localhost:E:/claude/
```

**选项B：手动复制**
1. 从GitHub仓库下载base64文件
2. 或者重建SSH隧道后传输

### 步骤3：在Windows上运行上传脚本

```powershell
cd E:\claude
powershell -ExecutionPolicy Bypass -File upload_hello.ps1
```

脚本会：
1. 通过COM14串口登录Luckfox
2. 分块传输base64内容（400字节/块）
3. 在Luckfox上解码为二进制
4. 设置可执行权限
5. 测试运行程序

### 步骤4：验证程序运行

程序会输出：
```
hello, evfwt
Program running successfully on Luckfox!
```

## 预计传输时间

- hello_evfwt (1.2MB): 约5-8分钟
- luckfox_network (2.6MB): 约10-15分钟

传输速度取决于串口115200波特率和base64编码开销。

## 手动操作方法（不使用脚本）

如果PowerShell脚本有问题，可以手动通过串口操作：

### 1. 使用PuTTY连接COM14
- Serial line: COM14
- Speed: 115200
- 登录: root/luckfox

### 2. 手动传输（小文件）
```bash
# 在Luckfox上
cat > /root/test.txt << 'EOF'
hello, evfwt
EOF

chmod +x /root/test.txt
cat /root/test.txt
```

### 3. 使用ZMODEM传输（如果可用）
```bash
# 在Luckfox上
rz
# 然后在PuTTY中选择文件发送
```

## 替代方案：通过网络传输

如果Luckfox的SSH服务已启用：

```bash
# 检查SSH服务
ps aux | grep sshd

# 如果有SSH，直接scp
scp hello_evfwt root@192.168.2.112:/root/

# SSH登录测试
ssh root@192.168.2.112
./hello_evfwt
```

## 完整版程序功能

`luckfox_network` 程序会：
1. 打印 "hello, evfwt"
2. 显示系统信息（OS、架构、CPU）
3. 列出所有网络接口和IP地址
4. 测试网络连通性：
   - www.baidu.com:80
   - 8.8.8.8:53
   - 114.114.114.114:53

## 当前障碍

❌ **SSH隧道断开** - 无法直接从Linux workspace传输到Windows
- 解决方案1: 手动下载base64文件到Windows
- 解决方案2: 重建SSH隧道
- 解决方案3: 直接使用串口PowerShell脚本

## 下一步

请告诉我：
1. 是否需要我创建SSH隧道修复脚本？
2. 还是你直接在Windows上运行PowerShell脚本？
3. 或者使用其他传输方法？

---

**创建时间：** 2026-06-02  
**程序位置：** /workspace/cell_proxy_ip/luckfox_go/  
**目标设备：** Luckfox Pico @ COM14 (192.168.2.112)
