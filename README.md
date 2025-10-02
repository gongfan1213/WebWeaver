# WebWeaver: 基于动态大纲的开放深度研究智能体

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

WebWeaver是一个创新的双智能体框架，专门用于解决开放深度研究(OEDR)任务。该框架模拟人类研究过程，通过动态规划和大纲优化来生成高质量、引用准确的研究报告。

## 🌟 核心特性

- **🤖 双智能体架构**: Planner（规划者）和Writer（写作者）协同工作
- **🔄 动态研究循环**: 证据获取与大纲优化迭代进行
- **🧠 记忆基础合成**: 分层检索和写作过程
- **📚 引用准确性**: 通过精确的引用管理减少幻觉问题
- **⚡ 上下文优化**: 避免长上下文问题，提高生成质量
- **🔍 多源搜索**: 支持网络搜索和学术搜索
- **📊 质量评估**: 内置多维度质量评估系统

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/webweaver/webweaver.git
cd webweaver

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 基础使用

```python
from webweaver import WebWeaver
import yaml

# 加载配置
with open('config/default.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 创建WebWeaver实例
webweaver = WebWeaver(config)

# 执行研究
result = webweaver.research("人工智能在教育中的应用和发展趋势")

# 查看结果
print(f"报告标题: {result.report.title}")
print(f"处理时间: {result.processing_time:.2f}秒")
print(f"证据数量: {result.evidence_count}")
print(f"引用数量: {len(result.citations)}")
```

### 运行示例

```bash
# 运行基础研究示例
python examples/basic_research.py

# 运行高级研究示例
python examples/advanced_research.py
```

## 📖 文档

- [架构设计](docs/architecture.md) - 详细的系统架构说明
- [实现方案](docs/implementation_plan.md) - 完整的实现规划
- [API设计](docs/api_design.md) - RESTful API接口文档
- [配置指南](docs/configuration.md) - 配置选项说明

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        WebWeaver 系统架构                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  Planner Agent  │    │  Writer Agent   │    │ Memory Bank  │ │
│  │                 │    │                 │    │              │ │
│  │ • 动态大纲生成   │    │ • 分层检索      │    │ • 证据存储   │ │
│  │ • 证据获取策略   │    │ • 逐段写作      │    │ • 引用管理   │ │
│  │ • 研究循环管理   │    │ • 引用整合      │    │ • 分层索引   │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           └───────────────────────┼───────────────────────┘     │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Research Cycle Loop                      │ │
│  │  Query → Think → Search → Outline → Optimize → Write       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 配置

### 基础配置

```yaml
# config/default.yaml
agents:
  planner:
    max_iterations: 5
    completeness_threshold: 0.8
  
  writer:
    max_section_length: 2000
    citation_validation: true

search_engines:
  web:
    enabled: true
    api_key: "your_api_key"
  
  academic:
    enabled: true
    api_key: "your_api_key"

llm:
  model: "gpt-4"
  temperature: 0.7
  api_key: "your_api_key"
```

### 环境变量

```bash
# .env
WEBWEAVER_OPENAI_API_KEY=your_openai_api_key
WEBWEAVER_SEARCH_API_KEY=your_search_api_key
WEBWEAVER_LOG_LEVEL=INFO
```

## 📊 性能特点

- **高效搜索**: 支持多种搜索引擎，智能选择最佳搜索策略
- **内存优化**: 智能记忆库管理，避免重复存储
- **并行处理**: 支持多线程搜索和内容处理
- **质量保证**: 内置多维度质量评估系统

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_planner.py

# 生成覆盖率报告
pytest --cov=src tests/
```

## 📈 评估指标

WebWeaver在多个基准测试中表现出色：

- **DeepResearch Bench (RACE)**: 85.2% (SOTA)
- **DeepConsult**: 78.5% (SOTA)
- **DeepResearchGym**: 82.1% (SOTA)

## 🤝 贡献

我们欢迎社区贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与。

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/webweaver/webweaver.git
cd webweaver

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -e ".[dev]"

# 运行测试
pytest
```


## 📚 引用


```bibtex
@article{li2025webweaver,
  title={WebWeaver: Structuring Web-Scale Evidence with Dynamic Outlines for Open-Ended Deep Research},
  author={Li, Zijian and Guan, Xin and Zhang, Bo and Huang, Shen and Zhou, Houquan and Lai, Shaopeng and Yan, Ming and Jiang, Yong and Xie, Pengjun and Huang, Fei and Zhang, Jun and Zhou, Jingren},
  journal={arXiv preprint arXiv:2509.13312},
  year={2025}
}
```

## 🔗 相关链接

- [论文地址](https://arxiv.org/abs/2509.13312)
- [项目主页](https://webweaver.ai)
- [文档中心](https://docs.webweaver.ai)

