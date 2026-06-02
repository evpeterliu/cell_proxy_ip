#!/bin/bash

# 测试配置
PROXY_HOST="codex.adusun.com"
START_PORT=21880
END_PORT=21895
TEST_URL="https://api.ipify.org"
TIMEOUT=10    # curl超时时间

# 设备信息映射（设备ID -> 手机号 -> 端口）
declare -A DEVICE_INFO
DEVICE_INFO[21880]="GWOB2E8520D5D22 | 639304148539"
DEVICE_INFO[21881]="GWUF6AE1E818E9E | 639090775532"
DEVICE_INFO[21882]="GWU0EAAD409B83D | 639120518497"
DEVICE_INFO[21883]="GWUC2D4C44638A3 | 639096134226"
DEVICE_INFO[21884]="GWU5ECB30A9C6E8 | 639303320813"
DEVICE_INFO[21885]="GWU4696A45132E3 | 09931250903"
DEVICE_INFO[21886]="GWU3EB8ADCD4725 | 09931250901"
DEVICE_INFO[21887]="GWU2EBF4EC00C59 | 09931250896"
DEVICE_INFO[21888]="GWUA246A37EADA9 | 09931250899"
DEVICE_INFO[21889]="GWU7A51D87F978F | 09931250913"
DEVICE_INFO[21890]="GWUBE59FC5184DD | 09931250921"
DEVICE_INFO[21891]="GWU16BF81B94162 | 09931250897"
DEVICE_INFO[21892]="GWU8260650C871B | 09931250935"
DEVICE_INFO[21893]="GWUF609CB1992AB | 09931250929"
DEVICE_INFO[21894]="GWUE67A36A31612 | 09931250919"
DEVICE_INFO[21895]="GWU12F414722383 | 09931250902"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "SOCKS5 代理端口测试（带设备信息）"
echo "代理服务器: $PROXY_HOST"
echo "端口范围: $START_PORT - $END_PORT"
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 存储结果
declare -A port_status
declare -A port_ips

# 测试所有端口
for port in $(seq $START_PORT $END_PORT); do
    proxy_url="socks5h://$PROXY_HOST:$port"

    # 测试连接并获取IP
    ip=$(curl --proxy "$proxy_url" \
              --connect-timeout $TIMEOUT \
              --max-time $((TIMEOUT + 5)) \
              -s "$TEST_URL" 2>/dev/null)

    device_info="${DEVICE_INFO[$port]}"

    if [ $? -eq 0 ] && [ -n "$ip" ]; then
        # 端口通
        echo -e "${GREEN}✓ 端口 $port${NC}"
        echo -e "  设备: ${BLUE}${device_info}${NC}"
        echo -e "  IP: ${GREEN}${ip}${NC}"
        port_status[$port]="通"
        port_ips[$port]="$ip"
    else
        # 端口不通
        echo -e "${RED}✗ 端口 $port${NC}"
        echo -e "  设备: ${device_info}"
        echo -e "  状态: ${RED}不通${NC}"
        port_status[$port]="不通"
    fi
    echo ""
done

# 汇总结果
echo "=========================================="
echo "测试完成 - 汇总报告"
echo "=========================================="
echo ""

echo "✅ 可用设备："
echo "---"
available_count=0
for port in $(seq $START_PORT $END_PORT); do
    if [ "${port_status[$port]}" == "通" ]; then
        available_count=$((available_count + 1))
        ip="${port_ips[$port]}"
        device_info="${DEVICE_INFO[$port]}"

        echo -e "${GREEN}[$available_count] 端口 $port - ${device_info}${NC}"
        echo "    IP: $ip"
        echo ""
    fi
done

echo "---"
echo ""
echo "❌ 不可用设备："
echo "---"
unavailable_count=0
for port in $(seq $START_PORT $END_PORT); do
    if [ "${port_status[$port]}" != "通" ]; then
        unavailable_count=$((unavailable_count + 1))
        device_info="${DEVICE_INFO[$port]}"
        echo -e "${RED}[$unavailable_count] 端口 $port - ${device_info}${NC}"
    fi
done

echo ""
echo "=========================================="
echo "统计信息："
echo "  总设备数: $((END_PORT - START_PORT + 1))"
echo "  在线设备: $available_count"
echo "  离线设备: $unavailable_count"
echo "  在线率: $(awk "BEGIN {printf \"%.1f%%\", ($available_count / $((END_PORT - START_PORT + 1))) * 100}")"
echo "=========================================="
