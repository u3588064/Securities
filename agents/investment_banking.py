"""
投资银行部门代理模块
"""

from typing import Dict, List, Any, Optional
from broker_simulation.core.sub_agent import BrokerSubAgent


class InvestmentBankingAgent(BrokerSubAgent):
    """投资银行部门代理类，专注于IPO、债券发行和并购咨询业务"""
    
    def __init__(
        self,
        name: str,
        broker_parent,
        description: str = "负责股票、债券承销和并购咨询业务",
        llm_config: Optional[Dict[str, Any]] = None,
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: Optional[int] = 10,
        **kwargs
    ):
        """
        初始化投资银行部门代理
        
        Args:
            name: 代理名称
            broker_parent: 所属券商
            description: 部门描述
            llm_config: LLM配置
            human_input_mode: 人类输入模式
            max_consecutive_auto_reply: 最大连续自动回复次数
        """
        system_message = f"""
        你是{name}，{broker_parent.name}的投资银行部门，专注于帮助企业进行IPO、再融资、债券发行和并购交易。
        {description}
        
        你的主要职责包括：
        1. 评估企业融资需求和市场条件
        2. 设计融资方案和定价策略
        3. 协调承销团队和路演活动
        4. 与监管机构沟通，确保合规
        
        你应该表现出专业、严谨的态度，注重风险控制和客户关系维护。
        """
        
        super().__init__(
            name=name,
            division="investment_banking",
            broker_parent=broker_parent,
            description=description,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            **kwargs
        )
        
        # 投行部门特有属性
        self.expertise_areas = ["IPO", "债券发行", "并购", "融资咨询"]
        self.risk_tolerance = 0.4
        self.current_deals = []  # 当前正在进行的交易
        self.deal_history = []   # 历史交易记录
        self.client_relationships = {}  # 客户关系
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理投行部门任务
        
        Args:
            task: 任务信息
            
        Returns:
            处理结果
        """
        task_type = task.get("type", "")
        
        if task_type == "ipo_underwriting":
            return self._handle_ipo_underwriting(task)
        elif task_type == "bond_issuance":
            return self._handle_bond_issuance(task)
        elif task_type == "ma_advisory":
            return self._handle_ma_advisory(task)
        elif task_type == "financing_advisory":
            return self._handle_financing_advisory(task)
        else:
            # 默认处理
            return super().process_task(task)
    
    def _handle_ipo_underwriting(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理IPO承销任务"""
        company = task.get("company", {})
        ipo_details = task.get("details", {})
        
        # 记录交易
        deal = {
            "type": "ipo",
            "company": company.get("name", "未知公司"),
            "status": "in_progress",
            "details": ipo_details,
        }
        
        self.current_deals.append(deal)
        
        # 构建回复
        response = {
            "message": f"我们已收到{company.get('name', '贵公司')}的IPO承销请求，并将开始进行评估和准备工作。",
            "next_steps": [
                "进行尽职调查",
                "评估市场条件",
                "制定发行方案",
                "准备路演材料",
                "与监管机构沟通"
            ],
            "estimated_timeline": "6-9个月",
            "deal": deal
        }
        
        # 通知研究部门
        self.send_internal_message(
            f"我们正在为{company.get('name', '一家公司')}准备IPO承销，请提供行业研究支持。",
            target_divisions=["research"]
        )
        
        # 通知风控合规部门
        self.send_internal_message(
            f"我们正在为{company.get('name', '一家公司')}准备IPO承销，请进行合规审查。",
            target_divisions=["risk_compliance"]
        )
        
        return response
    
    def _handle_bond_issuance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理债券发行任务"""
        issuer = task.get("issuer", {})
        bond_details = task.get("details", {})
        
        # 记录交易
        deal = {
            "type": "bond",
            "issuer": issuer.get("name", "未知发行人"),
            "status": "in_progress",
            "details": bond_details,
        }
        
        self.current_deals.append(deal)
        
        # 构建回复
        response = {
            "message": f"我们已收到{issuer.get('name', '贵机构')}的债券发行请求，并将开始进行评估和准备工作。",
            "next_steps": [
                "评估发行人信用状况",
                "确定债券类型和期限",
                "制定定价策略",
                "准备发行文件",
                "组建承销团队"
            ],
            "estimated_timeline": "2-3个月",
            "deal": deal
        }
        
        # 通知销售交易部门
        self.send_internal_message(
            f"我们正在为{issuer.get('name', '一家机构')}准备债券发行，请做好销售准备。",
            target_divisions=["sales_trading"]
        )
        
        # 通知风控合规部门
        self.send_internal_message(
            f"我们正在为{issuer.get('name', '一家机构')}准备债券发行，请进行风险评估。",
            target_divisions=["risk_compliance"]
        )
        
        return response
    
    def _handle_ma_advisory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理并购咨询任务"""
        client = task.get("client", {})
        target = task.get("target", {})
        deal_details = task.get("details", {})
        
        # 记录交易
        deal = {
            "type": "ma",
            "client": client.get("name", "未知客户"),
            "target": target.get("name", "未知目标"),
            "status": "in_progress",
            "details": deal_details,
        }
        
        self.current_deals.append(deal)
        
        # 构建回复
        response = {
            "message": f"我们已收到{client.get('name', '贵公司')}关于收购{target.get('name', '目标公司')}的咨询请求，并将开始进行评估和准备工作。",
            "next_steps": [
                "进行目标公司尽职调查",
                "评估交易结构和定价",
                "制定融资方案",
                "准备交易文件",
                "协调交易执行"
            ],
            "estimated_timeline": "3-6个月",
            "deal": deal
        }
        
        # 通知研究部门
        self.send_internal_message(
            f"我们正在为{client.get('name', '一家公司')}提供收购{target.get('name', '目标公司')}的咨询服务，请提供行业和目标公司研究。",
            target_divisions=["research"]
        )
        
        return response
    
    def _handle_financing_advisory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理融资咨询任务"""
        client = task.get("client", {})
        financing_details = task.get("details", {})
        
        # 记录交易
        deal = {
            "type": "financing",
            "client": client.get("name", "未知客户"),
            "status": "in_progress",
            "details": financing_details,
        }
        
        self.current_deals.append(deal)
        
        # 构建回复
        response = {
            "message": f"我们已收到{client.get('name', '贵公司')}的融资咨询请求，并将开始进行评估和方案设计。",
            "next_steps": [
                "评估融资需求和目的",
                "分析可行的融资渠道",
                "设计融资方案",
                "评估融资成本和风险",
                "制定实施计划"
            ],
            "estimated_timeline": "1-2个月",
            "deal": deal
        }
        
        # 通知资产管理部门
        self.send_internal_message(
            f"我们正在为{client.get('name', '一家公司')}提供融资咨询服务，可能需要资产管理部门的支持。",
            target_divisions=["asset_management"]
        )
        
        return response
    
    def get_viewpoint(self, issue: str) -> Dict[str, Any]:
        """
        获取投行部门对特定问题的观点
        
        Args:
            issue: 问题描述
            
        Returns:
            部门观点
        """
        # 这里应该实现基于LLM的观点生成
        # 简单实现：根据投行部门的特点生成观点
        
        viewpoint = {
            "division": "investment_banking",
            "perspective": f"从投资银行业务角度考虑，{issue}可能涉及到融资、并购或资本市场活动。我们应该评估其对我们现有客户和潜在交易的影响，同时考虑监管合规要求。",
            "risk_assessment": "中等风险",
            "opportunity_assessment": "可能存在业务机会",
            "recommendation": "建议进一步分析市场影响，并与客户沟通潜在需求。"
        }
        
        return viewpoint
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        获取部门状态报告
        
        Returns:
            状态报告
        """
        active_deals_count = len(self.current_deals)
        completed_deals_count = len([d for d in self.deal_history if d.get("status") == "completed"])
        
        return {
            "name": self.name,
            "division": self.division,
            "active_deals": active_deals_count,
            "completed_deals": completed_deals_count,
            "expertise_areas": self.expertise_areas,
            "risk_tolerance": self.risk_tolerance,
            "pending_tasks": len(self.tasks),
        }
    
    def complete_deal(self, deal_index: int, status: str = "completed", results: Dict[str, Any] = None):
        """
        完成交易
        
        Args:
            deal_index: 交易索引
            status: 交易状态
            results: 交易结果
        """
        if 0 <= deal_index < len(self.current_deals):
            deal = self.current_deals.pop(deal_index)
            deal["status"] = status
            deal["completion_date"] = self.get_current_time()
            
            if results:
                deal["results"] = results
            
            self.deal_history.append(deal)
            
            # 通知高管团队
            self.send_internal_message(
                f"投行部门已完成{deal.get('type', '未知类型')}交易：{deal.get('company', deal.get('issuer', deal.get('client', '未知客户')))}，状态为{status}。",
                target_divisions=["executive"]
            )
            
            return True
        
        return False 