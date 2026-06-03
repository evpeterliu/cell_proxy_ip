# SOCKS5监控系统

**说明：** SOCKS5相关的所有监控、检测和文档已迁移到独立分支

---

## 📍 访问方式

### 查看SOCKS5监控系统

```bash
# 切换到socks5-check分支
git checkout socks5-check
```

### 在线查看

**GitHub分支链接：**  
https://github.com/evpeterliu/cell_proxy_ip/tree/socks5-check

---

## 📁 socks5-check分支内容

```
socks5-check/
├── README.md              # 总览和快速开始
├── reports/               # 检测报告（按日期命名）
│   ├── 2026-06-03_device_mapping.md
│   └── 2026-06-03_status.md
├── scripts/               # 检测脚本
│   ├── quick_socks5_check.py
│   └── quick_ip.py
├── docs/                  # 文档
│   ├── server-access.md         # 服务器访问指南
│   └── monitoring-guide.md      # 监控系统指南
└── archive/               # 历史报告
```

---

## 🎯 为什么独立分支？

1. **分离关注点** - SOCKS5监控与主项目代码分离
2. **便于查找** - 所有SOCKS5相关文件集中在一个分支
3. **独立维护** - 检测报告更新不影响主代码库
4. **清晰结构** - main分支专注项目代码和需求文档

---

## 🚀 快速操作

### 查看最新检测报告

```bash
git checkout socks5-check
cat socks5-check/reports/$(ls -t socks5-check/reports/ | head -1)
```

### 执行检测

```bash
# 在socks5-check分支
ssh -i ~/.ssh/server_key root@203.3.113.133 'for port in {21880..21896}; do \
    echo -n "端口 $port: "; \
    ip=$(timeout 5 curl -x socks5://ppp:ppp@codex.adusun.com:$port -s https://ip.sb 2>/dev/null); \
    [ -n "$ip" ] && echo "✅ $ip" || echo "❌ 不可用"; \
    sleep 0.5; \
done'
```

### 切换回主分支

```bash
git checkout main
```

---

## 📊 最新状态（2026-06-03）

- **在线设备：** 6/17台（35.3%）
- **推荐端口：** 21883（最稳定）
- **服务器：** 203.3.113.133（中转）+ codex.adusun.com（SOCKS5）

**详细信息：** 请切换到 `socks5-check` 分支查看

---

## 📞 相关链接

- **socks5-check分支：** https://github.com/evpeterliu/cell_proxy_ip/tree/socks5-check
- **主分支（当前）：** https://github.com/evpeterliu/cell_proxy_ip/tree/main
- **创建PR：** https://github.com/evpeterliu/cell_proxy_ip/pull/new/socks5-check

---

**最后更新：** 2026-06-03  
**分支创建时间：** 2026-06-03
