"""
搜索引擎接口实现

提供统一的搜索引擎接口，支持多种搜索源。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
import json
import time
import logging

@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str
    content: str = ""
    source: str = ""
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "content": self.content,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata
        }

class BaseSearchEngine(ABC):
    """基础搜索引擎抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"webweaver.search.{self.__class__.__name__}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行搜索"""
        pass
    
    def _make_request(self, url: str, params: Dict[str, Any] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """发送HTTP请求"""
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return None

class WebSearchEngine(BaseSearchEngine):
    """网络搜索引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://api.search.com/v1/search')
        self.max_results = config.get('max_results', 20)
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行网络搜索"""
        if not self.api_key:
            self.logger.warning("No API key provided for web search")
            return self._fallback_search(query, num_results)
        
        self.logger.info(f"Searching web for: {query}")
        
        params = {
            'q': query,
            'key': self.api_key,
            'num': min(num_results, self.max_results)
        }
        
        response_data = self._make_request(self.base_url, params)
        if not response_data:
            return self._fallback_search(query, num_results)
        
        return self._parse_search_results(response_data, num_results)
    
    def _fallback_search(self, query: str, num_results: int) -> List[SearchResult]:
        """备用搜索方法"""
        self.logger.info("Using fallback search method")
        
        # 这里可以实现一个简单的备用搜索
        # 例如使用DuckDuckGo或其他免费搜索API
        return []
    
    def _parse_search_results(self, data: Dict[str, Any], num_results: int) -> List[SearchResult]:
        """解析搜索结果"""
        results = []
        
        # 根据不同的API响应格式解析
        items = data.get('items', []) or data.get('results', []) or data.get('webPages', {}).get('value', [])
        
        for item in items[:num_results]:
            try:
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', '') or item.get('link', ''),
                    snippet=item.get('snippet', '') or item.get('description', ''),
                    source=item.get('source', 'web'),
                    relevance_score=item.get('relevance_score', 0.0),
                    metadata=item.get('metadata', {})
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error parsing search result: {e}")
                continue
        
        return results

class AcademicSearchEngine(BaseSearchEngine):
    """学术搜索引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://api.semanticscholar.org/graph/v1/paper/search')
        self.max_results = config.get('max_results', 15)
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行学术搜索"""
        if not self.api_key:
            self.logger.warning("No API key provided for academic search")
            return []
        
        self.logger.info(f"Searching academic papers for: {query}")
        
        params = {
            'query': query,
            'limit': min(num_results, self.max_results),
            'fields': 'title,url,abstract,authors,venue,year,citationCount'
        }
        
        headers = {
            'x-api-key': self.api_key
        }
        
        try:
            response = self.session.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.logger.error(f"Academic search failed: {e}")
            return []
        
        return self._parse_academic_results(data, num_results)
    
    def _parse_academic_results(self, data: Dict[str, Any], num_results: int) -> List[SearchResult]:
        """解析学术搜索结果"""
        results = []
        
        papers = data.get('data', [])
        
        for paper in papers[:num_results]:
            try:
                # 构建URL
                paper_id = paper.get('paperId', '')
                url = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else ""
                
                # 构建摘要
                abstract = paper.get('abstract', '')
                snippet = abstract[:300] + "..." if len(abstract) > 300 else abstract
                
                # 构建来源信息
                authors = paper.get('authors', [])
                author_names = [author.get('name', '') for author in authors[:3]]
                venue = paper.get('venue', '')
                year = paper.get('year', '')
                
                source_info = f"{', '.join(author_names)}"
                if venue:
                    source_info += f" - {venue}"
                if year:
                    source_info += f" ({year})"
                
                result = SearchResult(
                    title=paper.get('title', ''),
                    url=url,
                    snippet=snippet,
                    content=abstract,
                    source=source_info,
                    relevance_score=paper.get('citationCount', 0) / 100.0,  # 基于引用数计算相关性
                    metadata={
                        'paperId': paper_id,
                        'authors': authors,
                        'venue': venue,
                        'year': year,
                        'citationCount': paper.get('citationCount', 0)
                    }
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error parsing academic result: {e}")
                continue
        
        return results

class MockSearchEngine(BaseSearchEngine):
    """模拟搜索引擎（用于测试）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mock_results = config.get('mock_results', [])
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """返回模拟搜索结果"""
        self.logger.info(f"Mock search for: {query}")
        
        results = []
        for i, mock_data in enumerate(self.mock_results[:num_results]):
            result = SearchResult(
                title=mock_data.get('title', f'Mock Result {i+1}'),
                url=mock_data.get('url', f'https://example.com/result{i+1}'),
                snippet=mock_data.get('snippet', f'This is a mock search result for query: {query}'),
                content=mock_data.get('content', ''),
                source=mock_data.get('source', 'mock'),
                relevance_score=mock_data.get('relevance_score', 0.8),
                metadata=mock_data.get('metadata', {})
            )
            results.append(result)
        
        return results
