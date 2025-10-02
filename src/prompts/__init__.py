"""
WebWeaver 提示词模板模块

包含各种智能体的提示词模板：
- planner_prompts: 规划者提示词
- writer_prompts: 写作者提示词
- evaluation_prompts: 评估提示词
"""

from .planner_prompts import PlannerPrompts
from .writer_prompts import WriterPrompts
from .evaluation_prompts import EvaluationPrompts

__all__ = [
    "PlannerPrompts",
    "WriterPrompts", 
    "EvaluationPrompts"
]
