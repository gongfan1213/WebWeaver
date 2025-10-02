"""
引用管理器

负责引用的生成、验证和管理。
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class Citation:
    """引用类"""
    id: str
    text: str
    source: str
    url: str
    page_number: Optional[int] = None
    author: Optional[str] = None
    year: Optional[int] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "text": self.text,
            "source": self.source,
            "url": self.url,
            "page_number": self.page_number,
            "author": self.author,
            "year": self.year,
            "title": self.title,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Citation':
        """从字典创建实例"""
        return cls(
            id=data["id"],
            text=data["text"],
            source=data["source"],
            url=data["url"],
            page_number=data.get("page_number"),
            author=data.get("author"),
            year=data.get("year"),
            title=data.get("title"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )

class CitationManager:
    """引用管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("webweaver.citation_manager")
        self.citations: Dict[str, Citation] = {}
        self.citation_counter = 0
        self.citation_formats = {
            'apa': self._format_apa,
            'mla': self._format_mla,
            'chicago': self._format_chicago,
            'ieee': self._format_ieee
        }
    
    def create_citation(self, text: str, source: str, url: str, **kwargs) -> Citation:
        """创建引用"""
        citation_id = self._generate_citation_id()
        
        citation = Citation(
            id=citation_id,
            text=text,
            source=source,
            url=url,
            page_number=kwargs.get('page_number'),
            author=kwargs.get('author'),
            year=kwargs.get('year'),
            title=kwargs.get('title'),
            metadata=kwargs.get('metadata', {})
        )
        
        self.citations[citation_id] = citation
        self.citation_counter += 1
        
        self.logger.info(f"Created citation: {citation_id}")
        return citation
    
    def get_citation(self, citation_id: str) -> Optional[Citation]:
        """获取引用"""
        return self.citations.get(citation_id)
    
    def get_all_citations(self) -> List[Citation]:
        """获取所有引用"""
        return list(self.citations.values())
    
    def format_citation(self, citation_id: str, format_style: str = 'apa') -> str:
        """格式化引用"""
        citation = self.get_citation(citation_id)
        if not citation:
            return f"[Citation not found: {citation_id}]"
        
        formatter = self.citation_formats.get(format_style.lower())
        if not formatter:
            self.logger.warning(f"Unknown citation format: {format_style}")
            return f"[{citation.source}]"
        
        return formatter(citation)
    
    def format_citations_in_text(self, text: str, format_style: str = 'apa') -> str:
        """格式化文本中的引用"""
        # 查找所有引用标记
        citation_pattern = r'\[citation_([a-zA-Z0-9_]+)\]'
        matches = re.findall(citation_pattern, text)
        
        formatted_text = text
        for citation_id in matches:
            citation = self.get_citation(citation_id)
            if citation:
                formatted_citation = self.format_citation(citation_id, format_style)
                # 替换引用标记
                formatted_text = formatted_text.replace(
                    f'[citation_{citation_id}]',
                    f'({formatted_citation})'
                )
        
        return formatted_text
    
    def extract_citations_from_text(self, text: str) -> List[str]:
        """从文本中提取引用ID"""
        citation_pattern = r'\[citation_([a-zA-Z0-9_]+)\]'
        matches = re.findall(citation_pattern, text)
        return matches
    
    def validate_citations_in_text(self, text: str) -> Dict[str, Any]:
        """验证文本中的引用"""
        extracted_citations = self.extract_citations_from_text(text)
        
        valid_citations = []
        invalid_citations = []
        
        for citation_id in extracted_citations:
            if citation_id in self.citations:
                valid_citations.append(citation_id)
            else:
                invalid_citations.append(citation_id)
        
        return {
            'total_citations': len(extracted_citations),
            'valid_citations': valid_citations,
            'invalid_citations': invalid_citations,
            'validity_ratio': len(valid_citations) / len(extracted_citations) if extracted_citations else 0
        }
    
    def generate_reference_list(self, format_style: str = 'apa') -> List[str]:
        """生成参考文献列表"""
        references = []
        for citation in self.citations.values():
            formatted = self.format_citation(citation.id, format_style)
            references.append(formatted)
        
        return references
    
    def _generate_citation_id(self) -> str:
        """生成引用ID"""
        self.citation_counter += 1
        return f"citation_{self.citation_counter:04d}"
    
    def _format_apa(self, citation: Citation) -> str:
        """APA格式引用"""
        parts = []
        
        if citation.author:
            parts.append(citation.author)
        
        if citation.year:
            parts.append(f"({citation.year})")
        
        if citation.title:
            parts.append(citation.title)
        
        if citation.source:
            parts.append(citation.source)
        
        if citation.url:
            parts.append(f"Retrieved from {citation.url}")
        
        return ". ".join(parts) if parts else citation.source
    
    def _format_mla(self, citation: Citation) -> str:
        """MLA格式引用"""
        parts = []
        
        if citation.author:
            parts.append(citation.author)
        
        if citation.title:
            parts.append(f'"{citation.title}"')
        
        if citation.source:
            parts.append(citation.source)
        
        if citation.year:
            parts.append(str(citation.year))
        
        if citation.url:
            parts.append(f"Web. {citation.url}")
        
        return ". ".join(parts) if parts else citation.source
    
    def _format_chicago(self, citation: Citation) -> str:
        """Chicago格式引用"""
        parts = []
        
        if citation.author:
            parts.append(citation.author)
        
        if citation.title:
            parts.append(f'"{citation.title}"')
        
        if citation.source:
            parts.append(citation.source)
        
        if citation.year:
            parts.append(str(citation.year))
        
        if citation.url:
            parts.append(f"Accessed {citation.url}")
        
        return ". ".join(parts) if parts else citation.source
    
    def _format_ieee(self, citation: Citation) -> str:
        """IEEE格式引用"""
        parts = []
        
        if citation.author:
            parts.append(citation.author)
        
        if citation.title:
            parts.append(f'"{citation.title}"')
        
        if citation.source:
            parts.append(citation.source)
        
        if citation.year:
            parts.append(str(citation.year))
        
        if citation.url:
            parts.append(f"[Online]. Available: {citation.url}")
        
        return ". ".join(parts) if parts else citation.source
    
    def export_citations(self) -> Dict[str, Any]:
        """导出引用"""
        return {
            "citations": {k: v.to_dict() for k, v in self.citations.items()},
            "total_count": len(self.citations),
            "exported_at": datetime.now().isoformat()
        }
    
    def import_citations(self, data: Dict[str, Any]):
        """导入引用"""
        citations_data = data.get("citations", {})
        
        for citation_id, citation_data in citations_data.items():
            citation = Citation.from_dict(citation_data)
            self.citations[citation_id] = citation
        
        self.logger.info(f"Imported {len(citations_data)} citations")
    
    def clear_citations(self):
        """清空所有引用"""
        self.citations.clear()
        self.citation_counter = 0
        self.logger.info("Cleared all citations")
    
    def get_citation_statistics(self) -> Dict[str, Any]:
        """获取引用统计信息"""
        if not self.citations:
            return {
                "total_citations": 0,
                "sources": 0,
                "years": [],
                "authors": []
            }
        
        sources = set()
        years = set()
        authors = set()
        
        for citation in self.citations.values():
            if citation.source:
                sources.add(citation.source)
            if citation.year:
                years.add(citation.year)
            if citation.author:
                authors.add(citation.author)
        
        return {
            "total_citations": len(self.citations),
            "sources": len(sources),
            "years": sorted(list(years)),
            "authors": sorted(list(authors))
        }
