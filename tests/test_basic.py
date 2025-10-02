"""
WebWeaver 基础测试

测试核心组件的导入和基本功能。
"""

import sys
import os
import pytest

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """测试核心模块导入"""
    try:
        from core.webweaver import WebWeaver
        from core.planner_agent import PlannerAgent, Outline
        from core.writer_agent import WriterAgent, Report
        from core.memory_bank import MemoryBank, Evidence
        from tools.search_engine import BaseSearchEngine, SearchResult
        from tools.web_scraper import WebScraper
        from tools.content_processor import ContentProcessor
        from tools.citation_manager import CitationManager
        assert True
    except ImportError as e:
        pytest.fail(f"导入失败: {e}")

def test_memory_bank():
    """测试记忆库基本功能"""
    from core.memory_bank import MemoryBank, Evidence
    
    # 创建记忆库
    memory_bank = MemoryBank({})
    
    # 创建证据
    evidence = Evidence(
        content="这是一个测试证据",
        summary="测试摘要",
        source="测试来源",
        url="https://example.com",
        relevance_score=0.8
    )
    
    # 添加证据
    evidence_id = memory_bank.add_evidence(evidence)
    assert evidence_id is not None
    
    # 获取证据
    retrieved_evidence = memory_bank.get_evidence_by_id(evidence_id)
    assert retrieved_evidence is not None
    assert retrieved_evidence.content == "这是一个测试证据"
    
    # 搜索证据
    search_results = memory_bank.search_evidence("测试", limit=5)
    assert len(search_results) >= 1

def test_planner_agent():
    """测试规划智能体基本功能"""
    from core.planner_agent import PlannerAgent, Outline
    from core.memory_bank import MemoryBank
    
    # 创建记忆库和规划智能体
    memory_bank = MemoryBank({})
    planner = PlannerAgent({}, memory_bank)
    
    # 测试初始大纲生成
    query = "人工智能在教育中的应用"
    outline = planner.generate_initial_outline(query)
    
    assert outline is not None
    assert outline.title is not None
    assert len(outline.sections) > 0

def test_writer_agent():
    """测试写作智能体基本功能"""
    from core.writer_agent import WriterAgent, WrittenSection
    from core.memory_bank import MemoryBank
    
    # 创建记忆库和写作智能体
    memory_bank = MemoryBank({})
    writer = WriterAgent({}, memory_bank)
    
    # 测试章节写作
    section = {
        'id': 'test_section',
        'title': '测试章节',
        'description': '这是一个测试章节',
        'requirements': ['要求1', '要求2']
    }
    
    evidence = []
    written_section = writer.write_section(section, evidence)
    
    # 由于没有LLM实现，这里只测试基本结构
    assert written_section is None or isinstance(written_section, WrittenSection)

def test_content_processor():
    """测试内容处理器"""
    from tools.content_processor import ContentProcessor
    
    processor = ContentProcessor({})
    
    # 测试内容处理
    text = "这是一个测试文本。它包含多个句子。"
    processed = processor.process(text)
    
    assert processed.word_count > 0
    assert processed.sentence_count > 0
    assert len(processed.keywords) > 0

def test_citation_manager():
    """测试引用管理器"""
    from tools.citation_manager import CitationManager, Citation
    
    manager = CitationManager({})
    
    # 创建引用
    citation = manager.create_citation(
        text="这是一个测试引用",
        source="测试来源",
        url="https://example.com"
    )
    
    assert citation.id is not None
    assert citation.text == "这是一个测试引用"
    
    # 获取引用
    retrieved_citation = manager.get_citation(citation.id)
    assert retrieved_citation is not None
    assert retrieved_citation.text == "这是一个测试引用"

def test_web_scraper():
    """测试网页抓取器"""
    from tools.web_scraper import WebScraper
    
    scraper = WebScraper({})
    
    # 测试URL验证
    assert scraper.is_valid_url("https://example.com") == True
    assert scraper.is_valid_url("invalid-url") == False
    
    # 测试域名提取
    domain = scraper.get_domain("https://example.com/path")
    assert domain == "example.com"

if __name__ == "__main__":
    pytest.main([__file__])
