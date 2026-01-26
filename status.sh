#!/bin/bash

# 查看所有项目的 Git 状态

echo "================================"
echo "查看所有项目的 Git 状态"
echo "================================"

# 检查 zcgames 项目
echo ""
echo "=== zcgames ==="
if [ -d "../zcgames" ]; then
    cd ../zcgames
    echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
    echo "最新提交: $(git log -1 --oneline)"
    echo "状态:"
    git status -s
    cd -
else
    echo "⚠️  zcgames 目录不存在"
fi

# 检查 edutool 项目
echo ""
echo "=== edutool ==="
if [ -d "../edutool" ]; then
    cd ../edutool
    echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
    echo "最新提交: $(git log -1 --oneline)"
    echo "状态:"
    git status -s
    cd -
else
    echo "⚠️  edutool 目录不存在"
fi

# 检查 webtool 项目
echo ""
echo "=== webtool ==="
if [ -d "../webtool" ]; then
    cd ../webtool
    echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
    echo "最新提交: $(git log -1 --oneline)"
    echo "状态:"
    git status -s
    cd -
else
    echo "⚠️  webtool 目录不存在"
fi

# 检查 clouddeploy 项目自身
echo ""
echo "=== clouddeploy（当前项目）==="
echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
echo "最新提交: $(git log -1 --oneline)"
echo "状态:"
git status -s

echo ""
echo "================================"
