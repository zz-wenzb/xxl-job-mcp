# XXL-JOB MCP

XXL-JOB 的 MCP (Model Context Protocol) 集成服务，让 AI 助手能够直接管理和操作 XXL-JOB 分布式任务调度平台。

## 快速开始

## 安装

### 前置要求

- Python 3.9+
- uv（推荐）：`irm https://astral.sh/uv/install.ps1 | iex` (Windows) 或 `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS)
- XXL-JOB 调度中心正在运行

### 使用 uvx 运行（推荐）

无需安装，直接运行：

```bash
uvx xxl-job-mcp
```

### 从源码运行

```bash
git clone <repository-url>
cd xxl-job-mcp
uv sync
uv run python -m xxl_job_mcp
```

## 配置

### 配置文件方式（推荐）

1. 复制配置模板：
```bash
cp config.example.yaml config.yaml
```

2. 编辑配置文件：
```yaml
xxl_job:
  admin_address: "http://your-xxl-job-host:8080/xxl-job-admin"
  access_token: "your-token-here"  # 如果启用了认证

mcp:
  transport: "stdio"  # 或 "streamable-http"
  host: "127.0.0.1"
  port: 25822
```

3. 运行：
```bash
uvx xxl-job-mcp --config config.yaml
```

### 环境变量方式

```bash
export XXL_JOB_ADMIN_ADDRESS="http://localhost:8080/xxl-job-admin"
export XXL_JOB_ACCESS_TOKEN="your-token"  # 可选
uvx xxl-job-mcp
```

### 命令行参数

```bash
# HTTP 模式
uvx xxl-job-mcp --transport http --host 0.0.0.0 --port 8000

# 指定配置文件
uvx xxl-job-mcp --config /path/to/config.yaml
```

## AI 助手配置

### Cursor IDE

设置 → MCP Servers → Edit Config：

```json
{
  "mcpServers": {
    "xxl-job": {
      "command": "uvx",
      "args": ["xxl-job-mcp", "--config", "/absolute/path/to/config.yaml"]
    }
  }
}
```

### Claude Desktop

配置文件位置：
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

内容与上面相同。重启后生效。

## 可用工具

### 执行器管理
- `list_executors()` - 获取所有执行器列表
- `get_executor(executor_id)` - 获取执行器详情

### 任务管理
- `list_jobs(page, page_size, executor_id, status)` - 获取任务列表
- `get_job(job_id)` - 获取任务详情
- `create_job(executor_id, description, author, schedule_type, schedule_conf, executor_handler, ...)` - 创建任务
- `update_job(job_id, ...)` - 更新任务
- `delete_job(job_id)` - 删除任务
- `start_job(job_id)` - 启动任务
- `stop_job(job_id)` - 停止任务
- `trigger_job(job_id, executor_param)` - 手动触发任务

### 日志管理
- `list_job_logs(page, page_size, job_id, status)` - 获取日志列表
- `get_job_log(log_id, from_line)` - 获取日志详情

### 统计信息
- `get_dashboard()` - 获取仪表盘统计

## 使用示例

```python
# 查询任务
list_jobs(page=1, page_size=20)
list_jobs(executor_id=1, status=1)  # 执行器1的运行中任务

# 创建任务
create_job(
    executor_id=1,
    description="数据备份任务",
    author="张三",
    schedule_type="CRON",
    schedule_conf="0 0 2 * * ?",  # 每天凌晨2点
    executor_handler="backupHandler"
)

# 控制任务
start_job(job_id=123)
stop_job(job_id=123)
trigger_job(job_id=123)  # 立即执行

# 查看日志
list_job_logs(job_id=123, page_size=10)
get_job_log(log_id=456)

# 统计信息
get_dashboard()
```

## 常见问题

### 连接超时
检查 `admin_address` 是否正确，XXL-JOB 调度中心是否运行。

### 认证失败
如果 XXL-JOB 启用了访问令牌，在配置文件中设置 `access_token`。

### 多环境配置
为每个环境创建独立的配置文件：
```bash
uvx xxl-job-mcp --config config.dev.yaml   # 开发
uvx xxl-job-mcp --config config.prod.yaml  # 生产
```

### 支持的 XXL-JOB 版本
支持 XXL-JOB 2.x 及以上版本。

## 更多文档

- [开发文档](DEVELOPMENT.md) - 架构设计、扩展开发

## 许可证

MIT License
