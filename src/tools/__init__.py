"""
WebWeaver 工具模块

包含各种工具和实用程序：
- search_engine: 搜索引擎接口
- web_scraper: 网页抓取器
- content_processor: 内容处理器
- citation_manager: 引用管理器
"""

from .search_engine import BaseSearchEngine, WebSearchEngine, AcademicSearchEngine, SearchResult
from .web_scraper import WebScraper
from .content_processor import ContentProcessor
from .citation_manager import CitationManager

__all__ = [
    "BaseSearchEngine",
    "WebSearchEngine", 
    "AcademicSearchEngine",
    "SearchResult",
    "WebScraper",
    "ContentProcessor",
    "CitationManager"
]
