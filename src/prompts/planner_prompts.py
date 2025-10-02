"""
规划者提示词模板

包含规划智能体使用的各种提示词模板。
"""

from typing import List, Dict, Any
from ..core.planner_agent import Outline
from ..core.memory_bank import Evidence

class PlannerPrompts:
    """规划者提示词模板"""
    
    def __init__(self):
        self.system_prompt = """你是一个专业的研究规划者，擅长制定详细的研究大纲和搜索策略。你的任务是：
1. 根据研究查询生成结构化的研究大纲
2. 基于新证据优化现有大纲
3. 制定有效的搜索策略来获取相关信息

请始终以专业、客观的态度进行分析，确保大纲的逻辑性和完整性。"""
    
    def get_initial_outline_prompt(self, query: str) -> str:
        """获取初始大纲生成提示词"""
        return f"""{self.system_prompt}

请根据以下研究查询生成一个详细的研究大纲：

研究查询: {query}

请生成一个结构化的研究大纲，要求：
1. 包含主要章节和子章节
2. 每个章节都有清晰的标题和描述
3. 章节之间具有逻辑关系
4. 涵盖研究的深度和广度
5. 考虑不同角度和观点

请以JSON格式输出大纲结构，格式如下：
{{
    "title": "研究标题",
    "description": "研究描述和背景",
    "sections": [
        {{
            "id": "section_1",
            "title": "章节标题",
            "description": "章节详细描述",
            "level": 1,
            "requirements": ["具体研究要求1", "具体研究要求2"],
            "children": [
                {{
                    "id": "section_1_1",
                    "title": "子章节标题",
                    "description": "子章节详细描述",
                    "level": 2,
                    "requirements": ["子章节要求1", "子章节要求2"]
                }}
            ]
        }}
    ]
}}

请确保大纲结构清晰、逻辑合理，能够指导后续的研究和写作工作。"""
    
    def get_outline_optimization_prompt(self, outline: Outline, new_evidence: List[Evidence]) -> str:
        """获取大纲优化提示词"""
        evidence_summaries = []
        for i, ev in enumerate(new_evidence, 1):
            evidence_summaries.append(f"证据 {i}:\n- 来源: {ev.source}\n- 摘要: {ev.summary}\n- 相关性: {ev.relevance_score:.2f}")
        
        return f"""{self.system_prompt}

基于新获取的证据，请优化当前的研究大纲：

当前大纲:
{self._format_outline_for_prompt(outline)}

新获取的证据:
{chr(10).join(evidence_summaries)}

请分析新证据如何影响现有大纲，并进行以下优化：
1. 评估新证据与现有章节的匹配度
2. 识别需要添加的新章节或子章节
3. 调整章节顺序和重点
4. 更新章节描述和要求
5. 确保大纲的完整性和逻辑性

请输出优化后的大纲，格式与初始大纲相同。如果某些证据与现有大纲不匹配，请考虑是否需要添加新的研究方向。"""
    
    def get_search_strategy_prompt(self, outline: Outline) -> str:
        """获取搜索策略提示词"""
        return f"""{self.system_prompt}

基于当前研究大纲，请制定详细的搜索策略：

当前大纲:
{self._format_outline_for_prompt(outline)}

请为每个需要更多信息的章节制定搜索策略，考虑以下因素：
1. 章节的重要性和优先级
2. 当前信息的完整度
3. 需要补充的具体信息类型
4. 搜索的深度和广度

请以JSON格式输出搜索策略，格式如下：
[
    {{
        "section_id": "section_1",
        "priority": 1,
        "keywords": ["关键词1", "关键词2", "关键词3"],
        "search_type": "web",
        "expected_info": "预期的信息类型描述",
        "depth": "high",
        "reasoning": "为什么需要这些信息"
    }}
]

搜索类型说明：
- "web": 网络搜索，适用于一般信息
- "academic": 学术搜索，适用于研究论文和学术资料
- "news": 新闻搜索，适用于最新动态和时事

深度说明：
- "high": 深度搜索，需要详细和深入的信息
- "medium": 中等深度，需要基本信息和概述
- "low": 浅层搜索，需要简要信息和背景

请确保搜索策略具有针对性和可执行性。"""
    
    def get_outline_quality_assessment_prompt(self, outline: Outline) -> str:
        """获取大纲质量评估提示词"""
        return f"""{self.system_prompt}

请评估以下研究大纲的质量：

大纲内容:
{self._format_outline_for_prompt(outline)}

请从以下维度进行评估：
1. 结构完整性：大纲是否涵盖了研究的主要方面
2. 逻辑性：章节之间的逻辑关系是否合理
3. 深度：研究深度是否足够
4. 广度：研究范围是否全面
5. 可操作性：大纲是否能够指导实际研究

请给出1-10分的评分，并提供具体的改进建议。

输出格式：
{{
    "overall_score": 8.5,
    "dimensions": {{
        "completeness": 8,
        "logic": 9,
        "depth": 8,
        "breadth": 7,
        "actionability": 9
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "improvements": ["改进建议1", "改进建议2"]
}}"""
    
    def get_research_gap_analysis_prompt(self, outline: Outline, evidence: List[Evidence]) -> str:
        """获取研究缺口分析提示词"""
        evidence_summaries = []
        for i, ev in enumerate(evidence, 1):
            evidence_summaries.append(f"证据 {i}: {ev.summary}")
        
        return f"""{self.system_prompt}

请分析当前研究大纲与已有证据之间的缺口：

研究大纲:
{self._format_outline_for_prompt(outline)}

已有证据:
{chr(10).join(evidence_summaries)}

请识别以下类型的缺口：
1. 信息缺口：大纲中需要但证据中缺失的信息
2. 深度缺口：某些方面需要更深入的研究
3. 广度缺口：某些领域需要更广泛的覆盖
4. 时效性缺口：需要更新的信息
5. 视角缺口：需要不同角度的观点

请为每个缺口提供具体的搜索建议。

输出格式：
{{
    "gaps": [
        {{
            "type": "信息缺口",
            "section_id": "section_1",
            "description": "缺口描述",
            "search_suggestions": ["搜索建议1", "搜索建议2"]
        }}
    ],
    "priority_gaps": ["高优先级缺口1", "高优先级缺口2"],
    "overall_assessment": "整体评估"
}}"""
    
    def _format_outline_for_prompt(self, outline: Outline) -> str:
        """格式化大纲用于提示词"""
        sections_text = []
        
        for section in outline.sections:
            section_text = self._format_section_for_prompt(section, 0)
            sections_text.append(section_text)
        
        return f"""
标题: {outline.title}
描述: {outline.description}

章节结构:
{chr(10).join(sections_text)}
"""
    
    def _format_section_for_prompt(self, section, indent_level: int) -> str:
        """格式化单个章节用于提示词"""
        indent = "  " * indent_level
        section_text = f"{indent}{section.id}: {section.title}\n"
        section_text += f"{indent}  描述: {section.description}\n"
        
        if section.requirements:
            section_text += f"{indent}  要求: {', '.join(section.requirements)}\n"
        
        if section.children:
            section_text += f"{indent}  子章节:\n"
            for child in section.children:
                child_text = self._format_section_for_prompt(child, indent_level + 2)
                section_text += child_text
        
        return section_text
