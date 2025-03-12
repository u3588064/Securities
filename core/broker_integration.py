"""
券商与金融市场模拟器的集成模块
"""

from typing import Dict, List, Any, Optional, Callable
import logging

from broker_simulation.core.broker_agent import BrokerAgent


class BrokerIntegration:
    """券商与金融市场模拟器的集成类"""
    
    def __init__(
        self,
        broker_agent: BrokerAgent,
        market_simulation=None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化券商集成模块
        
        Args:
            broker_agent: 券商智能体
            market_simulation: 金融市场模拟器实例
            config: 集成配置
        """
        self.broker = broker_agent
        self.market_simulation = market_simulation
        self.config = config or {}
        
        # 日志
        self.logger = logging.getLogger(f"BrokerIntegration.{broker_agent.name}")
        self.logger.setLevel(logging.INFO)
        
        # 注册到市场
        if market_simulation:
            self._register_to_market()
    
    def _register_to_market(self):
        """将券商注册到金融市场模拟器"""
        if not self.market_simulation:
            self.logger.warning("未提供金融市场模拟器实例，无法注册")
            return
        
        try:
            # 注册券商智能体到市场
            self.market_simulation.register_agent(self.broker)
            self.logger.info(f"已将{self.broker.name}注册到金融市场模拟器")
            
            # 建立与市场中其他主体的连接
            self._establish_market_connections()
        except Exception as e:
            self.logger.error(f"注册到市场失败: {str(e)}")
    
    def _establish_market_connections(self):
        """建立与市场中其他主体的连接"""
        if not self.market_simulation:
            return
        
        # 获取市场中的其他主体
        market_agents = self.market_simulation.get_agents()
        
        # 根据配置建立连接
        connection_config = self.config.get("connections", {})
        
        # 默认连接所有金融机构
        for agent in market_agents:
            if agent.id != self.broker.id:
                if agent.agent_type == "financial_institutions" or agent.agent_type in connection_config.get("agent_types", []):
                    self.broker.add_connection(agent)
                    self.logger.info(f"已建立与{agent.name}的连接")
    
    def process_market_event(self, event: Dict[str, Any]):
        """
        处理来自市场的事件
        
        Args:
            event: 市场事件
        
        Returns:
            处理结果
        """
        event_type = event.get("type", "")
        
        if event_type == "market_update":
            return self._handle_market_update(event)
        elif event_type == "trading_opportunity":
            return self._handle_trading_opportunity(event)
        elif event_type == "regulatory_announcement":
            return self._handle_regulatory_announcement(event)
        elif event_type == "client_request":
            return self._handle_client_request(event)
        else:
            # 默认处理
            return self.broker.process_message(
                message=event.get("content", ""),
                sender=event.get("sender"),
                metadata=event
            )
    
    def _handle_market_update(self, event: Dict[str, Any]):
        """处理市场更新事件"""
        # 将市场更新发送给研究部门和销售交易部门
        target_departments = ["research", "sales_trading", "executive"]
        
        responses = {}
        for dept in target_departments:
            if dept in self.broker.divisions:
                task = {
                    "type": "market_update",
                    "content": event.get("content", ""),
                    "data": event.get("data", {}),
                    "timestamp": event.get("timestamp", ""),
                }
                
                self.broker.divisions[dept].add_task(task)
                results = self.broker.divisions[dept].process_tasks()
                
                if results:
                    responses[dept] = results[0]
        
        # 由销售交易部门决定是否需要采取行动
        if "sales_trading" in responses:
            action = responses["sales_trading"].get("action")
            if action:
                return self._execute_market_action(action)
        
        return {"status": "processed", "action": "none"}
    
    def _handle_trading_opportunity(self, event: Dict[str, Any]):
        """处理交易机会事件"""
        # 将交易机会发送给销售交易部门和研究部门
        opportunity = event.get("content", "")
        data = event.get("data", {})
        
        # 首先由研究部门评估
        if "research" in self.broker.divisions:
            task = {
                "type": "opportunity_analysis",
                "content": opportunity,
                "data": data,
            }
            
            self.broker.divisions["research"].add_task(task)
            results = self.broker.divisions["research"].process_tasks()
            
            if results and results[0].get("recommendation") == "reject":
                return {"status": "rejected", "reason": results[0].get("reason", "研究部门不建议参与")}
        
        # 然后由销售交易部门执行
        if "sales_trading" in self.broker.divisions:
            task = {
                "type": "execute_trade",
                "content": opportunity,
                "data": data,
                "analysis": results[0] if results else None,
            }
            
            self.broker.divisions["sales_trading"].add_task(task)
            trade_results = self.broker.divisions["sales_trading"].process_tasks()
            
            if trade_results:
                return {"status": "executed", "result": trade_results[0]}
        
        return {"status": "processed", "action": "none"}
    
    def _handle_regulatory_announcement(self, event: Dict[str, Any]):
        """处理监管公告事件"""
        # 将监管公告发送给风控合规部门和高管团队
        announcement = event.get("content", "")
        
        if "risk_compliance" in self.broker.divisions:
            task = {
                "type": "regulatory_analysis",
                "content": announcement,
                "data": event.get("data", {}),
            }
            
            self.broker.divisions["risk_compliance"].add_task(task)
            results = self.broker.divisions["risk_compliance"].process_tasks()
            
            if results:
                # 如果需要采取行动，通知高管团队
                if results[0].get("action_required", False):
                    if "executive" in self.broker.divisions:
                        exec_task = {
                            "type": "regulatory_response",
                            "content": announcement,
                            "analysis": results[0],
                        }
                        
                        self.broker.divisions["executive"].add_task(exec_task)
                        exec_results = self.broker.divisions["executive"].process_tasks()
                        
                        if exec_results:
                            return {"status": "action_taken", "action": exec_results[0].get("action")}
                
                return {"status": "analyzed", "impact": results[0].get("impact", "unknown")}
        
        return {"status": "received"}
    
    def _handle_client_request(self, event: Dict[str, Any]):
        """处理客户请求事件"""
        request = event.get("content", "")
        client = event.get("sender", {})
        
        # 根据请求类型确定处理部门
        request_type = event.get("request_type", "general")
        
        if request_type == "investment_banking":
            target_dept = "investment_banking"
        elif request_type == "trading":
            target_dept = "sales_trading"
        elif request_type == "research":
            target_dept = "research"
        elif request_type == "wealth_management":
            target_dept = "wealth_management"
        elif request_type == "asset_management":
            target_dept = "asset_management"
        else:
            # 使用券商的消息分发机制
            return self.broker.process_message(request, sender=client)
        
        # 直接发送给目标部门
        if target_dept in self.broker.divisions:
            task = {
                "type": "client_request",
                "content": request,
                "client": client.name if hasattr(client, "name") else "unknown",
                "data": event.get("data", {}),
            }
            
            self.broker.divisions[target_dept].add_task(task)
            results = self.broker.divisions[target_dept].process_tasks()
            
            if results:
                return {"status": "processed", "response": results[0].get("message", "")}
        
        return {"status": "unprocessed"}
    
    def _execute_market_action(self, action: Dict[str, Any]):
        """执行市场行动"""
        action_type = action.get("type", "")
        
        if not self.market_simulation:
            self.logger.warning(f"无法执行市场行动 {action_type}：未连接到市场模拟器")
            return {"status": "failed", "reason": "未连接到市场模拟器"}
        
        try:
            if action_type == "place_order":
                # 下单交易
                order = action.get("order", {})
                result = self.market_simulation.place_order(
                    agent_id=self.broker.id,
                    symbol=order.get("symbol"),
                    order_type=order.get("type"),
                    quantity=order.get("quantity"),
                    price=order.get("price"),
                    side=order.get("side"),
                )
                return {"status": "success", "result": result}
                
            elif action_type == "cancel_order":
                # 取消订单
                order_id = action.get("order_id")
                result = self.market_simulation.cancel_order(
                    agent_id=self.broker.id,
                    order_id=order_id,
                )
                return {"status": "success", "result": result}
                
            elif action_type == "market_making":
                # 做市行为
                symbol = action.get("symbol")
                bid = action.get("bid")
                ask = action.get("ask")
                quantity = action.get("quantity")
                
                result = self.market_simulation.market_making(
                    agent_id=self.broker.id,
                    symbol=symbol,
                    bid=bid,
                    ask=ask,
                    quantity=quantity,
                )
                return {"status": "success", "result": result}
                
            else:
                self.logger.warning(f"未知的市场行动类型: {action_type}")
                return {"status": "failed", "reason": f"未知的市场行动类型: {action_type}"}
                
        except Exception as e:
            self.logger.error(f"执行市场行动失败: {str(e)}")
            return {"status": "failed", "reason": str(e)}
    
    def run_internal_cycle(self):
        """运行券商内部通信周期"""
        self.broker.internal_communication_round()
    
    def get_broker_status(self):
        """获取券商状态"""
        return self.broker.get_info()
    
    def visualize_broker_structure(self, output_file: str = None):
        """可视化券商内部结构"""
        if output_file is None:
            output_file = f"{self.broker.name}_structure.html"
        
        return self.broker.visualize_internal_network(output_file) 