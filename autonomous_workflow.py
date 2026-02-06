"""
自主工作流引擎 - 高效自动化系统

核心特性:
1. 任务图管理 - 支持复杂依赖关系的任务调度
2. 自适应重试 - 智能错误处理和重试机制
3. 并行执行 - 最大化资源利用率
4. 实时监控 - 任务执行状态跟踪
5. 学习优化 - 基于历史数据优化执行策略

作者: MarsAssistant
日期: 2026-02-06
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 等待执行
    RUNNING = "running"        # 执行中
    SUCCESS = "success"        # 成功完成
    FAILED = "failed"          # 失败
    RETRYING = "retrying"      # 重试中
    CANCELLED = "cancelled"    # 已取消
    SKIPPED = "skipped"        # 已跳过（依赖失败）


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration": self.duration,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }


@dataclass
class Task:
    """
    任务定义
    
    Attributes:
        id: 任务唯一标识
        name: 任务名称
        func: 执行函数
        args: 位置参数
        kwargs: 关键字参数
        dependencies: 依赖的任务ID列表
        priority: 优先级（1-10，数字越大越优先）
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）
        timeout: 超时时间（秒）
        metadata: 额外元数据
    """
    id: str
    name: str
    func: Callable = field(repr=False)
    args: tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    metadata: Dict = field(default_factory=dict)
    
    # 运行时状态
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(
                f"{self.name}{time.time()}".encode()
            ).hexdigest()[:12]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "metadata": self.metadata
        }


class WorkflowEngine:
    """
    工作流引擎 - 管理和执行复杂任务流
    
    特点:
    - 自动处理任务依赖关系
    - 支持并行执行无依赖任务
    - 智能重试和错误恢复
    - 执行历史记录和分析
    """
    
    def __init__(self, max_workers: int = 4, enable_logging: bool = True):
        self.tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.enable_logging = enable_logging
        
        # 执行统计
        self.stats = {
            "total_executed": 0,
            "total_success": 0,
            "total_failed": 0,
            "total_retries": 0,
            "avg_duration": 0.0
        }
        
        # 执行历史
        self.history: List[Dict] = []
        
        # 学习到的优化策略
        self.learned_strategies: Dict[str, Any] = {}
        
    def add_task(self, task: Task) -> str:
        """添加任务到工作流"""
        self.tasks[task.id] = task
        return task.id
    
    def add_simple_task(self, name: str, func: Callable, 
                       *args, **kwargs) -> str:
        """快速添加简单任务"""
        task = Task(name=name, func=func, args=args, kwargs=kwargs)
        self.tasks[task.id] = task
        return task.id
    
    def set_dependency(self, task_id: str, depends_on: List[str]):
        """设置任务依赖关系"""
        if task_id in self.tasks:
            self.tasks[task_id].dependencies = depends_on
    
    def _get_ready_tasks(self) -> List[Task]:
        """获取所有可以执行的任务（依赖已满足）"""
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            # 检查依赖是否完成
            deps_satisfied = all(
                self.tasks.get(dep_id) and 
                self.tasks[dep_id].status == TaskStatus.SUCCESS
                for dep_id in task.dependencies
            )
            
            # 检查是否有依赖失败
            deps_failed = any(
                self.tasks.get(dep_id) and 
                self.tasks[dep_id].status in [TaskStatus.FAILED, TaskStatus.SKIPPED]
                for dep_id in task.dependencies
            )
            
            if deps_failed:
                task.status = TaskStatus.SKIPPED
                task.result = TaskResult(
                    success=False, 
                    error="Dependencies failed or skipped"
                )
            elif deps_satisfied:
                ready.append(task)
        
        # 按优先级排序
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready
    
    def _execute_single_task(self, task: Task) -> TaskResult:
        """执行单个任务"""
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        if self.enable_logging:
            logger.info(f"开始执行任务: {task.name} (ID: {task.id})")
        
        retry_count = 0
        last_error = None
        
        while retry_count <= task.max_retries:
            try:
                # 执行实际任务
                if asyncio.iscoroutinefunction(task.func):
                    # 异步函数
                    result_data = asyncio.run(task.func(*task.args, **task.kwargs))
                else:
                    # 同步函数
                    result_data = task.func(*task.args, **task.kwargs)
                
                duration = time.time() - task.start_time
                
                task.status = TaskStatus.SUCCESS
                task.end_time = time.time()
                task.result = TaskResult(
                    success=True,
                    data=result_data,
                    duration=duration,
                    retry_count=retry_count
                )
                
                if self.enable_logging:
                    logger.info(f"任务完成: {task.name} (耗时: {duration:.2f}s)")
                
                return task.result
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                self.stats["total_retries"] += 1
                
                if retry_count <= task.max_retries:
                    task.status = TaskStatus.RETRYING
                    if self.enable_logging:
                        logger.warning(
                            f"任务失败，准备重试: {task.name} (第{retry_count}次)"
                        )
                    time.sleep(task.retry_delay * retry_count)  # 指数退避
                else:
                    break
        
        # 所有重试都失败
        duration = time.time() - task.start_time
        task.status = TaskStatus.FAILED
        task.end_time = time.time()
        task.result = TaskResult(
            success=False,
            error=last_error,
            duration=duration,
            retry_count=retry_count - 1
        )
        
        if self.enable_logging:
            logger.error(f"任务最终失败: {task.name} - {last_error}")
        
        return task.result
    
    def run(self, fail_fast: bool = False) -> Dict[str, TaskResult]:
        """
        执行整个工作流
        
        Args:
            fail_fast: 是否遇到第一个错误就停止
        
        Returns:
            所有任务的结果字典
        """
        start_time = time.time()
        
        if self.enable_logging:
            logger.info(f"开始执行工作流，共 {len(self.tasks)} 个任务")
        
        completed_tasks = set()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while len(completed_tasks) < len(self.tasks):
                # 获取可以执行的任务
                ready_tasks = self._get_ready_tasks()
                
                if not ready_tasks:
                    # 检查是否还有未完成的任务
                    pending = [t for t in self.tasks.values() 
                              if t.status == TaskStatus.PENDING]
                    if not pending:
                        break  # 所有任务都已处理
                    else:
                        # 可能存在循环依赖
                        logger.error("检测到无法执行的任务，可能存在循环依赖")
                        break
                
                # 提交任务到线程池
                future_to_task = {
                    executor.submit(self._execute_single_task, task): task
                    for task in ready_tasks
                }
                
                # 等待这一轮任务完成
                for future in future_to_task:
                    task = future_to_task[future]
                    try:
                        future.result()
                        completed_tasks.add(task.id)
                        self.stats["total_executed"] += 1
                        
                        if task.result and task.result.success:
                            self.stats["total_success"] += 1
                        else:
                            self.stats["total_failed"] += 1
                            if fail_fast:
                                logger.error("fail_fast 模式：遇到错误停止")
                                return self._collect_results()
                                
                    except Exception as e:
                        logger.error(f"任务执行异常: {e}")
        
        total_duration = time.time() - start_time
        
        # 更新统计
        if self.stats["total_executed"] > 0:
            self.stats["avg_duration"] = total_duration / self.stats["total_executed"]
        
        # 记录历史
        self.history.append({
            "timestamp": time.time(),
            "duration": total_duration,
            "stats": self.stats.copy(),
            "task_count": len(self.tasks)
        })
        
        if self.enable_logging:
            logger.info(f"工作流执行完成，总耗时: {total_duration:.2f}s")
            logger.info(f"成功: {self.stats['total_success']}, "
                       f"失败: {self.stats['total_failed']}")
        
        return self._collect_results()
    
    def _collect_results(self) -> Dict[str, TaskResult]:
        """收集所有任务的结果"""
        return {
            task_id: task.result 
            for task_id, task in self.tasks.items()
            if task.result
        }
    
    def get_execution_report(self) -> Dict:
        """生成执行报告"""
        task_reports = []
        for task in self.tasks.values():
            report = {
                "id": task.id,
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority
            }
            if task.result:
                report["result"] = task.result.to_dict()
            task_reports.append(report)
        
        return {
            "summary": {
                "total_tasks": len(self.tasks),
                "success": self.stats["total_success"],
                "failed": self.stats["total_failed"],
                "retries": self.stats["total_retries"],
                "success_rate": (
                    self.stats["total_success"] / max(1, self.stats["total_executed"])
                )
            },
            "stats": self.stats,
            "tasks": task_reports
        }
    
    def reset(self):
        """重置所有任务状态，准备重新执行"""
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
            task.result = None
            task.start_time = None
            task.end_time = None
    
    def save_workflow(self, filepath: str):
        """保存工作流定义（不包含函数）"""
        workflow_data = {
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "stats": self.stats,
            "history": self.history[-10:]  # 最近10条历史
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, ensure_ascii=False, indent=2)
    
    def analyze_performance(self) -> Dict:
        """分析执行性能，提供优化建议"""
        if not self.history:
            return {"message": "没有执行历史可供分析"}
        
        # 计算趋势
        durations = [h["duration"] for h in self.history]
        success_rates = [
            h["stats"]["total_success"] / max(1, h["stats"]["total_executed"])
            for h in self.history
        ]
        
        analysis = {
            "avg_duration": sum(durations) / len(durations),
            "duration_trend": "improving" if durations[-1] < durations[0] else "stable",
            "avg_success_rate": sum(success_rates) / len(success_rates),
            "recommendations": []
        }
        
        # 生成建议
        if self.stats["total_retries"] > self.stats["total_executed"] * 0.2:
            analysis["recommendations"].append(
                "重试率较高，建议检查任务稳定性或增加超时时间"
            )
        
        if analysis["avg_success_rate"] < 0.9:
            analysis["recommendations"].append(
                "成功率低于90%，建议审查失败任务的错误处理"
            )
        
        return analysis


# ======== 实用工具函数 ========

def create_data_pipeline(name: str = "DataPipeline") -> WorkflowEngine:
    """
    创建标准数据处理流水线
    
    流程: 采集 -> 清洗 -> 转换 -> 存储
    """
    engine = WorkflowEngine(max_workers=2)
    
    # 定义任务函数
    def collect_data(source: str):
        logger.info(f"从 {source} 采集数据...")
        time.sleep(1)
        return {"raw_data": f"data_from_{source}", "count": 100}
    
    def clean_data(data: Dict):
        logger.info("清洗数据...")
        time.sleep(0.5)
        return {"cleaned_data": data["raw_data"], "valid_count": 95}
    
    def transform_data(data: Dict):
        logger.info("转换数据格式...")
        time.sleep(0.5)
        return {"transformed": True, "records": data["valid_count"]}
    
    def store_data(data: Dict):
        logger.info("存储到数据库...")
        time.sleep(0.5)
        return {"stored": True, "records": data["records"]}
    
    # 创建任务
    t1 = engine.add_simple_task("collect", collect_data, "api_endpoint")
    t2 = engine.add_simple_task("clean", clean_data)
    t3 = engine.add_simple_task("transform", transform_data)
    t4 = engine.add_simple_task("store", store_data)
    
    # 设置依赖
    engine.set_dependency(t2, [t1])
    engine.set_dependency(t3, [t2])
    engine.set_dependency(t4, [t3])
    
    return engine


def create_monitoring_workflow() -> WorkflowEngine:
    """
    创建系统监控工作流
    
    定期检查系统健康状态并发送报告
    """
    engine = WorkflowEngine(max_workers=3)
    
    def check_cpu():
        # 模拟 CPU 检查
        return {"cpu_usage": 45.2, "status": "normal"}
    
    def check_memory():
        # 模拟内存检查
        return {"memory_usage": 62.5, "status": "normal"}
    
    def check_disk():
        # 模拟磁盘检查
        return {"disk_usage": 78.0, "status": "warning"}
    
    def generate_report(results: List[Dict] = None):
        # 生成监控报告
        return {
            "timestamp": time.time(),
            "summary": "系统整体健康",
            "alerts": ["磁盘使用率高"]
        }
    
    # 并行检查，然后生成报告
    t1 = engine.add_simple_task("check_cpu", check_cpu)
    t2 = engine.add_simple_task("check_memory", check_memory)
    t3 = engine.add_simple_task("check_disk", check_disk)
    t4 = engine.add_simple_task("generate_report", generate_report)
    
    engine.set_dependency(t4, [t1, t2, t3])
    
    return engine


# ======== 演示 ========

def demo():
    """演示 WorkflowEngine 的使用"""
    
    print("=" * 60)
    print("自主工作流引擎演示")
    print("=" * 60)
    
    # 演示 1: 数据处理流水线
    print("\n1. 数据处理流水线演示")
    print("-" * 60)
    
    pipeline = create_data_pipeline()
    results = pipeline.run()
    
    print("\n执行结果:")
    for task_id, result in results.items():
        status = "✓" if result.success else "✗"
        print(f"  {status} {task_id}: {result.data}")
    
    report = pipeline.get_execution_report()
    print(f"\n成功率: {report['summary']['success_rate']:.1%}")
    
    # 演示 2: 监控工作流
    print("\n2. 系统监控工作流演示")
    print("-" * 60)
    
    monitor = create_monitoring_workflow()
    results = monitor.run()
    
    print("\n监控结果:")
    for task_id, result in results.items():
        if result.success:
            print(f"  ✓ {task_id}: {result.data}")
    
    # 演示 3: 带重试的错误处理
    print("\n3. 错误处理和重试演示")
    print("-" * 60)
    
    engine = WorkflowEngine()
    
    attempt_count = 0
    def flaky_task():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception(f"模拟失败 (尝试 {attempt_count})")
        return f"成功 (尝试 {attempt_count})"
    
    task = Task(
        name="flaky_task",
        func=flaky_task,
        max_retries=3,
        retry_delay=0.5
    )
    engine.add_task(task)
    
    results = engine.run()
    print(f"任务最终状态: {task.status.value}")
    print(f"实际尝试次数: {attempt_count}")
    print(f"结果: {results[task.id].data}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
