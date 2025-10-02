"""
评估提示词模板

包含用于评估研究质量和内容质量的提示词模板。
"""

from typing import List, Dict, Any
from ..core.writer_agent import Report, WrittenSection
from ..core.planner_agent import Outline

class EvaluationPrompts:
    """评估提示词模板"""
    
    def __init__(self):
        self.system_prompt = """你是一个专业的研究质量评估专家，擅长从多个维度评估研究报告的质量。你的任务是：
1. 客观、公正地评估研究内容的质量
2. 从多个维度进行综合评估
3. 提供具体的改进建议
4. 确保评估标准的科学性和合理性

请始终以专业、客观的态度进行评估，确保评估结果的准确性和有用性。"""
    
    def get_report_quality_evaluation_prompt(self, report: Report, original_query: str) -> str:
        """获取报告质量评估提示词"""
        return f"""{self.system_prompt}

请评估以下研究报告的质量：

原始查询: {original_query}

报告信息:
- 标题: {report.title}
- 总字数: {report.total_word_count}
- 章节数: {len(report.sections)}
- 引用数: {report.total_citations}

报告内容:
{report.content[:2000]}{'...' if len(report.content) > 2000 else ''}

请从以下维度进行评估：
1. 内容相关性：内容是否与原始查询高度相关
2. 信息准确性：信息是否准确、可靠
3. 结构完整性：报告结构是否完整、逻辑清晰
4. 引用质量：引用是否恰当、准确
5. 语言表达：语言是否专业、清晰
6. 深度和广度：研究深度和广度是否合适
7. 创新性：是否有独特的见解或观点
8. 实用性：内容是否具有实用价值

请给出1-10分的评分，并提供具体的改进建议。

输出格式：
{{
    "overall_score": 8.5,
    "dimensions": {{
        "relevance": 9,
        "accuracy": 8,
        "structure": 8,
        "citation_quality": 7,
        "language": 9,
        "depth_breadth": 8,
        "innovation": 7,
        "practicality": 8
    }},
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["不足1", "不足2", "不足3"],
    "improvements": ["改进建议1", "改进建议2", "改进建议3"],
    "summary": "整体评估总结"
}}"""
    
    def get_outline_quality_evaluation_prompt(self, outline: Outline, original_query: str) -> str:
        """获取大纲质量评估提示词"""
        sections_text = []
        for i, section in enumerate(outline.sections, 1):
            sections_text.append(f"{i}. {section.title}: {section.description}")
        
        return f"""{self.system_prompt}

请评估以下研究大纲的质量：

原始查询: {original_query}

大纲信息:
- 标题: {outline.title}
- 描述: {outline.description}
- 章节数: {len(outline.get_all_sections())}

章节结构:
{chr(10).join(sections_text)}

请从以下维度进行评估：
1. 结构完整性：大纲是否涵盖了研究的主要方面
2. 逻辑性：章节之间的逻辑关系是否合理
3. 深度：研究深度是否足够
4. 广度：研究范围是否全面
5. 可操作性：大纲是否能够指导实际研究
6. 创新性：是否有独特的视角或方法
7. 平衡性：各章节的篇幅和重要性是否平衡

请给出1-10分的评分，并提供具体的改进建议。

输出格式：
{{
    "overall_score": 8.0,
    "dimensions": {{
        "completeness": 8,
        "logic": 9,
        "depth": 7,
        "breadth": 8,
        "actionability": 8,
        "innovation": 6,
        "balance": 7
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "improvements": ["改进建议1", "改进建议2"],
    "summary": "整体评估总结"
}}"""
    
    def get_section_quality_evaluation_prompt(self, section: WrittenSection, section_requirements: List[str]) -> str:
        """获取章节质量评估提示词"""
        return f"""{self.system_prompt}

请评估以下章节的质量：

章节信息:
- 标题: {section.title}
- 字数: {section.word_count}
- 引用数: {len(section.citations)}

章节要求:
{', '.join(section_requirements) if section_requirements else '无特殊要求'}

章节内容:
{section.content}

请从以下维度进行评估：
1. 内容准确性：信息是否准确、可靠
2. 逻辑性：内容组织是否逻辑清晰
3. 完整性：是否满足了章节要求
4. 引用质量：引用是否恰当、准确
5. 语言表达：语言是否专业、清晰
6. 结构组织：段落和句子组织是否合理
7. 深度：内容深度是否合适
8. 创新性：是否有独特的见解

请给出1-10分的评分，并提供具体的改进建议。

输出格式：
{{
    "overall_score": 8.5,
    "dimensions": {{
        "accuracy": 9,
        "logic": 8,
        "completeness": 8,
        "citation_quality": 7,
        "language": 9,
        "structure": 8,
        "depth": 8,
        "innovation": 7
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "improvements": ["改进建议1", "改进建议2"],
    "summary": "整体评估总结"
}}"""
    
    def get_citation_quality_evaluation_prompt(self, content: str, citations: List[str], available_evidence: List[Dict[str, Any]]) -> str:
        """获取引用质量评估提示词"""
        evidence_list = []
        for i, ev in enumerate(available_evidence, 1):
            evidence_list.append(f"证据 {i} (ID: {ev.get('id', 'unknown')}): {ev.get('summary', '')[:100]}...")
        
        return f"""{self.system_prompt}

请评估以下内容中引用的质量：

内容:
{content}

使用的引用:
{', '.join(citations) if citations else '无引用'}

可用证据:
{chr(10).join(evidence_list)}

请从以下维度进行评估：
1. 引用准确性：引用是否准确对应证据内容
2. 引用完整性：重要观点是否都有相应引用
3. 引用格式：引用格式是否正确
4. 引用分布：引用是否合理分布
5. 引用时效性：引用是否是最新的
6. 引用权威性：引用来源是否权威
7. 引用相关性：引用是否与内容高度相关

请给出1-10分的评分，并提供具体的改进建议。

输出格式：
{{
    "overall_score": 8.0,
    "dimensions": {{
        "accuracy": 8,
        "completeness": 7,
        "format": 9,
        "distribution": 8,
        "timeliness": 7,
        "authority": 8,
        "relevance": 8
    }},
    "valid_citations": ["有效引用列表"],
    "invalid_citations": ["无效引用列表"],
    "missing_citations": ["缺失引用列表"],
    "improvements": ["改进建议1", "改进建议2"],
    "summary": "整体评估总结"
}}"""
    
    def get_research_completeness_evaluation_prompt(self, outline: Outline, evidence_count: int, report: Report) -> str:
        """获取研究完整性评估提示词"""
        return f"""{self.system_prompt}

请评估以下研究的完整性：

研究大纲:
- 标题: {outline.title}
- 章节数: {len(outline.get_all_sections())}

研究数据:
- 证据数量: {evidence_count}
- 报告字数: {report.total_word_count}
- 引用数量: {report.total_citations}

请从以下维度进行评估：
1. 信息覆盖度：是否覆盖了所有重要方面
2. 证据充分性：证据是否充分支持结论
3. 研究深度：研究深度是否足够
4. 研究广度：研究范围是否全面
5. 数据质量：收集的数据质量如何
6. 方法适当性：研究方法是否适当
7. 结论可靠性：结论是否可靠

请给出1-10分的评分，并提供具体的改进建议。

输出格式：
{{
    "overall_score": 8.0,
    "dimensions": {{
        "coverage": 8,
        "evidence_sufficiency": 7,
        "depth": 8,
        "breadth": 7,
        "data_quality": 8,
        "method_appropriateness": 8,
        "conclusion_reliability": 8
    }},
    "coverage_gaps": ["覆盖缺口1", "覆盖缺口2"],
    "evidence_gaps": ["证据缺口1", "证据缺口2"],
    "improvements": ["改进建议1", "改进建议2"],
    "summary": "整体评估总结"
}}"""
    
    def get_overall_research_evaluation_prompt(self, query: str, report: Report, outline: Outline, evidence_count: int) -> str:
        """获取整体研究评估提示词"""
        return f"""{self.system_prompt}

请对以下研究进行整体评估：

研究查询: {query}

研究结果:
- 报告标题: {report.title}
- 报告字数: {report.total_word_count}
- 章节数: {len(report.sections)}
- 引用数: {report.total_citations}
- 证据数: {evidence_count}

大纲结构:
- 大纲标题: {outline.title}
- 大纲章节数: {len(outline.get_all_sections())}

请从以下维度进行综合评估：
1. 研究质量：整体研究质量如何
2. 内容质量：内容是否高质量
3. 结构质量：结构是否合理
4. 方法质量：研究方法是否适当
5. 创新性：是否有创新点
6. 实用性：是否有实用价值
7. 完整性：研究是否完整
8. 可信度：研究是否可信

请给出1-10分的评分，并提供综合的改进建议。

输出格式：
{{
    "overall_score": 8.5,
    "dimensions": {{
        "research_quality": 8,
        "content_quality": 9,
        "structure_quality": 8,
        "method_quality": 8,
        "innovation": 7,
        "practicality": 8,
        "completeness": 8,
        "credibility": 9
    }},
    "strengths": ["主要优势1", "主要优势2", "主要优势3"],
    "weaknesses": ["主要不足1", "主要不足2", "主要不足3"],
    "key_improvements": ["关键改进建议1", "关键改进建议2", "关键改进建议3"],
    "overall_assessment": "整体评估总结",
    "recommendation": "总体建议"
}}"""
