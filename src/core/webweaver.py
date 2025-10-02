"""
WebWeaver 主系统

协调规划智能体和写作智能体，实现完整的深度研究流程。
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import time
import json
from datetime import datetime

from .base_agent import BaseAgent
from .planner_agent import PlannerAgent, Outline
from .writer_agent import WriterAgent, Report
from .memory_bank import MemoryBank, Evidence
from ..tools.search_engine import BaseSearchEngine, WebSearchEngine, AcademicSearchEngine
from ..tools.web_scraper import WebScraper

@dataclass
class ResearchResult:
    """研究结果"""
    query: str
    report: Report
    outline: Outline
    evidence_count: int
    citations: List[str]
    processing_time: float
    iterations: int
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "query": self.query,
            "report": self.report.to_dict(),
            "outline": self.outline.to_dict(),
            "evidence_count": self.evidence_count,
            "citations": self.citations,
            "processing_time": self.processing_time,
            "iterations": self.iterations,
            "created_at": self.created_at.isoformat()
        }

class WebWeaver:
    """WebWeaver 主系统"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory_bank = MemoryBank(config.get("memory_bank", {}))
        self.planner = PlannerAgent(config.get("agents", {}).get("planner", {}), self.memory_bank)
        self.writer = WriterAgent(config.get("agents", {}).get("writer", {}), self.memory_bank)
        
        # 初始化搜索引擎
        self.search_engines = self._initialize_search_engines(config.get("search_engines", {}))
        self.web_scraper = WebScraper(config.get("web_scraper", {}))
        
        # 研究状态
        self.current_query = ""
        self.research_start_time = None
        self.research_iterations = 0
        
        self.logger = self._setup_logger()
    
    def research(self, query: str, max_iterations: Optional[int] = None) -> ResearchResult:
        """执行深度研究"""
        self.logger.info(f"Starting research for query: {query}")
        
        start_time = time.time()
        self.research_start_time = start_time
        self.current_query = query
        self.research_iterations = 0
        
        # 重置系统状态
        self._reset_system()
        
        # 生成初始大纲
        outline = self.planner.generate_initial_outline(query)
        self.logger.info(f"Generated initial outline with {len(outline.get_all_sections())} sections")
        
        # 研究循环
        max_iter = max_iterations or self.config.get("max_iterations", 5)
        
        while self.planner.should_continue_research() and self.research_iterations < max_iter:
            self.research_iterations += 1
            self.logger.info(f"Research iteration {self.research_iterations}")
            
            # 制定搜索策略
            search_strategies = self.planner.plan_search_strategy()
            
            if not search_strategies:
                self.logger.info("No more search strategies available")
                break
            
            # 执行搜索
            new_evidence = self._execute_search_strategies(search_strategies)
            
            if new_evidence:
                self.logger.info(f"Found {len(new_evidence)} new evidence items")
                
                # 优化大纲
                outline = self.planner.optimize_outline(new_evidence)
                self.logger.info(f"Optimized outline (version {outline.version})")
            else:
                self.logger.warning("No new evidence found in this iteration")
        
        # 写作阶段
        self.logger.info("Starting writing phase")
        report = self.writer.write_report(outline)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 创建研究结果
        result = ResearchResult(
            query=query,
            report=report,
            outline=outline,
            evidence_count=self.memory_bank.get_evidence_count(),
            citations=self._extract_all_citations(report),
            processing_time=processing_time,
            iterations=self.research_iterations
        )
        
        self.logger.info(f"Research completed in {processing_time:.2f}s with {result.evidence_count} evidence items")
        
        return result
    
    def _execute_search_strategies(self, strategies: List[Dict[str, Any]]) -> List[Evidence]:
        """执行搜索策略"""
        all_evidence = []
        
        for strategy in strategies:
            try:
                # 选择搜索引擎
                search_engine = self._select_search_engine(strategy.get("search_type", "web"))
                
                if not search_engine:
                    self.logger.warning(f"No search engine available for type: {strategy.get('search_type')}")
                    continue
                
                # 执行搜索
                keywords = strategy.get("keywords", [])
                search_query = " ".join(keywords)
                
                self.logger.info(f"Searching for: {search_query}")
                search_results = search_engine.search(search_query, num_results=5)
                
                # 处理搜索结果
                for result in search_results:
                    evidence = self._process_search_result(result, strategy)
                    if evidence:
                        evidence_id = self.memory_bank.add_evidence(evidence)
                        all_evidence.append(evidence)
                        self.logger.debug(f"Added evidence: {evidence_id}")
                
            except Exception as e:
                self.logger.error(f"Error executing search strategy: {e}")
                continue
        
        return all_evidence
    
    def _select_search_engine(self, search_type: str) -> Optional[BaseSearchEngine]:
        """选择搜索引擎"""
        if search_type == "web":
            return self.search_engines.get("web")
        elif search_type == "academic":
            return self.search_engines.get("academic")
        else:
            return self.search_engines.get("web")  # 默认使用网络搜索
    
    def _process_search_result(self, result, strategy: Dict[str, Any]) -> Optional[Evidence]:
        """处理搜索结果"""
        try:
            # 抓取网页内容
            scraped_content = self.web_scraper.scrape_url(result.url)
            
            if not scraped_content:
                self.logger.warning(f"Failed to scrape content from: {result.url}")
                return None
            
            # 创建证据
            evidence = Evidence(
                content=scraped_content.get("content", result.snippet),
                summary=result.snippet,
                source=scraped_content.get("title", result.title),
                url=result.url,
                relevance_score=self._calculate_relevance_score(result, strategy),
                metadata={
                    "search_strategy": strategy,
                    "scraped_at": datetime.now().isoformat(),
                    "original_title": result.title
                }
            )
            
            return evidence
            
        except Exception as e:
            self.logger.error(f"Error processing search result: {e}")
            return None
    
    def _calculate_relevance_score(self, result, strategy: Dict[str, Any]) -> float:
        """计算相关性分数"""
        # 简单的相关性计算
        # 实际实现中可以使用更复杂的NLP技术
        
        score = 0.0
        
        # 基于标题匹配
        title = result.title.lower()
        keywords = [kw.lower() for kw in strategy.get("keywords", [])]
        
        for keyword in keywords:
            if keyword in title:
                score += 0.3
        
        # 基于摘要匹配
        snippet = result.snippet.lower()
        for keyword in keywords:
            if keyword in snippet:
                score += 0.2
        
        # 基于优先级
        priority = strategy.get("priority", 1)
        score += (5 - priority) * 0.1
        
        return min(score, 1.0)
    
    def _extract_all_citations(self, report: Report) -> List[str]:
        """提取所有引用"""
        all_citations = []
        for section in report.sections:
            all_citations.extend(section.citations)
        return list(set(all_citations))  # 去重
    
    def _initialize_search_engines(self, search_config: Dict[str, Any]) -> Dict[str, BaseSearchEngine]:
        """初始化搜索引擎"""
        engines = {}
        
        # 网络搜索引擎
        if search_config.get("web", {}).get("enabled", True):
            try:
                engines["web"] = WebSearchEngine(search_config.get("web", {}))
                self.logger.info("Web search engine initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize web search engine: {e}")
        
        # 学术搜索引擎
        if search_config.get("academic", {}).get("enabled", True):
            try:
                engines["academic"] = AcademicSearchEngine(search_config.get("academic", {}))
                self.logger.info("Academic search engine initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize academic search engine: {e}")
        
        return engines
    
    def _reset_system(self):
        """重置系统状态"""
        self.memory_bank.clear()
        self.planner.reset()
        self.writer.written_sections.clear()
        self.writer.current_report = None
        self.research_iterations = 0
    
    def _setup_logger(self):
        """设置日志记录器"""
        import logging
        logger = logging.getLogger("webweaver.main")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "current_query": self.current_query,
            "research_iterations": self.research_iterations,
            "evidence_count": self.memory_bank.get_evidence_count(),
            "planner_state": self.planner.to_dict(),
            "writer_sections": len(self.writer.written_sections),
            "search_engines": list(self.search_engines.keys())
        }
    
    def export_research_data(self) -> Dict[str, Any]:
        """导出研究数据"""
        return {
            "memory_bank": self.memory_bank.export_to_dict(),
            "planner_outline": self.planner.get_current_outline().to_dict() if self.planner.get_current_outline() else None,
            "writer_report": self.writer.get_current_report().to_dict() if self.writer.get_current_report() else None,
            "system_status": self.get_system_status()
        }
    
    def import_research_data(self, data: Dict[str, Any]):
        """导入研究数据"""
        if "memory_bank" in data:
            self.memory_bank.import_from_dict(data["memory_bank"])
        
        # 可以添加更多导入逻辑
        self.logger.info("Research data imported successfully")
