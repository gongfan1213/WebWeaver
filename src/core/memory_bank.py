"""
记忆库实现

负责存储、索引和检索研究过程中收集的证据。
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import hashlib
import json
import time
from collections import defaultdict
from datetime import datetime
import logging

@dataclass
class Evidence:
    """证据类"""
    id: str = ""
    content: str = ""
    summary: str = ""
    source: str = ""
    url: str = ""
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
        if not self.summary and self.content:
            self.summary = self._generate_summary()
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        content_hash = hashlib.md5(self.content.encode('utf-8')).hexdigest()
        timestamp = str(int(time.time()))
        return f"evidence_{content_hash[:8]}_{timestamp[-6:]}"
    
    def _generate_summary(self) -> str:
        """生成内容摘要"""
        if len(self.content) <= 200:
            return self.content
        return self.content[:200] + "..."
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "content": self.content,
            "summary": self.summary,
            "source": self.source,
            "url": self.url,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evidence':
        """从字典创建实例"""
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            summary=data.get("summary", ""),
            source=data.get("source", ""),
            url=data.get("url", ""),
            relevance_score=data.get("relevance_score", 0.0),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )

class MemoryBank:
    """记忆库"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.evidence_store: Dict[str, Evidence] = {}
        self.content_index: Dict[str, List[str]] = defaultdict(list)
        self.source_index: Dict[str, List[str]] = defaultdict(list)
        self.topic_index: Dict[str, List[str]] = defaultdict(list)
        self.url_index: Dict[str, str] = {}  # URL -> Evidence ID mapping
        self.logger = logging.getLogger("webweaver.memory_bank")
        self.max_evidence_count = config.get("max_evidence_count", 1000)
        self.similarity_threshold = config.get("similarity_threshold", 0.7)
    
    def add_evidence(self, evidence: Evidence) -> str:
        """添加证据"""
        # 检查是否已存在相同内容
        if self._is_duplicate(evidence):
            self.logger.warning(f"Duplicate evidence detected: {evidence.id}")
            return evidence.id
        
        # 检查存储限制
        if len(self.evidence_store) >= self.max_evidence_count:
            self._remove_oldest_evidence()
        
        # 存储证据
        self.evidence_store[evidence.id] = evidence
        
        # 更新索引
        self._update_content_index(evidence)
        self._update_source_index(evidence)
        self._update_topic_index(evidence)
        self._update_url_index(evidence)
        
        self.logger.info(f"Added evidence: {evidence.id}")
        return evidence.id
    
    def search_evidence(self, query: str, limit: int = 10, 
                       source_filter: Optional[str] = None,
                       min_relevance: float = 0.0) -> List[Evidence]:
        """搜索证据"""
        results = []
        
        # 基于内容相似度搜索
        content_matches = self._search_by_content(query)
        
        # 基于来源过滤
        if source_filter:
            content_matches = [ev_id for ev_id in content_matches 
                             if self.evidence_store[ev_id].source == source_filter]
        
        # 计算相关性分数并排序
        for ev_id in content_matches:
            evidence = self.evidence_store[ev_id]
            if evidence.relevance_score >= min_relevance:
                results.append(evidence)
        
        # 按相关性分数排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:limit]
    
    def get_evidence_by_id(self, evidence_id: str) -> Optional[Evidence]:
        """根据ID获取证据"""
        return self.evidence_store.get(evidence_id)
    
    def get_evidence_by_citation(self, citation: str) -> Optional[Evidence]:
        """根据引用获取证据"""
        # 支持多种引用格式
        if citation.startswith("evidence_"):
            return self.get_evidence_by_id(citation)
        
        # 尝试从URL获取
        if citation in self.url_index:
            return self.get_evidence_by_id(self.url_index[citation])
        
        return None
    
    def get_evidence_by_url(self, url: str) -> Optional[Evidence]:
        """根据URL获取证据"""
        if url in self.url_index:
            return self.get_evidence_by_id(self.url_index[url])
        return None
    
    def get_all_evidence(self) -> List[Evidence]:
        """获取所有证据"""
        return list(self.evidence_store.values())
    
    def get_evidence_count(self) -> int:
        """获取证据数量"""
        return len(self.evidence_store)
    
    def get_sources(self) -> List[str]:
        """获取所有来源"""
        return list(self.source_index.keys())
    
    def get_topics(self) -> List[str]:
        """获取所有主题"""
        return list(self.topic_index.keys())
    
    def clear(self):
        """清空记忆库"""
        self.evidence_store.clear()
        self.content_index.clear()
        self.source_index.clear()
        self.topic_index.clear()
        self.url_index.clear()
        self.logger.info("Memory bank cleared")
    
    def export_to_dict(self) -> Dict[str, Any]:
        """导出为字典格式"""
        return {
            "evidence_store": {k: v.to_dict() for k, v in self.evidence_store.items()},
            "content_index": dict(self.content_index),
            "source_index": dict(self.source_index),
            "topic_index": dict(self.topic_index),
            "url_index": self.url_index,
            "config": self.config
        }
    
    def import_from_dict(self, data: Dict[str, Any]):
        """从字典导入"""
        self.clear()
        
        # 导入证据
        for ev_id, ev_data in data.get("evidence_store", {}).items():
            evidence = Evidence.from_dict(ev_data)
            self.evidence_store[ev_id] = evidence
        
        # 导入索引
        self.content_index = defaultdict(list, data.get("content_index", {}))
        self.source_index = defaultdict(list, data.get("source_index", {}))
        self.topic_index = defaultdict(list, data.get("topic_index", {}))
        self.url_index = data.get("url_index", {})
        
        self.logger.info(f"Imported {len(self.evidence_store)} evidence items")
    
    def _is_duplicate(self, evidence: Evidence) -> bool:
        """检查是否为重复证据"""
        # 基于URL检查
        if evidence.url and evidence.url in self.url_index:
            return True
        
        # 基于内容相似度检查
        for existing_evidence in self.evidence_store.values():
            if self._calculate_similarity(evidence.content, existing_evidence.content) > self.similarity_threshold:
                return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单的基于词汇重叠的相似度计算
        # 实际实现中可以使用更复杂的NLP技术
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _update_content_index(self, evidence: Evidence):
        """更新内容索引"""
        # 基于关键词建立索引
        keywords = self._extract_keywords(evidence.content)
        for keyword in keywords:
            self.content_index[keyword].append(evidence.id)
    
    def _update_source_index(self, evidence: Evidence):
        """更新来源索引"""
        if evidence.source:
            self.source_index[evidence.source].append(evidence.id)
    
    def _update_topic_index(self, evidence: Evidence):
        """更新主题索引"""
        # 基于元数据中的主题信息建立索引
        topics = evidence.metadata.get("topics", [])
        for topic in topics:
            self.topic_index[topic].append(evidence.id)
    
    def _update_url_index(self, evidence: Evidence):
        """更新URL索引"""
        if evidence.url:
            self.url_index[evidence.url] = evidence.id
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        # 实际实现中可以使用更复杂的NLP技术
        import re
        
        # 移除标点符号，转换为小写
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # 过滤停用词和短词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # 返回前10个最频繁的关键词
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _search_by_content(self, query: str) -> List[str]:
        """基于内容搜索"""
        query_keywords = self._extract_keywords(query)
        evidence_scores = defaultdict(float)
        
        for keyword in query_keywords:
            if keyword in self.content_index:
                for ev_id in self.content_index[keyword]:
                    evidence_scores[ev_id] += 1.0
        
        # 按分数排序
        sorted_evidence = sorted(evidence_scores.items(), key=lambda x: x[1], reverse=True)
        return [ev_id for ev_id, score in sorted_evidence]
    
    def _remove_oldest_evidence(self):
        """移除最旧的证据"""
        if not self.evidence_store:
            return
        
        # 找到最旧的证据
        oldest_id = min(self.evidence_store.keys(), 
                       key=lambda x: self.evidence_store[x].timestamp)
        
        # 移除证据
        evidence = self.evidence_store[oldest_id]
        del self.evidence_store[oldest_id]
        
        # 更新索引
        self._remove_from_indexes(evidence)
        
        self.logger.info(f"Removed oldest evidence: {oldest_id}")
    
    def _remove_from_indexes(self, evidence: Evidence):
        """从所有索引中移除证据"""
        # 从内容索引移除
        for keyword, ev_ids in self.content_index.items():
            if evidence.id in ev_ids:
                ev_ids.remove(evidence.id)
        
        # 从来源索引移除
        if evidence.source in self.source_index:
            if evidence.id in self.source_index[evidence.source]:
                self.source_index[evidence.source].remove(evidence.id)
        
        # 从主题索引移除
        for topic, ev_ids in self.topic_index.items():
            if evidence.id in ev_ids:
                ev_ids.remove(evidence.id)
        
        # 从URL索引移除
        if evidence.url in self.url_index:
            del self.url_index[evidence.url]
