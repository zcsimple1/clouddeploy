#!/bin/bash

# 停止自动更新服务

SERVICE_FILE="$HOME/Library/LaunchAgents/com.clouddeploy.auto-update.plist"

echo "================================"
echo "停止自动更新服务"
echo "================================"

# 卸载服务
launchctl unload "$SERVICE_FILE" 2>/dev/null

# 删除 plist 文件
if [ -f "$SERVICE_FILE" ]; then
    rm "$SERVICE_FILE"
    echo "已删除服务配置文件"
fi

echo ""
echo "================================"
echo "✅ 自动更新服务已停止！"
echo "================================"
