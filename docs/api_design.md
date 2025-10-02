# WebWeaver API 设计文档

## 1. 概述

WebWeaver提供了一套完整的API接口，支持深度研究任务的执行和管理。API设计遵循RESTful原则，提供清晰的接口定义和错误处理。

## 2. 核心API接口

### 2.1 研究执行接口

#### POST /api/v1/research
执行深度研究任务

**请求参数:**
```json
{
  "query": "研究查询字符串",
  "max_iterations": 5,
  "config": {
    "agents": {
      "planner": {
        "max_iterations": 5,
        "completeness_threshold": 0.8
      },
      "writer": {
        "max_section_length": 2000,
        "citation_validation": true
      }
    },
    "search_engines": {
      "web": {
        "enabled": true,
        "api_key": "your_api_key"
      }
    }
  }
}
```

**响应格式:**
```json
{
  "success": true,
  "data": {
    "query": "研究查询",
    "report": {
      "title": "研究报告标题",
      "content": "报告内容",
      "sections": [
        {
          "section_id": "section_1",
          "title": "章节标题",
          "content": "章节内容",
          "citations": ["citation_1", "citation_2"],
          "word_count": 500,
          "quality_score": 8.5
        }
      ],
      "total_word_count": 2000,
      "total_citations": 10,
      "quality_score": 8.2
    },
    "outline": {
      "title": "大纲标题",
      "description": "大纲描述",
      "sections": [
        {
          "id": "section_1",
          "title": "章节标题",
          "description": "章节描述",
          "level": 1,
          "children": []
        }
      ],
      "version": 2
    },
    "evidence_count": 25,
    "citations": ["citation_1", "citation_2"],
    "processing_time": 120.5,
    "iterations": 3,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message": "研究完成"
}
```

### 2.2 系统状态接口

#### GET /api/v1/status
获取系统状态

**响应格式:**
```json
{
  "success": true,
  "data": {
    "system_status": "running",
    "version": "1.0.0",
    "uptime": 3600,
    "memory_usage": "512MB",
    "active_research_count": 2,
    "total_research_count": 150
  }
}
```

### 2.3 研究历史接口

#### GET /api/v1/research/history
获取研究历史

**查询参数:**
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 10)
- `query`: 搜索查询 (可选)

**响应格式:**
```json
{
  "success": true,
  "data": {
    "research_list": [
      {
        "id": "research_001",
        "query": "研究查询",
        "title": "研究报告标题",
        "created_at": "2024-01-01T12:00:00Z",
        "status": "completed",
        "processing_time": 120.5,
        "quality_score": 8.2
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 150,
      "pages": 15
    }
  }
}
```

#### GET /api/v1/research/{research_id}
获取特定研究详情

**响应格式:**
```json
{
  "success": true,
  "data": {
    "id": "research_001",
    "query": "研究查询",
    "report": { /* 完整报告数据 */ },
    "outline": { /* 完整大纲数据 */ },
    "evidence_count": 25,
    "citations": ["citation_1", "citation_2"],
    "processing_time": 120.5,
    "iterations": 3,
    "created_at": "2024-01-01T12:00:00Z",
    "status": "completed"
  }
}
```

### 2.4 配置管理接口

#### GET /api/v1/config
获取当前配置

**响应格式:**
```json
{
  "success": true,
  "data": {
    "agents": {
      "planner": {
        "max_iterations": 5,
        "completeness_threshold": 0.8
      },
      "writer": {
        "max_section_length": 2000,
        "citation_validation": true
      }
    },
    "search_engines": {
      "web": {
        "enabled": true,
        "api_key": "***"
      }
    }
  }
}
```

#### PUT /api/v1/config
更新配置

**请求参数:**
```json
{
  "agents": {
    "planner": {
      "max_iterations": 3
    }
  }
}
```

### 2.5 评估接口

#### POST /api/v1/evaluate
评估研究质量

**请求参数:**
```json
{
  "research_id": "research_001",
  "evaluation_type": "comprehensive",
  "metrics": ["accuracy", "completeness", "citation_quality"]
}
```

**响应格式:**
```json
{
  "success": true,
  "data": {
    "overall_score": 8.5,
    "dimensions": {
      "accuracy": 9,
      "completeness": 8,
      "citation_quality": 8,
      "language": 9,
      "structure": 8
    },
    "strengths": ["内容准确", "结构清晰"],
    "weaknesses": ["引用不足", "深度不够"],
    "improvements": ["增加更多引用", "深化分析"],
    "summary": "整体质量良好，需要改进引用"
  }
}
```

## 3. 错误处理

### 3.1 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "field": "query",
      "reason": "不能为空"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3.2 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| AUTHENTICATION_ERROR | 401 | 认证失败 |
| AUTHORIZATION_ERROR | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 内部服务器错误 |
| RESEARCH_FAILED | 500 | 研究执行失败 |
| CONFIG_ERROR | 500 | 配置错误 |

## 4. 认证和授权

### 4.1 API密钥认证

```http
Authorization: Bearer your_api_key_here
```

### 4.2 请求限制

- 每分钟最多60个请求
- 每个研究任务最多5次迭代
- 单次研究最多处理100个证据

## 5. 使用示例

### 5.1 Python客户端示例

```python
import requests
import json

# 配置
API_BASE_URL = "https://api.webweaver.com/api/v1"
API_KEY = "your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 执行研究
def conduct_research(query, max_iterations=5):
    url = f"{API_BASE_URL}/research"
    data = {
        "query": query,
        "max_iterations": max_iterations
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.text}")

# 使用示例
result = conduct_research("人工智能在教育中的应用")
print(f"研究完成: {result['data']['report']['title']}")
```

### 5.2 JavaScript客户端示例

```javascript
const API_BASE_URL = 'https://api.webweaver.com/api/v1';
const API_KEY = 'your_api_key_here';

async function conductResearch(query, maxIterations = 5) {
    const response = await fetch(`${API_BASE_URL}/research`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: query,
            max_iterations: maxIterations
        })
    });
    
    if (!response.ok) {
        throw new Error(`API调用失败: ${response.statusText}`);
    }
    
    return await response.json();
}

// 使用示例
conductResearch("人工智能在教育中的应用")
    .then(result => {
        console.log(`研究完成: ${result.data.report.title}`);
    })
    .catch(error => {
        console.error('错误:', error);
    });
```

## 6. 版本控制

API使用语义化版本控制，当前版本为v1。

- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

## 7. 限流和配额

### 7.1 请求限流

- 免费用户：每分钟10个请求
- 付费用户：每分钟60个请求
- 企业用户：每分钟200个请求

### 7.2 研究配额

- 免费用户：每月10次研究
- 付费用户：每月100次研究
- 企业用户：无限制

## 8. 监控和日志

### 8.1 健康检查

```http
GET /api/v1/health
```

### 8.2 指标监控

- 请求数量
- 响应时间
- 错误率
- 研究成功率
- 系统资源使用率

## 9. 最佳实践

1. **错误处理**: 始终检查响应状态码和错误信息
2. **重试机制**: 对于临时性错误实现指数退避重试
3. **缓存**: 对于相同查询可以缓存结果
4. **异步处理**: 对于长时间运行的研究任务使用异步处理
5. **监控**: 监控API调用成功率和响应时间
