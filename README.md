# 券商多智能体模拟系统

这是一个基于多智能体架构的券商模拟系统，旨在模拟券商内部各部门之间的协作和决策过程，以及券商与外部市场和客户的交互。

## 项目概述

券商作为一个复合智能体，由多个子智能体组成，每个子智能体代表券商内部的一个部门或团队。这些部门包括：

- **投资银行部门**：负责IPO承销、债券发行和并购咨询等业务
- **销售交易部门**：负责证券交易、做市和客户订单执行
- **研究部门**：负责市场研究、行业分析和投资建议
- **财富管理部门**：负责高净值客户和零售客户的资产管理
- **资产管理部门**：负责基金产品设计和资产管理业务
- **风控合规部门**：负责风险管理和合规监督
- **高管团队**：负责战略决策和部门协调

## 券商内部结构

券商内部采用层次化的组织结构，各部门之间通过内部通信网络进行信息交换和协作。高管团队位于决策层，负责协调各部门的工作和解决部门间的冲突。

```
                    ┌─────────────┐
                    │  高管团队   │
                    └─────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ 风控合规部  │ │  投资银行部 │ │  研究部    │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
           │        ┌──────┴──────┐        │
           │        │             │        │
    ┌─────────────┐ │ ┌─────────────┐ ┌─────────────┐
    │ 财富管理部  │◄┼─┤ 销售交易部 │◄┼─┤ 资产管理部 │
    └─────────────┘ │ └─────────────┘ │ └─────────────┘
                    └─────────────────┘
```

## 项目结构

```
broker_simulation/
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── broker_agent.py     # 券商复合智能体
│   ├── sub_agent.py        # 子智能体基类
│   ├── internal_network.py # 内部通信网络
│   └── broker_integration.py # 与市场集成模块
├── agents/                 # 各部门智能体
│   ├── __init__.py
│   ├── investment_banking.py # 投资银行部门
│   ├── sales_trading.py    # 销售交易部门
│   ├── research.py         # 研究部门
│   ├── wealth_management.py # 财富管理部门
│   ├── asset_management.py # 资产管理部门
│   ├── risk_compliance.py  # 风控合规部门
│   └── executive.py        # 高管团队
├── utils/                  # 工具模块
│   ├── __init__.py
│   └── visualization.py    # 可视化工具
├── config/                 # 配置文件
│   └── default.json        # 默认配置
├── examples/               # 示例代码
│   └── simple_demo.py      # 简单示例
├── logs/                   # 日志目录
├── results/                # 结果输出目录
├── __init__.py             # 包初始化文件
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
└── README.md               # 项目说明
```

## 核心功能

1. **内部协作决策**：模拟券商内部各部门之间的信息交流和协作决策过程
2. **业务流程模拟**：模拟IPO承销、交易策略执行等业务流程
3. **外部交互接口**：与市场、客户和监管机构的交互接口
4. **冲突解决机制**：部门间观点冲突的解决机制
5. **可视化分析**：券商内部结构和通信网络的可视化

## 已完成的模块

- [x] 核心框架
  - [x] 券商复合智能体 (`BrokerAgent`)
  - [x] 子智能体基类 (`BrokerSubAgent`)
  - [x] 内部通信网络 (`InternalNetwork`)
  - [x] 与市场集成模块 (`BrokerIntegration`)

- [x] 部门智能体
  - [x] 投资银行部门 (`InvestmentBankingAgent`)
  - [x] 销售交易部门 (`SalesTradingAgent`)
  - [ ] 研究部门 (`ResearchAgent`)
  - [ ] 财富管理部门 (`WealthManagementAgent`)
  - [ ] 资产管理部门 (`AssetManagementAgent`)
  - [ ] 风控合规部门 (`RiskComplianceAgent`)
  - [ ] 高管团队 (`ExecutiveAgent`)

- [x] 工具模块
  - [x] 可视化工具 (`visualization.py`)

- [x] 配置和示例
  - [x] 默认配置 (`default.json`)
  - [x] 简单示例 (`simple_demo.py`)

## 安装和运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行示例

```bash
# 运行简单示例
python -m broker_simulation.examples.simple_demo

# 运行主程序（模拟模式）
python -m broker_simulation.main --config config/default.json --output results/simulation_result.json

# 运行主程序（对话模式）
python -m broker_simulation.main --mode conversation --config config/default.json --output results/conversation_result.json
```

## 与金融市场模拟器集成

本系统可以作为独立项目运行，也可以与金融市场模拟器（[https://github.com/u3588064/WallStreet] ）集成，作为市场中的一个参与者。集成方式如下：

```bash
python -m broker_simulation.main --market-integration path/to/market_simulation.py --config config/default.json
```

## 自定义配置

可以通过修改配置文件来自定义券商的结构和行为：

```json
{
  "name": "自定义券商名称",
  "description": "券商描述",
  "llm_config": {
    "config_list": [
      {
        "model": "gpt-4-turbo",
        "api_key": "YOUR_API_KEY"
      }
    ],
    "temperature": 0.7
  },
  "broker_config": {
    "initial_balance": 5000000000.0,
    "risk_tolerance": 0.6
  },
  "simulation": {
    "num_cycles": 5,
    "scenarios": [
      // 自定义场景
    ]
  }
}
```

## 示例场景

系统内置了多个示例场景，包括：

1. **IPO承销场景**：处理一家科技公司的IPO承销业务
2. **交易策略执行场景**：执行大额股票交易策略

## 后续开发计划

- [ ] 完成剩余部门智能体的实现
- [ ] 增加更多业务场景
- [ ] 实现更复杂的内部决策机制
- [ ] 增强与外部市场的交互能力
- [ ] 添加更多可视化和分析工具

## 许可证

本项目采用 MIT 许可证。 

如果您有任何问题或需要进一步的信息，请联系项目维护者：[u3588064@connect.hku.hk](mailto:u3588064@connect.hku.hk)。

![qrcode_for_gh_643efb7db5bc_344(1)](https://github.com/u3588064/LLMemory/assets/53069671/8bb26c0f-4cab-438b-9f8c-16b1c26b3587)
