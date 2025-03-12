"""
券商复合智能体模块
"""

import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
import autogen
import networkx as nx

from broker_simulation.core.sub_agent import BrokerSubAgent
from broker_simulation.core.internal_network import InternalNetwork


class BrokerAgent:
    """券商复合智能体，由多个子智能体组成"""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        llm_config: Optional[Dict[str, Any]] = None,
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: Optional[int] = 10,
        is_termination_msg: Optional[Callable[[Dict[str, Any]], bool]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化券商复合智能体
        
        Args:
            name: 券商名称
            description: 券商描述
            llm_config: LLM配置
            human_input_mode: 人类输入模式
            max_consecutive_auto_reply: 最大连续自动回复次数
            is_termination_msg: 终止消息判断函数
            config: 券商配置
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.agent_type = "financial_institutions"
        
        # 配置
        self.config = config or {}
        self.llm_config = llm_config
        self.human_input_mode = human_input_mode
        self.max_consecutive_auto_reply = max_consecutive_auto_reply
        self.is_termination_msg = is_termination_msg
        
        # 创建AutoGen代理作为对外接口
        system_message = f"""
        你是{name}，一家综合性投资银行/券商。
        {description}
        
        你的内部有多个专业部门，包括投资银行部门、销售交易部门、研究部门等。
        你应该根据请求的性质，将其分发给合适的内部部门处理，然后整合各部门的意见和建议，形成最终回复。
        """
        
        self.agent = autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            is_termination_msg=is_termination_msg,
        )
        
        # 内部通信网络
        self.internal_network = InternalNetwork()
        
        # 部门子智能体
        self.divisions = {}
        
        # 初始化各部门
        self._initialize_divisions()
        
        # 构建内部通信网络
        self._build_internal_network()
        
        # 状态和属性
        self.balance = self.config.get("initial_balance", 1000000000.0)  # 资金余额
        self.assets = {}  # 资产
        self.liabilities = {}  # 负债
        self.connections = []  # 与其他主体的连接
        self.transaction_history = []  # 交易历史
        self.regulatory_status = "compliant"  # 监管状态
        
        # 日志
        self.logger = logging.getLogger(f"BrokerAgent.{name}")
        self.logger.setLevel(logging.INFO)
    
    def _initialize_divisions(self):
        """初始化各部门子智能体"""
        # 投资银行部门
        self.divisions["investment_banking"] = BrokerSubAgent(
            name=f"{self.name} - 投行部",
            division="investment_banking",
            broker_parent=self,
            description="负责股票、债券承销和并购咨询业务",
            system_message=f"""
            你是{self.name}的投资银行部门，专注于帮助企业进行IPO、再融资、债券发行和并购交易。
            你的主要职责包括：
            1. 评估企业融资需求和市场条件
            2. 设计融资方案和定价策略
            3. 协调承销团队和路演活动
            4. 与监管机构沟通，确保合规
            
            你应该表现出专业、严谨的态度，注重风险控制和客户关系维护。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["investment_banking"].expertise_areas = ["IPO", "债券发行", "并购", "融资咨询"]
        self.divisions["investment_banking"].risk_tolerance = 0.4
        
        # 销售交易部门
        self.divisions["sales_trading"] = BrokerSubAgent(
            name=f"{self.name} - 销售交易部",
            division="sales_trading",
            broker_parent=self,
            description="负责证券交易、做市和客户订单执行",
            system_message=f"""
            你是{self.name}的销售交易部门，专注于证券交易、做市和客户订单执行。
            你的主要职责包括：
            1. 执行客户交易订单
            2. 提供市场流动性和做市服务
            3. 管理交易头寸和风险敞口
            4. 向客户提供交易策略建议
            
            你应该表现出敏捷、果断的态度，注重执行效率和市场时机把握。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["sales_trading"].expertise_areas = ["股票交易", "债券交易", "衍生品", "做市"]
        self.divisions["sales_trading"].risk_tolerance = 0.7
        
        # 研究部门
        self.divisions["research"] = BrokerSubAgent(
            name=f"{self.name} - 研究部",
            division="research",
            broker_parent=self,
            description="负责市场研究、行业分析和投资建议",
            system_message=f"""
            你是{self.name}的研究部门，专注于市场研究、行业分析和投资建议。
            你的主要职责包括：
            1. 分析宏观经济趋势和市场动态
            2. 研究行业发展和公司基本面
            3. 发布研究报告和投资建议
            4. 为内部交易和投资决策提供支持
            
            你应该表现出分析性、客观的态度，注重数据分析和逻辑推理。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["research"].expertise_areas = ["宏观分析", "行业研究", "公司研究", "投资策略"]
        self.divisions["research"].risk_tolerance = 0.3
        
        # 财富管理部门
        self.divisions["wealth_management"] = BrokerSubAgent(
            name=f"{self.name} - 财富管理部",
            division="wealth_management",
            broker_parent=self,
            description="负责高净值客户和零售客户的资产管理",
            system_message=f"""
            你是{self.name}的财富管理部门，专注于高净值客户和零售客户的资产管理。
            你的主要职责包括：
            1. 为客户制定个性化投资方案
            2. 管理客户投资组合
            3. 提供财务规划和税务咨询
            4. 维护客户关系和服务体验
            
            你应该表现出亲和、专业的态度，注重客户需求和长期关系维护。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["wealth_management"].expertise_areas = ["资产配置", "投资组合", "财务规划", "客户关系"]
        self.divisions["wealth_management"].risk_tolerance = 0.4
        
        # 资产管理部门
        self.divisions["asset_management"] = BrokerSubAgent(
            name=f"{self.name} - 资管部",
            division="asset_management",
            broker_parent=self,
            description="负责基金产品设计和资产管理业务",
            system_message=f"""
            你是{self.name}的资产管理部门，专注于基金产品设计和资产管理业务。
            你的主要职责包括：
            1. 设计和管理各类投资基金
            2. 制定投资策略和资产配置方案
            3. 执行投资决策和组合调整
            4. 监控投资绩效和风险指标
            
            你应该表现出专业、稳健的态度，注重长期业绩和风险管理。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["asset_management"].expertise_areas = ["基金管理", "资产配置", "投资策略", "绩效分析"]
        self.divisions["asset_management"].risk_tolerance = 0.5
        
        # 风控合规部门
        self.divisions["risk_compliance"] = BrokerSubAgent(
            name=f"{self.name} - 风控合规部",
            division="risk_compliance",
            broker_parent=self,
            description="负责风险管理和合规监督",
            system_message=f"""
            你是{self.name}的风控合规部门，专注于风险管理和合规监督。
            你的主要职责包括：
            1. 识别和评估各类业务风险
            2. 制定风险控制政策和流程
            3. 监督合规要求的执行情况
            4. 处理监管机构的检查和要求
            
            你应该表现出谨慎、严格的态度，始终将风险控制和合规要求放在首位。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["risk_compliance"].expertise_areas = ["风险管理", "合规监督", "内控审计", "监管关系"]
        self.divisions["risk_compliance"].risk_tolerance = 0.1
        
        # 高管团队
        self.divisions["executive"] = BrokerSubAgent(
            name=f"{self.name} - 高管团队",
            division="executive",
            broker_parent=self,
            description="负责战略决策和部门协调",
            system_message=f"""
            你是{self.name}的高管团队，负责战略决策和部门协调。
            你的主要职责包括：
            1. 制定公司战略和业务规划
            2. 协调各部门之间的合作
            3. 解决部门间的冲突和分歧
            4. 对外代表公司与重要客户和监管机构沟通
            
            你应该表现出全局视野和领导力，平衡业务发展和风险控制，协调各部门的专业意见。
            """,
            llm_config=self.llm_config,
            human_input_mode=self.human_input_mode,
            max_consecutive_auto_reply=self.max_consecutive_auto_reply,
        )
        self.divisions["executive"].expertise_areas = ["战略规划", "业务协调", "决策管理", "外部关系"]
        self.divisions["executive"].risk_tolerance = 0.5
    
    def _build_internal_network(self):
        """构建内部通信网络"""
        # 添加所有部门节点
        for div_name, div_agent in self.divisions.items():
            self.internal_network.add_division(div_name, {
                "name": div_agent.name,
                "risk_tolerance": div_agent.risk_tolerance,
                "expertise_areas": div_agent.expertise_areas,
            })
        
        # 高管团队与所有部门建立连接
        for div_name in self.divisions:
            if div_name != "executive":
                self.internal_network.add_connection(
                    "executive", div_name, bidirectional=True, 
                    frequency=1.0, priority=1.0
                )
        
        # 风控合规部门与所有业务部门建立连接
        for div_name in self.divisions:
            if div_name not in ["executive", "risk_compliance"]:
                self.internal_network.add_connection(
                    "risk_compliance", div_name, bidirectional=True, 
                    frequency=0.8, priority=0.9
                )
        
        # 研究部门与销售交易、资产管理和财富管理部门建立连接
        for div_name in ["sales_trading", "asset_management", "wealth_management"]:
            self.internal_network.add_connection(
                "research", div_name, bidirectional=True, 
                frequency=0.9, priority=0.8
            )
        
        # 投行部门与销售交易部门建立连接
        self.internal_network.add_connection(
            "investment_banking", "sales_trading", bidirectional=True, 
            frequency=0.7, priority=0.7
        )
        
        # 财富管理与资产管理部门建立连接
        self.internal_network.add_connection(
            "wealth_management", "asset_management", bidirectional=True, 
            frequency=0.8, priority=0.7
        )
    
    def send_message(self, recipient, message: str, sender=None):
        """向其他智能体发送消息"""
        if sender is None:
            sender = self.agent
        return self.agent.send(message, recipient.agent, sender=sender)
    
    def process_message(self, message: str, sender=None, metadata: Dict[str, Any] = None):
        """
        处理收到的消息，根据内容分发给相应部门
        
        Args:
            message: 消息内容
            sender: 消息发送者
            metadata: 消息元数据
            
        Returns:
            处理结果
        """
        if metadata is None:
            metadata = {}
        
        self.logger.info(f"收到消息: {message[:100]}...")
        
        # 分析消息内容，确定应该由哪个部门处理
        target_departments = self._determine_target_departments(message)
        
        if not target_departments:
            # 如果无法确定目标部门，默认由高管团队处理
            target_departments = ["executive"]
        
        self.logger.info(f"目标部门: {target_departments}")
        
        # 收集各部门的回复
        department_responses = {}
        for dept in target_departments:
            if dept in self.divisions:
                # 创建任务
                task = {
                    "id": str(uuid.uuid4()),
                    "type": "message_processing",
                    "content": message,
                    "sender": sender.name if sender else "unknown",
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat(),
                }
                
                # 添加任务到部门
                self.divisions[dept].add_task(task)
                
                # 处理任务
                results = self.divisions[dept].process_tasks()
                
                if results:
                    department_responses[dept] = results[0]  # 取第一个结果
        
        # 如果有多个部门回复，由高管团队整合
        if len(department_responses) > 1:
            final_response = self._integrate_responses(department_responses, message)
        elif department_responses:
            # 只有一个部门回复，直接使用
            dept, response = next(iter(department_responses.items()))
            final_response = response.get("message", f"{self.name}已收到您的消息，正在处理中。")
        else:
            # 没有部门回复
            final_response = f"{self.name}已收到您的消息，但目前无法提供具体回复。请稍后再试或联系我们的客服。"
        
        return final_response
    
    def _determine_target_departments(self, message: str) -> List[str]:
        """
        根据消息内容确定目标部门
        
        Args:
            message: 消息内容
            
        Returns:
            目标部门列表
        """
        # 这里应该实现基于LLM的消息分类逻辑
        # 简单实现：根据关键词匹配
        
        keywords = {
            "investment_banking": ["IPO", "上市", "融资", "承销", "并购", "重组", "发行"],
            "sales_trading": ["交易", "股票", "债券", "买入", "卖出", "市场", "报价", "做市"],
            "research": ["研究", "分析", "报告", "评级", "行业", "趋势", "预测"],
            "wealth_management": ["理财", "财富", "资产配置", "投资组合", "个人", "家族"],
            "asset_management": ["基金", "资管", "产品", "投资策略", "组合管理"],
            "risk_compliance": ["风险", "合规", "监管", "审计", "内控", "法规"],
            "executive": ["战略", "合作", "全局", "公司", "发展", "规划"],
        }
        
        # 计算每个部门的匹配分数
        scores = {}
        for dept, words in keywords.items():
            score = sum(1 for word in words if word in message)
            if score > 0:
                scores[dept] = score
        
        # 选择得分最高的部门，如果有多个相同得分，则都选择
        if not scores:
            return ["executive"]  # 默认高管团队
        
        max_score = max(scores.values())
        return [dept for dept, score in scores.items() if score == max_score]
    
    def _integrate_responses(self, department_responses: Dict[str, Any], original_message: str) -> str:
        """
        整合多个部门的回复
        
        Args:
            department_responses: 各部门的回复
            original_message: 原始消息
            
        Returns:
            整合后的回复
        """
        # 如果有高管团队的回复，优先使用
        if "executive" in department_responses:
            return department_responses["executive"].get("message", "")
        
        # 否则，整合所有部门的回复
        response_parts = []
        for dept, response in department_responses.items():
            message = response.get("message", "")
            if message:
                response_parts.append(f"{self.divisions[dept].name}的意见：{message}")
        
        if response_parts:
            integrated_response = f"{self.name}的综合回复：\n\n" + "\n\n".join(response_parts)
        else:
            integrated_response = f"{self.name}已收到您的消息，正在进一步分析中。"
        
        return integrated_response
    
    def internal_communication_round(self):
        """执行内部通信回合，各部门之间交换信息"""
        # 处理每个部门的待处理任务
        for div_name, div_agent in self.divisions.items():
            div_agent.process_tasks()
        
        # 处理内部消息
        for div_name, div_agent in self.divisions.items():
            if div_agent.internal_messages:
                for msg in div_agent.internal_messages:
                    # 记录通信
                    if "sender" in msg:
                        self.internal_network.record_communication(
                            msg["sender"], div_name, msg
                        )
                
                # 清空已处理的消息
                div_agent.internal_messages = []
    
    def resolve_conflict(self, issue: str, conflicting_divisions: List[str]):
        """
        解决部门间冲突
        
        Args:
            issue: 冲突问题
            conflicting_divisions: 冲突部门列表
            
        Returns:
            解决方案
        """
        if "executive" not in self.divisions:
            return None
        
        executive = self.divisions["executive"]
        
        # 收集各部门的观点
        viewpoints = {}
        for div_name in conflicting_divisions:
            if div_name in self.divisions:
                div_agent = self.divisions[div_name]
                viewpoint = div_agent.get_viewpoint(issue)
                viewpoints[div_name] = viewpoint
        
        # 创建冲突解决任务
        task = {
            "id": str(uuid.uuid4()),
            "type": "conflict_resolution",
            "issue": issue,
            "viewpoints": viewpoints,
            "timestamp": datetime.now().isoformat(),
        }
        
        # 添加任务到高管团队
        executive.add_task(task)
        
        # 处理任务
        results = executive.process_tasks()
        
        if results:
            decision = results[0].get("message", "")
            
            # 通知相关部门
            for div_name in conflicting_divisions:
                if div_name in self.divisions and div_name != "executive":
                    executive.send_internal_message(
                        f"关于{issue}的决策: {decision}", 
                        target_divisions=[div_name]
                    )
            
            return decision
        
        return None
    
    def add_connection(self, other_agent):
        """添加与其他主体的连接"""
        if other_agent not in self.connections:
            self.connections.append(other_agent)
            # 如果对方还没有与自己建立连接，则建立双向连接
            if self not in other_agent.connections:
                other_agent.add_connection(self)
    
    def transfer_funds(self, recipient, amount: float, description: str = ""):
        """转账给其他主体"""
        if amount <= 0:
            return False, "转账金额必须为正数"
        
        if self.balance < amount:
            return False, "余额不足"
        
        # 执行转账
        self.balance -= amount
        recipient.balance += amount
        
        # 记录交易
        transaction = {
            "from": self.id,
            "to": recipient.id,
            "amount": amount,
            "description": description,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.transaction_history.append(transaction)
        recipient.transaction_history.append(transaction)
        
        return True, transaction
    
    def get_info(self):
        """获取券商信息"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type,
            "description": self.description,
            "balance": self.balance,
            "assets": self.assets,
            "liabilities": self.liabilities,
            "connections": [conn.name for conn in self.connections],
            "regulatory_status": self.regulatory_status,
            "divisions": {div_name: div_agent.get_status_report() for div_name, div_agent in self.divisions.items()},
        }
    
    def visualize_internal_network(self, output_file: str = "broker_internal_network.html"):
        """可视化内部通信网络"""
        return self.internal_network.visualize(output_file)
    
    def __str__(self):
        return f"{self.name} (券商)"
    
    def __repr__(self):
        return self.__str__() 