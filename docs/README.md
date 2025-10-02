# WebWeaver: 基于动态大纲的开放深度研究智能体

## 项目概述

WebWeaver是一个创新的双智能体框架，专门用于解决开放深度研究(OEDR)任务。该框架模拟人类研究过程，通过动态规划和大纲优化来生成高质量、引用准确的研究报告。

## 核心特性

- **双智能体架构**: Planner（规划者）和Writer（写作者）协同工作
- **动态研究循环**: 证据获取与大纲优化迭代进行
- **记忆基础合成**: 分层检索和写作过程
- **引用准确性**: 通过精确的引用管理减少幻觉问题
- **上下文优化**: 避免长上下文问题，提高生成质量

## 技术架构

### 1. Planner Agent (规划智能体)
- 负责动态大纲生成和优化
- 执行证据获取策略
- 管理研究循环迭代

### 2. Writer Agent (写作智能体)
- 基于大纲执行分层检索
- 进行逐段写作
- 管理引用和证据整合

### 3. Memory Bank (记忆库)
- 存储检索到的证据和摘要
- 支持分层检索机制
- 提供引用管理功能

## 文档结构

- `architecture.md` - 详细架构设计
- `implementation_plan.md` - 实现方案和代码规划
- `api_design.md` - API接口设计
- `prompt_templates.md` - 提示词模板
- `evaluation_metrics.md` - 评估指标和方法

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行示例
python examples/basic_research.py
```

## 论文引用

```bibtex
@article{li2025webweaver,
  title={WebWeaver: Structuring Web-Scale Evidence with Dynamic Outlines for Open-Ended Deep Research},
  author={Li, Zijian and Guan, Xin and Zhang, Bo and Huang, Shen and Zhou, Houquan and Lai, Shaopeng and Yan, Ming and Jiang, Yong and Xie, Pengjun and Huang, Fei and Zhang, Jun and Zhou, Jingren},
  journal={arXiv preprint arXiv:2509.13312},
  year={2025}
}
```
