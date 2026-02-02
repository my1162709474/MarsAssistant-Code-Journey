#!/usr/bin/env python3
"""
Smart CSV Tool - 智能CSV数据处理工具
=====================================
功能强大的CSV数据处理和分析工具，支持筛选、统计、转换和导出。

作者: AI Assistant
日期: 2026-02-02
"""

import csv
import json
import argparse
import sys
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime


class SmartCSVTool:
    """智能CSV处理工具类"""
    
    def __init__(self, file_path: str):
        """初始化CSV工具
        
        Args:
            file_path: CSV文件路径
        """
        self.file_path = file_path
        self.headers: List[str] = []
        self.data: List[Dict[str, str]] = []
        self._load_csv()
    
    def _load_csv(self) -> None:
        """加载CSV文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.headers = reader.fieldnames or []
                self.data = list(reader)
        except FileNotFoundError:
            print(f"错误: 文件 '{self.file_path}' 不存在")
            sys.exit(1)
        except Exception as e:
            print(f"错误: 读取CSV文件失败 - {e}")
            sys.exit(1)
    
    def info(self) -> Dict[str, Any]:
        """获取CSV文件基本信息"""
        return {
            "file_path": self.file_path,
            "total_rows": len(self.data),
            "total_columns": len(self.headers),
            "columns": self.headers,
            "column_types": self._guess_column_types()
        }
    
    def _guess_column_types(self) -> Dict[str, str]:
        """猜测每列的数据类型"""
        types = {}
        for col in self.headers:
            values = [row.get(col, '') for row in self.data[:100]]  # 只检查前100行
            try:
                # 检查是否是数字
                if all(self._is_number(v) for v in values if v):
                    types[col] = "numeric"
                # 检查是否是日期
                elif all(self._is_date(v) for v in values if v):
                    types[col] = "date"
                else:
                    types[col] = "string"
            except:
                types[col] = "string"
        return types
    
    def _is_number(self, value: str) -> bool:
        """检查值是否为数字"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _is_date(self, value: str) -> bool:
        """检查值是否为日期"""
        date_formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S', '%d-%m-%Y'
        ]
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False
    
    def filter(self, condition: Callable[[Dict[str, str]], bool]) -> List[Dict[str, str]]:
        """根据条件筛选数据
        
        Args:
            condition: 筛选条件函数
            
        Returns:
            筛选后的数据列表
        """
        return [row for row in self.data if condition(row)]
    
    def filter_by_column(self, column: str, value: str, operator: str = "==") -> List[Dict[str, str]]:
        """根据列值筛选数据
        
        Args:
            column: 列名
            value: 匹配的值
            operator: 操作符 (==, !=, >, <, >=, <=, contains, startswith, endswith)
        """
        results = []
        for row in self.data:
            row_value = row.get(column, '')
            match = False
            
            if operator == "==":
                match = row_value == value
            elif operator == "!=":
                match = row_value != value
            elif operator == ">":
                match = self._is_number(row_value) and self._is_number(value) and float(row_value) > float(value)
            elif operator == "<":
                match = self._is_number(row_value) and self._is_number(value) and float(row_value) < float(value)
            elif operator == ">=":
                match = self._is_number(row_value) and self._is_number(value) and float(row_value) >= float(value)
            elif operator == "<=":
                match = self._is_number(row_value) and self._is_number(value) and float(row_value) <= float(value)
            elif operator == "contains":
                match = value in row_value
            elif operator == "startswith":
                match = row_value.startswith(value)
            elif operator == "endswith":
                match = row_value.endswith(value)
            
            if match:
                results.append(row)
        
        return results
    
    def statistics(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """计算数值列的统计信息
        
        Args:
            columns: 要统计的列名，None表示所有数值列
            
        Returns:
            统计信息字典
        """
        if columns is None:
            col_types = self._guess_column_types()
            columns = [col for col, type_ in col_types.items() if type_ == "numeric"]
        
        stats = {}
        for col in columns:
            values = []
            for row in self.data:
                val = row.get(col, '')
                if val and self._is_number(val):
                    values.append(float(val))
            
            if values:
                n = len(values)
                total = sum(values)
                mean_val = total / n if n > 0 else 0
                sorted_vals = sorted(values)
                mid = n // 2
                
                stats[col] = {
                    "count": n,
                    "sum": round(total, 2),
                    "mean": round(mean_val, 2),
                    "min": min(values),
                    "max": max(values),
                    "median": sorted_vals[mid] if n % 2 else (sorted_vals[mid-1] + sorted_vals[mid]) / 2,
                    "std": self._standard_deviation(values, mean_val) if n > 1 else 0
                }
        
        return stats
    
    def _standard_deviation(self, values: List[float], mean: float) -> float:
        """计算标准差"""
        n = len(values)
        if n <= 1:
            return 0
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        return round(variance ** 0.5, 2)
    
    def group_by(self, column: str) -> Dict[str, List[Dict[str, str]]]:
        """按列分组数据
        
        Args:
            column: 分组依据的列名
            
        Returns:
            分组后的字典
        """
        groups = defaultdict(list)
        for row in self.data:
            key = row.get(column, 'N/A')
            groups[key].append(row)
        return dict(groups)
    
    def aggregate(self, group_column: str, agg_columns: List[str], 
                  agg_func: str = "sum") -> List[Dict[str, Any]]:
        """分组聚合计算
        
        Args:
            group_column: 分组列名
            agg_columns: 要聚合的数值列
            agg_func: 聚合函数 (sum, avg, count, min, max)
            
        Returns:
            聚合结果列表
        """
        groups = self.group_by(group_column)
        results = []
        
        for key, rows in groups.items():
            result = {group_column: key}
            result["count"] = len(rows)
            
            for col in agg_columns:
                values = []
                for row in rows:
                    val = row.get(col, '')
                    if val and self._is_number(val):
                        values.append(float(val))
                
                if values:
                    if agg_func == "sum":
                        result[f"{col}_sum"] = round(sum(values), 2)
                    elif agg_func == "avg":
                        result[f"{col}_avg"] = round(sum(values) / len(values), 2)
                    elif agg_func == "count":
                        result[f"{col}_count"] = len(values)
                    elif agg_func == "min":
                        result[f"{col}_min"] = min(values)
                    elif agg_func == "max":
                        result[f"{col}_max"] = max(values)
            
            results.append(result)
        
        return results
    
    def sort(self, column: str, reverse: bool = False) -> List[Dict[str, str]]:
        """按列排序数据
        
        Args:
            column: 排序依据的列名
            reverse: 是否降序排序
            
        Returns:
            排序后的数据列表
        """
        return sorted(self.data, key=lambda x: x.get(column, ''), reverse=reverse)
    
    def select_columns(self, columns: List[str]) -> List[Dict[str, str]]:
        """选择指定的列
        
        Args:
            columns: 要保留的列名列表
            
        Returns:
            只包含指定列的数据列表
        """
        return [{col: row.get(col, '') for col in columns} for row in self.data]
    
    def rename_column(self, old_name: str, new_name: str) -> None:
        """重命名列
        
        Args:
            old_name: 原列名
            new_name: 新列名
        """
        if old_name not in self.headers:
            print(f"错误: 列 '{old_name}' 不存在")
            return
        
        self.headers = [new_name if col == old_name else col for col in self.headers]
        for row in self.data:
            if old_name in row:
                row[new_name] = row.pop(old_name)
    
    def add_column(self, column_name: str, default_value: str = "") -> None:
        """添加新列
        
        Args:
            column_name: 新列名
            default_value: 默认值
        """
        if column_name in self.headers:
            print(f"警告: 列 '{column_name}' 已存在")
            return
        
        self.headers.append(column_name)
        for row in self.data:
            row[column_name] = default_value
    
    def export_json(self, output_path: str, data: Optional[List[Dict[str, str]]] = None) -> None:
        """导出为JSON格式
        
        Args:
            output_path: 输出文件路径
            data: 要导出的数据，None表示全部数据
        """
        export_data = data if data is not None else self.data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"已导出到: {output_path}")
    
    def export_csv(self, output_path: str, data: Optional[List[Dict[str, str]]] = None,
                   columns: Optional[List[str]] = None) -> None:
        """导出为CSV格式
        
        Args:
            output_path: 输出文件路径
            data: 要导出的数据，None表示全部数据
            columns: 要导出的列，None表示所有列
        """
        export_data = data if data is not None else self.data
        cols = columns if columns else self.headers
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            for row in export_data:
                filtered_row = {col: row.get(col, '') for col in cols}
                writer.writerow(filtered_row)
        print(f"已导出到: {output_path}")
    
    def preview(self, n: int = 5) -> None:
        """预览数据
        
        Args:
            n: 预览行数
        """
        print(f"\n{'='*60}")
        print(f"文件: {self.file_path}")
        print(f"总行数: {len(self.data)}, 总列数: {len(self.headers)}")
        print(f"列名: {', '.join(self.headers)}")
        print(f"{'='*60}")
        print("\n前5行预览:")
        for i, row in enumerate(self.data[:n]):
            print(f"行{i+1}: {row}")
        print()


def demo():
    """演示函数"""
    print("Smart CSV Tool 演示")
    print("=" * 40)
    
    # 创建示例CSV文件
    sample_data = [
        {"name": "张三", "age": "25", "city": "北京", "score": "85"},
        {"name": "李四", "age": "30", "city": "上海", "score": "92"},
        {"name": "王五", "age": "28", "city": "北京", "score": "78"},
        {"name": "赵六", "age": "35", "city": "深圳", "score": "95"},
        {"name": "钱七", "age": "22", "city": "上海", "score": "88"},
    ]
    
    sample_file = "sample_data.csv"
    with open(sample_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "city", "score"])
        writer.writeheader()
        writer.writerows(sample_data)
    
    # 使用工具处理
    tool = SmartCSVTool(sample_file)
    
    # 基本信息
    print("1. 文件信息:")
    info = tool.info()
    print(f"   - 总行数: {info['total_rows']}")
    print(f"   - 总列数: {info['total_columns']}")
    print(f"   - 列名: {info['columns']}")
    print(f"   - 推断类型: {info['column_types']}")
    
    # 筛选
    print("\n2. 筛选北京的用户:")
    filtered = tool.filter_by_column("city", "北京")
    for row in filtered:
        print(f"   - {row}")
    
    # 统计
    print("\n3. 数值统计:")
    stats = tool.statistics()
    for col, stat in stats.items():
        print(f"   - {col}: 平均={stat['mean']}, 总和={stat['sum']}, 最大={stat['max']}")
    
    # 分组聚合
    print("\n4. 按城市分组统计:")
    agg_results = tool.aggregate("city", ["score"], "avg")
    for result in agg_results:
        print(f"   - {result}")
    
    # 导出
    print("\n5. 导出筛选结果:")
    tool.export_json("filtered_output.json", filtered)
    tool.export_csv("filtered_output.csv", filtered)
    
    # 清理
    import os
    os.remove(sample_file)
    print("\n演示完成！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Smart CSV Tool - 智能CSV数据处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s data.csv --info                    # 查看文件信息
  %(prog)s data.csv --filter city=北京         # 筛选北京数据
  %(prog)s data.csv --stats score age         # 统计指定列
  %(prog)s data.csv --group city              # 按城市分组
  %(prog)s data.csv --export json output.json # 导出为JSON
  %(prog)s data.csv --preview                 # 预览数据
        """
    )
    
    parser.add_argument("file", help="CSV文件路径")
    parser.add_argument("--info", action="store_true", help="显示文件信息")
    parser.add_argument("--filter", help="筛选条件 (列名=值)")
    parser.add_argument("--filter-op", default="==", 
                        choices=["==", "!=", ">", "<", ">=", "<=", "contains"],
                        help="筛选操作符")
    parser.add_argument("--stats", nargs="+", help="要统计的列名")
    parser.add_argument("--group", help="分组依据的列名")
    parser.add_argument("--agg", nargs="+", help="聚合函数和列 (如: sum score age)")
    parser.add_argument("--sort", help="排序依据的列名")
    parser.add_argument("--reverse", action="store_true", help="降序排序")
    parser.add_argument("--select", nargs="+", help="选择指定的列")
    parser.add_argument("--export", choices=["json", "csv"], help="导出格式")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--preview", action="store_true", help="预览数据")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    
    args = parser.parse_args()
    
    # 运行演示
    if args.demo:
        demo()
        return
    
    # 加载CSV工具
    tool = SmartCSVTool(args.file)
    
    # 显示信息
    if args.info:
        info = tool.info()
        print(f"文件: {info['file_path']}")
        print(f"总行数: {info['total_rows']}")
        print(f"总列数: {info['total_columns']}")
        print(f"列名: {info['columns']}")
        print(f"列类型: {info['column_types']}")
    
    # 预览
    if args.preview:
        tool.preview()
    
    # 筛选
    if args.filter:
        col, val = args.filter.split("=", 1)
        filtered = tool.filter_by_column(col.strip(), val.strip(), args.filter_op)
        print(f"\n筛选结果 ({len(filtered)} 行):")
        for row in filtered:
            print(row)
        # 导出筛选结果
        if args.export and args.output:
            if args.export == "json":
                tool.export_json(args.output, filtered)
            else:
                tool.export_csv(args.output, filtered)
    
    # 统计
    if args.stats:
        stats = tool.statistics(args.stats)
        print("\n统计结果:")
        for col, stat in stats.items():
            print(f"  {col}:")
            for k, v in stat.items():
                print(f"    - {k}: {v}")
    
    # 分组
    if args.group:
        groups = tool.group_by(args.group)
        print(f"\n分组结果 ({len(groups)} 组):")
        for key, rows in groups.items():
            print(f"  {key}: {len(rows)} 行")
    
    # 聚合
    if args.agg:
        func_name = args.agg[0]
        agg_cols = args.agg[1:]
        if args.group:
            results = tool.aggregate(args.group, agg_cols, func_name)
            print(f"\n聚合结果:")
            for result in results:
                print(f"  {result}")
        else:
            print("错误: 聚合操作需要指定 --group")
    
    # 排序
    if args.sort:
        sorted_data = tool.sort(args.sort, args.reverse)
        print(f"\n排序结果 (前10行):")
        for row in sorted_data[:10]:
            print(row)
    
    # 选择列
    if args.select:
        selected = tool.select_columns(args.select)
        print(f"\n选择列结果 ({len(selected)} 行):")
        for row in selected[:5]:
            print(row)


if __name__ == "__main__":
    main()
