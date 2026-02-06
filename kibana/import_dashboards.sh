#!/bin/bash

# OneNet 物联网设备 Dashboard 导入脚本
# Kibana 版本：8.12.0
# 需要在服务器上运行此脚本

KIBANA_URL="${KIBANA_URL:-http://101.35.135.63:5601}"
DASHBOARDS_DIR="$(dirname "$0")/dashboards"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== OneNet Dashboard 导入工具 ===${NC}"
echo "Kibana URL: $KIBANA_URL"
echo ""

# 检查 Kibana 连接
check_kibana() {
    echo -n "检查 Kibana 连接..."
    if curl -s --connect-timeout 5 "$KIBANA_URL/api/status" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        echo "无法连接到 Kibana，请检查："
        echo "  1. Kibana 是否正在运行"
        echo "  2. URL 是否正确: $KIBANA_URL"
        exit 1
    fi
}

# 导入单个 Dashboard
import_dashboard() {
    local dashboard_file=$1
    local dashboard_name=$2

    echo -n "导入 $dashboard_name..."

    if [ ! -f "$dashboard_file" ]; then
        echo -e "${RED}✗${NC} 文件不存在: $dashboard_file"
        return 1
    fi

    # 导入 Dashboard
    response=$(curl -s -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
        -H "kbn-xsrf: true" \
        --form file=@"$dashboard_file")

    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠${NC}"
        echo "响应: $response"
        return 1
    fi
}

# 主函数
main() {
    check_kibana

    echo ""
    echo -e "${YELLOW}开始导入 Dashboards...${NC}"
    echo ""

    # 导入各 Dashboard
    # 1. 设备状态总览
    import_dashboard "$DASHBOARDS_DIR/dashboard_overview.ndjson" "设备状态总览"

    # 2. 水箱监控
    import_dashboard "$DASHBOARDS_DIR/dashboard_tanks.ndjson" "水箱监控"

    # 3. 温度监控
    import_dashboard "$DASHBOARDS_DIR/dashboard_temperature.ndjson" "温度监控"

    # 4. 水泵监控
    import_dashboard "$DASHBOARDS_DIR/dashboard_pumps.ndjson" "水泵监控"

    # 5. 发热管监控
    import_dashboard "$DASHBOARDS_DIR/dashboard_heaters.ndjson" "发热管监控"

    # 6. 流量监控
    import_dashboard "$DASHBOARDS_DIR/dashboard_flowmeters.ndjson" "流量监控"

    # 7. 其他设备
    import_dashboard "$DASHBOARDS_DIR/dashboard_others.ndjson" "其他设备"

    echo ""
    echo -e "${GREEN}=== 导入完成 ===${NC}"
    echo ""
    echo "请访问 Kibana Dashboard 页面查看导入的结果："
    echo "  $KIBANA_URL/app/dashboards/list"
    echo ""
}

main "$@"
