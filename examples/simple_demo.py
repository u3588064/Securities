"""
券商多智能体模拟系统 - 简单示例
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from broker_simulation.core.broker_agent import BrokerAgent
from broker_simulation.core.broker_integration import BrokerIntegration


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """主函数"""
    # 创建输出目录
    os.makedirs("output", exist_ok=True)
    
    # 设置LLM配置
    llm_config = {
        "config_list": [
            {
                "model": "gpt-4-turbo",
                "api_key": os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY")
            }
        ],
        "temperature": 0.7,
        "request_timeout": 120
    }
    
    # 创建券商智能体
    logging.info("创建券商智能体...")
    broker = BrokerAgent(
        name="华信证券",
        description="一家综合性投资银行/券商，提供全方位的金融服务，包括投资银行、销售交易、研究、财富管理和资产管理等业务。",
        llm_config=llm_config,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        config={
            "initial_balance": 5000000000.0,
            "risk_tolerance": 0.6,
            "market_share": 0.08,
            "reputation": 0.75
        }
    )
    
    # 创建集成模块
    integration = BrokerIntegration(
        broker_agent=broker,
        config={
            "connections": {
                "agent_types": ["financial_institutions", "corporate", "individual_investor", "regulatory"]
            }
        }
    )
    
    # 运行内部通信周期
    logging.info("运行内部通信周期...")
    for i in range(3):
        logging.info(f"内部通信周期 {i+1}/3")
        integration.run_internal_cycle()
    
    # 可视化内部结构
    logging.info("生成内部结构可视化...")
    visualization_file = "output/broker_structure.html"
    integration.visualize_broker_structure(visualization_file)
    logging.info(f"内部结构可视化已保存到: {visualization_file}")
    
    # 处理IPO承销请求
    logging.info("处理IPO承销请求...")
    ipo_request = {
        "type": "client_request",
        "request_type": "investment_banking",
        "content": "我们是一家人工智能科技公司，计划在未来6个月内进行IPO，希望贵公司能够担任我们的主承销商。",
        "sender": {
            "name": "智能科技有限公司",
            "type": "corporate",
            "industry": "technology"
        },
        "data": {
            "company_valuation": 5000000000,
            "annual_revenue": 800000000,
            "growth_rate": 0.35,
            "profit_margin": 0.22
        }
    }
    
    ipo_response = integration.process_market_event(ipo_request)
    logging.info(f"IPO承销请求处理结果: {ipo_response}")
    
    # 运行内部通信周期
    integration.run_internal_cycle()
    
    # 处理交易请求
    logging.info("处理交易请求...")
    trading_request = {
        "type": "client_request",
        "request_type": "trading",
        "content": "我们计划在未来三天内买入约500万股中国石油，请帮我们设计一个交易策略，尽量减小市场冲击。",
        "sender": {
            "name": "远景基金管理公司",
            "type": "financial_institutions",
            "aum": 50000000000
        },
        "data": {
            "symbol": "601857",
            "quantity": 5000000,
            "side": "buy",
            "time_constraint": "3 days",
            "price_constraint": "VWAP + 0.5%"
        }
    }
    
    trading_response = integration.process_market_event(trading_request)
    logging.info(f"交易请求处理结果: {trading_response}")
    
    # 运行内部通信周期
    integration.run_internal_cycle()
    
    # 处理市场更新
    logging.info("处理市场更新...")
    market_update = {
        "type": "market_update",
        "content": "近期市场对科技股IPO反应积极，多家科技公司IPO首日涨幅超过30%。",
        "data": {
            "securities": [
                {
                    "symbol": "TECH1",
                    "price": 68.5,
                    "price_change": 0.32,
                    "volume_change": 2.5
                },
                {
                    "symbol": "TECH2",
                    "price": 42.3,
                    "price_change": 0.28,
                    "volume_change": 1.8
                }
            ],
            "market_sentiment": "positive",
            "sector_performance": {
                "technology": 0.15,
                "finance": 0.05,
                "healthcare": 0.08
            }
        }
    }
    
    market_response = integration.process_market_event(market_update)
    logging.info(f"市场更新处理结果: {market_response}")
    
    # 运行内部通信周期
    integration.run_internal_cycle()
    
    # 获取券商状态
    broker_status = integration.get_broker_status()
    
    # 保存结果
    results = {
        "broker_info": broker_status,
        "ipo_response": ipo_response,
        "trading_response": trading_response,
        "market_response": market_response,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("output/demo_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logging.info("示例运行完成，结果已保存到 output/demo_results.json")


if __name__ == "__main__":
    main() 