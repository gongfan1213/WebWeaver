"""
写作智能体实现

负责基于大纲执行分层检索和逐段写作。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re
import json
from datetime import datetime

from .base_agent import BaseAgent
from .memory_bank import MemoryBank, Evidence
from .planner_agent import Outline, Section

@dataclass
class WrittenSection:
    """已写作章节"""
    section_id: str
    title: str
    content: str
    citations: List[str] = field(default_factory=list)
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0
    
    def __post_init__(self):
        self.word_count = len(self.content.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "section_id": self.section_id,
            "title": self.title,
            "content": self.content,
            "citations": self.citations,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat(),
            "quality_score": self.quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WrittenSection':
        """从字典创建实例"""
        return cls(
            section_id=data["section_id"],
            title=data["title"],
            content=data["content"],
            citations=data.get("citations", []),
            word_count=data.get("word_count", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            quality_score=data.get("quality_score", 0.0)
        )

@dataclass
class Report:
    """报告类"""
    title: str
    content: str
    sections: List[WrittenSection] = field(default_factory=list)
    total_word_count: int = 0
    total_citations: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0
    
    def add_section(self, section: WrittenSection):
        """添加章节"""
        self.sections.append(section)
        self.total_word_count += section.word_count
        self.total_citations += len(section.citations)
        self._update_quality_score()
    
    def _update_quality_score(self):
        """更新质量分数"""
        if not self.sections:
            self.quality_score = 0.0
            return
        
        # 计算平均质量分数
        total_score = sum(section.quality_score for section in self.sections)
        self.quality_score = total_score / len(self.sections)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "content": self.content,
            "sections": [section.to_dict() for section in self.sections],
            "total_word_count": self.total_word_count,
            "total_citations": self.total_citations,
            "created_at": self.created_at.isoformat(),
            "quality_score": self.quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """从字典创建实例"""
        report = cls(
            title=data["title"],
            content=data["content"],
            total_word_count=data.get("total_word_count", 0),
            total_citations=data.get("total_citations", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            quality_score=data.get("quality_score", 0.0)
        )
        
        # 创建章节
        for section_data in data.get("sections", []):
            section = WrittenSection.from_dict(section_data)
            report.sections.append(section)
        
        return report

class WriterAgent(BaseAgent):
    """写作智能体"""
    
    def __init__(self, config: Dict[str, Any], memory_bank: MemoryBank):
        super().__init__("Writer", config)
        self.memory_bank = memory_bank
        self.written_sections: List[WrittenSection] = []
        self.current_report: Optional[Report] = None
        self.max_section_length = config.get("max_section_length", 2000)
        self.citation_validation = config.get("citation_validation", True)
        self.quality_check = config.get("quality_check", True)
    
    def write_report(self, outline: Outline) -> Report:
        """基于大纲写作完整报告"""
        self.logger.info(f"Starting to write report based on outline: {outline.title}")
        
        # 创建报告
        report = Report(title=outline.title)
        self.current_report = report
        
        # 按顺序写作所有章节
        all_sections = outline.get_all_sections()
        for section in all_sections:
            if not section.is_complete:
                written_section = self.write_section(section)
                if written_section:
                    report.add_section(written_section)
        
        # 生成完整内容
        report.content = self._generate_full_content(report.sections)
        
        self.logger.info(f"Completed report with {len(report.sections)} sections, {report.total_word_count} words")
        
        return report
    
    def write_section(self, section: Section) -> Optional[WrittenSection]:
        """写作单个章节"""
        self.logger.info(f"Writing section: {section.title}")
        
        # 检索相关证据
        evidence = self.retrieve_evidence_for_section(section)
        
        if not evidence:
            self.logger.warning(f"No evidence found for section: {section.title}")
            # 即使没有证据也尝试写作
            evidence = []
        
        # 生成章节内容
        content = self._generate_section_content(section, evidence)
        
        if not content:
            self.logger.error(f"Failed to generate content for section: {section.title}")
            return None
        
        # 提取引用
        citations = self._extract_citations(content)
        
        # 验证引用
        if self.citation_validation:
            citations = self._validate_citations(citations, evidence)
        
        # 创建已写作章节
        written_section = WrittenSection(
            section_id=section.id,
            title=section.title,
            content=content,
            citations=citations
        )
        
        # 质量检查
        if self.quality_check:
            written_section.quality_score = self._assess_section_quality(written_section, evidence)
        
        self.written_sections.append(written_section)
        
        # 更新章节状态
        section.is_complete = True
        section.content = content
        section.citations = citations
        
        self.logger.info(f"Completed section: {section.title} ({written_section.word_count} words)")
        
        return written_section
    
    def retrieve_evidence_for_section(self, section: Section) -> List[Evidence]:
        """为章节检索证据"""
        # 构建搜索查询
        search_query = self._build_search_query(section)
        
        # 从记忆库搜索证据
        evidence = self.memory_bank.search_evidence(
            query=search_query,
            limit=10,
            min_relevance=0.3
        )
        
        self.logger.info(f"Retrieved {len(evidence)} evidence items for section: {section.title}")
        
        return evidence
    
    def integrate_citations(self, content: str, evidence: List[Evidence]) -> str:
        """整合引用到内容中"""
        # 为每个证据创建引用标记
        citation_map = {}
        for i, ev in enumerate(evidence):
            citation_id = f"cite_{i+1}"
            citation_map[citation_id] = ev.id
        
        # 在内容中插入引用
        # 这里可以实现更复杂的引用插入逻辑
        return content
    
    def validate_citations(self, content: str) -> bool:
        """验证内容中的引用"""
        # 提取所有引用
        citations = self._extract_citations(content)
        
        # 验证每个引用
        for citation in citations:
            evidence = self.memory_bank.get_evidence_by_citation(citation)
            if not evidence:
                self.logger.warning(f"Invalid citation: {citation}")
                return False
        
        return True
    
    def get_written_sections(self) -> List[WrittenSection]:
        """获取已写作章节"""
        return self.written_sections
    
    def get_current_report(self) -> Optional[Report]:
        """获取当前报告"""
        return self.current_report
    
    def _build_search_query(self, section: Section) -> str:
        """构建搜索查询"""
        # 基于章节标题和描述构建查询
        query_parts = [section.title]
        
        if section.description:
            query_parts.append(section.description)
        
        # 添加要求作为查询的一部分
        if section.requirements:
            query_parts.extend(section.requirements)
        
        return " ".join(query_parts)
    
    def _generate_section_content(self, section: Section, evidence: List[Evidence]) -> str:
        """生成章节内容"""
        prompt = self._get_section_writing_prompt(section, evidence)
        response = self._call_llm(prompt)
        
        # 清理和格式化内容
        content = self._clean_content(response)
        
        # 检查长度限制
        if len(content.split()) > self.max_section_length:
            content = self._truncate_content(content, self.max_section_length)
        
        return content
    
    def _get_section_writing_prompt(self, section: Section, evidence: List[Evidence]) -> str:
        """获取章节写作提示词"""
        evidence_text = "\n\n".join([
            f"证据 {i+1} (ID: {ev.id}):\n{ev.content[:500]}..."
            for i, ev in enumerate(evidence)
        ])
        
        return f"""
你是一个专业的研究报告写作者。请基于提供的证据写作以下章节：

章节信息:
- 标题: {section.title}
- 描述: {section.description}
- 要求: {', '.join(section.requirements) if section.requirements else '无特殊要求'}

相关证据:
{evidence_text}

写作要求:
1. 内容要准确、客观、有逻辑性
2. 必须基于提供的证据进行写作
3. 每个重要观点都要有相应的引用，格式为 [证据ID]
4. 语言要专业、清晰、易懂
5. 确保内容的连贯性和完整性
6. 字数控制在合理范围内

请输出章节内容。
"""
    
    def _extract_citations(self, content: str) -> List[str]:
        """提取内容中的引用"""
        # 查找 [evidence_xxx] 格式的引用
        citation_pattern = r'\[evidence_[a-zA-Z0-9_]+\]'
        citations = re.findall(citation_pattern, content)
        
        # 移除方括号
        citations = [citation[1:-1] for citation in citations]
        
        return citations
    
    def _validate_citations(self, citations: List[str], evidence: List[Evidence]) -> List[str]:
        """验证引用"""
        valid_citations = []
        evidence_ids = {ev.id for ev in evidence}
        
        for citation in citations:
            if citation in evidence_ids:
                valid_citations.append(citation)
            else:
                self.logger.warning(f"Invalid citation: {citation}")
        
        return valid_citations
    
    def _assess_section_quality(self, section: WrittenSection, evidence: List[Evidence]) -> float:
        """评估章节质量"""
        quality_factors = []
        
        # 内容长度合理性
        if 100 <= section.word_count <= self.max_section_length:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.5)
        
        # 引用覆盖率
        if evidence:
            citation_coverage = len(section.citations) / len(evidence)
            quality_factors.append(min(citation_coverage, 1.0))
        else:
            quality_factors.append(0.5)
        
        # 内容完整性（简单检查）
        if section.content and len(section.content.strip()) > 50:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.0)
        
        # 计算平均质量分数
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    def _clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 移除多余的换行
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 确保段落之间有适当的间距
        content = content.strip()
        
        return content
    
    def _truncate_content(self, content: str, max_words: int) -> str:
        """截断内容到指定字数"""
        words = content.split()
        if len(words) <= max_words:
            return content
        
        # 截断到最大字数
        truncated_words = words[:max_words]
        
        # 确保句子完整性
        truncated_content = ' '.join(truncated_words)
        
        # 找到最后一个句号
        last_period = truncated_content.rfind('.')
        if last_period > 0:
            truncated_content = truncated_content[:last_period + 1]
        
        return truncated_content
    
    def _generate_full_content(self, sections: List[WrittenSection]) -> str:
        """生成完整内容"""
        if not sections:
            return ""
        
        # 按章节顺序组织内容
        content_parts = []
        
        for section in sections:
            content_parts.append(f"## {section.title}")
            content_parts.append(section.content)
            content_parts.append("")  # 添加空行
        
        return "\n".join(content_parts)
