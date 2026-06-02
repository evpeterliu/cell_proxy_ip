# Luckfox Go Program

## 程序说明

这是一个在Luckfox Pico上运行的Go程序，用于测试网络连接。

### 功能
- 打印 "hello, evfwt"
- 显示系统信息（OS、架构、CPU数量）
- 列出所有网络接口及IP地址
- 测试网络连通性（连接百度、Google DNS、114 DNS）

## 编译步骤

### Windows上交叉编译

```powershell
# 进入项目目录
cd luckfox_go

# 设置交叉编译环境变量
$env:GOOS="linux"
$env:GOARCH="arm"
$env:GOARM="7"
$env:CGO_ENABLED="0"

# 编译
go build -o luckfox_network main.go
```

或使用CMD：
```cmd
cd luckfox_go
set GOOS=linux
set GOARCH=arm
set GOARM=7
set CGO_ENABLED=0
go build -o luckfox_network main.go
```

## 传输到Luckfox

### 方法1：通过网络（推荐）
```bash
scp luckfox_network root@192.168.2.112:/root/
```

### 方法2：通过Windows SSH
```powershell
scp -i .ssh/id_rsa_windows -P 16022 luckfox_network administrator@localhost:E:/claude/
# 然后通过串口传输到Luckfox
```

## 运行

```bash
# SSH登录到Luckfox
ssh root@192.168.2.112

# 添加执行权限
chmod +x /root/luckfox_network

# 运行程序
./luckfox_network
```

## 预期输出

```
=== Luckfox Network Test Program ===
hello, evfwt

OS: linux
Architecture: arm
CPU Count: 1

Network Interfaces:

[lo]
  MAC: 
  MTU: 65536
  Flags: up|loopback
  IP: 127.0.0.1/8

[eth0]
  MAC: 32:93:65:12:90:0c
  MTU: 1500
  Flags: up|broadcast|multicast
  IP: 192.168.2.112/16

=== Testing Network Connectivity ===
Testing www.baidu.com:80 ... OK
Testing 8.8.8.8:53 ... OK
Testing 114.114.114.114:53 ... OK

=== Program completed successfully ===
```
