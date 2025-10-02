"""
网页抓取器实现

负责从网页中提取内容和元数据。
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
import time
import random
import logging
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

@dataclass
class ScrapedContent:
    """抓取的内容"""
    url: str
    title: str
    content: str
    summary: str
    metadata: Dict[str, Any]
    status_code: int
    scraped_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "metadata": self.metadata,
            "status_code": self.status_code,
            "scraped_at": self.scraped_at
        }

class WebScraper:
    """网页抓取器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.timeout = config.get('timeout', 10)
        self.max_retries = config.get('max_retries', 3)
        self.delay_range = config.get('delay_range', [1, 3])
        self.max_content_length = config.get('max_content_length', 50000)
        
        self.logger = logging.getLogger("webweaver.web_scraper")
    
    def scrape_url(self, url: str) -> Optional[ScrapedContent]:
        """抓取网页内容"""
        self.logger.info(f"Scraping URL: {url}")
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    self.logger.warning(f"Non-HTML content type: {content_type}")
                    return None
                
                # 解析HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 提取内容
                title = self._extract_title(soup)
                content = self._extract_content(soup)
                summary = self._extract_summary(content)
                metadata = self._extract_metadata(soup, response)
                
                # 检查内容长度
                if len(content) > self.max_content_length:
                    content = content[:self.max_content_length] + "..."
                
                scraped_content = ScrapedContent(
                    url=url,
                    title=title,
                    content=content,
                    summary=summary,
                    metadata=metadata,
                    status_code=response.status_code,
                    scraped_at=time.strftime('%Y-%m-%d %H:%M:%S')
                )
                
                self.logger.info(f"Successfully scraped: {title[:50]}...")
                return scraped_content
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    delay = random.uniform(*self.delay_range)
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to scrape {url} after {self.max_retries} attempts")
                    return None
            except Exception as e:
                self.logger.error(f"Unexpected error scraping {url}: {e}")
                return None
        
        return None
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[ScrapedContent]:
        """批量抓取多个URL"""
        results = []
        
        for url in urls:
            content = self.scrape_url(url)
            if content:
                results.append(content)
            
            # 添加延迟避免被封
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
        
        return results
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        # 尝试多种标题选择器
        title_selectors = [
            'title',
            'h1',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip() if element.name != 'meta' else element.get('content', '').strip()
                if title:
                    return title
        
        return "无标题"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取主要内容"""
        # 移除不需要的标签
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            tag.decompose()
        
        # 尝试找到主要内容区域
        content_selectors = [
            'article',
            'main',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '#main'
        ]
        
        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            content_element = soup.find('body')
        
        if not content_element:
            return ""
        
        # 提取文本内容
        text = content_element.get_text()
        
        # 清理文本
        text = self._clean_text(text)
        
        return text
    
    def _extract_summary(self, content: str) -> str:
        """提取摘要"""
        if not content:
            return ""
        
        # 取前200个字符作为摘要
        summary = content[:200].strip()
        
        # 确保以句号结尾
        if summary and not summary.endswith(('.', '!', '?')):
            # 找到最后一个句号
            last_period = summary.rfind('.')
            if last_period > 50:  # 确保摘要不会太短
                summary = summary[:last_period + 1]
            else:
                summary += "..."
        
        return summary
    
    def _extract_metadata(self, soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
        """提取元数据"""
        metadata = {
            'url': response.url,
            'status_code': response.status_code,
            'content_length': len(response.content),
            'content_type': response.headers.get('content-type', ''),
            'last_modified': response.headers.get('last-modified', ''),
            'language': self._detect_language(soup),
            'images': self._extract_images(soup),
            'links': self._extract_links(soup),
            'meta_tags': self._extract_meta_tags(soup)
        }
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除多余的换行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    def _detect_language(self, soup: BeautifulSoup) -> str:
        """检测语言"""
        # 从html标签的lang属性获取
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        # 从meta标签获取
        lang_meta = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if lang_meta and lang_meta.get('content'):
            return lang_meta.get('content')
        
        return 'unknown'
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """提取图片URL"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                images.append(src)
        return images[:10]  # 限制数量
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """提取链接"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href.startswith('http'):
                links.append(href)
        return links[:20]  # 限制数量
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """提取meta标签"""
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                meta_tags[name] = content
        
        return meta_tags
    
    def is_valid_url(self, url: str) -> bool:
        """检查URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def get_domain(self, url: str) -> str:
        """获取域名"""
        try:
            return urlparse(url).netloc
        except:
            return ""
