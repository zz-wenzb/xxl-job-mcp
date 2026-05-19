"""
XXL-JOB MCP 服务器
通过 Model Context Protocol 暴露 XXL-JOB 任务调度功能
"""
import logging
import sys
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

from .config import Config
from .xxl_job_client import XXLJobClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class XXLJobMCPServer:
    """XXL-JOB MCP 服务器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.xxl_job_client = XXLJobClient(config)
        
        # 创建 MCP 服务器实例
        self.mcp = FastMCP(
            name=config.mcp.name,
            description=config.mcp.description
        )
        
        # 注册工具
        self._register_tools()
    
    def _register_tools(self):
        """注册所有 MCP 工具"""
        
        # ========== 执行器管理工具 ==========
        
        @self.mcp.tool()
        async def list_executors() -> Dict[str, Any]:
            """获取所有执行器列表
            
            Returns:
                执行器列表信息
            """
            try:
                result = await self.xxl_job_client.get_executor_list()
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取执行器列表失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def get_executor(executor_id: int) -> Dict[str, Any]:
            """获取指定执行器的详细信息
            
            Args:
                executor_id: 执行器ID
                
            Returns:
                执行器详细信息
            """
            try:
                result = await self.xxl_job_client.get_executor_by_id(executor_id)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取执行器信息失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # ========== 任务管理工具 ==========
        
        @self.mcp.tool()
        async def list_jobs(
            page: int = 1,
            page_size: int = 20,
            executor_id: Optional[int] = None,
            status: Optional[int] = None
        ) -> Dict[str, Any]:
            """获取任务列表
            
            Args:
                page: 页码，默认1
                page_size: 每页数量，默认20
                executor_id: 执行器ID过滤（可选）
                status: 调度状态过滤（0-停止，1-运行，可选）
                
            Returns:
                任务列表信息
            """
            try:
                result = await self.xxl_job_client.get_job_list(
                    page=page,
                    page_size=page_size,
                    job_group=executor_id,
                    trigger_status=status
                )
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取任务列表失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def get_job(job_id: int) -> Dict[str, Any]:
            """获取指定任务的详细信息
            
            Args:
                job_id: 任务ID
                
            Returns:
                任务详细信息
            """
            try:
                result = await self.xxl_job_client.get_job_by_id(job_id)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取任务信息失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def create_job(
            executor_id: int,
            description: str,
            author: str,
            schedule_type: str = "CRON",
            schedule_conf: str = "0 0 0 * * ? *",
            executor_handler: str = "",
            executor_param: Optional[str] = None,
            route_strategy: str = "FIRST",
            block_strategy: str = "SERIAL_EXECUTION",
            timeout: int = 0,
            retry_count: int = 0
        ) -> Dict[str, Any]:
            """创建新任务
            
            Args:
                executor_id: 执行器ID
                description: 任务描述
                author: 负责人
                schedule_type: 调度类型（CRON/FIX_RATE/FIX_DELAY）
                schedule_conf: 调度配置（CRON表达式或时间间隔）
                executor_handler: 执行器Handler名称
                executor_param: 执行参数（可选）
                route_strategy: 路由策略（FIRST/LAST/ROUND/RANDOM/CONSISTENT_HASH等）
                block_strategy: 阻塞处理策略（SERIAL_EXECUTION/DISCARD_LATER/COVER_EARLY）
                timeout: 任务超时时间（秒），0表示不限制
                retry_count: 失败重试次数
                
            Returns:
                创建结果
            """
            try:
                job_data = {
                    "jobGroup": executor_id,
                    "jobDesc": description,
                    "author": author,
                    "scheduleType": schedule_type,
                    "scheduleConf": schedule_conf,
                    "executorHandler": executor_handler,
                    "executorRouteStrategy": route_strategy,
                    "executorBlockStrategy": block_strategy,
                    "executorTimeout": timeout,
                    "executorFailRetryCount": retry_count
                }
                
                if executor_param:
                    job_data["executorParam"] = executor_param
                
                result = await self.xxl_job_client.create_job(job_data)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"创建任务失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def update_job(
            job_id: int,
            description: Optional[str] = None,
            author: Optional[str] = None,
            schedule_type: Optional[str] = None,
            schedule_conf: Optional[str] = None,
            executor_handler: Optional[str] = None,
            executor_param: Optional[str] = None,
            route_strategy: Optional[str] = None,
            block_strategy: Optional[str] = None,
            timeout: Optional[int] = None,
            retry_count: Optional[int] = None
        ) -> Dict[str, Any]:
            """更新任务信息
            
            Args:
                job_id: 任务ID
                description: 任务描述（可选）
                author: 负责人（可选）
                schedule_type: 调度类型（可选）
                schedule_conf: 调度配置（可选）
                executor_handler: 执行器Handler（可选）
                executor_param: 执行参数（可选）
                route_strategy: 路由策略（可选）
                block_strategy: 阻塞处理策略（可选）
                timeout: 任务超时时间（可选）
                retry_count: 失败重试次数（可选）
                
            Returns:
                更新结果
            """
            try:
                # 先获取当前任务信息
                current_job = await self.xxl_job_client.get_job_by_id(job_id)
                job_data = current_job.get("content", {})
                job_data["id"] = job_id
                
                # 更新提供的字段
                if description:
                    job_data["jobDesc"] = description
                if author:
                    job_data["author"] = author
                if schedule_type:
                    job_data["scheduleType"] = schedule_type
                if schedule_conf:
                    job_data["scheduleConf"] = schedule_conf
                if executor_handler:
                    job_data["executorHandler"] = executor_handler
                if executor_param is not None:
                    job_data["executorParam"] = executor_param
                if route_strategy:
                    job_data["executorRouteStrategy"] = route_strategy
                if block_strategy:
                    job_data["executorBlockStrategy"] = block_strategy
                if timeout is not None:
                    job_data["executorTimeout"] = timeout
                if retry_count is not None:
                    job_data["executorFailRetryCount"] = retry_count
                
                result = await self.xxl_job_client.update_job(job_data)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"更新任务失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def delete_job(job_id: int) -> Dict[str, Any]:
            """删除任务
            
            Args:
                job_id: 任务ID
                
            Returns:
                删除结果
            """
            try:
                result = await self.xxl_job_client.delete_job(job_id)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"删除任务失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def start_job(job_id: int) -> Dict[str, Any]:
            """启动任务（开始调度）
            
            Args:
                job_id: 任务ID
                
            Returns:
                启动结果
            """
            try:
                result = await self.xxl_job_client.start_job(job_id)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"启动任务失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def stop_job(job_id: int) -> Dict[str, Any]:
            """停止任务（暂停调度）
            
            Args:
                job_id: 任务ID
                
            Returns:
                停止结果
            """
            try:
                result = await self.xxl_job_client.stop_job(job_id)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"停止任务失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def trigger_job(job_id: int, executor_param: Optional[str] = None) -> Dict[str, Any]:
            """手动触发任务执行（立即执行一次）
            
            Args:
                job_id: 任务ID
                executor_param: 执行参数（可选）
                
            Returns:
                触发结果
            """
            try:
                result = await self.xxl_job_client.trigger_job(job_id, executor_param)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"触发任务失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # ========== 任务日志工具 ==========
        
        @self.mcp.tool()
        async def list_job_logs(
            page: int = 1,
            page_size: int = 20,
            job_id: Optional[int] = None,
            status: Optional[int] = None
        ) -> Dict[str, Any]:
            """获取任务执行日志列表
            
            Args:
                page: 页码，默认1
                page_size: 每页数量，默认20
                job_id: 任务ID过滤（可选）
                status: 日志状态（1-成功，2-失败，3-进行中，可选）
                
            Returns:
                日志列表信息
            """
            try:
                result = await self.xxl_job_client.get_job_log_list(
                    page=page,
                    page_size=page_size,
                    job_id=job_id,
                    log_status=status
                )
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取日志列表失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        async def get_job_log(log_id: int, from_line: int = 1) -> Dict[str, Any]:
            """获取任务执行日志详情
            
            Args:
                log_id: 日志ID
                from_line: 起始行号，默认1
                
            Returns:
                日志详情
            """
            try:
                result = await self.xxl_job_client.get_job_log_detail(log_id, from_line)
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取日志详情失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # ========== 统计工具 ==========
        
        @self.mcp.tool()
        async def get_dashboard() -> Dict[str, Any]:
            """获取仪表盘统计信息
            
            Returns:
                仪表盘统计数据
            """
            try:
                result = await self.xxl_job_client.get_dashboard_info()
                return {
                    "success": True,
                    "data": result
                }
            except Exception as e:
                logger.error(f"获取仪表盘信息失败: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def run(self):
        """运行 MCP 服务器"""
        transport = self.config.mcp.transport
        
        if transport == "stdio":
            logger.info("以 STDIO 模式启动 MCP 服务器")
            self.mcp.run(transport="stdio")
        elif transport == "streamable-http":
            host = self.config.mcp.host
            port = self.config.mcp.port
            path = self.config.mcp.path
            logger.info(f"以 HTTP 模式启动 MCP 服务器: http://{host}:{port}{path}")
            self.mcp.run(
                transport="streamable-http",
                host=host,
                port=port,
                path=path
            )
        else:
            raise ValueError(f"不支持的传输方式: {transport}")
    
    async def cleanup(self):
        """清理资源"""
        await self.xxl_job_client.close()
