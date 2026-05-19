"""
XXL-JOB API 客户端
提供与 XXL-JOB 调度中心的交互接口
"""
import logging
from typing import Optional, Dict, Any, List
import httpx
from .config import Config

logger = logging.getLogger(__name__)


class XXLJobClient:
    """XXL-JOB API 客户端"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.xxl_job.admin_address.rstrip('/')
        self.access_token = config.xxl_job.access_token
        self.timeout = config.xxl_job.timeout
        self.max_retries = config.xxl_job.max_retries
        
        # 创建 HTTP 客户端
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.access_token:
            headers["XXL-JOB-ACCESS-TOKEN"] = self.access_token
        return headers
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                continue
    
    # ========== 执行器管理 ==========
    
    async def get_executor_list(self) -> Dict[str, Any]:
        """获取执行器列表"""
        return await self._request("GET", "/api/jobGroup/list")
    
    async def get_executor_by_id(self, group_id: int) -> Dict[str, Any]:
        """根据 ID 获取执行器信息"""
        return await self._request("GET", f"/api/jobGroup/load?id={group_id}")
    
    # ========== 任务管理 ==========
    
    async def get_job_list(self, page: int = 1, page_size: int = 20, 
                          job_group: Optional[int] = None,
                          trigger_status: Optional[int] = None) -> Dict[str, Any]:
        """获取任务列表
        
        Args:
            page: 页码
            page_size: 每页数量
            job_group: 执行器ID过滤
            trigger_status: 调度状态过滤（0-停止，1-运行）
        """
        params = {
            "start": (page - 1) * page_size,
            "length": page_size
        }
        if job_group is not None:
            params["jobGroup"] = job_group
        if trigger_status is not None:
            params["triggerStatus"] = trigger_status
        
        return await self._request("GET", "/api/jobInfo/pageList", params=params)
    
    async def get_job_by_id(self, job_id: int) -> Dict[str, Any]:
        """根据 ID 获取任务信息"""
        return await self._request("GET", f"/api/jobInfo/load?id={job_id}")
    
    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建任务
        
        Args:
            job_data: 任务数据，包含以下字段：
                - jobGroup: 执行器ID
                - jobDesc: 任务描述
                - author: 负责人
                - scheduleType: 调度类型（CRON/FIX_RATE/FIX_DELAY）
                - scheduleConf: 调度配置（CRON表达式或时间间隔）
                - executorHandler: 执行器Handler
                - executorParam: 执行参数（可选）
                - misfireStrategy: 调度过期策略
                - executorRouteStrategy: 路由策略
                - executorBlockStrategy: 阻塞处理策略
                - executorTimeout: 任务超时时间
                - executorFailRetryCount: 失败重试次数
        """
        return await self._request("POST", "/api/jobInfo/add", json=job_data)
    
    async def update_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新任务"""
        return await self._request("POST", "/api/jobInfo/update", json=job_data)
    
    async def delete_job(self, job_id: int) -> Dict[str, Any]:
        """删除任务"""
        return await self._request("POST", "/api/jobInfo/remove", json={"id": job_id})
    
    async def start_job(self, job_id: int) -> Dict[str, Any]:
        """启动任务"""
        return await self._request("POST", "/api/jobInfo/start", json={"id": job_id})
    
    async def stop_job(self, job_id: int) -> Dict[str, Any]:
        """停止任务"""
        return await self._request("POST", "/api/jobInfo/stop", json={"id": job_id})
    
    async def trigger_job(self, job_id: int, executor_param: Optional[str] = None) -> Dict[str, Any]:
        """手动触发任务
        
        Args:
            job_id: 任务ID
            executor_param: 执行参数（可选）
        """
        data = {"id": job_id}
        if executor_param:
            data["executorParam"] = executor_param
        return await self._request("POST", "/api/jobInfo/trigger", json=data)
    
    # ========== 任务日志 ==========
    
    async def get_job_log_list(self, page: int = 1, page_size: int = 20,
                              job_id: Optional[int] = None,
                              log_status: Optional[int] = None) -> Dict[str, Any]:
        """获取任务日志列表
        
        Args:
            page: 页码
            page_size: 每页数量
            job_id: 任务ID过滤
            log_status: 日志状态（1-成功，2-失败，3-进行中）
        """
        params = {
            "start": (page - 1) * page_size,
            "length": page_size
        }
        if job_id is not None:
            params["jobId"] = job_id
        if log_status is not None:
            params["logStatus"] = log_status
        
        return await self._request("GET", "/api/log/pageList", params=params)
    
    async def get_job_log_detail(self, log_id: int, from_line_num: int = 1) -> Dict[str, Any]:
        """获取任务日志详情
        
        Args:
            log_id: 日志ID
            from_line_num: 起始行号
        """
        params = {
            "logId": log_id,
            "fromLineNum": from_line_num
        }
        return await self._request("GET", "/api/log/logDetailCat", params=params)
    
    # ========== 任务统计 ==========
    
    async def get_dashboard_info(self) -> Dict[str, Any]:
        """获取仪表盘信息"""
        return await self._request("GET", "/api/dashboard/info")
    
    async def get_job_report(self) -> Dict[str, Any]:
        """获取任务报表"""
        return await self._request("GET", "/api/chartInfo")
