# 给用户的简单测试指令

## 🎯 请你运行以下命令测试Luckfox程序

### 方法1：一键测试（推荐）

在Windows PowerShell或CMD中复制粘贴运行：

```cmd
ssh root@192.168.2.112
```

**密码：** `luckfox`

登录后，依次运行以下命令：

```bash
# 测试1: Ultra simple版本 (GOARM=5)
/oem/hello_ultra

# 如果上面段错误，测试2:
/oem/hello_arm5

# 如果还是段错误，测试3:
/root/hello_evfwt
```

**期望输出：**
```
hello, evfwt
```

---

### 方法2：不登录直接测试

如果你的SSH客户端支持密码，运行：

```cmd
ssh root@192.168.2.112 "/oem/hello_ultra"
```

输入密码 `luckfox`，应该直接看到输出。

---

### 方法3：检查文件是否存在

```cmd
ssh root@192.168.2.112 "ls -lh /oem/hello_* /root/hello_*"
```

应该看到：
```
-rwxr-xr-x    1 root     root      1.1M Jun  2 12:xx /oem/hello_ultra
-rwxr-xr-x    1 root     root      1.3M Jun  2 12:xx /oem/hello_arm5
-rwxr-xr-x    1 root     root      336K Jun  2 12:xx /root/hello_evfwt
```

---

## 📋 测试结果判断

✅ **成功：** 看到 `hello, evfwt` 输出
❌ **失败：** 看到 `Segmentation fault`
❓ **文件不存在：** 看到 `not found` 或 `No such file`

请告诉我你看到的输出结果！
