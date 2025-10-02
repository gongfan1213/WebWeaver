"""
基础智能体抽象类

定义了所有智能体的通用接口和基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import time
from datetime import datetime

@dataclass
class AgentState:
    """智能体状态"""
    current_task: str = ""
    iteration_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    memory: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    last_update: Optional[datetime] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        self.last_update = datetime.now()

class BaseAgent(ABC):
    """基础智能体抽象类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.state = AgentState()
        self.logger = self._setup_logger()
    
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
        
        self.state.last_update = datetime.now()
        self.logger.info(f"Agent {self.name} state updated: {kwargs}")
    
    def add_to_memory(self, item: Dict[str, Any]):
        """添加项目到记忆"""
        self.state.memory.append({
            "timestamp": datetime.now().isoformat(),
            "item": item
        })
        self.logger.debug(f"Added item to memory: {item}")
    
    def get_memory(self, filter_func: Optional[callable] = None) -> List[Dict[str, Any]]:
        """获取记忆"""
        if filter_func is None:
            return self.state.memory
        
        return [item for item in self.state.memory if filter_func(item)]
    
    def clear_memory(self):
        """清空记忆"""
        self.state.memory.clear()
        self.logger.info(f"Cleared memory for agent {self.name}")
    
    def get_elapsed_time(self) -> float:
        """获取已用时间（秒）"""
        if self.state.start_time is None:
            return 0.0
        return (datetime.now() - self.state.start_time).total_seconds()
    
    def reset(self):
        """重置智能体状态"""
        self.state = AgentState()
        self.logger.info(f"Reset agent {self.name}")
    
    def _setup_logger(self):
        """设置日志记录器"""
        import logging
        logger = logging.getLogger(f"webweaver.{self.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _call_llm(self, prompt: str, **kwargs) -> str:
        """调用大语言模型"""
        # 这里应该实现具体的LLM调用逻辑
        # 为了演示，我们返回一个占位符
        self.logger.info(f"Calling LLM with prompt length: {len(prompt)}")
        
        # 实际实现中，这里应该调用具体的LLM API
        # 例如 OpenAI, Anthropic, 或其他LLM服务
        return "LLM response placeholder"
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "config": self.config,
            "state": {
                "current_task": self.state.current_task,
                "iteration_count": self.state.iteration_count,
                "context": self.state.context,
                "memory_count": len(self.state.memory),
                "elapsed_time": self.get_elapsed_time()
            }
        }
