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
    # 尝试多个可能的路径
    possible_paths = [
        Path("config.yaml"),  # 当前目录
        Path(__file__).parent.parent / "config.yaml",  # 项目根目录
    ]
    
    config_file = None
    for path in possible_paths:
        if path.exists():
            config_file = path
            break
    
    if config_file:
        print(f"\n✓ 从配置文件加载: {config_file}")
        config = Config.from_yaml(str(config_file))
    else:
        print("\n⚠ 配置文件不存在，使用默认配置")
        print("提示: 复制 config.example.yaml 为 config.yaml 并修改配置")
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
        print(f"响应状态: {'成功' if result.get('code') == 200 or 'data' in result else '失败'}")
        # XXL-JOB 2.x 返回结构可能不同，兼容处理
        executors = result.get('data', [])
        if not executors and isinstance(result.get('data'), dict):
            executors = result['data'].get('data', [])
        
        if executors:
            print(f"执行器数量: {len(executors)}")
            for executor in executors[:3]:  # 只显示前3个
                print(f"  - ID: {executor.get('id')}, 名称: {executor.get('appname')}, 标题: {executor.get('title')}")
            
            # 测试 2: 基于第一个执行器获取任务列表
            first_executor_id = executors[0].get('id')
            print(f"\n使用第一个执行器 ID: {first_executor_id} 查询任务")
            
            print("\n" + "-" * 60)
            print(f"测试 2: 获取执行器 {first_executor_id} 的任务列表（前5个）")
            print("-" * 60)
            result = await client.get_job_list(page=1, page_size=5, job_group=first_executor_id)
            print(f"响应状态: {'成功' if result.get('code') == 200 or 'data' in result or 'recordsTotal' in result else '失败'}")
            # XXL-JOB 2.x 可能直接返回数据，没有 code 字段
            if 'recordsTotal' in result:
                # 直接返回的结构
                total = result.get('recordsTotal', 0)
                jobs = result.get('data', [])
            elif isinstance(result.get('data'), dict):
                # 嵌套在 data 中的结构
                total = result['data'].get('recordsTotal', 0)
                jobs = result['data'].get('data', [])
            else:
                total = 0
                jobs = []
            
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
        
        # XXL-JOB 2.x 返回的是 content 而不是 data
        content = result.get('content', result.get('data', {}))
        if content:
            print(f"触发成功总数: {content.get('triggerCountSucTotal', 0)}")
            print(f"触发失败总数: {content.get('triggerCountFailTotal', 0)}")
            print(f"触发运行中总数: {content.get('triggerCountRunningTotal', 0)}")
            
            # 显示最近7天的趋势
            trigger_day_list = content.get('triggerDayList', [])
            trigger_day_count_suc_list = content.get('triggerDayCountSucList', [])
            if trigger_day_list:
                print(f"\n最近7天调度趋势:")
                for i, day in enumerate(trigger_day_list):
                    suc_count = trigger_day_count_suc_list[i] if i < len(trigger_day_count_suc_list) else 0
                    print(f"  {day}: 成功 {suc_count} 次")
        else:
            print(f"错误信息: {result.get('msg')}")
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        print("\n可能的原因：")
        print("1. XXL-JOB 调度中心未启动")
        print("2. admin_address 配置不正确")
        print("3. 网络连接问题")
        print("\n解决方法：")
        print("1. 确保 XXL-JOB 调度中心正在运行")
        print("2. 复制 config.example.yaml 为 config.yaml 并修改 admin_address")
        print("3. 运行: uvx xxl-job-mcp --config config.yaml")
        # import traceback
        # traceback.print_exc()
        return False
    finally:
        await client.close()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
