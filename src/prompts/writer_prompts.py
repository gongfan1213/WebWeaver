"""
写作者提示词模板

包含写作智能体使用的各种提示词模板。
"""

from typing import List, Dict, Any
from ..core.writer_agent import WrittenSection
from ..core.planner_agent import Section
from ..core.memory_bank import Evidence

class WriterPrompts:
    """写作者提示词模板"""
    
    def __init__(self):
        self.system_prompt = """你是一个专业的研究报告写作者，擅长基于证据进行客观、准确的写作。你的任务是：
1. 基于提供的证据写作高质量的研究内容
2. 确保所有观点都有相应的证据支持
3. 正确使用引用格式
4. 保持内容的逻辑性和连贯性

请始终以专业、客观的态度进行写作，确保内容的准确性和可信度。"""
    
    def get_section_writing_prompt(self, section: Section, evidence: List[Evidence]) -> str:
        """获取章节写作提示词"""
        evidence_text = self._format_evidence_for_prompt(evidence)
        
        return f"""{self.system_prompt}

请基于提供的证据写作以下章节：

章节信息:
- 标题: {section.title}
- 描述: {section.description}
- 要求: {', '.join(section.requirements) if section.requirements else '无特殊要求'}

相关证据:
{evidence_text}

写作要求:
1. 内容要准确、客观、有逻辑性
2. 必须基于提供的证据进行写作，不能编造信息
3. 每个重要观点都要有相应的引用，格式为 [证据ID]
4. 语言要专业、清晰、易懂
5. 确保内容的连贯性和完整性
6. 适当使用过渡词和连接词
7. 保持学术写作的严谨性

引用格式说明：
- 在需要引用的地方使用 [证据ID] 格式
- 例如：根据研究显示[evidence_001]，这种方法具有显著效果
- 确保每个引用都对应提供的证据

请输出章节内容，确保内容充实、逻辑清晰、引用准确。"""
    
    def get_content_revision_prompt(self, original_content: str, feedback: str) -> str:
        """获取内容修订提示词"""
        return f"""{self.system_prompt}

请根据反馈意见修订以下内容：

原始内容:
{original_content}

反馈意见:
{feedback}

修订要求:
1. 仔细分析反馈意见，理解需要改进的地方
2. 保持原文的核心观点和结构
3. 改进语言表达和逻辑组织
4. 确保引用格式正确
5. 保持内容的客观性和准确性

请输出修订后的内容。"""
    
    def get_citation_validation_prompt(self, content: str, evidence: List[Evidence]) -> str:
        """获取引用验证提示词"""
        evidence_list = []
        for i, ev in enumerate(evidence, 1):
            evidence_list.append(f"证据 {i} (ID: {ev.id}):\n- 来源: {ev.source}\n- 内容: {ev.content[:200]}...")
        
        return f"""{self.system_prompt}

请验证以下内容中的引用是否准确：

内容:
{content}

可用证据:
{chr(10).join(evidence_list)}

请检查：
1. 每个引用 [证据ID] 是否都有对应的证据
2. 引用是否准确反映了证据内容
3. 是否有遗漏的重要引用
4. 引用格式是否正确
5. 引用是否在适当的位置

请输出验证结果，格式如下：
{{
    "valid_citations": ["有效的引用列表"],
    "invalid_citations": ["无效的引用列表"],
    "missing_citations": ["缺失的引用列表"],
    "suggestions": ["改进建议列表"]
}}"""
    
    def get_content_quality_assessment_prompt(self, content: str, section: Section) -> str:
        """获取内容质量评估提示词"""
        return f"""{self.system_prompt}

请评估以下内容的质量：

章节信息:
- 标题: {section.title}
- 描述: {section.description}

内容:
{content}

请从以下维度进行评估：
1. 内容准确性：信息是否准确、可靠
2. 逻辑性：内容组织是否逻辑清晰
3. 完整性：是否涵盖了章节要求的所有方面
4. 引用质量：引用是否恰当、准确
5. 语言表达：语言是否专业、清晰
6. 结构组织：段落和句子组织是否合理

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
        "structure": 8
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "improvements": ["改进建议1", "改进建议2"]
}}"""
    
    def get_summary_generation_prompt(self, content: str, max_length: int = 200) -> str:
        """获取摘要生成提示词"""
        return f"""{self.system_prompt}

请为以下内容生成一个简洁的摘要：

内容:
{content}

摘要要求:
1. 长度控制在{max_length}字以内
2. 包含主要内容要点
3. 保持客观、准确
4. 语言简洁、清晰
5. 突出核心观点

请输出摘要。"""
    
    def get_transition_writing_prompt(self, previous_section: WrittenSection, current_section: Section) -> str:
        """获取过渡段落写作提示词"""
        return f"""{self.system_prompt}

请为以下两个章节之间写一个过渡段落：

前一章节:
- 标题: {previous_section.title}
- 内容摘要: {previous_section.content[:300]}...

当前章节:
- 标题: {current_section.title}
- 描述: {current_section.description}

过渡段落要求:
1. 连接前后两个章节的内容
2. 长度控制在50-100字
3. 语言流畅、自然
4. 体现章节间的逻辑关系
5. 为当前章节做适当铺垫

请输出过渡段落。"""
    
    def get_conclusion_writing_prompt(self, sections: List[WrittenSection], main_topic: str) -> str:
        """获取结论写作提示词"""
        section_summaries = []
        for i, section in enumerate(sections, 1):
            section_summaries.append(f"{i}. {section.title}: {section.content[:100]}...")
        
        return f"""{self.system_prompt}

请为以下研究内容写一个结论段落：

研究主题: {main_topic}

各章节摘要:
{chr(10).join(section_summaries)}

结论要求:
1. 总结主要研究发现
2. 回答研究问题
3. 指出研究的局限性
4. 提出未来研究方向
5. 长度控制在300-500字
6. 语言严谨、客观

请输出结论段落。"""
    
    def _format_evidence_for_prompt(self, evidence: List[Evidence]) -> str:
        """格式化证据用于提示词"""
        if not evidence:
            return "暂无相关证据"
        
        evidence_text = []
        for i, ev in enumerate(evidence, 1):
            evidence_text.append(f"""
证据 {i} (ID: {ev.id}):
- 来源: {ev.source}
- 摘要: {ev.summary}
- 内容: {ev.content[:500]}{'...' if len(ev.content) > 500 else ''}
- 相关性: {ev.relevance_score:.2f}
""")
        
        return "\n".join(evidence_text)
    
    def get_style_consistency_prompt(self, content: str, style_guide: Dict[str, Any]) -> str:
        """获取风格一致性检查提示词"""
        return f"""{self.system_prompt}

请检查以下内容是否符合指定的写作风格：

内容:
{content}

风格指南:
{self._format_style_guide(style_guide)}

请检查：
1. 语言风格是否一致
2. 术语使用是否统一
3. 引用格式是否符合要求
4. 段落结构是否规范
5. 学术写作规范是否遵循

请输出检查结果和改进建议。"""
    
    def _format_style_guide(self, style_guide: Dict[str, Any]) -> str:
        """格式化风格指南"""
        guide_text = []
        for key, value in style_guide.items():
            guide_text.append(f"- {key}: {value}")
        return "\n".join(guide_text)
