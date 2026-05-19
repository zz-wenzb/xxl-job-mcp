# XXL-JOB MCP 开发文档

## 项目概述

XXL-JOB MCP 是一个基于 Model Context Protocol (MCP) 的集成服务，将 XXL-JOB 分布式任务调度平台的功能通过 MCP 协议暴露出来，使得 AI 助手（如 Claude、Cursor 等）能够直接管理和操作 XXL-JOB 的任务调度功能。

## 架构设计

### 核心组件

```
┌─────────────────────────────────────────┐
│         MCP Client (AI Assistant)       │
└──────────────┬──────────────────────────┘
               │ MCP Protocol (STDIO/HTTP)
┌──────────────▼──────────────────────────┐
│      XXL-JOB MCP Server (FastMCP)       │
│  ┌───────────────────────────────────┐  │
│  │   Tool Registration Layer         │  │
│  │   - list_executors                │  │
│  │   - list_jobs                     │  │
│  │   - create_job                    │  │
│  │   - trigger_job                   │  │
│  │   - ...                           │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │   XXL-JOB API Client              │  │
│  │   - HTTP Request Handler          │  │
│  │   - Retry Logic                   │  │
│  │   - Error Handling                │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │ HTTP REST API
┌──────────────▼──────────────────────────┐
│     XXL-JOB Admin (调度中心)             │
└─────────────────────────────────────────┘
```

### 技术栈

- **Python**: >= 3.9
- **FastMCP**: MCP 服务器框架
- **httpx**: 异步 HTTP 客户端
- **pydantic**: 数据验证和配置管理
- **PyYAML**: YAML 配置文件解析
- **uv/uvx**: 现代 Python 包管理和运行工具

## 项目结构

```
xxl-job-mcp/
├── pyproject.toml              # 项目配置和依赖
├── config.example.yaml         # 配置文件示例
├── .gitignore                  # Git 忽略文件
├── README.md                   # 使用文档
├── DEVELOPMENT.md              # 开发文档（本文件）
├── xxl_job_mcp/
│   ├── __init__.py            # 包初始化
│   ├── __main__.py            # 入口点（支持 python -m）
│   ├── config.py              # 配置管理模块
│   ├── xxl_job_client.py      # XXL-JOB API 客户端
│   └── server.py              # MCP 服务器实现
└── .venv/                     # 虚拟环境（不提交到 Git）
```

## 配置系统

### 多开发者协同模式

项目采用独立的配置文件管理方式，支持多开发者协同工作：

1. **config.example.yaml**: 配置文件模板，提交到版本控制
2. **config.yaml**: 本地配置文件，每个开发者自行创建，不提交到 Git
3. **环境变量**: 作为配置文件的补充或替代

### 配置加载优先级

```
命令行参数 > 配置文件 (config.yaml) > 环境变量 > 默认值
```

### 配置项说明

#### XXL-JOB 配置

```yaml
xxl_job:
  admin_address: "http://localhost:8080/xxl-job-admin"  # 调度中心地址
  access_token: null                                     # 访问令牌（可选）
  timeout: 30                                            # 请求超时时间（秒）
  max_retries: 3                                         # 最大重试次数
```

#### MCP 服务器配置

```yaml
mcp:
  name: "xxl-job-mcp"                                    # 服务器名称
  description: "XXL-JOB 分布式任务调度 MCP 服务"         # 服务器描述
  transport: "stdio"                                     # 传输方式：stdio 或 streamable-http
  host: "127.0.0.1"                                      # HTTP 主机地址
  port: 25822                                            # HTTP 端口
  path: "/mcp"                                           # HTTP 路径
```

## 核心功能模块

### 1. 配置管理 (config.py)

使用 Pydantic 模型进行配置验证和管理：

- `XXLJobConfig`: XXL-JOB 调度中心配置
- `MCPConfig`: MCP 服务器配置
- `Config`: 完整配置模型

支持两种加载方式：
- `Config.from_yaml()`: 从 YAML 文件加载
- `Config.from_env()`: 从环境变量加载

### 2. XXL-JOB API 客户端 (xxl_job_client.py)

封装 XXL-JOB 调度中心的 REST API：

#### 执行器管理
- `get_executor_list()`: 获取执行器列表
- `get_executor_by_id()`: 获取指定执行器信息

#### 任务管理
- `get_job_list()`: 获取任务列表（支持分页和过滤）
- `get_job_by_id()`: 获取任务详情
- `create_job()`: 创建新任务
- `update_job()`: 更新任务
- `delete_job()`: 删除任务
- `start_job()`: 启动任务调度
- `stop_job()`: 停止任务调度
- `trigger_job()`: 手动触发任务执行

#### 日志管理
- `get_job_log_list()`: 获取日志列表
- `get_job_log_detail()`: 获取日志详情

#### 统计信息
- `get_dashboard_info()`: 获取仪表盘统计
- `get_job_report()`: 获取任务报表

### 3. MCP 服务器 (server.py)

使用 FastMCP 框架实现 MCP 服务器，注册以下工具：

#### 执行器工具
- `list_executors`: 列出所有执行器
- `get_executor`: 获取执行器详情

#### 任务工具
- `list_jobs`: 列出任务（支持分页、过滤）
- `get_job`: 获取任务详情
- `create_job`: 创建任务
- `update_job`: 更新任务
- `delete_job`: 删除任务
- `start_job`: 启动任务
- `stop_job`: 停止任务
- `trigger_job`: 触发任务执行

#### 日志工具
- `list_job_logs`: 列出日志
- `get_job_log`: 获取日志详情

#### 统计工具
- `get_dashboard`: 获取仪表盘信息

## 开发指南

### 环境准备

1. **安装 uv**（推荐）：
```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **克隆项目**：
```bash
git clone <repository-url>
cd xxl-job-mcp
```

3. **创建虚拟环境并安装依赖**：
```bash
uv venv
uv sync
```

### 添加新功能

#### 1. 在 XXLJobClient 中添加新的 API 方法

```python
# xxl_job_mcp/xxl_job_client.py

async def new_api_method(self, param1: str, param2: int) -> Dict[str, Any]:
    """新方法描述"""
    return await self._request("POST", "/api/newEndpoint", json={
        "param1": param1,
        "param2": param2
    })
```

#### 2. 在 MCP 服务器中注册新工具

```python
# xxl_job_mcp/server.py

@self.mcp.tool()
async def new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """新工具的描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明，默认10
        
    Returns:
        返回结果说明
    """
    try:
        result = await self.xxl_job_client.new_api_method(param1, param2)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"操作失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

#### 3. 测试新工具

```bash
# STDIO 模式测试
uv run python -m xxl_job_mcp

# HTTP 模式测试
uv run python -m xxl_job_mcp --transport http --port 25822
```

### 代码规范

1. **类型注解**: 所有函数必须包含完整的类型注解
2. **文档字符串**: 使用 Google 风格的 docstring
3. **错误处理**: 所有异步操作必须包含 try-except
4. **日志记录**: 使用 logging 模块记录关键操作和错误

### 调试技巧

1. **启用详细日志**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **测试单个工具**：
```python
# 创建测试脚本
import asyncio
from xxl_job_mcp.config import Config
from xxl_job_mcp.xxl_job_client import XXLJobClient

async def test():
    config = Config.from_yaml("config.yaml")
    client = XXLJobClient(config)
    
    # 测试特定 API
    result = await client.get_job_list()
    print(result)
    
    await client.close()

asyncio.run(test())
```

## XXL-JOB API 参考

### 认证

如果 XXL-JOB 启用了访问令牌认证，需要在请求头中包含：
```
XXL-JOB-ACCESS-TOKEN: your-token-here
```

### 主要 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/jobGroup/list | GET | 获取执行器列表 |
| /api/jobInfo/pageList | GET | 获取任务列表 |
| /api/jobInfo/add | POST | 创建任务 |
| /api/jobInfo/update | POST | 更新任务 |
| /api/jobInfo/remove | POST | 删除任务 |
| /api/jobInfo/start | POST | 启动任务 |
| /api/jobInfo/stop | POST | 停止任务 |
| /api/jobInfo/trigger | POST | 触发任务 |
| /api/log/pageList | GET | 获取日志列表 |
| /api/log/logDetailCat | GET | 获取日志详情 |

详细的 API 文档请参考 XXL-JOB 官方文档。

## 测试

### 单元测试

```bash
uv run pytest tests/ -v
```

### 集成测试

1. 确保 XXL-JOB 调度中心正在运行
2. 配置正确的 `admin_address`
3. 运行测试脚本

## 部署

### 本地开发

```bash
# 使用 uvx 直接运行（无需安装）
uvx xxl-job-mcp

# 或从源码运行
uv run python -m xxl_job_mcp
```

### Docker 部署（未来扩展）

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "xxl_job_mcp"]
```

## 常见问题

### 1. 连接超时

检查 `admin_address` 是否正确，确保 XXL-JOB 调度中心正在运行。

### 2. 认证失败

如果 XXL-JOB 启用了访问令牌，确保在配置文件中正确设置 `access_token`。

### 3. 工具调用失败

查看 stderr 输出的日志信息，定位具体错误原因。

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

MIT License
