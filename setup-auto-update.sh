#!/bin/bash

# 设置自动更新服务（使用 launchd）

SERVICE_FILE="$HOME/Library/LaunchAgents/com.clouddeploy.auto-update.plist"
WORK_DIR=$(pwd)

echo "================================"
echo "设置自动更新服务"
echo "================================"

# 创建 plist 文件
cat > "$SERVICE_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clouddeploy.auto-update</string>
    <key>ProgramArguments</key>
    <array>
        <string>$WORK_DIR/check-and-update.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>WorkingDirectory</key>
    <string>$WORK_DIR</string>
    <key>StandardOutPath</key>
    <string>/tmp/clouddeploy-auto-update.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/clouddeploy-auto-update-error.log</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加载服务
echo "加载 launchd 服务..."
launchctl unload "$SERVICE_FILE" 2>/dev/null || true
launchctl load "$SERVICE_FILE"

echo ""
echo "================================"
echo "✅ 自动更新服务已启动！"
echo "================================"
echo ""
echo "每 5 分钟自动检查一次代码更新（包括 clouddeploy 自身）"
echo "日志文件："
echo "  - 标准日志: /tmp/clouddeploy-auto-update.log"
echo "  - 错误日志: /tmp/clouddeploy-auto-update-error.log"
echo "  - 更新日志: /tmp/auto-update.log"
echo ""
echo "查看实时日志："
echo "  tail -f /tmp/clouddeploy-auto-update.log"
echo ""
echo "停止自动更新服务："
echo "  ./stop-auto-update.sh"
echo ""
