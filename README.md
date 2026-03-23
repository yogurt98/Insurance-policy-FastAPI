# Policy Management API

**一个生产级的加拿大保险保单管理系统**，专为 Sun Life / Manulife / Definity 等保险公司设计。

## 项目亮点

- **FastAPI + PostgreSQL** 异步高性能后端
- **JWT 认证 + 角色权限控制**（Admin / Underwriter）
- **完整 CRUD 操作** + **批量导入**（支持 10万+ 条 CSV/JSON）
- **保险业务规则校验**：反欺诈检查、OSFI 合规字段自动生成
- **Docker 一键部署**
- 符合加拿大保险监管（OSFI）场景设计

### 技术栈
- **Backend**: FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic
- **Database**: PostgreSQL (Async)
- **Auth**: JWT (PyJWT + bcrypt)
- **Validation**: Pydantic v2
- **Deployment**: Docker + docker-compose
- **Data Processing**: Pandas（批量导入）

---

## 快速启动

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd policy-management-api

# 2. 启动服务
docker-compose up --build -d

# 3. 打开 Swagger 文档
http://localhost:8000/docs
```

## 环境变量
复制 .env.example 为 .env 并根据需要修改。

## API 主要功能
- **认证**

POST /api/v1/auth/register — 用户注册
POST /api/v1/auth/login — 用户登录

- **保单管理**

POST /api/v1/policies/ — 创建保单（带反欺诈校验）
GET /api/v1/policies/ — 查询保单列表
GET /api/v1/policies/{id} — 查询单个保单
PUT /api/v1/policies/{id} — 更新保单
DELETE /api/v1/policies/{id} — 删除保单（仅 Admin）

- **批量导入（核心功能）**

POST /api/v1/policies/bulk-upload — 支持 CSV / JSON 大文件上传（10万条级别）


- **保险业务特性**

反欺诈规则引擎：风险分数、异常高保费自动标记 flag / review
OSFI 合规：自动生成 OSFI-YYYY-XXXXXX 标识
精确金额处理：使用 Numeric(precision=2) 保存保费
角色权限：Underwriter 可创建/查看，Admin 可删除



Postman Collection
项目根目录已提供 postman_collection.json，可直接导入测试所有接口。
License
MIT License