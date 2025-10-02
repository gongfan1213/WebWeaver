"""
规划智能体实现

负责动态大纲生成、优化和搜索策略制定。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json
import re
from datetime import datetime

from .base_agent import BaseAgent
from .memory_bank import MemoryBank, Evidence

@dataclass
class Section:
    """章节类"""
    id: str
    title: str
    description: str
    level: int
    parent_id: Optional[str] = None
    children: List['Section'] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    content: str = ""
    is_complete: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "parent_id": self.parent_id,
            "children": [child.to_dict() for child in self.children],
            "requirements": self.requirements,
            "citations": self.citations,
            "content": self.content,
            "is_complete": self.is_complete
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Section':
        """从字典创建实例"""
        section = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            level=data["level"],
            parent_id=data.get("parent_id"),
            requirements=data.get("requirements", []),
            citations=data.get("citations", []),
            content=data.get("content", ""),
            is_complete=data.get("is_complete", False)
        )
        
        # 递归创建子章节
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            child.parent_id = section.id
            section.children.append(child)
        
        return section

@dataclass
class Outline:
    """大纲类"""
    title: str
    description: str
    sections: List[Section] = field(default_factory=list)
    citations: Dict[str, List[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def add_section(self, section: Section):
        """添加章节"""
        self.sections.append(section)
        self.updated_at = datetime.now()
        self.version += 1
    
    def get_section_by_id(self, section_id: str) -> Optional[Section]:
        """根据ID获取章节"""
        for section in self.sections:
            if section.id == section_id:
                return section
            # 递归搜索子章节
            found = self._find_section_recursive(section, section_id)
            if found:
                return found
        return None
    
    def _find_section_recursive(self, section: Section, section_id: str) -> Optional[Section]:
        """递归查找章节"""
        for child in section.children:
            if child.id == section_id:
                return child
            found = self._find_section_recursive(child, section_id)
            if found:
                return found
        return None
    
    def get_all_sections(self) -> List[Section]:
        """获取所有章节（包括子章节）"""
        all_sections = []
        for section in self.sections:
            all_sections.append(section)
            all_sections.extend(self._get_sections_recursive(section))
        return all_sections
    
    def _get_sections_recursive(self, section: Section) -> List[Section]:
        """递归获取子章节"""
        sections = []
        for child in section.children:
            sections.append(child)
            sections.extend(self._get_sections_recursive(child))
        return sections
    
    def calculate_completeness(self) -> float:
        """计算大纲完整性"""
        all_sections = self.get_all_sections()
        if not all_sections:
            return 0.0
        
        completed_sections = sum(1 for section in all_sections if section.is_complete)
        return completed_sections / len(all_sections)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "description": self.description,
            "sections": [section.to_dict() for section in self.sections],
            "citations": self.citations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Outline':
        """从字典创建实例"""
        outline = cls(
            title=data["title"],
            description=data["description"],
            citations=data.get("citations", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            version=data.get("version", 1)
        )
        
        # 创建章节
        for section_data in data.get("sections", []):
            section = Section.from_dict(section_data)
            outline.sections.append(section)
        
        return outline

class PlannerAgent(BaseAgent):
    """规划智能体"""
    
    def __init__(self, config: Dict[str, Any], memory_bank: MemoryBank):
        super().__init__("Planner", config)
        self.memory_bank = memory_bank
        self.current_outline: Optional[Outline] = None
        self.search_history: List[Dict[str, Any]] = []
        self.max_iterations = config.get("max_iterations", 5)
        self.completeness_threshold = config.get("completeness_threshold", 0.8)
        self.outline_optimization_threshold = config.get("outline_optimization_threshold", 0.7)
    
    def generate_initial_outline(self, query: str) -> Outline:
        """生成初始大纲"""
        self.logger.info(f"Generating initial outline for query: {query}")
        
        prompt = self._get_initial_outline_prompt(query)
        response = self._call_llm(prompt)
        outline_data = self._parse_outline_response(response)
        
        outline = Outline(
            title=outline_data.get("title", query),
            description=outline_data.get("description", ""),
            sections=self._create_sections_from_data(outline_data.get("sections", []))
        )
        
        self.current_outline = outline
        self.update_state(current_task=f"Generated initial outline: {outline.title}")
        
        return outline
    
    def optimize_outline(self, new_evidence: List[Evidence]) -> Outline:
        """优化大纲"""
        if not self.current_outline:
            raise ValueError("No current outline to optimize")
        
        self.logger.info(f"Optimizing outline with {len(new_evidence)} new evidence items")
        
        prompt = self._get_outline_optimization_prompt(self.current_outline, new_evidence)
        response = self._call_llm(prompt)
        optimization_data = self._parse_outline_optimization_response(response)
        
        # 应用优化
        optimized_outline = self._apply_outline_optimization(optimization_data)
        self.current_outline = optimized_outline
        
        self.update_state(
            current_task=f"Optimized outline: {optimized_outline.title}",
            iteration_count=self.state.iteration_count + 1
        )
        
        return optimized_outline
    
    def plan_search_strategy(self) -> List[Dict[str, Any]]:
        """制定搜索策略"""
        if not self.current_outline:
            return []
        
        self.logger.info("Planning search strategy")
        
        prompt = self._get_search_strategy_prompt(self.current_outline)
        response = self._call_llm(prompt)
        strategy_data = self._parse_search_strategy_response(response)
        
        # 记录搜索策略
        self.search_history.append({
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy_data,
            "outline_version": self.current_outline.version
        })
        
        return strategy_data
    
    def should_continue_research(self) -> bool:
        """判断是否继续研究"""
        # 检查迭代次数限制
        if self.state.iteration_count >= self.max_iterations:
            self.logger.info("Reached maximum iterations")
            return False
        
        # 检查大纲完整性
        if not self.current_outline:
            return True
        
        completeness = self.current_outline.calculate_completeness()
        if completeness >= self.completeness_threshold:
            self.logger.info(f"Outline completeness reached: {completeness:.2f}")
            return False
        
        # 检查是否有新的搜索策略
        if not self.search_history:
            return True
        
        last_strategy = self.search_history[-1]["strategy"]
        if not last_strategy or len(last_strategy) == 0:
            self.logger.info("No more search strategies available")
            return False
        
        return True
    
    def get_current_outline(self) -> Optional[Outline]:
        """获取当前大纲"""
        return self.current_outline
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """获取搜索历史"""
        return self.search_history
    
    def _get_initial_outline_prompt(self, query: str) -> str:
        """获取初始大纲生成提示词"""
        return f"""
你是一个专业的研究规划者。请根据以下查询生成一个详细的研究大纲：

查询: {query}

请生成一个结构化的研究大纲，包括：
1. 主要章节和子章节
2. 每个章节的核心内容描述
3. 章节之间的逻辑关系
4. 预期的研究深度和广度

请以JSON格式输出大纲结构，格式如下：
{{
    "title": "研究标题",
    "description": "研究描述",
    "sections": [
        {{
            "id": "section_1",
            "title": "章节标题",
            "description": "章节描述",
            "level": 1,
            "requirements": ["要求1", "要求2"],
            "children": [
                {{
                    "id": "section_1_1",
                    "title": "子章节标题",
                    "description": "子章节描述",
                    "level": 2,
                    "requirements": ["子要求1", "子要求2"]
                }}
            ]
        }}
    ]
}}
"""
    
    def _get_outline_optimization_prompt(self, outline: Outline, new_evidence: List[Evidence]) -> str:
        """获取大纲优化提示词"""
        evidence_summaries = [f"- {ev.summary}" for ev in new_evidence]
        
        return f"""
基于新获取的证据，请优化当前的研究大纲：

当前大纲:
{json.dumps(outline.to_dict(), ensure_ascii=False, indent=2)}

新证据:
{chr(10).join(evidence_summaries)}

请考虑：
1. 新证据如何补充现有大纲
2. 是否需要添加新的章节或子章节
3. 是否需要调整章节顺序或重点
4. 如何确保大纲的完整性和逻辑性

请输出优化后的大纲，格式与初始大纲相同。
"""
    
    def _get_search_strategy_prompt(self, outline: Outline) -> str:
        """获取搜索策略提示词"""
        return f"""
基于当前研究大纲，请制定详细的搜索策略：

当前大纲:
{json.dumps(outline.to_dict(), ensure_ascii=False, indent=2)}

请为每个需要更多信息的章节制定搜索策略，包括：
1. 具体的搜索关键词
2. 搜索的优先级
3. 预期的信息类型
4. 搜索的深度和广度

请以JSON格式输出搜索策略，格式如下：
[
    {{
        "section_id": "section_1",
        "priority": 1,
        "keywords": ["关键词1", "关键词2"],
        "search_type": "web",
        "expected_info": "预期信息类型",
        "depth": "high"
    }}
]
"""
    
    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """解析大纲响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                self.logger.error("Failed to parse outline response")
                return {"title": "解析失败", "sections": []}
    
    def _parse_outline_optimization_response(self, response: str) -> Dict[str, Any]:
        """解析大纲优化响应"""
        return self._parse_outline_response(response)
    
    def _parse_search_strategy_response(self, response: str) -> List[Dict[str, Any]]:
        """解析搜索策略响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                self.logger.error("Failed to parse search strategy response")
                return []
    
    def _create_sections_from_data(self, sections_data: List[Dict[str, Any]]) -> List[Section]:
        """从数据创建章节"""
        sections = []
        for section_data in sections_data:
            section = Section(
                id=section_data.get("id", f"section_{len(sections) + 1}"),
                title=section_data.get("title", ""),
                description=section_data.get("description", ""),
                level=section_data.get("level", 1),
                requirements=section_data.get("requirements", [])
            )
            
            # 递归创建子章节
            for child_data in section_data.get("children", []):
                child = self._create_section_from_data(child_data, section.id)
                section.children.append(child)
            
            sections.append(section)
        
        return sections
    
    def _create_section_from_data(self, section_data: Dict[str, Any], parent_id: str) -> Section:
        """从数据创建单个章节"""
        section = Section(
            id=section_data.get("id", f"section_{parent_id}_{len(section_data)}"),
            title=section_data.get("title", ""),
            description=section_data.get("description", ""),
            level=section_data.get("level", 2),
            parent_id=parent_id,
            requirements=section_data.get("requirements", [])
        )
        
        # 递归创建子章节
        for child_data in section_data.get("children", []):
            child = self._create_section_from_data(child_data, section.id)
            section.children.append(child)
        
        return section
    
    def _apply_outline_optimization(self, optimization_data: Dict[str, Any]) -> Outline:
        """应用大纲优化"""
        if not self.current_outline:
            raise ValueError("No current outline to optimize")
        
        # 创建优化后的大纲
        optimized_outline = Outline(
            title=optimization_data.get("title", self.current_outline.title),
            description=optimization_data.get("description", self.current_outline.description),
            sections=self._create_sections_from_data(optimization_data.get("sections", [])),
            citations=self.current_outline.citations,
            created_at=self.current_outline.created_at,
            version=self.current_outline.version + 1
        )
        
        return optimized_outline
