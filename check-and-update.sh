#!/bin/bash

# 检测代码更新并自动部署

LOG_FILE="/tmp/auto-update.log"
LOG_TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$LOG_TIME] 开始检查代码更新..." >> $LOG_FILE

# 检查是否有更新
HAS_UPDATE=false

# 检查 zcgames
if [ -d "../zcgames" ]; then
    cd ../zcgames
    git fetch origin $(git rev-parse --abbrev-ref HEAD) >> $LOG_FILE 2>&1
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[$LOG_TIME] zcgames 有新代码" >> $LOG_FILE
        HAS_UPDATE=true
    fi
    cd -
fi

# 检查 edutool
if [ -d "../edutool" ]; then
    cd ../edutool
    git fetch origin $(git rev-parse --abbrev-ref HEAD) >> $LOG_FILE 2>&1
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[$LOG_TIME] edutool 有新代码" >> $LOG_FILE
        HAS_UPDATE=true
    fi
    cd -
fi

# 检查 webtool
if [ -d "../webtool" ]; then
    cd ../webtool
    git fetch origin $(git rev-parse --abbrev-ref HEAD) >> $LOG_FILE 2>&1
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[$LOG_TIME] webtool 有新代码" >> $LOG_FILE
        HAS_UPDATE=true
    fi
    cd -
fi

# 检查 commonserv
if [ -d "../commonserv" ]; then
    cd ../commonserv
    git fetch origin $(git rev-parse --abbrev-ref HEAD) >> $LOG_FILE 2>&1
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[$LOG_TIME] commonserv 有新代码" >> $LOG_FILE
        HAS_UPDATE=true
    fi
    cd -
fi

# 检查 clouddeploy 自身
cd .
git fetch origin $(git rev-parse --abbrev-ref HEAD) >> $LOG_FILE 2>&1
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$LOG_TIME] clouddeploy 有新代码" >> $LOG_FILE
    HAS_UPDATE=true
fi

# 如果有更新，执行部署
if [ "$HAS_UPDATE" = true ]; then
    echo "[$LOG_TIME] 检测到代码更新，开始自动部署..." >> $LOG_FILE
    ./pull-all.sh >> $LOG_FILE 2>&1

    # 如果 clouddeploy 自身有更新，需要重启容器
    cd .
    git fetch origin $(git rev-parse --abbrev-ref HEAD) >> $LOG_FILE 2>&1
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "[$LOG_TIME] clouddeploy 配置已更新，重新构建..." >> $LOG_FILE
        docker-compose up -d --build >> $LOG_FILE 2>&1
    else
        echo "[$LOG_TIME] 仅更新项目代码，重启容器..." >> $LOG_FILE
        docker-compose restart >> $LOG_FILE 2>&1
    fi
    echo "[$LOG_TIME] 自动部署完成！" >> $LOG_FILE
else
    echo "[$LOG_TIME] 没有检测到代码更新" >> $LOG_FILE
fi

echo "----------------------------------------" >> $LOG_FILE
