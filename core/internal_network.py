"""
券商内部通信网络模块
"""

import networkx as nx
from typing import Dict, List, Tuple, Any, Optional


class InternalNetwork:
    """券商内部通信网络，管理部门之间的通信关系"""
    
    def __init__(self):
        """初始化内部通信网络"""
        # 使用有向图表示部门间的通信关系
        self.network = nx.DiGraph()
        
        # 通信频率和优先级
        self.communication_frequency = {}  # (source, target) -> frequency
        self.communication_priority = {}  # (source, target) -> priority
        
        # 通信历史
        self.communication_history = []
    
    def add_division(self, division_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        添加部门节点
        
        Args:
            division_name: 部门名称
            attributes: 部门属性
        """
        if attributes is None:
            attributes = {}
        
        self.network.add_node(division_name, **attributes)
    
    def add_connection(
        self,
        source: str,
        target: str,
        bidirectional: bool = True,
        frequency: float = 1.0,
        priority: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        添加部门间的连接
        
        Args:
            source: 源部门
            target: 目标部门
            bidirectional: 是否双向连接
            frequency: 通信频率 (0-1)
            priority: 通信优先级 (0-1)
            attributes: 连接属性
        """
        if attributes is None:
            attributes = {}
        
        # 添加从源到目标的连接
        self.network.add_edge(source, target, **attributes)
        self.communication_frequency[(source, target)] = frequency
        self.communication_priority[(source, target)] = priority
        
        # 如果是双向连接，添加从目标到源的连接
        if bidirectional:
            self.network.add_edge(target, source, **attributes)
            self.communication_frequency[(target, source)] = frequency
            self.communication_priority[(target, source)] = priority
    
    def remove_connection(self, source: str, target: str, bidirectional: bool = True):
        """
        移除部门间的连接
        
        Args:
            source: 源部门
            target: 目标部门
            bidirectional: 是否双向移除
        """
        if self.network.has_edge(source, target):
            self.network.remove_edge(source, target)
            if (source, target) in self.communication_frequency:
                del self.communication_frequency[(source, target)]
            if (source, target) in self.communication_priority:
                del self.communication_priority[(source, target)]
        
        if bidirectional and self.network.has_edge(target, source):
            self.network.remove_edge(target, source)
            if (target, source) in self.communication_frequency:
                del self.communication_frequency[(target, source)]
            if (target, source) in self.communication_priority:
                del self.communication_priority[(target, source)]
    
    def get_connections(self, division: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        获取部门的所有连接
        
        Args:
            division: 部门名称
            
        Returns:
            连接列表，每个元素为 (目标部门, 连接属性)
        """
        if not self.network.has_node(division):
            return []
        
        connections = []
        for target in self.network.successors(division):
            edge_data = self.network.get_edge_data(division, target)
            connections.append((target, edge_data or {}))
        
        return connections
    
    def get_all_divisions(self) -> List[str]:
        """获取所有部门"""
        return list(self.network.nodes())
    
    def get_communication_path(self, source: str, target: str) -> List[str]:
        """
        获取两个部门之间的通信路径
        
        Args:
            source: 源部门
            target: 目标部门
            
        Returns:
            部门路径列表
        """
        if not (self.network.has_node(source) and self.network.has_node(target)):
            return []
        
        try:
            path = nx.shortest_path(self.network, source=source, target=target)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def record_communication(self, source: str, target: str, message: Dict[str, Any]):
        """
        记录通信历史
        
        Args:
            source: 源部门
            target: 目标部门
            message: 消息内容
        """
        self.communication_history.append({
            "source": source,
            "target": target,
            "message": message,
            "timestamp": message.get("timestamp", ""),
        })
        
        # 更新通信频率
        if (source, target) in self.communication_frequency:
            # 简单的增加通信频率的逻辑，实际应用中可能需要更复杂的算法
            self.communication_frequency[(source, target)] = min(
                1.0, self.communication_frequency[(source, target)] + 0.01
            )
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """
        获取通信统计信息
        
        Returns:
            通信统计信息
        """
        if not self.communication_history:
            return {
                "total_communications": 0,
                "division_stats": {},
                "pair_stats": {},
            }
        
        # 计算各部门的通信统计
        division_stats = {}
        for node in self.network.nodes():
            outgoing = sum(1 for comm in self.communication_history if comm["source"] == node)
            incoming = sum(1 for comm in self.communication_history if comm["target"] == node)
            division_stats[node] = {
                "outgoing": outgoing,
                "incoming": incoming,
                "total": outgoing + incoming,
            }
        
        # 计算部门对的通信统计
        pair_stats = {}
        for source, target in self.communication_frequency.keys():
            count = sum(1 for comm in self.communication_history 
                       if comm["source"] == source and comm["target"] == target)
            pair_stats[(source, target)] = {
                "count": count,
                "frequency": self.communication_frequency.get((source, target), 0),
                "priority": self.communication_priority.get((source, target), 0),
            }
        
        return {
            "total_communications": len(self.communication_history),
            "division_stats": division_stats,
            "pair_stats": pair_stats,
        }
    
    def get_central_divisions(self, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        获取最中心的部门
        
        Args:
            top_n: 返回前N个中心部门
            
        Returns:
            中心部门列表，每个元素为 (部门名称, 中心度)
        """
        if not self.network.nodes():
            return []
        
        # 计算中心度
        centrality = nx.betweenness_centrality(self.network)
        
        # 按中心度排序
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_centrality[:top_n]
    
    def visualize(self, output_file: str = "internal_network.html"):
        """
        可视化内部通信网络
        
        Args:
            output_file: 输出文件路径
        """
        try:
            from pyvis.network import Network
            
            # 创建可视化网络
            net = Network(height="800px", width="100%", directed=True)
            
            # 添加节点
            for node in self.network.nodes():
                net.add_node(node, label=node, title=node)
            
            # 添加边
            for source, target in self.network.edges():
                frequency = self.communication_frequency.get((source, target), 0.5)
                priority = self.communication_priority.get((source, target), 0.5)
                
                # 根据频率和优先级设置边的宽度和颜色
                width = 1 + 5 * frequency
                value = int(10 * priority)
                
                net.add_edge(source, target, width=width, value=value)
            
            # 保存为HTML文件
            net.save_graph(output_file)
            return True
        except ImportError:
            print("无法导入pyvis，请安装：pip install pyvis")
            return False
        except Exception as e:
            print(f"可视化网络时出错：{e}")
            return False 