"""
XXL-JOB MCP 测试脚本
用于验证 API 连接和基本功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from xxl_job_mcp.config import Config
from xxl_job_mcp.xxl_job_client import XXLJobClient


async def test_connection():
    """测试与 XXL-JOB 的连接"""
    print("=" * 60)
    print("XXL-JOB MCP 连接测试")
    print("=" * 60)
    
    # 加载配置
    config_file = Path("config.yaml")
    if config_file.exists():
        print(f"\n✓ 从配置文件加载: {config_file}")
        config = Config.from_yaml(str(config_file))
    else:
        print("\n⚠ 配置文件不存在，使用默认配置")
        config = Config.from_env()
    
    print(f"\n调度中心地址: {config.xxl_job.admin_address}")
    print(f"访问令牌: {'已配置' if config.xxl_job.access_token else '未配置'}")
    print(f"超时时间: {config.xxl_job.timeout}秒")
    print(f"最大重试: {config.xxl_job.max_retries}次")
    
    # 创建客户端
    client = XXLJobClient(config)
    
    try:
        # 测试 1: 获取执行器列表
        print("\n" + "-" * 60)
        print("测试 1: 获取执行器列表")
        print("-" * 60)
        result = await client.get_executor_list()
        print(f"响应状态: {'成功' if result.get('code') == 200 else '失败'}")
        if result.get('code') == 200:
            executors = result.get('data', [])
            print(f"执行器数量: {len(executors)}")
            for executor in executors[:3]:  # 只显示前3个
                print(f"  - ID: {executor.get('id')}, 名称: {executor.get('appname')}")
        else:
            print(f"错误信息: {result.get('msg')}")
        
        # 测试 2: 获取任务列表
        print("\n" + "-" * 60)
        print("测试 2: 获取任务列表（前5个）")
        print("-" * 60)
        result = await client.get_job_list(page=1, page_size=5)
        print(f"响应状态: {'成功' if result.get('code') == 200 else '失败'}")
        if result.get('code') == 200:
            data = result.get('data', {})
            total = data.get('recordsTotal', 0)
            jobs = data.get('data', [])
            print(f"任务总数: {total}")
            print(f"当前页数量: {len(jobs)}")
            for job in jobs:
                status = "运行中" if job.get('triggerStatus') == 1 else "已停止"
                print(f"  - ID: {job.get('id')}, 描述: {job.get('jobDesc')}, 状态: {status}")
        else:
            print(f"错误信息: {result.get('msg')}")
        
        # 测试 3: 获取仪表盘信息
        print("\n" + "-" * 60)
        print("测试 3: 获取仪表盘统计")
        print("-" * 60)
        result = await client.get_dashboard_info()
        print(f"响应状态: {'成功' if result.get('code') == 200 else '失败'}")
        if result.get('code') == 200:
            data = result.get('data', {})
            print(f"任务总数: {data.get('jobCount', 0)}")
            print(f"运行中任务: {data.get('jobRunningCount', 0)}")
            print(f"执行器数量: {data.get('executorCount', 0)}")
        else:
            print(f"错误信息: {result.get('msg')}")
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
