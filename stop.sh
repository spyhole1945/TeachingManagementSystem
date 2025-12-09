#!/bin/bash
# 教学管理系统 - 停止脚本

echo "⏹️  停止教学管理系统..."

# 读取保存的PID
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "停止后端 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null && echo "✅ 后端已停止" || echo "⚠️  后端进程未运行"
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo "停止前端 (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null && echo "✅ 前端已停止" || echo "⚠️  前端进程未运行"
    rm .frontend.pid
fi

# 额外清理：杀死所有相关进程
echo "清理残留进程..."
pkill -f "uvicorn tms.api.main" 2>/dev/null
pkill -f "python3 -m http.server 3000" 2>/dev/null

echo ""
echo "✅ 系统已停止！"
