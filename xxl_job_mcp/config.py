"""
XXL-JOB MCP 配置模块
支持多开发者协同模式，配置文件独立管理
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class XXLJobConfig(BaseModel):
    """XXL-JOB 调度中心配置"""
    
    # 调度中心地址
    admin_address: str = Field(
        default="http://localhost:8080/xxl-job-admin",
        description="XXL-JOB 调度中心地址"
    )
    
    # 访问令牌（如果启用了安全认证）
    access_token: Optional[str] = Field(
        default=None,
        description="访问令牌，用于安全认证"
    )
    
    # 超时设置
    timeout: int = Field(
        default=30,
        description="HTTP 请求超时时间（秒）"
    )
    
    # 重试次数
    max_retries: int = Field(
        default=3,
        description="最大重试次数"
    )


class MCPConfig(BaseModel):
    """MCP 服务器配置"""
    
    # 服务器名称
    name: str = Field(
        default="xxl-job-mcp",
        description="MCP 服务器名称"
    )
    
    # 服务器描述
    description: str = Field(
        default="XXL-JOB 分布式任务调度 MCP 服务",
        description="MCP 服务器描述"
    )
    
    # 传输方式：stdio 或 streamable-http
    transport: str = Field(
        default="stdio",
        description="MCP 传输方式：stdio 或 streamable-http"
    )
    
    # HTTP 模式下的主机地址
    host: str = Field(
        default="127.0.0.1",
        description="HTTP 传输模式下的主机地址"
    )
    
    # HTTP 模式下的端口
    port: int = Field(
        default=25822,
        description="HTTP 传输模式下的端口"
    )
    
    # HTTP 模式下的路径
    path: str = Field(
        default="/mcp",
        description="HTTP 传输模式下的路径"
    )


class Config(BaseModel):
    """完整配置"""
    
    xxl_job: XXLJobConfig = Field(
        default_factory=XXLJobConfig,
        description="XXL-JOB 配置"
    )
    
    mcp: MCPConfig = Field(
        default_factory=MCPConfig,
        description="MCP 服务器配置"
    )
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """从 YAML 文件加载配置"""
        import yaml
        
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量加载配置"""
        return cls(
            xxl_job=XXLJobConfig(
                admin_address=os.getenv("XXL_JOB_ADMIN_ADDRESS", "http://localhost:8080/xxl-job-admin"),
                access_token=os.getenv("XXL_JOB_ACCESS_TOKEN"),
                timeout=int(os.getenv("XXL_JOB_TIMEOUT", "30")),
                max_retries=int(os.getenv("XXL_JOB_MAX_RETRIES", "3")),
            ),
            mcp=MCPConfig(
                name=os.getenv("MCP_SERVER_NAME", "xxl-job-mcp"),
                description=os.getenv("MCP_SERVER_DESCRIPTION", "XXL-JOB 分布式任务调度 MCP 服务"),
                transport=os.getenv("MCP_TRANSPORT", "stdio"),
                host=os.getenv("MCP_HOST", "127.0.0.1"),
                port=int(os.getenv("MCP_PORT", "25822")),
                path=os.getenv("MCP_PATH", "/mcp"),
            )
        )
