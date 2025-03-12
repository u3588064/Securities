"""
销售交易部门代理模块
"""

from typing import Dict, List, Any, Optional
from broker_simulation.core.sub_agent import BrokerSubAgent


class SalesTradingAgent(BrokerSubAgent):
    """销售交易部门代理类，专注于证券交易、做市和客户订单执行"""
    
    def __init__(
        self,
        name: str,
        broker_parent,
        description: str = "负责证券交易、做市和客户订单执行",
        llm_config: Optional[Dict[str, Any]] = None,
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: Optional[int] = 10,
        **kwargs
    ):
        """
        初始化销售交易部门代理
        
        Args:
            name: 代理名称
            broker_parent: 所属券商
            description: 部门描述
            llm_config: LLM配置
            human_input_mode: 人类输入模式
            max_consecutive_auto_reply: 最大连续自动回复次数
        """
        system_message = f"""
        你是{name}，{broker_parent.name}的销售交易部门，专注于证券交易、做市和客户订单执行。
        {description}
        
        你的主要职责包括：
        1. 执行客户交易订单
        2. 提供市场流动性和做市服务
        3. 管理交易头寸和风险敞口
        4. 向客户提供交易策略建议
        
        你应该表现出敏捷、果断的态度，注重执行效率和市场时机把握。
        """
        
        super().__init__(
            name=name,
            division="sales_trading",
            broker_parent=broker_parent,
            description=description,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            **kwargs
        )
        
        # 销售交易部门特有属性
        self.expertise_areas = ["股票交易", "债券交易", "衍生品", "做市"]
        self.risk_tolerance = 0.7
        self.trading_positions = {}  # 当前交易头寸
        self.order_history = []      # 订单历史
        self.market_making_securities = []  # 做市证券列表
        self.client_orders = []      # 客户订单
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理销售交易部门任务
        
        Args:
            task: 任务信息
            
        Returns:
            处理结果
        """
        task_type = task.get("type", "")
        
        if task_type == "execute_trade":
            return self._handle_execute_trade(task)
        elif task_type == "market_making":
            return self._handle_market_making(task)
        elif task_type == "client_order":
            return self._handle_client_order(task)
        elif task_type == "market_update":
            return self._handle_market_update(task)
        else:
            # 默认处理
            return super().process_task(task)
    
    def _handle_execute_trade(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理执行交易任务"""
        trade_details = task.get("details", {})
        analysis = task.get("analysis", {})
        
        # 记录订单
        order = {
            "type": trade_details.get("type", "market"),
            "symbol": trade_details.get("symbol", ""),
            "quantity": trade_details.get("quantity", 0),
            "price": trade_details.get("price"),
            "side": trade_details.get("side", "buy"),
            "status": "pending",
            "timestamp": self.get_current_time(),
        }
        
        self.client_orders.append(order)
        
        # 检查风险
        risk_check = self._check_trade_risk(order)
        if risk_check["risk_level"] == "high" and not task.get("force_execution", False):
            # 通知风控部门
            self.send_internal_message(
                f"发现高风险交易：{order['side']} {order['quantity']} {order['symbol']}，风险原因：{risk_check['reason']}",
                target_divisions=["risk_compliance"]
            )
            
            return {
                "message": f"交易风险评估结果为高风险，原因：{risk_check['reason']}。已暂停执行并通知风控部门。",
                "status": "pending_risk_approval",
                "order": order,
                "risk_assessment": risk_check
            }
        
        # 执行交易
        execution_result = {
            "executed_price": order.get("price"),  # 在实际系统中，这应该是从市场获取的实际执行价格
            "executed_quantity": order.get("quantity"),
            "execution_time": self.get_current_time(),
            "transaction_cost": self._calculate_transaction_cost(order),
            "status": "executed"
        }
        
        # 更新订单状态
        order["status"] = "executed"
        order["execution_result"] = execution_result
        
        # 更新头寸
        self._update_position(order)
        
        # 构建回复
        response = {
            "message": f"已执行{order['side']}入{order['symbol']}的订单，数量：{order['quantity']}，价格：{execution_result['executed_price']}。",
            "order": order,
            "execution_result": execution_result,
            "action": {
                "type": "place_order",
                "order": order
            }
        }
        
        return response
    
    def _handle_market_making(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理做市任务"""
        security = task.get("security", {})
        making_details = task.get("details", {})
        
        # 记录做市活动
        market_making = {
            "symbol": security.get("symbol", ""),
            "bid": making_details.get("bid"),
            "ask": making_details.get("ask"),
            "bid_size": making_details.get("bid_size", 1000),
            "ask_size": making_details.get("ask_size", 1000),
            "status": "active",
            "start_time": self.get_current_time(),
        }
        
        # 添加到做市证券列表
        self.market_making_securities.append(market_making)
        
        # 构建回复
        response = {
            "message": f"已开始为{security.get('symbol', '未知证券')}提供做市服务，买入价：{market_making['bid']}，卖出价：{market_making['ask']}。",
            "market_making": market_making,
            "action": {
                "type": "market_making",
                "symbol": market_making["symbol"],
                "bid": market_making["bid"],
                "ask": market_making["ask"],
                "quantity": min(market_making["bid_size"], market_making["ask_size"])
            }
        }
        
        return response
    
    def _handle_client_order(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理客户订单任务"""
        client = task.get("client", "未知客户")
        order_details = task.get("details", {})
        
        # 记录客户订单
        order = {
            "client": client,
            "type": order_details.get("type", "market"),
            "symbol": order_details.get("symbol", ""),
            "quantity": order_details.get("quantity", 0),
            "price": order_details.get("price"),
            "side": order_details.get("side", "buy"),
            "status": "received",
            "timestamp": self.get_current_time(),
        }
        
        self.client_orders.append(order)
        
        # 检查订单有效性
        validation = self._validate_order(order)
        if not validation["valid"]:
            order["status"] = "rejected"
            order["rejection_reason"] = validation["reason"]
            
            return {
                "message": f"客户订单无效，原因：{validation['reason']}。",
                "status": "rejected",
                "order": order
            }
        
        # 准备执行订单
        order["status"] = "pending_execution"
        
        # 构建回复
        response = {
            "message": f"已接收客户{client}的{order['side']}入{order['symbol']}订单，数量：{order['quantity']}，正在准备执行。",
            "status": "pending_execution",
            "order": order,
            "next_step": "execute_trade"
        }
        
        # 创建执行交易任务
        execution_task = {
            "type": "execute_trade",
            "details": order,
            "client": client,
            "priority": "high"
        }
        
        # 添加到任务队列
        self.add_task(execution_task)
        
        return response
    
    def _handle_market_update(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理市场更新任务"""
        content = task.get("content", "")
        market_data = task.get("data", {})
        
        # 分析市场数据
        analysis = self._analyze_market_data(market_data)
        
        # 检查是否需要调整做市价格
        if analysis.get("adjust_market_making", False):
            for security in analysis.get("affected_securities", []):
                self._adjust_market_making(security)
        
        # 检查是否需要调整头寸
        if analysis.get("adjust_positions", False):
            for position in analysis.get("affected_positions", []):
                self._adjust_position(position)
        
        # 构建回复
        response = {
            "message": f"已分析市场更新：{content[:50]}...",
            "analysis": analysis,
        }
        
        # 如果需要采取行动，添加行动信息
        if analysis.get("action_required", False):
            response["action"] = analysis.get("recommended_action", {})
        
        return response
    
    def _check_trade_risk(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查交易风险
        
        Args:
            order: 订单信息
            
        Returns:
            风险评估结果
        """
        # 这里应该实现更复杂的风险评估逻辑
        # 简单实现：基于订单规模和当前头寸
        
        symbol = order.get("symbol", "")
        quantity = order.get("quantity", 0)
        side = order.get("side", "buy")
        
        # 获取当前头寸
        current_position = self.trading_positions.get(symbol, 0)
        
        # 计算交易后的头寸
        if side == "buy":
            new_position = current_position + quantity
        else:
            new_position = current_position - quantity
        
        # 风险评估
        risk_level = "low"
        reason = ""
        
        # 检查头寸规模
        if abs(new_position) > 10000:
            risk_level = "medium"
            reason = "交易后头寸规模较大"
        
        if abs(new_position) > 50000:
            risk_level = "high"
            reason = "交易后头寸规模过大，可能导致过度集中风险"
        
        # 检查头寸变化幅度
        if current_position != 0 and abs(new_position / current_position - 1) > 0.5:
            risk_level = "high"
            reason = "头寸变化幅度过大，超过50%"
        
        return {
            "risk_level": risk_level,
            "reason": reason,
            "current_position": current_position,
            "new_position": new_position,
            "change_percentage": 0 if current_position == 0 else abs(new_position / current_position - 1)
        }
    
    def _calculate_transaction_cost(self, order: Dict[str, Any]) -> float:
        """
        计算交易成本
        
        Args:
            order: 订单信息
            
        Returns:
            交易成本
        """
        # 简单实现：基于交易金额的固定比例
        price = order.get("price", 0)
        quantity = order.get("quantity", 0)
        
        if price is None:
            price = 100  # 默认价格，实际应该从市场数据获取
        
        transaction_amount = price * quantity
        commission_rate = 0.001  # 0.1%佣金率
        
        return transaction_amount * commission_rate
    
    def _update_position(self, order: Dict[str, Any]):
        """
        更新交易头寸
        
        Args:
            order: 已执行的订单
        """
        symbol = order.get("symbol", "")
        quantity = order.get("quantity", 0)
        side = order.get("side", "buy")
        
        # 获取当前头寸
        current_position = self.trading_positions.get(symbol, 0)
        
        # 更新头寸
        if side == "buy":
            self.trading_positions[symbol] = current_position + quantity
        else:
            self.trading_positions[symbol] = current_position - quantity
    
    def _validate_order(self, order: Dict[str, Any]) -> Dict[str, bool]:
        """
        验证订单有效性
        
        Args:
            order: 订单信息
            
        Returns:
            验证结果
        """
        # 检查必要字段
        if not order.get("symbol"):
            return {"valid": False, "reason": "缺少证券代码"}
        
        if not order.get("quantity"):
            return {"valid": False, "reason": "缺少交易数量"}
        
        # 检查数量是否为正数
        if order.get("quantity", 0) <= 0:
            return {"valid": False, "reason": "交易数量必须为正数"}
        
        # 检查限价单是否有价格
        if order.get("type") == "limit" and order.get("price") is None:
            return {"valid": False, "reason": "限价单必须指定价格"}
        
        # 检查交易方向
        if order.get("side") not in ["buy", "sell"]:
            return {"valid": False, "reason": "交易方向必须为buy或sell"}
        
        return {"valid": True}
    
    def _analyze_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析市场数据
        
        Args:
            market_data: 市场数据
            
        Returns:
            分析结果
        """
        # 这里应该实现更复杂的市场数据分析逻辑
        # 简单实现：检查价格变化和交易量
        
        analysis = {
            "market_trend": "stable",
            "volatility": "low",
            "liquidity": "normal",
            "action_required": False,
            "adjust_market_making": False,
            "adjust_positions": False,
            "affected_securities": [],
            "affected_positions": []
        }
        
        # 检查价格变化
        securities = market_data.get("securities", [])
        for security in securities:
            symbol = security.get("symbol")
            price_change = security.get("price_change", 0)
            volume_change = security.get("volume_change", 0)
            
            # 如果价格变化显著
            if abs(price_change) > 0.05:  # 5%以上的价格变化
                analysis["market_trend"] = "up" if price_change > 0 else "down"
                analysis["volatility"] = "high"
                analysis["action_required"] = True
                analysis["adjust_market_making"] = True
                analysis["affected_securities"].append(security)
                
                # 如果我们有相关头寸
                if symbol in self.trading_positions:
                    analysis["adjust_positions"] = True
                    analysis["affected_positions"].append({
                        "symbol": symbol,
                        "current_position": self.trading_positions[symbol],
                        "recommended_action": "reduce" if (price_change < 0 and self.trading_positions[symbol] > 0) or
                                             (price_change > 0 and self.trading_positions[symbol] < 0) else "hold"
                    })
            
            # 如果交易量变化显著
            if volume_change > 1.0:  # 交易量翻倍
                analysis["liquidity"] = "high"
                analysis["action_required"] = True
                
                if symbol not in [s.get("symbol") for s in analysis["affected_securities"]]:
                    analysis["adjust_market_making"] = True
                    analysis["affected_securities"].append(security)
        
        # 如果需要采取行动，生成建议
        if analysis["action_required"]:
            if analysis["adjust_market_making"]:
                analysis["recommended_action"] = {
                    "type": "adjust_market_making",
                    "securities": analysis["affected_securities"]
                }
            elif analysis["adjust_positions"]:
                analysis["recommended_action"] = {
                    "type": "adjust_positions",
                    "positions": analysis["affected_positions"]
                }
        
        return analysis
    
    def _adjust_market_making(self, security: Dict[str, Any]):
        """
        调整做市价格
        
        Args:
            security: 证券信息
        """
        symbol = security.get("symbol")
        
        # 查找是否正在为该证券做市
        for i, mm in enumerate(self.market_making_securities):
            if mm["symbol"] == symbol and mm["status"] == "active":
                # 根据市场数据调整做市价格
                price = security.get("price", 0)
                price_change = security.get("price_change", 0)
                
                # 调整买卖价差
                spread = max(0.01, abs(price * 0.002 * (1 + abs(price_change) * 10)))  # 价格波动越大，价差越大
                
                # 更新做市价格
                self.market_making_securities[i]["bid"] = price - spread / 2
                self.market_making_securities[i]["ask"] = price + spread / 2
                self.market_making_securities[i]["last_update"] = self.get_current_time()
                
                # 通知市场
                self.send_internal_message(
                    f"已调整{symbol}的做市价格，新买入价：{self.market_making_securities[i]['bid']}，新卖出价：{self.market_making_securities[i]['ask']}",
                    target_divisions=["executive"]
                )
                
                break
    
    def _adjust_position(self, position_info: Dict[str, Any]):
        """
        调整交易头寸
        
        Args:
            position_info: 头寸信息
        """
        symbol = position_info.get("symbol")
        current_position = position_info.get("current_position", 0)
        recommended_action = position_info.get("recommended_action", "hold")
        
        if recommended_action == "reduce" and current_position != 0:
            # 计算减仓数量，减少20%的头寸
            reduction_quantity = abs(int(current_position * 0.2))
            
            if reduction_quantity > 0:
                # 创建减仓订单
                order = {
                    "type": "market",
                    "symbol": symbol,
                    "quantity": reduction_quantity,
                    "side": "sell" if current_position > 0 else "buy",  # 如果是多头就卖出，空头就买入
                    "status": "pending",
                    "timestamp": self.get_current_time(),
                    "reason": "position_adjustment"
                }
                
                # 添加执行交易任务
                task = {
                    "type": "execute_trade",
                    "details": order,
                    "priority": "medium"
                }
                
                self.add_task(task)
                
                # 通知风控部门
                self.send_internal_message(
                    f"根据市场变化，计划调整{symbol}头寸，当前：{current_position}，计划{order['side']}出{reduction_quantity}。",
                    target_divisions=["risk_compliance"]
                )
    
    def get_viewpoint(self, issue: str) -> Dict[str, Any]:
        """
        获取销售交易部门对特定问题的观点
        
        Args:
            issue: 问题描述
            
        Returns:
            部门观点
        """
        # 这里应该实现基于LLM的观点生成
        # 简单实现：根据销售交易部门的特点生成观点
        
        viewpoint = {
            "division": "sales_trading",
            "perspective": f"从交易执行角度考虑，{issue}可能影响市场流动性和交易成本。我们应该评估其对交易策略和执行效率的影响，并考虑如何调整做市和交易活动。",
            "risk_assessment": "中高风险",
            "opportunity_assessment": "可能存在短期交易机会",
            "recommendation": "建议密切监控市场变化，准备调整交易策略和做市活动。"
        }
        
        return viewpoint
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        获取部门状态报告
        
        Returns:
            状态报告
        """
        active_positions = len(self.trading_positions)
        total_position_value = sum(abs(pos) for pos in self.trading_positions.values())
        active_market_making = len([mm for mm in self.market_making_securities if mm["status"] == "active"])
        
        return {
            "name": self.name,
            "division": self.division,
            "active_positions": active_positions,
            "total_position_value": total_position_value,
            "active_market_making": active_market_making,
            "pending_orders": len([o for o in self.client_orders if o["status"] == "pending_execution"]),
            "expertise_areas": self.expertise_areas,
            "risk_tolerance": self.risk_tolerance,
            "pending_tasks": len(self.tasks),
        } 