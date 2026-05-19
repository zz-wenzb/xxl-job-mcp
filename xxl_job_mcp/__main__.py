"""
XXL-JOB MCP 服务器入口
支持从配置文件或环境变量加载配置
"""
import sys
import argparse
from pathlib import Path

from .config import Config
from .server import XXLJobMCPServer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XXL-JOB MCP Server - 通过 Model Context Protocol 访问 XXL-JOB 任务调度功能"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="配置文件路径（YAML格式），默认使用 config.yaml 或环境变量"
    )
    
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http"],
        default=None,
        help="传输方式：stdio（本地）或 http（远程），覆盖配置文件设置"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="HTTP 模式下的主机地址，覆盖配置文件设置"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="HTTP 模式下的端口，覆盖配置文件设置"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    try:
        if args.config:
            # 从指定配置文件加载
            config_path = args.config
            print(f"从配置文件加载: {config_path}", file=sys.stderr)
            config = Config.from_yaml(config_path)
        else:
            # 尝试从当前目录的 config.yaml 加载
            default_config = Path("config.yaml")
            if default_config.exists():
                print(f"从默认配置文件加载: {default_config}", file=sys.stderr)
                config = Config.from_yaml(str(default_config))
            else:
                # 从环境变量加载
                print("从环境变量加载配置", file=sys.stderr)
                config = Config.from_env()
    except Exception as e:
        print(f"配置加载失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 应用命令行参数覆盖
    if args.transport:
        config.mcp.transport = args.transport
    if args.host:
        config.mcp.host = args.host
    if args.port:
        config.mcp.port = args.port
    
    # 创建并运行服务器
    server = XXLJobMCPServer(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"服务器运行错误: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        import asyncio
        asyncio.run(server.cleanup())


if __name__ == "__main__":
    main()
