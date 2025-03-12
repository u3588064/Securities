"""
券商多智能体模拟系统 - 主程序入口
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

import autogen

from broker_simulation.core.broker_agent import BrokerAgent
from broker_simulation.core.broker_integration import BrokerIntegration


# 配置日志
def setup_logging(log_level=logging.INFO, log_file=None):
    """设置日志配置"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 创建日志处理器
    handlers = []
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        return {}


def save_results(results: Dict[str, Any], output_path: str):
    """
    保存模拟结果
    
    Args:
        results: 模拟结果
        output_path: 输出路径
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logging.info(f"结果已保存到 {output_path}")
    except Exception as e:
        logging.error(f"保存结果失败: {str(e)}")


def create_broker_agent(config: Dict[str, Any]) -> BrokerAgent:
    """
    创建券商智能体
    
    Args:
        config: 配置字典
        
    Returns:
        券商智能体
    """
    # 获取LLM配置
    llm_config = config.get("llm_config", {})
    
    # 创建券商智能体
    broker = BrokerAgent(
        name=config.get("name", "示例券商"),
        description=config.get("description", "一家综合性投资银行/券商"),
        llm_config=llm_config,
        human_input_mode=config.get("human_input_mode", "NEVER"),
        max_consecutive_auto_reply=config.get("max_consecutive_auto_reply", 10),
        config=config.get("broker_config", {})
    )
    
    return broker


def run_simulation(broker: BrokerAgent, config: Dict[str, Any], market_simulation=None) -> Dict[str, Any]:
    """
    运行模拟
    
    Args:
        broker: 券商智能体
        config: 配置字典
        market_simulation: 市场模拟器（可选）
        
    Returns:
        模拟结果
    """
    # 创建集成模块
    integration = BrokerIntegration(
        broker_agent=broker,
        market_simulation=market_simulation,
        config=config.get("integration_config", {})
    )
    
    # 获取模拟参数
    simulation_config = config.get("simulation", {})
    num_cycles = simulation_config.get("num_cycles", 10)
    scenarios = simulation_config.get("scenarios", [])
    
    # 记录结果
    results = {
        "broker_info": broker.get_info(),
        "start_time": datetime.now().isoformat(),
        "cycles": [],
        "scenarios_results": [],
        "final_state": {}
    }
    
    # 运行内部通信周期
    logging.info(f"开始运行{num_cycles}个内部通信周期")
    for i in range(num_cycles):
        logging.info(f"运行内部通信周期 {i+1}/{num_cycles}")
        integration.run_internal_cycle()
        
        # 记录周期结果
        cycle_result = {
            "cycle": i + 1,
            "broker_state": broker.get_info()
        }
        results["cycles"].append(cycle_result)
    
    # 运行场景
    if scenarios:
        logging.info(f"开始运行{len(scenarios)}个场景")
        for i, scenario in enumerate(scenarios):
            logging.info(f"运行场景 {i+1}/{len(scenarios)}: {scenario.get('name', f'场景{i+1}')}")
            scenario_result = run_scenario(integration, scenario)
            results["scenarios_results"].append(scenario_result)
    
    # 记录最终状态
    results["final_state"] = broker.get_info()
    results["end_time"] = datetime.now().isoformat()
    
    return results


def run_scenario(integration: BrokerIntegration, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行单个场景
    
    Args:
        integration: 券商集成模块
        scenario: 场景配置
        
    Returns:
        场景结果
    """
    scenario_name = scenario.get("name", "未命名场景")
    scenario_type = scenario.get("type", "")
    events = scenario.get("events", [])
    
    logging.info(f"运行场景: {scenario_name}, 类型: {scenario_type}, 事件数: {len(events)}")
    
    # 记录结果
    results = {
        "name": scenario_name,
        "type": scenario_type,
        "start_time": datetime.now().isoformat(),
        "events_results": []
    }
    
    # 处理事件
    for i, event in enumerate(events):
        logging.info(f"处理事件 {i+1}/{len(events)}: {event.get('description', f'事件{i+1}')}")
        
        # 处理事件
        event_result = integration.process_market_event(event)
        
        # 记录事件结果
        event_record = {
            "event": event,
            "result": event_result
        }
        results["events_results"].append(event_record)
        
        # 运行内部通信周期
        integration.run_internal_cycle()
    
    # 记录场景结束时间
    results["end_time"] = datetime.now().isoformat()
    results["broker_state"] = integration.get_broker_status()
    
    return results


def run_agent_conversation(broker: BrokerAgent, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行智能体对话
    
    Args:
        broker: 券商智能体
        config: 配置字典
        
    Returns:
        对话结果
    """
    conversation_config = config.get("conversation", {})
    user_proxy_config = conversation_config.get("user_proxy", {})
    
    # 创建用户代理
    user_proxy = autogen.UserProxyAgent(
        name=user_proxy_config.get("name", "用户"),
        human_input_mode=user_proxy_config.get("human_input_mode", "ALWAYS"),
        max_consecutive_auto_reply=user_proxy_config.get("max_consecutive_auto_reply", 0),
    )
    
    # 初始化对话
    initial_message = conversation_config.get("initial_message", "你好，我想了解一下你们券商的服务。")
    
    # 开始对话
    logging.info("开始智能体对话")
    user_proxy.initiate_chat(
        broker.agent,
        message=initial_message
    )
    
    # 获取对话历史
    chat_history = user_proxy.chat_messages[broker.agent.name]
    
    # 记录结果
    results = {
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "chat_history": chat_history
    }
    
    return results


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="券商多智能体模拟系统")
    parser.add_argument("--config", type=str, default="config/default.json", help="配置文件路径")
    parser.add_argument("--output", type=str, default="results/simulation_result.json", help="输出文件路径")
    parser.add_argument("--log-file", type=str, default="logs/simulation.log", help="日志文件路径")
    parser.add_argument("--mode", type=str, choices=["simulation", "conversation"], default="simulation", help="运行模式")
    parser.add_argument("--market-integration", type=str, default=None, help="市场模拟器集成模块路径")
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(log_file=args.log_file)
    
    # 加载配置
    config = load_config(args.config)
    if not config:
        logging.error("无法加载配置，退出程序")
        sys.exit(1)
    
    # 创建券商智能体
    broker = create_broker_agent(config)
    
    # 加载市场模拟器（如果指定）
    market_simulation = None
    if args.market_integration:
        try:
            # 动态导入市场模拟器
            import importlib.util
            spec = importlib.util.spec_from_file_location("market_module", args.market_integration)
            market_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(market_module)
            
            # 创建市场模拟器实例
            market_simulation = market_module.create_market_simulation(config.get("market_config", {}))
            logging.info(f"已加载市场模拟器: {args.market_integration}")
        except Exception as e:
            logging.error(f"加载市场模拟器失败: {str(e)}")
    
    # 根据模式运行
    if args.mode == "simulation":
        # 运行模拟
        results = run_simulation(broker, config, market_simulation)
    else:
        # 运行对话
        results = run_agent_conversation(broker, config)
    
    # 保存结果
    save_results(results, args.output)
    
    logging.info("模拟完成")


if __name__ == "__main__":
    main() 