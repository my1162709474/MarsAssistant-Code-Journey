#!/usr/bin/env python3
"""
智能数据库工具 (Day 52)
======================
支持 SQLite、MySQL、PostgreSQL、MongoDB 的多功能数据库管理工具

功能特性:
- 多数据库支持 (SQLite/MySQL/PostgreSQL/MongoDB)
- 智能查询生成 (自然语言转 SQL)
- 数据备份与恢复
- 性能分析与优化建议
- ER 图生成
- 数据导入导出 (CSV/JSON/SQL)

使用方式:
    python smart_database_tool.py --help
    python smart_database_tool.py --query "查询所有用户" --db sqlite:////tmp/test.db
    python smart_database_tool.py --backup --db sqlite:////tmp/test.db --output backup/
    python smart_database_tool.py --export --db sqlite:////tmp/test.db --format csv --table users
"""

import argparse
import json
import csv
import sqlite3
import subprocess
import sys
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
import sqlparse
from collections import defaultdict


class DatabaseType:
    """数据库类型常量"""
    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


class SmartDatabaseTool:
    """智能数据库工具主类"""
    
    def __init__(self, db_url: str):
        """
        初始化数据库连接
        
        Args:
            db_url: 数据库连接 URL
                - SQLite: sqlite:///path/to/database.db
                - MySQL: mysql://user:password@host:port/database
                - PostgreSQL: postgresql://user:password@host:port/database
                - MongoDB: mongodb://user:password@host:port/database
        """
        self.db_url = db_url
        self.db_type = self._parse_db_type(db_url)
        self.connection = None
        self._connect()
    
    def _parse_db_type(self, db_url: str) -> str:
        """解析数据库类型"""
        parsed = urlparse(db_url)
        scheme = parsed.scheme.lower()
        
        if scheme == DatabaseType.SQLITE:
            return DatabaseType.SQLITE
        elif scheme == DatabaseType.MYSQL:
            return DatabaseType.MYSQL
        elif scheme == DatabaseType.POSTGRESQL:
            return DatabaseType.POSTGRESQL
        elif scheme == DatabaseType.MONGODB:
            return DatabaseType.MONGODB
        else:
            raise ValueError(f"不支持的数据库类型: {scheme}")
    
    def _connect(self):
        """建立数据库连接"""
        if self.db_type == DatabaseType.SQLITE:
            path = self.db_url.replace("sqlite:///", "").replace("sqlite://", "")
            if not path:
                path = ":memory:"
            self.connection = sqlite3.connect(path)
            self.connection.row_factory = sqlite3.Row
        
        elif self.db_type == DatabaseType.MYSQL:
            try:
                import pymysql
                parsed = urlparse(self.db_url)
                self.connection = pymysql.connect(
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 3306,
                    user=parsed.username or "root",
                    password=parsed.password or "",
                    database=parsed.path[1:] or ""
                )
            except ImportError:
                print("⚠️  需要安装 pymysql: pip install pymysql")
                raise
        
        elif self.db_type == DatabaseType.POSTGRESQL:
            try:
                import psycopg2
                parsed = urlparse(self.db_url)
                self.connection = psycopg2.connect(
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 5432,
                    user=parsed.username or "postgres",
                    password=parsed.password or "",
                    database=parsed.path[1:] or "postgres"
                )
            except ImportError:
                print("⚠️  需要安装 psycopg2: pip install psycopg2-binary")
                raise
        
        elif self.db_type == DatabaseType.MONGODB:
            try:
                from pymongo import MongoClient
                parsed = urlparse(self.db_url)
                host = parsed.hostname or "localhost"
                port = parsed.port or 27017
                auth = parsed.username and parsed.password
                if auth:
                    self.connection = MongoClient(
                        f"mongodb://{parsed.username}:{parsed.password}@{host}:{port}/"
                    )
                else:
                    self.connection = MongoClient(f"mongodb://{host}:{port}/")
            except ImportError:
                print("⚠️  需要安装 pymongo: pip install pymongo")
                raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            if self.db_type == DatabaseType.MONGODB:
                self.connection.close()
            else:
                self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ==================== 数据库信息 ====================
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库基本信息"""
        info = {
            "db_type": self.db_type,
            "db_url": self.db_url,
            "tables": [],
            "size": 0
        }
        
        if self.db_type == DatabaseType.SQLITE:
            info["tables"] = self._get_sqlite_tables()
            info["size"] = self._get_sqlite_size()
        
        elif self.db_type == DatabaseType.MYSQL:
            info["tables"] = self._get_mysql_tables()
        
        elif self.db_type == DatabaseType.POSTGRESQL:
            info["tables"] = self._get_postgresql_tables()
        
        elif self.db_type == DatabaseType.MONGODB:
            info["collections"] = self._get_mongodb_collections()
        
        return info
    
    def _get_sqlite_tables(self) -> List[Dict]:
        """获取 SQLite 数据库中的表信息"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = []
        for row in cursor.fetchall():
            cursor.execute(f"SELECT COUNT(*) FROM {row['name']}")
            count = cursor.fetchone()[0]
            tables.append({
                "name": row["name"],
                "sql": row["sql"],
                "row_count": count
            })
        return tables
    
    def _get_sqlite_size(self) -> int:
        """获取 SQLite 数据库大小"""
        path = self.db_url.replace("sqlite:///", "").replace("sqlite://", "")
        if path and os.path.exists(path):
            return os.path.getsize(path)
        return 0
    
    def _get_mysql_tables(self) -> List[Dict]:
        """获取 MySQL 数据库中的表信息"""
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = cursor.fetchone()[0]
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_sql = cursor.fetchone()[1]
            tables.append({
                "name": table_name,
                "sql": create_sql,
                "row_count": count
            })
        return tables
    
    def _get_postgresql_tables(self) -> List[Dict]:
        """获取 PostgreSQL 数据库中的表信息"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = []
        for row in cursor.fetchall():
            table_name = row[0]
            cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
            count = cursor.fetchone()[0]
            cursor.execute("""
                SELECT pg_get_tabledef('%s') WHERE EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = '%s'
                )
            """ % (table_name, table_name))
            create_sql = cursor.fetchone()
            tables.append({
                "name": table_name,
                "sql": create_sql[0] if create_sql else "",
                "row_count": count
            })
        return tables
    
    def _get_mongodb_collections(self) -> List[Dict]:
        """获取 MongoDB 数据库中的集合信息"""
        db_name = urlparse(self.db_url).path[1:] or "test"
        db = self.connection[db_name]
        collections = []
        for name in db.list_collection_names():
            count = db[name].count_documents({})
            collections.append({
                "name": name,
                "document_count": count
            })
        return collections
    
    # ==================== 查询执行 ====================
    
    def execute_query(self, query: str, params: tuple = None) -> Tuple[List[Dict], List[str]]:
        """
        执行 SQL 查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            (查询结果列表, 列名列表)
        """
        cursor = self.connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            columns = []
            rows = []
        
        self.connection.commit()
        return rows, columns
    
    def execute_file(self, filepath: str) -> Tuple[int, float]:
        """
        执行 SQL 文件
        
        Args:
            filepath: SQL 文件路径
            
        Returns:
            (影响的行数, 执行时间秒)
        """
        with open(filepath, 'r') as f:
            sql_content = f.read()
        
        statements = sqlparse.split(sql_content)
        start_time = datetime.now()
        total_affected = 0
        
        cursor = self.connection.cursor()
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                total_affected += cursor.rowcount
        
        self.connection.commit()
        elapsed = (datetime.now() - start_time).total_seconds()
        return total_affected, elapsed
    
    # ==================== 自然语言转 SQL ====================
    
    def nl_to_sql(self, natural_query: str, schema_info: str = None) -> str:
        """
        将自然语言查询转换为 SQL (简化版本)
        
        Args:
            natural_query: 自然语言查询
            schema_info: 数据库 schema 信息
            
        Returns:
            SQL 查询语句
        """
        query_lower = natural_query.lower()
        
        # 提取表名和列名
        if not schema_info:
            if self.db_type == DatabaseType.SQLITE:
                tables = [t["name"] for t in self._get_sqlite_tables()]
                schema_info = "Tables: " + ", ".join(tables)
        
        # 简单的模式匹配转换
        if "所有" in query_lower or "查询所有" in query_lower:
            if "用户" in query_lower:
                return "SELECT * FROM users"
            elif "订单" in query_lower:
                return "SELECT * FROM orders"
            elif "产品" in query_lower:
                return "SELECT * FROM products"
            else:
                return "SELECT * FROM table_name"
        
        elif "统计" in query_lower or "数量" in query_lower:
            if "用户" in query_lower:
                return "SELECT COUNT(*) as count FROM users"
            else:
                return "SELECT COUNT(*) as count FROM table_name"
        
        elif "最新" in query_lower or "最近" in query_lower:
            return "SELECT * FROM table_name ORDER BY created_at DESC LIMIT 10"
        
        elif "平均" in query_lower:
            return "SELECT AVG(column) as avg_value FROM table_name"
        
        elif "求和" in query_lower or "总计" in query_lower:
            return "SELECT SUM(column) as total FROM table_name"
        
        else:
            return f"-- 无法解析的查询: {natural_query}\nSELECT * FROM table_name LIMIT 10"
    
    # ==================== 数据导入导出 ====================
    
    def export_table(self, table_name: str, format: str = "csv", 
                     output_path: str = None) -> str:
        """
        导出表数据
        
        Args:
            table_name: 表名
            format: 导出格式 (csv/json/sql)
            output_path: 输出路径
            
        Returns:
            输出文件路径
        """
        if not output_path:
            output_path = f"{table_name}_export.{format}"
        
        if format == "csv":
            return self._export_to_csv(table_name, output_path)
        elif format == "json":
            return self._export_to_json(table_name, output_path)
        elif format == "sql":
            return self._export_to_sql(table_name, output_path)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _export_to_csv(self, table_name: str, output_path: str) -> str:
        """导出为 CSV 格式"""
        rows, columns = self.execute_query(f"SELECT * FROM {table_name}")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        
        return output_path
    
    def _export_to_json(self, table_name: str, output_path: str) -> str:
        """导出为 JSON 格式"""
        rows, columns = self.execute_query(f"SELECT * FROM {table_name}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def _export_to_sql(self, table_name: str, output_path: str) -> str:
        """导出为 SQL 格式"""
        rows, columns = self.execute_query(f"SELECT * FROM {table_name}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"-- Export of {table_name} at {datetime.now()}\n")
            for row in rows:
                values = []
                for val in row.values():
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str):
                        values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")
                    else:
                        values.append(str(val))
                f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
        
        return output_path
    
    def import_data(self, table_name: str, filepath: str, 
                    format: str = "csv", create_table: bool = False):
        """
        导入数据
        
        Args:
            table_name: 目标表名
            filepath: 数据文件路径
            format: 数据格式 (csv/json/sql)
            create_table: 是否自动创建表
        """
        if format == "csv":
            self._import_from_csv(table_name, filepath, create_table)
        elif format == "json":
            self._import_from_json(table_name, filepath, create_table)
        elif format == "sql":
            self._import_from_sql(filepath)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _import_from_csv(self, table_name: str, filepath: str, create_table: bool):
        """从 CSV 导入"""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if create_table:
                self._create_table_from_csv(table_name, reader.fieldnames, list(reader))
            
            cursor = self.connection.cursor()
            for row in reader:
                placeholders = ', '.join(['?' for _ in row])
                columns = ', '.join(row.keys())
                cursor.execute(
                    f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                    list(row.values())
                )
        self.connection.commit()
    
    def _create_table_from_csv(self, table_name: str, columns: List[str], sample_rows: List[Dict]):
        """从 CSV 创建表"""
        if not sample_rows:
            return
        
        # 推断列类型
        type_mapping = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT"
        }
        
        col_defs = []
        for col in columns:
            sample_val = sample_rows[0].get(col, "")
            col_type = type_mapping.get(type(sample_val), "TEXT")
            col_defs.append(f"{col} {col_type}")
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"
        self.connection.execute(create_sql)
        self.connection.commit()
    
    def _import_from_json(self, table_name: str, filepath: str, create_table: bool):
        """从 JSON 导入"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            return
        
        if create_table:
            self._create_table_from_json(table_name, data[0])
        
        cursor = self.connection.cursor()
        for row in data:
            placeholders = ', '.join(['?' for _ in row])
            columns = ', '.join(row.keys())
            cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                list(row.values())
            )
        self.connection.commit()
    
    def _create_table_from_json(self, table_name: str, sample: Dict):
        """从 JSON 创建表"""
        col_defs = []
        for key, val in sample.items():
            col_type = "INTEGER" if isinstance(val, int) else \
                      "REAL" if isinstance(val, float) else \
                      "TEXT"
            col_defs.append(f"{key} {col_type}")
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"
        self.connection.execute(create_sql)
        self.connection.commit()
    
    def _import_from_sql(self, filepath: str):
        """从 SQL 文件导入"""
        self.execute_file(filepath)
    
    # ==================== 备份恢复 ====================
    
    def backup(self, output_dir: str = ".") -> str:
        """
        备份数据库
        
        Args:
            output_dir: 输出目录
            
        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{self.db_type}_{timestamp}.sql"
        filepath = os.path.join(output_dir, filename)
        
        if self.db_type == DatabaseType.SQLITE:
            self._backup_sqlite(filepath)
        elif self.db_type == DatabaseType.MYSQL:
            self._backup_mysql(filepath)
        elif self.db_type == DatabaseType.POSTGRESQL:
            self._backup_postgresql(filepath)
        
        return filepath
    
    def _backup_sqlite(self, filepath: str):
        """SQLite 备份"""
        path = self.db_url.replace("sqlite:///", "").replace("sqlite://", "")
        if path and os.path.exists(path):
            with open(filepath, 'w') as f:
                for line in self.connection.iterdump():
                    f.write(f"{line}\n")
    
    def _backup_mysql(self, filepath: str):
        """MySQL 备份 (使用 mysqldump)"""
        parsed = urlparse(self.db_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 3306
        user = parsed.username or "root"
        password = parsed.password or ""
        database = parsed.path[1:] or ""
        
        cmd = [
            "mysqldump",
            f"-h{host}",
            f"-P{port}",
            f"-u{user}",
            f"-p{password}",
            database
        ]
        
        with open(filepath, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
    
    def _backup_postgresql(self, filepath: str):
        """PostgreSQL 备份 (使用 pg_dump)"""
        parsed = urlparse(self.db_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        user = parsed.username or "postgres"
        password = parsed.password or ""
        database = parsed.path[1:] or "postgres"
        
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        
        cmd = [
            "pg_dump",
            f"-h{host}",
            f"-p{port}",
            f"-U{user}",
            database
        ]
        
        with open(filepath, 'w') as f:
            subprocess.run(cmd, stdout=f, env=env, check=True)
    
    # ==================== 性能分析 ====================
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析数据库性能"""
        analysis = {
            "slow_queries": [],
            "missing_indexes": [],
            "table_stats": [],
            "recommendations": []
        }
        
        if self.db_type == DatabaseType.SQLITE:
            analysis = self._analyze_sqlite_performance()
        
        return analysis
    
    def _analyze_sqlite_performance(self) -> Dict[str, Any]:
        """SQLite 性能分析"""
        analysis = {
            "slow_queries": [],
            "missing_indexes": [],
            "table_stats": [],
            "recommendations": []
        }
        
        cursor = self.connection.cursor()
        
        # 获取表统计信息
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        for (table_name,) in cursor.fetchall():
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            analysis["table_stats"].append({
                "name": table_name,
                "row_count": count,
                "columns": len(columns),
                "has_autoindex": any(c[1].startswith("sqlite_") for c in columns)
            })
        
        # 分析查询建议
        for table in analysis["table_stats"]:
            if table["row_count"] > 10000 and not table["has_autoindex"]:
                analysis["missing_indexes"].append({
                    "table": table["name"],
                    "reason": "大表缺少索引",
                    "suggestion": f"CREATE INDEX idx_{table['name']}_id ON {table['name']}(id)"
                })
        
        # 生成优化建议
        if analysis["missing_indexes"]:
            analysis["recommendations"].append(
                f"建议为 {len(analysis['missing_indexes'])} 个大表创建索引"
            )
        
        return analysis
    
    # ==================== ER 图生成 ====================
    
    def generate_er_diagram(self, output_path: str = "er_diagram.dot") -> str:
        """
        生成 ER 图 (Graphviz DOT 格式)
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        if self.db_type == DatabaseType.MONGODB:
            raise ValueError("MongoDB 不支持 ER 图生成")
        
        dot_content = ["digraph ERDiagram {"]
        dot_content.append('  rankdir=LR;')
        dot_content.append('  node [shape=box];')
        dot_content.append('')
        
        if self.db_type == DatabaseType.SQLITE:
            tables = self._get_sqlite_tables()
        
        for table in tables:
            table_name = table["name"]
            dot_content.append(f'  {table_name} [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">')
            dot_content.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#E8E8E8"><B>{table_name}</B></TD></TR>')
            
            # 解析表结构获取列信息
            if table["sql"]:
                col_matches = re.findall(r'(\w+)\s+(\w+)', table["sql"])
                for col_name, col_type in col_matches[:10]:  # 限制列数
                    dot_content.append(f'    <TR><TD>{col_name}</TD><TD>{col_type}</TD></TR>')
            
            dot_content.append('  </TABLE>>];')
            dot_content.append('')
        
        dot_content.append('}')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_content))
        
        return output_path
    
    # ==================== SQL 格式化 ====================
    
    def format_sql(self, sql: str) -> str:
        """格式化 SQL 语句"""
        return sqlparse.format(sql, reindent=True, keyword_case='upper')
    
    # ==================== 安全查询 ====================
    
    def safe_query(self, query: str, max_results: int = 1000) -> Tuple[List[Dict], str]:
        """
        安全执行查询 (防止 SQL 注入)
        
        Args:
            query: SQL 查询
            max_results: 最大返回行数
            
        Returns:
            (查询结果, 状态消息)
        """
        # 检查危险关键字
        dangerous = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE", "EXEC", "EXECUTE"]
        query_upper = query.upper()
        
        for keyword in dangerous:
            if keyword in query_upper and "SELECT" not in query_upper:
                return [], f"⛔ 危险查询已阻止: 包含 {keyword} 关键字"
        
        # 检查 SELECT 是否存在
        if "SELECT" not in query_upper:
            return [], "⛔ 只支持 SELECT 查询"
        
        # 添加 LIMIT
        if "LIMIT" not in query_upper:
            query = f"{query} LIMIT {max_results}"
        
        try:
            rows, columns = self.execute_query(query)
            return rows, f"✅ 查询成功，返回 {len(rows)} 行"
        except Exception as e:
            return [], f"❌ 查询失败: {str(e)}"


# ==================== CLI 界面 ====================

def main():
    parser = argparse.ArgumentParser(
        description="智能数据库工具 - 支持多种数据库的多功能管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看数据库信息
  python smart_database_tool.py --info --db sqlite:///test.db
  
  # 执行查询
  python smart_database_tool.py --query "SELECT * FROM users" --db sqlite:///test.db
  
  # 导出表数据
  python smart_database_tool.py --export --db sqlite:///test.db --table users --format csv
  
  # 备份数据库
  python smart_database_tool.py --backup --db sqlite:///test.db --output ./backups/
  
  # 分析性能
  python smart_database_tool.py --analyze --db sqlite:///test.db
  
  # 生成 ER 图
  python smart_database_tool.py --er --db sqlite:///test.db
        """
    )
    
    parser.add_argument("--db", required=True, help="数据库连接 URL")
    parser.add_argument("--query", help="要执行的 SQL 查询")
    parser.add_argument("--export", action="store_true", help="导出数据模式")
    parser.add_argument("--table", help="导出/导入的表名")
    parser.add_argument("--format", default="csv", choices=["csv", "json", "sql"], help="导出格式")
    parser.add_argument("--output", default=".", help="输出目录")
    parser.add_argument("--import-file", help="导入数据文件")
    parser.add_argument("--backup", action="store_true", help="备份数据库")
    parser.add_argument("--analyze", action="store_true", help="性能分析")
    parser.add_argument("--er", action="store_true", help="生成 ER 图")
    parser.add_argument("--info", action="store_true", help="显示数据库信息")
    parser.add_argument("--nl", help="自然语言转 SQL")
    parser.add_argument("--limit", type=int, default=1000, help="查询结果限制")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    try:
        with SmartDatabaseTool(args.db) as db_tool:
            
            # 显示数据库信息
            if args.info:
                info = db_tool.get_database_info()
                print(f"\n🗄️  数据库信息")
                print(f"   类型: {info['db_type']}")
                print(f"   URL: {info['db_url']}")
                if 'tables' in info:
                    print(f"   表数量: {len(info['tables'])}")
                    for table in info['tables'][:10]:
                        print(f"   - {table['name']} ({table['row_count']} 行)")
                if 'collections' in info:
                    print(f"   集合数量: {len(info['collections'])}")
                    for coll in info['collections'][:10]:
                        print(f"   - {coll['name']} ({coll['document_count']} 文档)")
            
            # 执行查询
            elif args.query:
                if args.verbose:
                    formatted = db_tool.format_sql(args.query)
                    print(f"\n📝 格式化后的 SQL:\n{formatted}")
                
                rows, status = db_tool.safe_query(args.query, args.limit)
                print(f"\n{status}")
                if rows:
                    if args.verbose:
                        columns = list(rows[0].keys())
                        print(f"列: {', '.join(columns)}")
                    for row in rows[:20]:
                        print(f"   {row}")
                    if len(rows) > 20:
                        print(f"   ... 还有 {len(rows) - 20} 行")
            
            # 自然语言转 SQL
            elif args.nl:
                sql = db_tool.nl_to_sql(args.nl)
                print(f"\n💡 生成的 SQL:\n{sql}")
                if input("\n是否执行? (y/n): ").lower() == 'y':
                    rows, status = db_tool.safe_query(sql, args.limit)
                    print(f"\n{status}")
                    for row in rows[:10]:
                        print(f"   {row}")
            
            # 导出数据
            elif args.export:
                if not args.table:
                    print("⛔ 请指定 --table 参数")
                    sys.exit(1)
                filepath = db_tool.export_table(args.table, args.format, args.output)
                print(f"\n✅ 已导出到: {filepath}")
            
            # 导入数据
            elif args.import_file:
                if not args.table:
                    print("⛔ 请指定 --table 参数")
                    sys.exit(1)
                fmt = args.import_file.split('.')[-1].lower()
                db_tool.import_data(args.table, args.import_file, fmt, create_table=True)
                print(f"\n✅ 已从 {args.import_file} 导入到 {args.table}")
            
            # 备份
            elif args.backup:
                filepath = db_tool.backup(args.output)
                print(f"\n✅ 备份已保存到: {filepath}")
            
            # 性能分析
            elif args.analyze:
                analysis = db_tool.analyze_performance()
                print("\n📊 性能分析报告")
                print(f": {len(   表统计analysis['table_stats'])} 个表")
                if analysis['missing_indexes']:
                    print(f"   缺失索引: {len(analysis['missing_indexes'])} 个")
                    for idx in analysis['missing_indexes'][:5]:
                        print(f"   - {idx['table']}: {idx['suggestion']}")
                if analysis['recommendations']:
                    print("\n💡 优化建议:")
                    for rec in analysis['recommendations']:
                        print(f"   - {rec}")
            
            # ER 图
            elif args.er:
                filepath = db_tool.generate_er_diagram(args.output)
                print(f"\n✅ ER 图已生成: {filepath}")
                print("   使用 Graphviz 转换为图片: dot -Tpng er_diagram.dot -o er_diagram.png")
            
            else:
                parser.print_help()
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
