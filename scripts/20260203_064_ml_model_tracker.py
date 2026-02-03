#!/usr/bin/env python3
"""
Day 64: ML Model Performance Tracker
机器学习模型性能跟踪器

功能：
- 记录模型训练指标（准确率、损失、F1等）
- 版本对比分析
- 可视化趋势图表
- 性能告警设置

作者: MarsAssistant
日期: 2026-02-03
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics


class MetricType(Enum):
    """指标类型枚举"""
    ACCURACY = "accuracy"
    LOSS = "loss"
    F1_SCORE = "f1_score"
    PRECISION = "precision"
    RECALL = "recall"
    AUC = "auc"
    MSE = "mse"
    RMSE = "rmse"
    MAE = "mae"
    CUSTOM = "custom"


@dataclass
class Metric:
    """单个指标数据"""
    name: str
    value: float
    metric_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    epoch: Optional[int] = None
    phase: str = "validation"  # training, validation, test
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelVersion:
    """模型版本信息"""
    version_id: str
    name: str
    created_at: str
    metrics: List[Metric] = field(default_factory=list)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    def get_metric_by_type(self, metric_type: MetricType) -> Optional[Metric]:
        """根据类型获取最新指标"""
        for metric in reversed(self.metrics):
            if metric.metric_type == metric_type.value:
                return metric
        return None
    
    def get_best_metric(self, metric_type: MetricType, 
                        higher_is_better: bool = True) -> Optional[Metric]:
        """获取最佳指标"""
        type_metrics = [m for m in self.metrics 
                       if m.metric_type == metric_type.value]
        if not type_metrics:
            return None
        
        return max(type_metrics, 
                  key=lambda x: x.value if higher_is_better else -x.value)


class MLModelTracker:
    """机器学习模型性能跟踪器"""
    
    def __init__(self, storage_path: str = "./model_history"):
        self.storage_path = storage_path
        self.versions: Dict[str, ModelVersion] = {}
        self.current_version: Optional[ModelVersion] = None
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        self._load_existing()
    
    def _load_existing(self):
        """加载已存在的历史记录"""
        history_file = os.path.join(self.storage_path, "model_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    for v_data in data.get("versions", []):
                        version = ModelVersion(
                            version_id=v_data["version_id"],
                            name=v_data["name"],
                            created_at=v_data["created_at"],
                            hyperparameters=v_data.get("hyperparameters", {}),
                            notes=v_data.get("notes", ""),
                            tags=v_data.get("tags", [])
                        )
                        for m_data in v_data.get("metrics", []):
                            version.metrics.append(Metric(
                                name=m_data["name"],
                                value=m_data["value"],
                                metric_type=m_data["metric_type"],
                                timestamp=m_data.get("timestamp", ""),
                                epoch=m_data.get("epoch"),
                                phase=m_data.get("phase", "validation"),
                                metadata=m_data.get("metadata", {})
                            ))
                        self.versions[version.version_id] = version
            except Exception as e:
                print(f"Warning: Could not load history: {e}")
    
    def _save_history(self):
        """保存历史记录到文件"""
        history_file = os.path.join(self.storage_path, "model_history.json")
        data = {
            "last_updated": datetime.now().isoformat(),
            "versions": []
        }
        
        for version in self.versions.values():
            version_data = {
                "version_id": version.version_id,
                "name": version.name,
                "created_at": version.created_at,
                "metrics": [
                    {
                        "name": m.name,
                        "value": m.value,
                        "metric_type": m.metric_type,
                        "timestamp": m.timestamp,
                        "epoch": m.epoch,
                        "phase": m.phase,
                        "metadata": m.metadata
                    }
                    for m in version.metrics
                ],
                "hyperparameters": version.hyperparameters,
                "notes": version.notes,
                "tags": version.tags
            }
            data["versions"].append(version_data)
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_version(self, name: str, 
                       hyperparameters: Optional[Dict] = None,
                       tags: Optional[List[str]] = None) -> str:
        """创建新模型版本"""
        version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        version = ModelVersion(
            version_id=version_id,
            name=name,
            created_at=datetime.now().isoformat(),
            hyperparameters=hyperparameters or {},
            tags=tags or []
        )
        self.versions[version_id] = version
        self.current_version = version
        self._save_history()
        return version_id
    
    def log_metric(self, value: float, metric_type: MetricType,
                   name: Optional[str] = None, epoch: Optional[int] = None,
                   phase: str = "validation", metadata: Optional[Dict] = None):
        """记录模型指标"""
        if not self.current_version:
            raise RuntimeError("No current version. Call create_version() first.")
        
        metric = Metric(
            name=name or metric_type.value,
            value=value,
            metric_type=metric_type.value,
            epoch=epoch,
            phase=phase,
            metadata=metadata or {}
        )
        self.current_version.metrics.append(metric)
        self._save_history()
    
    def compare_versions(self, version_ids: List[str], 
                        metric_type: MetricType) -> Dict[str, Any]:
        """比较多个版本的指定指标"""
        comparison = {
            "metric": metric_type.value,
            "comparisons": [],
            "summary": {}
        }
        
        values = []
        for vid in version_ids:
            if vid in self.versions:
                version = self.versions[vid]
                best = version.get_best_metric(metric_type)
                if best:
                    comparison["comparisons"].append({
                        "version_id": vid,
                        "version_name": version.name,
                        "best_value": best.value,
                        "epoch": best.epoch
                    })
                    values.append(best.value)
        
        if values:
            comparison["summary"] = {
                "mean": statistics.mean(values),
                "max": max(values),
                "min": min(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0
            }
        
        return comparison
    
    def generate_report(self, version_id: str) -> str:
        """生成模型版本性能报告"""
        if version_id not in self.versions:
            return f"Version {version_id} not found."
        
        version = self.versions[version_id]
        report_lines = [
            f"Model Performance Report",
            f"=" * 40,
            f"Version ID: {version.version_id}",
            f"Name: {version.name}",
            f"Created: {version.created_at}",
            f"Notes: {version.notes or 'N/A'}",
            f"Tags: {', '.join(version.tags) if version.tags else 'None'}",
            "",
            f"Metrics Summary:",
            f"-" * 40
        ]
        
        # 按类型分组指标
        metrics_by_type = {}
        for metric in version.metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric.value)
        
        for mtype, values in metrics_by_type.items():
            report_lines.append(f"{mtype}:")
            report_lines.append(f"  Latest: {values[-1]:.4f}")
            if len(values) > 1:
                report_lines.append(f"  Best: {max(values):.4f}")
                report_lines.append(f"  Worst: {min(values):.4f}")
                report_lines.append(f"  Mean: {statistics.mean(values):.4f}")
        
        if version.hyperparameters:
            report_lines.extend([
                "",
                f"Hyperparameters:",
                f"-" * 40
            ])
            for key, value in version.hyperparameters.items():
                report_lines.append(f"  {key}: {value}")
        
        return "\n".join(report_lines)
    
    def export_to_csv(self, version_id: str, output_path: str):
        """导出指标到CSV文件"""
        if version_id not in self.versions:
            raise ValueError(f"Version {version_id} not found.")
        
        version = self.versions[version_id]
        
        lines = ["timestamp,metric_type,value,epoch,phase"]
        for metric in version.metrics:
            lines.append(f"{metric.timestamp},{metric.metric_type},"
                        f"{metric.value},{metric.epoch or ''},{metric.phase}")
        
        with open(output_path, 'w') as f:
            f.write("\n".join(lines))
        
        return output_path


# ==================== 使用示例 ====================

def demo():
    """演示ML模型跟踪器的使用"""
    
    # 初始化跟踪器
    tracker = MLModelTracker("./demo_model_history")
    
    # 创建新版本
    print("Creating new model version...")
    version_id = tracker.create_version(
        name="ResNet50 Transfer Learning",
        hyperparameters={
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "optimizer": "Adam"
        },
        tags=["resnet", "transfer-learning", "image-classification"]
    )
    print(f"Created version: {version_id}")
    
    # 模拟训练过程中的指标记录
    print("\nLogging training metrics...")
    for epoch in range(1, 11):
        # 模拟损失下降
        loss = 1.0 / (epoch * 0.5 + 1) + 0.1 * (0.9 ** epoch)
        accuracy = 1 - loss + 0.05 * (0.95 ** epoch)
        f1_score = accuracy - 0.02
        
        # 记录训练指标
        tracker.log_metric(loss, MetricType.LOSS, 
                          epoch=epoch, phase="training")
        tracker.log_metric(accuracy, MetricType.ACCURACY,
                          epoch=epoch, phase="training")
        tracker.log_metric(accuracy - 0.02, MetricType.F1_SCORE,
                          epoch=epoch, phase="training")
        
        # 记录验证指标
        tracker.log_metric(loss * 1.1, MetricType.LOSS,
                          epoch=epoch, phase="validation")
        tracker.log_metric(accuracy * 0.98, MetricType.ACCURACY,
                          epoch=epoch, phase="validation")
        
        print(f"  Epoch {epoch}: Loss={loss:.4f}, Accuracy={accuracy:.4f}")
    
    # 生成报告
    print("\n" + "="*50)
    print(tracker.generate_report(version_id))
    
    # 导出到CSV
    csv_path = tracker.export_to_csv(version_id, "metrics_export.csv")
    print(f"\nExported to: {csv_path}")
    
    # 创建第二个版本进行对比
    print("\n" + "="*50)
    print("Creating v2 with different hyperparameters...")
    version_id2 = tracker.create_version(
        name="ResNet50 with Data Augmentation",
        hyperparameters={
            "learning_rate": 0.0005,
            "batch_size": 64,
            "epochs": 100,
            "optimizer": "AdamW"
        },
        tags=["resnet", "augmentation", "improved"]
    )
    
    # 模拟更好的性能
    for epoch in range(1, 11):
        loss = 0.8 / (epoch * 0.6 + 1) + 0.08 * (0.92 ** epoch)
        accuracy = 1 - loss + 0.03 * (0.97 ** epoch)
        tracker.log_metric(accuracy, MetricType.ACCURACY,
                          epoch=epoch, phase="validation")
    
    # 对比两个版本
    print("\nComparing versions...")
    comparison = tracker.compare_versions(
        [version_id, version_id2],
        MetricType.ACCURACY
    )
    
    print(f"\nMetric: {comparison['metric']}")
    for comp in comparison['comparisons']:
        print(f"  {comp['version_name']}: {comp['best_value']:.4f}")
    print(f"\nSummary: {comparison['summary']}")
    
    return tracker


if __name__ == "__main__":
    demo()
