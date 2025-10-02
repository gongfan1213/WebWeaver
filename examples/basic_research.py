"""
WebWeaver 基础研究示例

演示如何使用WebWeaver进行基础的研究任务。
"""

import sys
import os
import yaml
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.webweaver import WebWeaver
from tools.search_engine import MockSearchEngine

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'default.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def setup_mock_search_engine(config):
    """设置模拟搜索引擎"""
    mock_results = [
        {
            "title": "人工智能在教育中的应用研究",
            "url": "https://example.com/ai-education-1",
            "snippet": "人工智能技术在现代教育中发挥着越来越重要的作用，包括个性化学习、智能辅导系统等。",
            "content": "人工智能技术在现代教育中发挥着越来越重要的作用。通过机器学习算法，AI可以为每个学生提供个性化的学习体验，根据学生的学习进度和能力调整教学内容和方式。智能辅导系统能够实时监测学生的学习状态，提供及时的反馈和指导。",
            "source": "教育技术期刊",
            "relevance_score": 0.9
        },
        {
            "title": "机器学习在个性化学习中的应用",
            "url": "https://example.com/ml-personalized-learning",
            "snippet": "机器学习技术使个性化学习成为可能，通过分析学生的学习数据来优化学习路径。",
            "content": "机器学习技术使个性化学习成为可能。通过分析学生的学习数据，包括学习行为、成绩、兴趣等，机器学习算法可以构建个性化的学习模型，为每个学生推荐最适合的学习内容和学习路径。这种方法显著提高了学习效率和效果。",
            "source": "计算机教育研究",
            "relevance_score": 0.8
        },
        {
            "title": "智能教学系统的设计与实现",
            "url": "https://example.com/intelligent-teaching-system",
            "snippet": "智能教学系统结合了人工智能、大数据和云计算技术，为教育提供了新的解决方案。",
            "content": "智能教学系统结合了人工智能、大数据和云计算技术，为教育提供了新的解决方案。系统能够自动生成教学内容、评估学习效果、提供个性化建议，大大提高了教学效率和质量。",
            "source": "教育信息化研究",
            "relevance_score": 0.85
        }
    ]
    
    config['search_engines']['mock'] = {
        'enabled': True,
        'mock_results': mock_results
    }
    
    return config

def main():
    """主函数"""
    print("WebWeaver 基础研究示例")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    
    # 设置模拟搜索引擎
    config = setup_mock_search_engine(config)
    
    # 创建WebWeaver实例
    webweaver = WebWeaver(config)
    
    # 研究查询
    query = "人工智能在教育中的应用和发展趋势"
    
    print(f"研究查询: {query}")
    print("开始研究...")
    print("-" * 30)
    
    try:
        # 执行研究
        result = webweaver.research(query, max_iterations=3)
        
        # 显示结果
        print("\n研究完成！")
        print("=" * 50)
        print(f"处理时间: {result.processing_time:.2f}秒")
        print(f"迭代次数: {result.iterations}")
        print(f"证据数量: {result.evidence_count}")
        print(f"引用数量: {len(result.citations)}")
        
        print("\n报告标题:")
        print(f"  {result.report.title}")
        
        print("\n报告内容:")
        print("-" * 30)
        print(result.report.content)
        
        print("\n大纲结构:")
        print("-" * 30)
        for i, section in enumerate(result.outline.sections, 1):
            print(f"{i}. {section.title}")
            print(f"   描述: {section.description}")
            if section.children:
                for j, child in enumerate(section.children, 1):
                    print(f"   {i}.{j} {child.title}")
        
        print("\n引用列表:")
        print("-" * 30)
        for i, citation in enumerate(result.citations, 1):
            print(f"{i}. {citation}")
        
        # 保存结果到文件
        output_file = f"research_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"研究过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
