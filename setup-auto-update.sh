#!/bin/bash

# 设置自动更新服务（使用 crontab）

WORK_DIR="/Users/zora/Documents/Work/mygithub/clouddeploy"
SCRIPT="$WORK_DIR/check-and-update.sh"

echo "================================"
echo "设置自动更新定时任务"
echo "================================"

# 检查是否已存在
CRON_EXISTS=$(crontab -l 2>/dev/null | grep "check-and-update.sh" || echo "")

if [ -z "$CRON_EXISTS" ]; then
    # 添加定时任务：每5分钟执行一次
    (crontab -l 2>/dev/null; echo "*/5 * * * * $SCRIPT") | crontab -
    
    echo ""
    echo "================================"
    echo "✅ 定时任务已启动！"
    echo "================================"
    echo ""
    echo "每 5 分钟自动检查一次代码更新"
    echo "日志文件：/tmp/auto-update.log"
    echo ""
    echo "查看实时日志："
    echo "  tail -f /tmp/auto-update.log"
    echo ""
    echo "停止定时任务："
    echo "  ./stop-auto-update.sh"
    echo ""
else
    echo "定时任务已存在，无需重复设置"
fi
