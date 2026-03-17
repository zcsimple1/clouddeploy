#!/bin/bash

echo "================================"
echo "停止自动更新定时任务"
echo "================================"

# 从 crontab 中移除定时任务
crontab -l 2>/dev/null | grep -v "check-and-update.sh" | crontab -

echo ""
echo "================================"
echo "✅ 定时任务已停止"
echo "================================"
