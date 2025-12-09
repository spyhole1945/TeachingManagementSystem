# 🚀 教学管理系统 - 快速启动指南

## ⚠️ 解决 "Failed to fetch" 错误

如果登录时看到 "Failed to fetch" 错误，说明**后端 API 未启动**。

## 🔧 正确的启动步骤

### 方法一：使用启动脚本（推荐）

```bash
# 在项目根目录运行
./start.sh
```

这会自动启动前端和后端！

### 方法二：手动启动（分两步）

**第1步：启动后端 API**

打开**第一个**终端窗口：

```bash
cd /Users/fanxuejuan/Documents/AntigravityProject/TeachingManagementSystem

# 启动后端
uvicorn tms.api.main:app --reload --host 0.0.0.0 --port 8000
```

等待看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**第2步：启动前端**

打开**第二个**终端窗口：

```bash
cd /Users/fanxuejuan/Documents/AntigravityProject/TeachingManagementSystem/frontend

# 启动前端
python3 -m http.server 3000
```

等待看到：
```
Serving HTTP on 0.0.0.0 port 3000
```

## ✅ 验证服务器是否启动

打开浏览器测试：

1. **后端 API**: http://localhost:8000/docs
   - 应该看到 Swagger API 文档

2. **前端界面**: http://localhost:3000
   - 应该看到登录页面

## 🔍 检查命令

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查端口占用
lsof -i :8000  # 后端
lsof -i :3000  # 前端
```

## 🛑 停止服务器

### 使用停止脚本
```bash
./stop.sh
```

### 手动停止
在运行服务器的终端按 `Ctrl + C`

或者：
```bash
# 杀死所有相关进程
pkill -f uvicorn
pkill -f "http.server 3000"
```

## 📱 访问地址

启动成功后访问：

- **前端**: http://localhost:3000
- **API 文档**: http://localhost:8000/docs
- **备用文档**: http://localhost:8000/redoc

## 👤 测试账号

```
管理员: admin / admin123
教师: prof_zhang / teacher123
学生: student1 / student123
```

## ❓ 常见问题

### 问题1: "Failed to fetch"
**原因**: 后端未启动
**解决**: 按照上述步骤启动后端

### 问题2: "Address already in use"
**原因**: 端口被占用
**解决**: 
```bash
# 杀死占用端口的进程
lsof -ti:8000 | xargs kill -9  # 后端
lsof -ti:3000 | xargs kill -9  # 前端
```

### 问题3: "Module not found"
**原因**: 依赖未安装
**解决**:
```bash
pip3 install -r requirements.txt
```

### 问题4: "Database not found"
**原因**: 数据库未初始化
**解决**:
```bash
python3 -m tms.init_db
```

## 📝 完整流程（从头开始）

```bash
# 1. 进入项目目录
cd /Users/fanxuejuan/Documents/AntigravityProject/TeachingManagementSystem

# 2. 安装依赖（如果还没安装）
pip3 install -r requirements.txt

# 3. 初始化数据库（如果还没初始化）
python3 -m tms.init_db

# 4. 启动服务器
./start.sh

# 5. 打开浏览器访问
open http://localhost:3000
```

## 🎉 成功标志

如果一切正常，您应该看到：

1. ✅ 终端显示 "Uvicorn running on..."
2. ✅ 浏览器打开美观的登录页面
3. ✅ 可以点击"快速登录"按钮登录
4. ✅ 登录后看到精美的仪表板

祝使用愉快！🚀
