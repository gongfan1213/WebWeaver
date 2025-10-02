# WebWeaver 实现方案和代码规划

## 1. 项目结构设计

```
webweaver/
├── docs/                          # 文档目录
│   ├── README.md
│   ├── architecture.md
│   ├── implementation_plan.md
│   ├── api_design.md
│   └── prompt_templates.md
├── src/                           # 源代码目录
│   ├── __init__.py
│   ├── core/                      # 核心模块
│   │   ├── __init__.py
│   │   ├── base_agent.py          # 基础智能体类
│   │   ├── planner_agent.py       # 规划智能体
│   │   ├── writer_agent.py        # 写作智能体
│   │   └── memory_bank.py         # 记忆库
│   ├── tools/                     # 工具模块
│   │   ├── __init__.py
│   │   ├── search_engine.py       # 搜索引擎接口
│   │   ├── web_scraper.py         # 网页抓取器
│   │   ├── content_processor.py   # 内容处理器
│   │   └── citation_manager.py    # 引用管理器
│   ├── prompts/                   # 提示词模板
│   │   ├── __init__.py
│   │   ├── planner_prompts.py     # 规划者提示词
│   │   ├── writer_prompts.py      # 写作者提示词
│   │   └── evaluation_prompts.py  # 评估提示词
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── text_processing.py     # 文本处理
│   │   ├── similarity.py          # 相似度计算
│   │   └── validation.py          # 验证工具
│   └── api/                       # API接口
│       ├── __init__.py
│       ├── main.py                # 主API入口
│       └── schemas.py             # 数据模式
├── examples/                      # 示例代码
│   ├── basic_research.py
│   ├── advanced_research.py
│   └── custom_agent.py
├── tests/                         # 测试代码
│   ├── __init__.py
│   ├── test_planner.py
│   ├── test_writer.py
│   └── test_memory_bank.py
├── config/                        # 配置文件
│   ├── default.yaml
│   └── development.yaml
├── requirements.txt               # 依赖包
├── setup.py                      # 安装脚本
└── README.md                     # 项目说明
```

## 2. 核心类设计

### 2.1 基础智能体类

```python
# src/core/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AgentState:
    """智能体状态"""
    current_task: str
    iteration_count: int
    context: Dict[str, Any]
    memory: List[Dict[str, Any]]

class BaseAgent(ABC):
    """基础智能体抽象类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.state = AgentState(
            current_task="",
            iteration_count=0,
            context={},
            memory=[]
        )
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """处理输入数据"""
        pass
    
    @abstractmethod
    def should_continue(self) -> bool:
        """判断是否应该继续执行"""
        pass
    
    def update_state(self, **kwargs):
        """更新智能体状态"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
```

### 2.2 规划智能体

```python
# src/core/planner_agent.py
from typing import List, Dict, Any
from .base_agent import BaseAgent
from .memory_bank import MemoryBank, Evidence
from ..prompts.planner_prompts import PlannerPrompts

class Outline:
    """大纲类"""
    def __init__(self, title: str, sections: List[Dict[str, Any]]):
        self.title = title
        self.sections = sections
        self.citations = {}
    
    def add_citation(self, section_id: str, evidence_id: str):
        """添加引用"""
        if section_id not in self.citations:
            self.citations[section_id] = []
        self.citations[section_id].append(evidence_id)

class PlannerAgent(BaseAgent):
    """规划智能体"""
    
    def __init__(self, config: Dict[str, Any], memory_bank: MemoryBank):
        super().__init__("Planner", config)
        self.memory_bank = memory_bank
        self.prompts = PlannerPrompts()
        self.current_outline = None
        self.search_history = []
    
    def generate_initial_outline(self, query: str) -> Outline:
        """生成初始大纲"""
        prompt = self.prompts.get_initial_outline_prompt(query)
        # 调用LLM生成大纲
        outline_data = self._call_llm(prompt)
        return self._parse_outline(outline_data)
    
    def optimize_outline(self, new_evidence: List[Evidence]) -> Outline:
        """优化大纲"""
        if not self.current_outline:
            raise ValueError("No current outline to optimize")
        
        prompt = self.prompts.get_outline_optimization_prompt(
            self.current_outline, new_evidence
        )
        optimized_data = self._call_llm(prompt)
        return self._parse_outline(optimized_data)
    
    def plan_search_strategy(self) -> List[Dict[str, Any]]:
        """制定搜索策略"""
        if not self.current_outline:
            return []
        
        prompt = self.prompts.get_search_strategy_prompt(self.current_outline)
        strategy_data = self._call_llm(prompt)
        return self._parse_search_strategy(strategy_data)
    
    def should_continue_research(self) -> bool:
        """判断是否继续研究"""
        if self.state.iteration_count >= self.config.get('max_iterations', 5):
            return False
        
        # 检查大纲完整性
        completeness = self._calculate_outline_completeness()
        return completeness < self.config.get('completeness_threshold', 0.8)
    
    def _call_llm(self, prompt: str) -> str:
        """调用大语言模型"""
        # 实现LLM调用逻辑
        pass
    
    def _parse_outline(self, data: str) -> Outline:
        """解析大纲数据"""
        # 实现大纲解析逻辑
        pass
    
    def _parse_search_strategy(self, data: str) -> List[Dict[str, Any]]:
        """解析搜索策略"""
        # 实现搜索策略解析逻辑
        pass
    
    def _calculate_outline_completeness(self) -> float:
        """计算大纲完整性"""
        # 实现完整性计算逻辑
        pass
```

### 2.3 写作智能体

```python
# src/core/writer_agent.py
from typing import List, Dict, Any
from .base_agent import BaseAgent
from .memory_bank import MemoryBank, Evidence
from ..prompts.writer_prompts import WriterPrompts

class WrittenSection:
    """已写作章节"""
    def __init__(self, section_id: str, content: str, citations: List[str]):
        self.section_id = section_id
        self.content = content
        self.citations = citations

class WriterAgent(BaseAgent):
    """写作智能体"""
    
    def __init__(self, config: Dict[str, Any], memory_bank: MemoryBank):
        super().__init__("Writer", config)
        self.memory_bank = memory_bank
        self.prompts = WriterPrompts()
        self.written_sections = []
    
    def retrieve_evidence_for_section(self, section: Dict[str, Any]) -> List[Evidence]:
        """为章节检索证据"""
        # 根据章节内容检索相关证据
        search_query = self._extract_search_query(section)
        evidence = self.memory_bank.search_evidence(search_query)
        return evidence
    
    def write_section(self, section: Dict[str, Any], evidence: List[Evidence]) -> WrittenSection:
        """写作章节"""
        prompt = self.prompts.get_section_writing_prompt(section, evidence)
        content = self._call_llm(prompt)
        citations = self._extract_citations(content)
        
        written_section = WrittenSection(
            section_id=section['id'],
            content=content,
            citations=citations
        )
        
        self.written_sections.append(written_section)
        return written_section
    
    def integrate_citations(self, content: str, evidence: List[Evidence]) -> str:
        """整合引用"""
        # 实现引用整合逻辑
        pass
    
    def validate_citations(self, content: str) -> bool:
        """验证引用准确性"""
        # 实现引用验证逻辑
        pass
    
    def _extract_search_query(self, section: Dict[str, Any]) -> str:
        """提取搜索查询"""
        # 实现搜索查询提取逻辑
        pass
    
    def _extract_citations(self, content: str) -> List[str]:
        """提取引用"""
        # 实现引用提取逻辑
        pass
```

### 2.4 记忆库

```python
# src/core/memory_bank.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import hashlib
import json

@dataclass
class Evidence:
    """证据类"""
    id: str
    content: str
    summary: str
    source: str
    url: str
    relevance_score: float
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"evidence_{content_hash[:8]}"

class MemoryBank:
    """记忆库"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.evidence_store: Dict[str, Evidence] = {}
        self.content_index: Dict[str, List[str]] = defaultdict(list)
        self.source_index: Dict[str, List[str]] = defaultdict(list)
        self.topic_index: Dict[str, List[str]] = defaultdict(list)
    
    def add_evidence(self, evidence: Evidence) -> str:
        """添加证据"""
        self.evidence_store[evidence.id] = evidence
        
        # 更新索引
        self._update_content_index(evidence)
        self._update_source_index(evidence)
        self._update_topic_index(evidence)
        
        return evidence.id
    
    def search_evidence(self, query: str, limit: int = 10) -> List[Evidence]:
        """搜索证据"""
        # 实现基于查询的证据搜索
        pass
    
    def get_evidence_by_id(self, evidence_id: str) -> Optional[Evidence]:
        """根据ID获取证据"""
        return self.evidence_store.get(evidence_id)
    
    def get_evidence_by_citation(self, citation: str) -> Optional[Evidence]:
        """根据引用获取证据"""
        # 实现引用到证据的映射
        pass
    
    def _update_content_index(self, evidence: Evidence):
        """更新内容索引"""
        # 实现内容索引更新逻辑
        pass
    
    def _update_source_index(self, evidence: Evidence):
        """更新来源索引"""
        self.source_index[evidence.source].append(evidence.id)
    
    def _update_topic_index(self, evidence: Evidence):
        """更新主题索引"""
        # 实现主题索引更新逻辑
        pass
```

## 3. 工具模块设计

### 3.1 搜索引擎接口

```python
# src/tools/search_engine.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
import json

class SearchResult:
    """搜索结果"""
    def __init__(self, title: str, url: str, snippet: str, content: str = ""):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.content = content

class BaseSearchEngine(ABC):
    """基础搜索引擎抽象类"""
    
    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行搜索"""
        pass

class WebSearchEngine(BaseSearchEngine):
    """网络搜索引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.search.com')
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行网络搜索"""
        # 实现网络搜索逻辑
        pass

class AcademicSearchEngine(BaseSearchEngine):
    """学术搜索引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.semanticscholar.org')
    
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行学术搜索"""
        # 实现学术搜索逻辑
        pass
```

### 3.2 网页抓取器

```python
# src/tools/web_scraper.py
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import time
import random

class WebScraper:
    """网页抓取器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """抓取网页内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取主要内容
            content = self._extract_content(soup)
            title = self._extract_title(soup)
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'status_code': response.status_code
            }
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取主要内容"""
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取文本内容
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
```

## 4. 提示词模板设计

### 4.1 规划者提示词

```python
# src/prompts/planner_prompts.py
class PlannerPrompts:
    """规划者提示词模板"""
    
    def get_initial_outline_prompt(self, query: str) -> str:
        """获取初始大纲生成提示词"""
        return f"""
你是一个专业的研究规划者。请根据以下查询生成一个详细的研究大纲：

查询: {query}

请生成一个结构化的研究大纲，包括：
1. 主要章节和子章节
2. 每个章节的核心内容描述
3. 章节之间的逻辑关系
4. 预期的研究深度和广度

请以JSON格式输出大纲结构。
"""
    
    def get_outline_optimization_prompt(self, current_outline: Outline, new_evidence: List[Evidence]) -> str:
        """获取大纲优化提示词"""
        evidence_summaries = [f"- {ev.summary}" for ev in new_evidence]
        
        return f"""
基于新获取的证据，请优化当前的研究大纲：

当前大纲:
{current_outline}

新证据:
{chr(10).join(evidence_summaries)}

请考虑：
1. 新证据如何补充现有大纲
2. 是否需要添加新的章节或子章节
3. 是否需要调整章节顺序或重点
4. 如何确保大纲的完整性和逻辑性

请输出优化后的大纲。
"""
    
    def get_search_strategy_prompt(self, outline: Outline) -> str:
        """获取搜索策略提示词"""
        return f"""
基于当前研究大纲，请制定详细的搜索策略：

当前大纲:
{outline}

请为每个需要更多信息的章节制定搜索策略，包括：
1. 具体的搜索关键词
2. 搜索的优先级
3. 预期的信息类型
4. 搜索的深度和广度

请以JSON格式输出搜索策略。
"""
```

### 4.2 写作者提示词

```python
# src/prompts/writer_prompts.py
class WriterPrompts:
    """写作者提示词模板"""
    
    def get_section_writing_prompt(self, section: Dict[str, Any], evidence: List[Evidence]) -> str:
        """获取章节写作提示词"""
        evidence_text = "\n\n".join([f"证据 {i+1}: {ev.content}" for i, ev in enumerate(evidence)])
        
        return f"""
你是一个专业的研究报告写作者。请基于提供的证据写作以下章节：

章节信息:
- 标题: {section.get('title', '')}
- 描述: {section.get('description', '')}
- 要求: {section.get('requirements', '')}

相关证据:
{evidence_text}

写作要求:
1. 内容要准确、客观、有逻辑性
2. 必须基于提供的证据进行写作
3. 每个重要观点都要有相应的引用
4. 引用格式: [证据编号]
5. 语言要专业、清晰、易懂
6. 确保内容的连贯性和完整性

请输出章节内容。
"""
    
    def get_citation_validation_prompt(self, content: str, evidence: List[Evidence]) -> str:
        """获取引用验证提示词"""
        return f"""
请验证以下内容中的引用是否准确：

内容:
{content}

可用证据:
{chr(10).join([f"证据 {i+1}: {ev.content[:200]}..." for i, ev in enumerate(evidence)])}

请检查：
1. 每个引用是否都有对应的证据
2. 引用是否准确反映了证据内容
3. 是否有遗漏的重要引用
4. 引用格式是否正确

请输出验证结果和修改建议。
"""
```

## 5. 配置管理

### 5.1 默认配置

```yaml
# config/default.yaml
# WebWeaver 默认配置

# 智能体配置
agents:
  planner:
    max_iterations: 5
    completeness_threshold: 0.8
    outline_optimization_threshold: 0.7
  
  writer:
    max_section_length: 2000
    citation_validation: true
    quality_check: true

# 记忆库配置
memory_bank:
  max_evidence_count: 1000
  similarity_threshold: 0.7
  indexing_strategy: "semantic"

# 搜索引擎配置
search_engines:
  web:
    enabled: true
    api_key: ""
    base_url: "https://api.search.com"
    max_results: 20
  
  academic:
    enabled: true
    api_key: ""
    base_url: "https://api.semanticscholar.org"
    max_results: 15

# 网页抓取配置
web_scraper:
  timeout: 10
  max_retries: 3
  delay_range: [1, 3]
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# LLM配置
llm:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 4000
  api_key: ""

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/webweaver.log"
```

## 6. API接口设计

### 6.1 主要API端点

```python
# src/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="WebWeaver API", version="1.0.0")

class ResearchRequest(BaseModel):
    query: str
    max_iterations: int = 5
    config: Dict[str, Any] = {}

class ResearchResponse(BaseModel):
    report: str
    outline: Dict[str, Any]
    evidence_count: int
    citations: List[str]
    processing_time: float

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """执行深度研究"""
    try:
        # 初始化WebWeaver系统
        webweaver = WebWeaver(request.config)
        
        # 执行研究
        result = await webweaver.research(request.query, request.max_iterations)
        
        return ResearchResponse(
            report=result.report,
            outline=result.outline,
            evidence_count=result.evidence_count,
            citations=result.citations,
            processing_time=result.processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 7. 测试策略

### 7.1 单元测试

```python
# tests/test_planner.py
import pytest
from src.core.planner_agent import PlannerAgent, Outline
from src.core.memory_bank import MemoryBank, Evidence

class TestPlannerAgent:
    def test_generate_initial_outline(self):
        """测试初始大纲生成"""
        config = {"max_iterations": 5}
        memory_bank = MemoryBank({})
        planner = PlannerAgent(config, memory_bank)
        
        query = "人工智能在教育中的应用"
        outline = planner.generate_initial_outline(query)
        
        assert isinstance(outline, Outline)
        assert outline.title is not None
        assert len(outline.sections) > 0
    
    def test_optimize_outline(self):
        """测试大纲优化"""
        # 测试实现
        pass
    
    def test_plan_search_strategy(self):
        """测试搜索策略制定"""
        # 测试实现
        pass
```

### 7.2 集成测试

```python
# tests/test_integration.py
import pytest
from src.core.webweaver import WebWeaver

class TestWebWeaverIntegration:
    def test_full_research_cycle(self):
        """测试完整研究循环"""
        config = {
            "agents": {
                "planner": {"max_iterations": 3},
                "writer": {"max_section_length": 1000}
            }
        }
        
        webweaver = WebWeaver(config)
        result = webweaver.research("机器学习在医疗诊断中的应用")
        
        assert result.report is not None
        assert len(result.citations) > 0
        assert result.evidence_count > 0
```

## 8. 部署和运维

### 8.1 Docker配置

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8000

CMD ["python", "-m", "src.api.main"]
```

### 8.2 依赖管理

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
beautifulsoup4==4.12.2
openai==1.3.0
langchain==0.0.350
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

## 9. 性能优化建议

### 9.1 缓存策略
- 搜索结果缓存
- 证据摘要缓存
- 大纲状态缓存

### 9.2 并行处理
- 多线程搜索
- 异步内容处理
- 并行章节写作

### 9.3 资源管理
- 内存使用监控
- 网络请求限制
- 计算资源分配

这个实现方案提供了WebWeaver系统的完整技术架构和代码规划，涵盖了从核心组件到部署运维的各个方面。每个模块都有清晰的职责定义和接口设计，便于后续的开发和维护。
