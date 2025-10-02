"""
WebWeaver 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "WebWeaver: 基于动态大纲的开放深度研究智能体"

# 读取requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="webweaver",
    version="1.0.0",
    author="WebWeaver Team",
    author_email="webweaver@example.com",
    description="基于动态大纲的开放深度研究智能体",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/webweaver/webweaver",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "llm": [
            "openai>=1.3.0",
            "anthropic>=0.7.8",
            "langchain>=0.0.350",
        ],
        "vector": [
            "chromadb>=0.4.18",
            "sentence-transformers>=2.2.2",
        ],
        "cache": [
            "redis>=5.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "webweaver=webweaver.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "webweaver": [
            "config/*.yaml",
            "prompts/*.py",
            "templates/*.html",
        ],
    },
    keywords="ai, research, nlp, llm, agent, web-search, content-generation",
    project_urls={
        "Bug Reports": "https://github.com/webweaver/webweaver/issues",
        "Source": "https://github.com/webweaver/webweaver",
        "Documentation": "https://webweaver.readthedocs.io/",
    },
)
