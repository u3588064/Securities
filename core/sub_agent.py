"""
券商子智能体基类模块
"""

import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import autogen


class BrokerSubAgent:
    """券商子智能体基类，代表券商内部的一个部门或团队"""
    
    def __init__(
        self,
        name: str,
        division: str,
        broker_parent: Any,
        description: str = "",
        system_message: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: Optional[int] = 10,
        is_termination_msg: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        """
        初始化券商子智能体
        
        Args:
            name: 子智能体名称
            division: 部门类型
            broker_parent: 所属券商
            description: 子智能体描述
            system_message: 系统消息
            llm_config: LLM配置
            human_input_mode: 人类输入模式
            max_consecutive_auto_reply: 最大连续自动回复次数
            is_termination_msg: 终止消息判断函数
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.division = division
        self.broker_parent = broker_parent
        self.description = description
        
        # 创建AutoGen代理
        if system_message is None:
            system_message = f"""
            你是{name}，{broker_parent.name}的{division}部门。
            {description}
            
            你应该根据你的专业领域和职责行事，考虑实际券商业务中的规则和限制。
            在与其他部门协作时，要清晰表达你的专业观点，同时尊重其他部门的专业判断。
            """
        
        self.agent = autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            is_termination_msg=is_termination_msg,
        )
        
        # 内部状态
        self.internal_messages = []  # 内部消息队列
        self.pending_tasks = []  # 待处理任务
        self.completed_tasks = []  # 已完成任务
        self.knowledge_base = {}  # 知识库
        self.decision_history = []  # 决策历史
        
        # 部门特定属性
        self.risk_tolerance = 0.5  # 风险容忍度 (0-1)
        self.expertise_areas = []  # 专业领域
        self.performance_metrics = {  # 绩效指标
            "revenue": 0.0,
            "cost": 0.0,
            "client_satisfaction": 0.0,
            "compliance_score": 1.0,
        }
    
    def send_message(self, recipient, message: str, sender=None):
        """向其他智能体发送消息"""
        if sender is None:
            sender = self.agent
        return self.agent.send(message, recipient.agent, sender=sender)
    
    def receive_internal_message(self, message: Dict[str, Any], sender):
        """接收来自其他部门的内部消息"""
        self.internal_messages.append({
            "sender": sender.division,
            "content": message.get("content", ""),
            "metadata": message.get("metadata", {}),
            "timestamp": datetime.now().isoformat(),
        })
        
        # 处理内部消息
        return self._process_internal_message(self.internal_messages[-1])
    
    def _process_internal_message(self, message: Dict[str, Any]):
        """处理内部消息的默认实现，子类可以重写"""
        # 默认实现只是记录消息
        self.decision_history.append({
            "type": "message_received",
            "message": message,
            "timestamp": datetime.now().isoformat(),
        })
        return None
    
    def send_internal_message(self, content: str, target_divisions=None, metadata=None):
        """向其他部门发送内部消息"""
        if metadata is None:
            metadata = {}
            
        message = {
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        }
        
        if target_divisions:
            for div_name in target_divisions:
                if div_name in self.broker_parent.divisions:
                    self.broker_parent.divisions[div_name].internal_messages.append({
                        "sender": self.division,
                        "content": content,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat(),
                    })
        else:
            # 如果没有指定目标部门，则发送给所有连接的部门
            for div_name, connection in self.broker_parent.internal_network.get_connections(self.division):
                if div_name in self.broker_parent.divisions:
                    self.broker_parent.divisions[div_name].internal_messages.append({
                        "sender": self.division,
                        "content": content,
                        "metadata": metadata,
                        "timestamp": datetime.now().isoformat(),
                    })
        
        return message
    
    def make_decision(self, issue: str, options: List[str], context: Dict[str, Any] = None):
        """
        根据部门专业做出决策
        
        Args:
            issue: 决策问题
            options: 可选选项
            context: 决策上下文
            
        Returns:
            决策结果
        """
        # 这里应该实现基于LLM的决策逻辑
        # 默认实现是随机选择一个选项
        import random
        decision = random.choice(options)
        
        # 记录决策
        self.decision_history.append({
            "type": "decision",
            "issue": issue,
            "options": options,
            "decision": decision,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        })
        
        return decision
    
    def get_viewpoint(self, issue: str):
        """获取部门对特定问题的观点"""
        # 这里应该实现基于LLM的观点生成逻辑
        # 默认实现是返回一个通用观点
        return f"{self.name}认为这个问题需要进一步分析。"
    
    def update_knowledge(self, key: str, value: Any):
        """更新知识库"""
        self.knowledge_base[key] = value
    
    def get_knowledge(self, key: str, default=None):
        """获取知识库中的信息"""
        return self.knowledge_base.get(key, default)
    
    def add_task(self, task: Dict[str, Any]):
        """添加待处理任务"""
        self.pending_tasks.append(task)
    
    def process_tasks(self):
        """处理待处理任务"""
        if not self.pending_tasks:
            return []
        
        results = []
        remaining_tasks = []
        
        for task in self.pending_tasks:
            # 检查是否可以处理该任务
            if self._can_process_task(task):
                result = self._process_task(task)
                results.append(result)
                self.completed_tasks.append({
                    "task": task,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
            else:
                remaining_tasks.append(task)
        
        self.pending_tasks = remaining_tasks
        return results
    
    def _can_process_task(self, task: Dict[str, Any]):
        """检查是否可以处理任务，子类可以重写"""
        # 默认实现总是返回True
        return True
    
    def _process_task(self, task: Dict[str, Any]):
        """处理任务的默认实现，子类应该重写"""
        # 默认实现只是返回一个通用结果
        return {
            "status": "completed",
            "message": f"{self.name}已处理任务",
            "task_id": task.get("id", "unknown"),
        }
    
    def update_performance(self, metrics: Dict[str, float]):
        """更新绩效指标"""
        for key, value in metrics.items():
            if key in self.performance_metrics:
                self.performance_metrics[key] += value
    
    def get_status_report(self):
        """获取状态报告"""
        return {
            "id": self.id,
            "name": self.name,
            "division": self.division,
            "pending_tasks": len(self.pending_tasks),
            "completed_tasks": len(self.completed_tasks),
            "internal_messages": len(self.internal_messages),
            "performance_metrics": self.performance_metrics,
        }
    
    def __str__(self):
        return f"{self.name} ({self.division})"
    
    def __repr__(self):
        return self.__str__() 