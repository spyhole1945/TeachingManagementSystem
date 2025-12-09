#!/bin/bash
# 教学管理系统 - 启动脚本（优化版）

echo "🚀 启动教学管理系统..."
echo ""

# 函数：检查端口是否被占用
check_port() {
    local port=$1
    lsof -i :$port -t 2>/dev/null
}

# 函数：清理端口
cleanup_port() {
    local port=$1
    local port_name=$2
    
    local pid=$(check_port $port)
    if [ ! -z "$pid" ]; then
        echo "⚠️  端口 $port 已被占用 (PID: $pid)"
        echo "   正在清理..."
        kill -9 $pid 2>/dev/null
        sleep 1
        
        # 再次检查
        pid=$(check_port $port)
        if [ -z "$pid" ]; then
            echo "   ✅ 端口 $port 已释放"
        else
            echo "   ❌ 无法释放端口 $port，请手动处理"
            return 1
        fi
    fi
    return 0
}

# 清理旧的PID文件
rm -f .backend.pid .frontend.pid

# 1. 检查并清理端口
echo "🔍 检查端口占用..."
cleanup_port 8000 "后端API"
cleanup_port 3000 "前端"
echo ""

# 2. 检查数据库
if [ ! -f "tms_database.db" ]; then
    echo "📊 初始化数据库..."
    python3 -m tms.init_db
    if [ $? -ne 0 ]; then
        echo "❌ 数据库初始化失败！"
        exit 1
    fi
    echo ""
fi

# 3. 启动后端API
echo "🔧 启动后端 API (端口 8000)..."

# 使用 python3 -m uvicorn 而不是直接调用 uvicorn（解决命令找不到问题）
python3 -m uvicorn tms.api.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 等待后端启动
echo "   等待后端启动..."
sleep 3

# 检查后端进程是否还在运行
if ps -p $BACKEND_PID > /dev/null; then
    # 检查是否可以访问
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ 后端启动成功！"
    else
        echo "   ⚠️  后端进程运行中，正在初始化..."
        echo "   查看日志: tail -f backend.log"
    fi
else
    echo "   ❌ 后端启动失败！"
    echo "   查看错误日志: cat backend.log"
    exit 1
fi

echo ""

# 4. 启动前端
echo "🎨 启动前端界面 (端口 3000)..."
cd frontend
python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"
cd ..

# 检查前端进程
sleep 1
if ps -p $FRONTEND_PID > /dev/null; then
    echo "   ✅ 前端启动成功！"
else
    echo "   ❌ 前端启动失败！"
    echo "   查看错误日志: cat frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 系统启动完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 访问地址："
echo "   🎨 前端: http://localhost:3000"
echo "   📚 API文档: http://localhost:8000/docs"
echo "   📖 备用文档: http://localhost:8000/redoc"
echo ""
echo "👤 测试账号："
echo "   👑 管理员: admin / admin123"
echo "   👨‍🏫 教师: prof_zhang / teacher123"
echo "   👨‍🎓 学生: student1 / student123"
echo ""
echo "� 服务状态："
echo "   后端 PID: $BACKEND_PID (日志: backend.log)"
echo "   前端 PID: $FRONTEND_PID (日志: frontend.log)"
echo ""
echo "⏹️  停止服务器："
echo "   ./stop.sh"
echo "   或: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 查看日志："
echo "   tail -f backend.log   # 后端日志"
echo "   tail -f frontend.log  # 前端日志"
echo ""

# 保存PID到文件以便停止
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 自动打开浏览器（可选）
# sleep 2
# open http://localhost:3000 2>/dev/null || echo "请手动打开浏览器访问 http://localhost:3000"
