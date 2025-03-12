"""
券商多智能体模拟系统 - 可视化工具
"""

import os
import json
import networkx as nx
from pyvis.network import Network
from typing import Dict, Any, List, Optional


def visualize_broker_structure(
    broker_data: Dict[str, Any],
    output_file: str = "broker_structure.html",
    width: str = "800px",
    height: str = "600px",
    bgcolor: str = "#ffffff",
    font_color: str = "#000000",
    directed: bool = True
):
    """
    可视化券商内部结构
    
    Args:
        broker_data: 券商数据
        output_file: 输出文件路径
        width: 可视化宽度
        height: 可视化高度
        bgcolor: 背景颜色
        font_color: 字体颜色
        directed: 是否为有向图
    """
    # 创建图
    G = nx.DiGraph() if directed else nx.Graph()
    
    # 添加节点
    divisions = broker_data.get("divisions", {})
    for div_name, div_info in divisions.items():
        # 节点属性
        node_attrs = {
            "label": div_info.get("name", div_name),
            "title": f"{div_info.get('name', div_name)}\n"
                    f"任务数: {div_info.get('pending_tasks', 0)}\n"
                    f"风险容忍度: {div_info.get('risk_tolerance', 0)}",
            "group": div_name
        }
        G.add_node(div_name, **node_attrs)
    
    # 添加边
    connections = broker_data.get("internal_network", {}).get("connections", [])
    for conn in connections:
        source = conn.get("source")
        target = conn.get("target")
        if source and target:
            # 边属性
            edge_attrs = {
                "title": f"频率: {conn.get('frequency', 0)}\n"
                        f"优先级: {conn.get('priority', 0)}",
                "value": conn.get("frequency", 1) * 5,  # 边的粗细
                "arrows": "to" if directed else ""
            }
            G.add_edge(source, target, **edge_attrs)
    
    # 创建可视化网络
    net = Network(height=height, width=width, directed=directed, bgcolor=bgcolor, font_color=font_color)
    
    # 设置物理布局
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250, spring_strength=0.001, damping=0.09)
    
    # 从NetworkX图导入
    net.from_nx(G)
    
    # 设置节点颜色和形状
    for node in net.nodes:
        node_id = node["id"]
        if node_id == "executive":
            node["color"] = "#FF5733"  # 红色
            node["shape"] = "diamond"
        elif node_id == "risk_compliance":
            node["color"] = "#33FF57"  # 绿色
            node["shape"] = "triangle"
        elif node_id == "investment_banking":
            node["color"] = "#3357FF"  # 蓝色
            node["shape"] = "square"
        elif node_id == "sales_trading":
            node["color"] = "#FF33A8"  # 粉色
            node["shape"] = "square"
        elif node_id == "research":
            node["color"] = "#33FFF6"  # 青色
            node["shape"] = "dot"
        elif node_id == "wealth_management":
            node["color"] = "#F6FF33"  # 黄色
            node["shape"] = "dot"
        elif node_id == "asset_management":
            node["color"] = "#A833FF"  # 紫色
            node["shape"] = "dot"
        else:
            node["color"] = "#AAAAAA"  # 灰色
            node["shape"] = "dot"
    
    # 保存为HTML文件
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    net.save_graph(output_file)
    
    return output_file


def visualize_communication_history(
    communication_data: List[Dict[str, Any]],
    output_file: str = "communication_history.html",
    width: str = "800px",
    height: str = "600px",
    bgcolor: str = "#ffffff",
    font_color: str = "#000000"
):
    """
    可视化部门间通信历史
    
    Args:
        communication_data: 通信历史数据
        output_file: 输出文件路径
        width: 可视化宽度
        height: 可视化高度
        bgcolor: 背景颜色
        font_color: 字体颜色
    """
    # 创建图
    G = nx.DiGraph()
    
    # 统计部门间通信频率
    comm_freq = {}
    for comm in communication_data:
        source = comm.get("source")
        target = comm.get("target")
        if source and target:
            key = (source, target)
            comm_freq[key] = comm_freq.get(key, 0) + 1
    
    # 添加节点和边
    for (source, target), freq in comm_freq.items():
        if source not in G.nodes:
            G.add_node(source, label=source, title=f"部门: {source}")
        
        if target not in G.nodes:
            G.add_node(target, label=target, title=f"部门: {target}")
        
        G.add_edge(source, target, title=f"通信次数: {freq}", value=freq, width=freq)
    
    # 创建可视化网络
    net = Network(height=height, width=width, directed=True, bgcolor=bgcolor, font_color=font_color)
    
    # 设置物理布局
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250, spring_strength=0.001, damping=0.09)
    
    # 从NetworkX图导入
    net.from_nx(G)
    
    # 设置节点颜色和形状
    for node in net.nodes:
        node_id = node["id"]
        if node_id == "executive":
            node["color"] = "#FF5733"  # 红色
            node["shape"] = "diamond"
        elif node_id == "risk_compliance":
            node["color"] = "#33FF57"  # 绿色
            node["shape"] = "triangle"
        elif node_id == "investment_banking":
            node["color"] = "#3357FF"  # 蓝色
            node["shape"] = "square"
        elif node_id == "sales_trading":
            node["color"] = "#FF33A8"  # 粉色
            node["shape"] = "square"
        elif node_id == "research":
            node["color"] = "#33FFF6"  # 青色
            node["shape"] = "dot"
        elif node_id == "wealth_management":
            node["color"] = "#F6FF33"  # 黄色
            node["shape"] = "dot"
        elif node_id == "asset_management":
            node["color"] = "#A833FF"  # 紫色
            node["shape"] = "dot"
        else:
            node["color"] = "#AAAAAA"  # 灰色
            node["shape"] = "dot"
    
    # 保存为HTML文件
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    net.save_graph(output_file)
    
    return output_file


def visualize_broker_performance(
    performance_data: List[Dict[str, Any]],
    output_file: str = "broker_performance.html",
    metrics: Optional[List[str]] = None
):
    """
    可视化券商业绩
    
    Args:
        performance_data: 业绩数据
        output_file: 输出文件路径
        metrics: 要可视化的指标列表
    """
    if not metrics:
        metrics = ["balance", "revenue", "profit", "client_satisfaction"]
    
    # 创建HTML内容
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>券商业绩可视化</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .chart-container {
                width: 80%;
                margin: 20px auto;
            }
            h1 {
                text-align: center;
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>券商业绩可视化</h1>
        <div class="chart-container">
            <canvas id="performanceChart"></canvas>
        </div>
        
        <script>
            // 性能数据
            const performanceData = %s;
            
            // 要可视化的指标
            const metrics = %s;
            
            // 准备数据
            const labels = performanceData.map(d => d.timestamp || d.cycle || '');
            const datasets = metrics.map(metric => {
                const color = getRandomColor();
                return {
                    label: metric,
                    data: performanceData.map(d => d[metric] || 0),
                    borderColor: color,
                    backgroundColor: color + '33',
                    tension: 0.1
                };
            });
            
            // 创建图表
            const ctx = document.getElementById('performanceChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: '券商业绩趋势'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: '时间/周期'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: '指标值'
                            }
                        }
                    }
                }
            });
            
            // 生成随机颜色
            function getRandomColor() {
                const letters = '0123456789ABCDEF';
                let color = '#';
                for (let i = 0; i < 6; i++) {
                    color += letters[Math.floor(Math.random() * 16)];
                }
                return color;
            }
        </script>
    </body>
    </html>
    """ % (json.dumps(performance_data), json.dumps(metrics))
    
    # 保存HTML文件
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file 