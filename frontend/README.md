# 教学管理系统 - 前端使用指南

## 🎨 前端界面

现代化的纯 HTML/CSS/JavaScript 前端界面，无需构建工具，开箱即用！

### ✨ 特性

- 🎭 **现代化设计** - 深色主题 + 渐变效果 + 玻璃态
- 🎬 **流畅动画** - 微交互动画提升用户体验
- 📱 **响应式布局** - 完美适配各种屏幕尺寸
- ⚡ **零依赖** - 纯原生 JavaScript，无需框架
- 🔐 **完整功能** - 登录、选课、成绩、作业、通知等

### 📁 文件结构

```
frontend/
├── index.html              # 首页
├── login.html             # 登录页
├── student-dashboard.html # 学生仪表板
├── teacher-dashboard.html # 教师仪表板
├── admin-dashboard.html   # 管理员仪表板
├── css/
│   └── styles.css        # 全局样式
└── js/
    └── api.js            # API 客户端
```

## 🚀 快速开始

### 方法一：Python 简易服务器（推荐）

```bash
# 在 frontend 目录下运行
cd /Users/fanxuejuan/Documents/AntigravityProject/TeachingManagementSystem/frontend

# 启动静态文件服务器
python3 -m http.server 3000
```

然后访问: http://localhost:3000

### 方法二：直接打开文件

确保后端 API 已启动（http://localhost:8000），然后：

1. 用浏览器打开 `frontend/index.html`
2. 或者打开 `frontend/login.html` 直接登录

### 前置条件

**必须先启动后端 API 服务！**

```bash
# 在项目根目录
uvicorn tms.api.main:app --reload
```

API 服务会运行在: http://localhost:8000

## 👤 测试账号

系统已预置三个测试账号：

| 角色 | 用户名 | 密码 | 功能 |
|------|--------|------|------|
| 👑 管理员 | `admin` | `admin123` | 系统管理、统计、配置 |
| 👨‍🏫 教师 | `prof_zhang` | `teacher123` | 课程管理、成绩录入、作业批改 |
| 👨‍🎓 学生 | `student1` | `student123` | 选课、查看成绩、提交作业 |

## 🎯 功能展示

### 1️⃣ 学生端 (`student-dashboard.html`)

**功能模块：**
- ✅ 我的课程 - 查看已选课程
- ✅ 选课 - 浏览和选择课程（带冲突检测）
- ✅ 成绩 - 查看所有成绩和平均分
- ✅ 作业 - 查看和提交作业
- ✅ 通知 - 接收系统通知

**特色：**
- 实时显示统计数据（已选课程数、待提交作业、平均成绩）
- 课程搜索功能
- 自动冲突检测（选课时）
- 美观的卡片式布局

### 2️⃣ 教师端 (`teacher-dashboard.html`)

**功能模块：**
- ✅ 我的课程 - 查看授课课程
- ✅ 学生管理 - 查看选课学生
- ✅ 成绩管理 - 录入和修改成绩
- ✅ 作业管理 - 发布作业、查看提交

**特色：**
- 课程统计（学生数、作业数、待批改）
- 快速操作按钮

### 3️⃣ 管理员端 (`admin-dashboard.html`)

**功能模块：**
- ✅ 系统统计 - 用户、课程、选课数据
- ✅ 用户管理 - 创建用户、冻结账号
- ✅ 系统配置 - 学期设置、备份数据库
- ✅ 快速操作 - 常用管理功能

**特色：**
- 实时系统数据
- 一键数据库备份
- 完整的系统监控

## 🎨 设计亮点

### 现代化配色
- 深色主题为主
- 使用紫色 (#4F46E5) 和绿色 (#10B981) 渐变
- 玻璃态效果 (glassmorphism)

### 动画效果
- 页面加载淡入动画
- 卡片悬停效果
- 按钮交互动画
- 平滑的标签切换

### 响应式设计
- 桌面端 - 多列网格布局
- 平板 - 2列布局
- 手机 - 单列布局

## 🔧 技术细节

### API 客户端 (`js/api.js`)

```javascript
// 使用示例
const api = new TMSApi();

// 登录
await api.login('admin', 'admin123');

// 获取课程
const courses = await api.getCourses();

// 选课
await api.enrollInCourse(studentId, courseId);
```

**功能：**
- 自动处理 Token 存储
- 统一的错误处理
- 支持所有后端 API 接口
- LocalStorage 持久化登录

### 样式系统 (`css/styles.css`)

**CSS 变量：**
```css
--primary: #4F46E5;       /* 主色调 */
--secondary: #10B981;     /* 辅助色 */
--bg-primary: #0F172A;    /* 背景色 */
```

**组件样式：**
- `.card` - 卡片组件
- `.btn` - 按钮组件
- `.form-input` - 表单输入
- `.stat-card` - 统计卡片
- `.badge` - 徽章标签

## 📝 开发建议

### 扩展功能

1. **添加新页面**
   - 复制现有页面作为模板
   - 修改标题和内容
   - 更新导航链接

2. **添加新 API 调用**
   - 在 `api.js` 中添加方法
   - 参考现有方法格式

3. **自定义样式**
   - 修改 `styles.css` 中的 CSS 变量
   - 添加自定义组件样式

### 调试技巧

**查看 API 请求：**
```javascript
// 在浏览器控制台
console.log(api.token);  // 查看 token
console.log(api.user);   // 查看用户信息
```

**常见问题：**
- ❌ API 请求失败 → 检查后端是否启动
- ❌ CORS 错误 → 后端已配置允许所有来源
- ❌ 登录失败 → 检查用户名密码是否正确

## 🌐 浏览器兼容性

✅ 支持所有现代浏览器：
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 📦 生产部署

### 选项一：静态托管

将 `frontend` 文件夹部署到：
- Netlify
- Vercel
- GitHub Pages
- nginx/Apache

### 选项二：集成到后端

将前端文件放入 FastAPI 的静态文件目录：

```python
# main.py
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

## 🎉 总结

前端界面已完成，包含：
- ✅ 5 个完整页面
- ✅ 现代化 UI 设计
- ✅ 完整的 API 集成
- ✅ 响应式布局
- ✅ 流畅的动画效果

立即启动体验：
```bash
cd frontend
python3 -m http.server 3000
```

然后访问 http://localhost:3000 🚀
