"""
WebWeaver: 基于动态大纲的开放深度研究智能体

这是一个创新的双智能体框架，专门用于解决开放深度研究(OEDR)任务。
该框架模拟人类研究过程，通过动态规划和大纲优化来生成高质量、引用准确的研究报告。

主要组件:
- PlannerAgent: 规划智能体，负责动态大纲生成和优化
- WriterAgent: 写作智能体，负责分层检索和逐段写作
- MemoryBank: 记忆库，存储和管理证据
- WebWeaver: 主系统，协调各个组件工作

使用示例:
    from src.core.webweaver import WebWeaver
    
    # 初始化系统
    webweaver = WebWeaver(config)
    
    # 执行研究
    result = webweaver.research("人工智能在教育中的应用")
    print(result.report)
"""

__version__ = "1.0.0"
__author__ = "WebWeaver Team"

from .core.webweaver import WebWeaver
from .core.planner_agent import PlannerAgent
from .core.writer_agent import WriterAgent
from .core.memory_bank import MemoryBank, Evidence

__all__ = [
    "WebWeaver",
    "PlannerAgent", 
    "WriterAgent",
    "MemoryBank",
    "Evidence"
]
