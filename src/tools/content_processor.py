"""
内容处理器

负责文本内容的清理、分析和处理。
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
from collections import Counter

@dataclass
class ProcessedContent:
    """处理后的内容"""
    original_text: str
    cleaned_text: str
    word_count: int
    sentence_count: int
    paragraph_count: int
    keywords: List[str]
    summary: str
    language: str
    readability_score: float
    metadata: Dict[str, Any]

class ContentProcessor:
    """内容处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("webweaver.content_processor")
        
        # 停用词列表（简化版）
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours',
            'hers', 'ours', 'theirs'
        }
    
    def process(self, text: str) -> ProcessedContent:
        """处理文本内容"""
        if not text:
            return ProcessedContent(
                original_text="",
                cleaned_text="",
                word_count=0,
                sentence_count=0,
                paragraph_count=0,
                keywords=[],
                summary="",
                language="unknown",
                readability_score=0.0,
                metadata={}
            )
        
        # 清理文本
        cleaned_text = self._clean_text(text)
        
        # 分析文本
        word_count = self._count_words(cleaned_text)
        sentence_count = self._count_sentences(cleaned_text)
        paragraph_count = self._count_paragraphs(cleaned_text)
        
        # 提取关键词
        keywords = self._extract_keywords(cleaned_text)
        
        # 生成摘要
        summary = self._generate_summary(cleaned_text)
        
        # 检测语言
        language = self._detect_language(cleaned_text)
        
        # 计算可读性分数
        readability_score = self._calculate_readability(cleaned_text)
        
        # 生成元数据
        metadata = self._generate_metadata(text, cleaned_text)
        
        return ProcessedContent(
            original_text=text,
            cleaned_text=cleaned_text,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            keywords=keywords,
            summary=summary,
            language=language,
            readability_score=readability_score,
            metadata=metadata
        )
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除多余的换行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    def _count_words(self, text: str) -> int:
        """计算词数"""
        words = text.split()
        return len(words)
    
    def _count_sentences(self, text: str) -> int:
        """计算句子数"""
        # 简单的句子分割
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    def _count_paragraphs(self, text: str) -> int:
        """计算段落数"""
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return len(paragraphs)
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        # 转换为小写并分割
        words = text.lower().split()
        
        # 移除停用词和短词
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        ]
        
        # 计算词频
        word_counts = Counter(filtered_words)
        
        # 返回最频繁的词
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成摘要"""
        if len(text) <= max_length:
            return text
        
        # 按句子分割
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:max_length] + "..."
        
        # 选择前几个句子直到达到最大长度
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip()
    
    def _detect_language(self, text: str) -> str:
        """检测语言（简化版）"""
        # 简单的语言检测，基于常见词汇
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        
        if chinese_chars:
            return 'zh'
        elif any(word in text.lower() for word in english_words):
            return 'en'
        else:
            return 'unknown'
    
    def _calculate_readability(self, text: str) -> float:
        """计算可读性分数（简化版Flesch Reading Ease）"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return 0.0
        
        # 计算平均句子长度
        avg_sentence_length = len(words) / len(sentences)
        
        # 计算平均词长度
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # 简化的可读性公式
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length / 100)
        
        return max(0.0, min(100.0, readability))
    
    def _generate_metadata(self, original_text: str, cleaned_text: str) -> Dict[str, Any]:
        """生成元数据"""
        return {
            'original_length': len(original_text),
            'cleaned_length': len(cleaned_text),
            'compression_ratio': len(cleaned_text) / len(original_text) if original_text else 0,
            'content_hash': hashlib.md5(cleaned_text.encode()).hexdigest(),
            'processing_timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_citations(self, text: str) -> List[str]:
        """提取引用"""
        # 查找各种引用格式
        citation_patterns = [
            r'\[evidence_[a-zA-Z0-9_]+\]',  # [evidence_xxx]
            r'\[[0-9]+\]',  # [1], [2], etc.
            r'\([A-Za-z]+ et al\. \d{4}\)',  # (Author et al. 2024)
            r'\([A-Za-z]+, \d{4}\)',  # (Author, 2024)
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        
        return list(set(citations))  # 去重
    
    def validate_citations(self, text: str, available_citations: List[str]) -> Dict[str, Any]:
        """验证引用"""
        extracted_citations = self.extract_citations(text)
        
        valid_citations = []
        invalid_citations = []
        
        for citation in extracted_citations:
            if citation in available_citations:
                valid_citations.append(citation)
            else:
                invalid_citations.append(citation)
        
        return {
            'total_citations': len(extracted_citations),
            'valid_citations': valid_citations,
            'invalid_citations': invalid_citations,
            'validity_ratio': len(valid_citations) / len(extracted_citations) if extracted_citations else 0
        }
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 简单的基于词汇重叠的相似度计算
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
