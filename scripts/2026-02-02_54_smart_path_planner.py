#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路径规划器
实现多种经典路径查找算法

作者: MarsAssistant
日期: 2026-02-02
"""

import heapq
from collections import deque
from typing import List, Tuple, Dict, Optional, Set
import json


class Graph:
    """图数据结构 - 支持有向/无向图"""
    
    def __init__(self, directed: bool = False):
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = {}
        self.directed = directed
    
    def add_node(self, node: str) -> None:
        """添加节点"""
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []
    
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0) -> None:
        """添加边"""
        self.add_node(from_node)
        self.add_node(to_node)
        self.adjacency_list[from_node].append((to_node, weight))
        if not self.directed:
            self.adjacency_list[to_node].append((from_node, weight))
    
    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """获取邻居节点"""
        return self.adjacency_list.get(node, [])
    
    def get_all_nodes(self) -> List[str]:
        """获取所有节点"""
        return list(self.adjacency_list.keys())
    
    def display(self) -> str:
        """以字符串形式显示图"""
        result = []
        for node, neighbors in self.adjacency_list.items():
            neighbor_str = ", ".join([f"{n}({w})" for n, w in neighbors])
            result.append(f"{node}: [{neighbor_str}]")
        return "\n".join(result)


class Dijkstra:
    """Dijkstra 算法 - 单源最短路径"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[Optional[List[str]], float]:
        """
        查找最短路径
        
        Args:
            start: 起点
            end: 终点
            
        Returns:
            (路径列表, 总距离) 或 (None, inf) 如果不存在路径
        """
        # 距离字典
        distances = {node: float('inf') for node in self.graph.get_all_nodes()}
        distances[start] = 0
        
        # 路径记录
        previous = {node: None for node in self.graph.get_all_nodes()}
        
        # 优先队列 (距离, 节点)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end:
                break
            
            for neighbor, weight in self.graph.get_neighbors(current_node):
                if neighbor in visited:
                    continue
                
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # 重建路径
        if distances[end] == float('inf'):
            return None, float('inf')
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        return path, distances[end]
    
    def find_all_shortest_paths(self, start: str) -> Dict[str, Tuple[List[str], float]]:
        """
        查找从起点到所有节点的最短路径
        
        Returns:
            {节点: (路径, 距离)}
        """
        distances = {node: float('inf') for node in self.graph.get_all_nodes()}
        distances[start] = 0
        
        previous = {node: None for node in self.graph.get_all_nodes()}
        
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            for neighbor, weight in self.graph.get_neighbors(current_node):
                if neighbor in visited:
                    continue
                
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # 重建所有路径
        result = {}
        for node in self.graph.get_all_nodes():
            if distances[node] != float('inf'):
                path = []
                current = node
                while current is not None:
                    path.append(current)
                    current = previous[current]
                path.reverse()
                result[node] = (path, distances[node])
        
        return result


class AStar:
    """A* 算法 - 启发式最短路径搜索"""
    
    def __init__(self, graph: Graph, heuristic: Dict[str, float]):
        """
        初始化 A* 算法
        
        Args:
            graph: 图
            heuristic: 启发式函: 估计距离数字典 {节点}
        """
        self.graph = graph
        self.heuristic = heuristic
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[Optional[List[str]], float]:
        """
        使用 A* 算法查找最短路径
        
        Args:
            start: 起点
            end: 终点
            
        Returns:
            (路径列表, 总距离)
        """
        # f(n) = g(n) + h(n)
        # g(n): 从起点到 n 的实际距离
        # h(n): 从 n 到终点的估计距离
        
        g_scores = {node: float('inf') for node in self.graph.get_all_nodes()}
        g_scores[start] = 0
        
        f_scores = {node: float('inf') for node in self.graph.get_all_nodes()}
        f_scores[start] = self.heuristic.get(start, 0)
        
        previous = {node: None for node in self.graph.get_all_nodes()}
        
        # 优先队列 (f_score, g_score, 节点)
        pq = [(f_scores[start], 0, start)]
        visited = set()
        
        while pq:
            _, current_g, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if current_node == end:
                break
            
            for neighbor, weight in self.graph.get_neighbors(current_node):
                if neighbor in visited:
                    continue
                
                new_g = current_g + weight
                
                if new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    previous[neighbor] = current_node
                    h = self.heuristic.get(neighbor, 0)
                    f = new_g + h
                    f_scores[neighbor] = f
                    heapq.heappush(pq, (f, new_g, neighbor))
        
        # 重建路径
        if g_scores[end] == float('inf'):
            return None, float('inf')
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        return path, g_scores[end]


class BFSPathFinder:
    """BFS 路径查找 - 适用于无权图"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        查找最短路径（无权图）
        
        Returns:
            路径列表 或 None
        """
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor, _ in self.graph.get_neighbors(current):
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def find_all_paths(self, start: str, end: str, max_paths: int = 10) -> List[List[str]]:
        """
        查找所有路径
        
        Args:
            start: 起点
            end: 终点
            max_paths: 最大路径数量
        """
        paths = []
        
        def dfs(current: str, path: List[str], visited: Set[str]):
            if len(paths) >= max_paths:
                return
            
            if current == end:
                paths.append(path.copy())
                return
            
            for neighbor, _ in self.graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)
        
        visited = {start}
        dfs(start, [start], visited)
        
        return paths


class PathVisualizer:
    """路径可视化工具"""
    
    @staticmethod
    def format_path(path: List[str]) -> str:
        """格式化路径显示"""
        return " -> ".join(path)
    
    @staticmethod
    def format_result(path: Optional[List[str]], distance: float = 0) -> str:
        """格式化结果输出"""
        if path is None:
            return "X 路径不存在"
        
        result = f"V 路径: {PathVisualizer.format_path(path)}"
        if distance > 0:
            result += f"\n# 总距离: {distance}"
        return result
    
    @staticmethod
    def compare_algorithms(algorithms: Dict[str, Tuple[Optional[List[str]], float]]) -> str:
        """比较不同算法的结果"""
        result = "# 算法比较结果:\n"
        result += "=" * 40 + "\n"
        
        for name, (path, distance) in algorithms.items():
            if path:
                result += f"\n* {name}:\n"
                result += f"   路径: {PathVisualizer.format_path(path)}\n"
                result += f"   距离: {distance}\n"
            else:
                result += f"\n* {name}:\n"
                result += f"   路径: 不存在\n"
        
        return result


class MazeSolver:
    """迷宫求解器 - 二维网格迷宫"""
    
    def __init__(self, maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]):
        """
        初始化迷宫求解器
        
        Args:
            maze: 迷宫网格 (0=通路, 1=墙壁)
            start: 起点坐标 (row, col)
            end: 终点坐标 (row, col)
        """
        self.maze = maze
        self.start = start
        self.end = end
        self.rows = len(maze)
        self.cols = len(maze[0]) if self.rows > 0 else 0
    
    def is_valid(self, row: int, col: int) -> bool:
        """检查位置是否有效"""
        return 0 <= row < self.rows and 0 <= col < self.cols and self.maze[row][col] == 0
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """获取相邻位置（上右下左）"""
        row, col = pos
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        neighbors = []
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid(new_row, new_col):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def bfs_solve(self) -> Optional[List[Tuple[int, int]]]:
        """BFS 求解迷宫"""
        if not self.is_valid(*self.start) or not self.is_valid(*self.end):
            return None
        
        visited = {self.start}
        queue = deque([(self.start, [self.start])])
        
        while queue:
            current, path = queue.popleft()
            
            if current == self.end:
                return path
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def astar_solve(self) -> Optional[List[Tuple[int, int]]]:
        """A* 求解迷宫"""
        if not self.is_valid(*self.start) or not self.is_valid(*self.end):
            return None
        
        def heuristic(pos: Tuple[int, int]) -> float:
            """曼哈顿距离启发式"""
            return abs(pos[0] - self.end[0]) + abs(pos[1] - self.end[1])
        
        g_scores = {}
        f_scores = {}
        previous = {}
        
        start_key = self.start
        end_key = self.end
        
        g_scores[start_key] = 0
        f_scores[start_key] = heuristic(start_key)
        
        pq = [(f_scores[start_key], 0, start_key)]
        visited = set()
        
        while pq:
            _, g, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == end_key:
                # 重建路径
                path = []
                while current:
                    path.append(current)
                    current = previous.get(current)
                return list(reversed(path))
            
            for neighbor in self.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                new_g = g + 1
                
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    previous[neighbor] = current
                    f = new_g + heuristic(neighbor)
                    f_scores[neighbor] = f
                    heapq.heappush(pq, (f, new_g, neighbor))
        
        return None
    
    def print_maze(self, path: Optional[List[Tuple[int, int]]] = None):
        """打印迷宫（可选显示路径）"""
        if path:
            path_set = set(path)
        
        print("\n# 迷宫地图:")
        print("  " + " ".join(str(i % 10) for i in range(self.cols)))
        print("  " + "-" * (self.cols * 2 - 1))
        
        for r in range(self.rows):
            row_str = f"{r % 10}| "
            for c in range(self.cols):
                if (r, c) == self.start:
                    row_str += "S "  # 起点
                elif (r, c) == self.end:
                    row_str += "E "  # 终点
                elif path and (r, c) in path_set:
                    row_str += ". "  # 路径
                elif self.maze[r][c] == 1:
                    row_str += "# "  # 墙壁
                else:
                    row_str += "  "  # 通路
            print(row_str)


def demo_graph_pathfinding():
    """演示：图路径查找"""
    print("\n" + "=" * 50)
    print("= 图路径查找演示")
    print("=" * 50)
    
    # 创建图
    graph = Graph(directed=False)
    
    # 添加节点和边
    cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都"]
    
    edges = [
        ("北京", "上海", 1200),
        ("北京", "南京", 1000),
        ("北京", "武汉", 1100),
        ("上海", "杭州", 200),
        ("上海", "南京", 300),
        ("上海", "广州", 1400),
        ("广州", "深圳", 150),
        ("广州", "武汉", 900),
        ("深圳", "广州", 150),
        ("杭州", "南京", 300),
        ("杭州", "上海", 200),
        ("武汉", "南京", 600),
        ("武汉", "成都", 800),
        ("武汉", "广州", 900),
    ]
    
    for from_city, to_city, distance in edges:
        graph.add_edge(from_city, to_city, distance)
    
    print("\n# 城市地图:")
    print(graph.display())
    
    # Dijkstra 算法
    print("\n* Dijkstra 算法:")
    dijkstra = Dijkstra(graph)
    path, distance = dijkstra.find_shortest_path("北京", "深圳")
    print(PathVisualizer.format_result(path, distance))
    
    # A* 算法（使用直线距离作为启发式）
    print("\n* A* 算法:")
    heuristic = {
        "北京": 2200, "上海": 1400, "广州": 0, "深圳": 150,
        "杭州": 1600, "南京": 1200, "武汉": 1000, "成都": 800
    }
    astar = AStar(graph, heuristic)
    path, distance = astar.find_shortest_path("北京", "深圳")
    print(PathVisualizer.format_result(path, distance))
    
    # BFS 算法
    print("\n* BFS 算法:")
    bfs = BFSPathFinder(graph)
    path = bfs.find_shortest_path("北京", "深圳")
    print(PathVisualizer.format_result(path))
    
    # 比较算法
    print("\n" + PathVisualizer.compare_algorithms({
        "Dijkstra": dijkstra.find_shortest_path("北京", "成都"),
        "A*": astar.find_shortest_path("北京", "成都"),
        "BFS": (bfs.find_shortest_path("北京", "成都"), 0)
    }))


def demo_maze_solving():
    """演示：迷宫求解"""
    print("\n" + "=" * 50)
    print("= 迷宫求解演示")
    print("=" * 50)
    
    # 创建迷宫 (0=通路, 1=墙壁)
    maze = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    
    start = (0, 0)
    end = (6, 7)
    
    solver = MazeSolver(maze, start, end)
    
    print("\n原始迷宫:")
    solver.print_maze()
    
    # BFS 求解
    print("\n* BFS 求解:")
    path = solver.bfs_solve()
    if path:
        solver.print_maze(path)
        print(f"# 路径长度: {len(path) - 1} 步")
    
    # A* 求解
    print("\n* A* 求解:")
    path = solver.astar_solve()
    if path:
        solver.print_maze(path)
        print(f"# 路径长度: {len(path) - 1} 步")


def demo_road_network():
    """演示：道路网络分析"""
    print("\n" + "=" * 50)
    print("= 道路网络分析演示")
    print("=" * 50)
    
    # 模拟城市道路网络
    graph = Graph(directed=False)
    
    roads = [
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 1),
        ("B", "D", 5), ("C", "D", 8), ("C", "E", 10),
        ("D", "E", 2), ("D", "F", 6), ("E", "F", 3)
    ]
    
    for from_node, to_node, distance in roads:
        graph.add_edge(from_node, to_node, distance)
    
    print("\n道路网络:")
    print(graph.display())
    
    # 查找从 A 到 F 的最短路径
    dijkstra = Dijkstra(graph)
    
    print("\n* 最短路径分析 (A -> F):")
    path, distance = dijkstra.find_shortest_path("A", "F")
    print(PathVisualizer.format_result(path, distance))
    
    # 查找所有最短路径
    print("\n* 所有节点的最短路径:")
    all_paths = dijkstra.find_all_shortest_paths("A")
    for node, (path, dist) in sorted(all_paths.items()):
        print(f"  {node}: {path} (距离: {dist})")


def create_city_navigation():
    """创建城市导航示例"""
    print("\n" + "=" * 50)
    print("= 智能城市导航系统")
    print("=" * 50)
    
    # 城市地图
    city_map = Graph(directed=True)  # 有向图（单行道）
    
    locations = [
        ("火车站", "市中心", 15),
        ("火车站", "大学城", 25),
        ("市中心", "商业区", 10),
        ("市中心", "医院", 20),
        ("大学城", "科技园区", 15),
        ("商业区", "科技园区", 30),
        ("医院", "科技园区", 35),
        ("科技园区", "机场", 45),
        ("商业区", "机场", 50),
    ]
    
    for from_loc, to_loc, time in locations:
        city_map.add_edge(from_loc, to_loc, time)
    
    print("\n# 可达位置:")
    for loc in city_map.get_all_nodes():
        print(f"  - {loc}")
    
    # 导航查询
    dijkstra = Dijkstra(city_map)
    
    queries = [
        ("火车站", "机场"),
        ("医院", "科技园区"),
        ("大学城", "商业区"),
    ]
    
    print("\n# 导航查询:")
    for start, end in queries:
        path, time = dijkstra.find_shortest_path(start, end)
        if path:
            print(f"\n从 {start} 到 {end}:")
            print(f"  推荐路线: {' -> '.join(path)}")
            print(f"  预计时间: {time} 分钟")


if __name__ == "__main__":
    print("= 智能路径规划器")
    print("=" * 50)
    
    # 演示各种功能
    demo_graph_pathfinding()
    demo_road_network()
    demo_maze_solving()
    create_city_navigation()
    
    print("\n" + "=" * 50)
    print("* 所有演示完成!")
    print("=" * 50)
