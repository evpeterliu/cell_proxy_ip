# SOCKS5监控系统

**说明：** SOCKS5监控系统已迁移到独立仓库

---

## 📍 新仓库地址

**GitHub：** https://github.com/evpeterliu/socks5_port_check

**克隆命令：**
```bash
git clone https://github.com/evpeterliu/socks5_port_check.git
```

---

## 📁 仓库内容

```
socks5_port_check/
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

## 🎯 为什么独立仓库？

1. **完全分离** - SOCKS5监控与主项目完全独立
2. **专注功能** - 仓库只关注SOCKS5端口监控
3. **便于查找** - 不需要切换分支，直接访问
4. **独立维护** - 有自己的Issues、PRs和版本管理
5. **清晰职责** - cell_proxy_ip专注硬件项目，socks5_port_check专注监控

---

## 🚀 快速操作

### 查看最新检测报告

```bash
git clone https://github.com/evpeterliu/socks5_port_check.git
cd socks5_port_check
cat reports/$(ls -t reports/ | head -1)
```

### 执行检测

```bash
ssh -i ~/.ssh/server_key root@203.3.113.133 'for port in {21880..21896}; do \
    echo -n "端口 $port: "; \
    ip=$(timeout 5 curl -x socks5://ppp:ppp@codex.adusun.com:$port -s https://ip.sb 2>/dev/null); \
    [ -n "$ip" ] && echo "✅ $ip" || echo "❌ 不可用"; \
    sleep 0.5; \
done'
```

---

## 📊 最新状态（2026-06-03）

- **在线设备：** 6/17台（35.3%）
- **推荐端口：** 21883（最稳定）
- **服务器：** 203.3.113.133（中转）+ codex.adusun.com（SOCKS5）

**详细信息：** 访问 https://github.com/evpeterliu/socks5_port_check

---

## 📞 相关链接

- **SOCKS5监控仓库：** https://github.com/evpeterliu/socks5_port_check
- **主项目仓库：** https://github.com/evpeterliu/cell_proxy_ip
- **提交Issue：** https://github.com/evpeterliu/socks5_port_check/issues

---

## 🔄 迁移说明

原来的 `socks5-check` 分支已废弃，所有内容已迁移到独立仓库 `socks5_port_check`。

如果你本地还有旧分支，可以删除：
```bash
git branch -d socks5-check
```

---

**最后更新：** 2026-06-03  
**迁移时间：** 2026-06-03  
**新仓库创建：** 2026-06-03
