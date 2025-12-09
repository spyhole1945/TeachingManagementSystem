# TeachingManagementSystem
Teaching Management System (TMS) 是一个使用 Python 实现的模块化教学管理系统 Demo。系统覆盖教学场景中的核心功能，包括用户、课程、选课、成绩、作业与资源管理等
本项目设计强调：

模块化、可扩展

清晰的领域模型

适合作为实训/教学管理类系统的原型

🧩 功能模块概览（10 大核心模块）
1️⃣ 用户与权限模块（User & Auth）

负责系统访问控制与基础身份体系。

功能：

用户登录 / 登出

用户角色：Admin / Teacher / Student

RBAC 简易权限控制

用户档案管理（创建/更新/删除）

2️⃣ 课程管理模块（Course Management）

用于管理课程基础信息。

功能：

创建、修改、删除课程

课程列表、详情查询

课程与教师绑定

课程时间、描述、容量等管理

3️⃣ 学生管理模块（Student Management）

管理学生基本信息，是学习流程核心。

功能：

学生档案（年级、联系方式、状态等）

查看学生已选课程

学生状态管理（在读/休学/毕业）

4️⃣ 教师管理模块（Teacher Management）

管理教师档案以及授课信息。

功能：

教师基本资料

教师授课课程列表

教师与课程绑定

5️⃣ 班级与选课模块（Enrollment）

负责选课逻辑与课程资源分配。

功能：

学生选课 / 退课

课程容量校验

冲突检测（课程时间冲突）

查询学生/课程的选课情况

这是教学系统的中心模块之一。

6️⃣ 成绩管理模块（Grade Management）

负责课程成绩的管理与统计。

功能：

教师录入、修改成绩

学生查看成绩

成绩统计（平均分/最高分/通过率）

7️⃣ 教学资源管理模块（Material Management）

课程相关资料存储与权限控制。

功能：

上传 / 下载教学资源

课件、视频、作业模板等管理

资源访问权限控制（仅本课程学生可下载）

8️⃣ 作业与提交模块（Assignment & Submission）

配合课程教学流程的作业管理。

功能：

教师布置作业

学生提交作业

教师批改作业、评分

作业历史记录查询

9️⃣ 通知/消息模块（Notification）

系统事件触发通知。

功能：

新作业通知

成绩发布提醒

选课结果通知

可扩展邮件/站内信/Pub-Sub 事件机制

🔟 系统管理模块（System Admin）

所有全局设置与管理集中在此模块。

功能：

系统配置（学期设置、容量等）

用户管理（冻结/启用）

数据备份与恢复

日志管理（登录日志、操作审计）

🏗 系统架构设计

项目采用 分层架构 + Repository Pattern，确保可维护性与替换性。

/tms
├── api/              # API 层（可使用 Flask/FastAPI）
├── application/      # 业务流程（Service 层）
├── domain/           # 领域模型（User/Course/Teacher/Student...）
├── infra/            # 基础设施（数据库、文件、Repository）
├── tests/            # 单元测试
└── README.md


API 层 提供统一访问入口

Service 层 承担业务流程 orchestration

Domain 层 聚焦实体/值对象与业务规则

Infra 层 负责数据持久化（可替换 SQLite, MySQL）

📊 数据模型（ER 简化）
User (id, name, role)
├── Student (user_id → User.id)
└── Teacher (user_id → User.id)

Course (id, name, teacher_id → Teacher.user_id, schedule, capacity)
Enrollment (student_id → Student, course_id → Course)

Assignment (id, course_id → Course)
Submission (id, student_id → Student, assignment_id → Assignment)

Material (id, course_id → Course, path)

Grade (student_id, course_id, score)

Notification (id, user_id, message, created_at)

🛠 技术栈

Python 3.9+

SQLite / MySQL（可切换）

Flask / FastAPI（可选）

Repository Pattern

面向对象设计（OOP）

单元测试（pytest）
