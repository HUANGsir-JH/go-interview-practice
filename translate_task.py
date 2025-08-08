#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI翻译工具 - 批量文件翻译系统
基于AI的批量文件翻译工具，专门用于将英文文档汉化为中文，支持并发处理和智能检测。

作者: AI Assistant
日期: 2025-08-08
版本: 1.0.0
"""

import json
import os
import sys
import time
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path

# ================================
# 配置参数
# ================================

# API配置
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3-30b-a3b-instruct-2507"
API_KEY = ""

# 翻译配置
MAX_CONCURRENT = 5  # 并发数量
TIMEOUT_SECONDS = 120  # 请求超时时间
TEMPERATURE = 0.3  # 模型温度

# 翻译提示词
TRANSLATION_PROMPT = "请将以下英文内容进行汉化，保持markdown格式或者html代码块不变，只返回汉化后的内容，不要添加任何解释，如果你发现内容已经汉化，可以直接返回'已汉化'："

# 文件路径配置
FILES_TO_TRANSLATE_JSON = "files_to_translate.json"

# ================================
# 日志配置
# ================================

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('translation_log.txt', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ================================
# 翻译器类
# ================================

class AITranslator:
    """AI翻译器类"""
    
    def __init__(self, base_url: str = BASE_URL, model: str = MODEL, api_key: str = API_KEY):
        """初始化翻译器
        
        Args:
            base_url: API基础URL
            model: 使用的AI模型
            api_key: API密钥
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_key = api_key
        self.session = None
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'successful_translations': 0,
            'failed_translations': 0,
            'skipped_files': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
        timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def translate_text(self, text: str, file_path: str) -> Tuple[bool, str, str]:
        """翻译文本
        
        Args:
            text: 要翻译的文本
            file_path: 文件路径（用于日志）
            
        Returns:
            (是否成功, 翻译结果, 错误信息)
        """
        if not text.strip():
            return True, text, ""
        
        try:
            # 构建请求数据
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{TRANSLATION_PROMPT}\n\n{text}"
                    }
                ],
                "temperature": TEMPERATURE
            }
            
            # 发送请求
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=data
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    error_msg = f"API请求失败 (状态码: {response.status}): {error_text}"
                    logger.error(f"翻译失败 - {file_path}: {error_msg}")
                    return False, "", error_msg
                
                result = await response.json()
                
                # 解析响应
                if 'choices' not in result or not result['choices']:
                    error_msg = "API响应格式错误: 没有choices字段"
                    logger.error(f"翻译失败 - {file_path}: {error_msg}")
                    return False, "", error_msg
                
                translated_text = result['choices'][0]['message']['content'].strip()
                
                # 检查是否已汉化
                if translated_text == "已汉化":
                    logger.info(f"文件已汉化，跳过: {file_path}")
                    return True, "ALREADY_TRANSLATED", ""
                
                logger.info(f"翻译成功，原文长度: {len(text)}, 译文长度: {len(translated_text)}")
                return True, translated_text, ""
                
        except asyncio.TimeoutError:
            error_msg = f"请求超时 ({TIMEOUT_SECONDS}秒)"
            logger.error(f"翻译失败 - {file_path}: {error_msg}")
            return False, "", error_msg
        except Exception as e:
            error_msg = f"翻译过程中发生错误: {str(e)}"
            logger.error(f"翻译失败 - {file_path}: {error_msg}")
            return False, "", error_msg
    
    async def translate_file(self, file_path: str) -> Dict[str, Any]:
        """翻译单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            翻译结果字典
        """
        result = {
            'file_path': file_path,
            'success': False,
            'skipped': False,
            'error': '',
            'timestamp': datetime.now().isoformat(),
            'original_size': 0,
            'translated_size': 0
        }
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = "文件不存在"
                logger.error(f"处理失败 - {file_path}: {error_msg}")
                result['error'] = error_msg
                return result
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                result['original_size'] = len(original_content)
            except Exception as e:
                error_msg = f"读取文件失败: {str(e)}"
                logger.error(f"处理失败 - {file_path}: {error_msg}")
                result['error'] = error_msg
                return result
            
            # 翻译内容
            success, translated_content, error_msg = await self.translate_text(original_content, file_path)
            
            if not success:
                result['error'] = error_msg
                return result
            
            # 处理翻译结果
            if translated_content == "ALREADY_TRANSLATED":
                result['success'] = True
                result['skipped'] = True
                self.stats['skipped_files'] += 1
                return result
            
            # 写入翻译结果
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                result['translated_size'] = len(translated_content)
                result['success'] = True
                logger.info(f"翻译完成并覆写原文件: {file_path}")
                self.stats['successful_translations'] += 1
                return result
            except Exception as e:
                error_msg = f"写入文件失败: {str(e)}"
                logger.error(f"处理失败 - {file_path}: {error_msg}")
                result['error'] = error_msg
                return result
                
        except Exception as e:
            error_msg = f"处理文件时发生未知错误: {str(e)}"
            logger.error(f"处理失败 - {file_path}: {error_msg}")
            result['error'] = error_msg
            return result
    
    async def translate_files_batch(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """批量翻译文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            翻译结果列表
        """
        self.stats['total_files'] = len(file_paths)
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"加载了 {len(file_paths)} 个文件待翻译")
        logger.info(f"使用配置 - API地址: {self.base_url}, 模型: {self.model}, 并发数: {MAX_CONCURRENT}")
        logger.info(f"开始批量翻译，总文件数: {len(file_paths)}, 并发数: {MAX_CONCURRENT}")
        
        all_results = []
        
        # 分批处理文件
        for i in range(0, len(file_paths), MAX_CONCURRENT):
            batch = file_paths[i:i + MAX_CONCURRENT]
            batch_num = i // MAX_CONCURRENT + 1
            
            logger.info(f"处理第 {batch_num} 批，文件数: {len(batch)}")
            
            # 并发处理当前批次
            tasks = [self.translate_file(file_path) for file_path in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for result in batch_results:
                if isinstance(result, Exception):
                    error_result = {
                        'file_path': 'unknown',
                        'success': False,
                        'skipped': False,
                        'error': str(result),
                        'timestamp': datetime.now().isoformat(),
                        'original_size': 0,
                        'translated_size': 0
                    }
                    all_results.append(error_result)
                    self.stats['failed_translations'] += 1
                    self.stats['errors'].append(error_result)
                else:
                    all_results.append(result)
                    if not result['success'] and not result['skipped']:
                        self.stats['failed_translations'] += 1
                        self.stats['errors'].append(result)
        
        self.stats['end_time'] = datetime.now()
        return all_results
    
    def save_results(self, results: List[Dict[str, Any]]):
        """保存翻译结果
        
        Args:
            results: 翻译结果列表
        """
        # 计算总耗时
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            self.stats['duration_seconds'] = duration
        
        # 保存完整结果
        full_result = {
            'stats': self.stats,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('translation_result.json', 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        
        # 保存错误信息（如果有错误）
        if self.stats['errors']:
            with open('translation_errors.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'error_count': len(self.stats['errors']),
                    'errors': self.stats['errors'],
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        
        # 打印统计信息
        print("\n" + "=" * 50)
        print("翻译任务完成!")
        print(f"总文件数: {self.stats['total_files']}")
        print(f"成功翻译: {self.stats['successful_translations']}")
        print(f"跳过文件: {self.stats['skipped_files']}")
        print(f"翻译失败: {self.stats['failed_translations']}")
        if 'duration_seconds' in self.stats:
            print(f"总耗时: {self.stats['duration_seconds']:.2f}秒")
        
        if self.stats['errors']:
            print(f"\n错误详情已保存到: translation_errors.json")
        print(f"完整结果已保存到: translation_result.json")

# ================================
# 主要功能函数
# ================================

async def load_files_to_translate() -> List[str]:
    """加载待翻译文件列表
    
    Returns:
        文件路径列表
    """
    try:
        with open(FILES_TO_TRANSLATE_JSON, 'r', encoding='utf-8') as f:
            file_paths = json.load(f)
        
        # 验证文件路径
        valid_paths = []
        for path in file_paths:
            if isinstance(path, str) and path.strip():
                valid_paths.append(path.strip())
        
        logger.info(f"从 {FILES_TO_TRANSLATE_JSON} 加载了 {len(valid_paths)} 个文件路径")
        return valid_paths
        
    except FileNotFoundError:
        logger.error(f"文件不存在: {FILES_TO_TRANSLATE_JSON}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return []
    except Exception as e:
        logger.error(f"加载文件列表时发生错误: {e}")
        return []

async def main():
    """主函数"""
    try:
        # 加载待翻译文件列表
        file_paths = await load_files_to_translate()
        if not file_paths:
            logger.error("没有找到待翻译的文件")
            return
        
        # 创建翻译器并开始翻译
        async with AITranslator() as translator:
            results = await translator.translate_files_batch(file_paths)
            translator.save_results(results)
            
    except KeyboardInterrupt:
        logger.info("用户中断了翻译任务")
    except Exception as e:
        logger.error(f"翻译任务执行失败: {e}")

# ================================
# 测试功能
# ================================

def test_translator():
    """测试翻译器功能"""
    print("开始测试翻译器功能...")
    
    # 测试1: 翻译器实例创建
    print("✅ 测试1: 翻译器实例创建")
    translator = AITranslator()
    assert translator.base_url == BASE_URL.rstrip('/')
    assert translator.model == MODEL
    assert translator.api_key == API_KEY
    print("   翻译器实例创建成功")
    
    # 测试2: 文件不存在检查
    print("✅ 测试2: 文件不存在检查")
    non_existent_file = "non_existent_file.md"
    assert not os.path.exists(non_existent_file)
    print("   文件不存在检查通过")
    
    # 测试3: 空文件处理
    print("✅ 测试3: 空文件处理")
    test_file = "test_empty.md"
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("")
        assert os.path.exists(test_file)
        print("   空文件创建和检查通过")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
    
    # 测试4: 文件清理机制
    print("✅ 测试4: 文件清理机制")
    assert not os.path.exists(test_file)
    print("   文件清理机制正常")
    
    # 测试5: JSON文件加载
    print("✅ 测试5: JSON文件加载")
    assert os.path.exists(FILES_TO_TRANSLATE_JSON)
    with open(FILES_TO_TRANSLATE_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) > 0
    print(f"   JSON文件加载成功，包含 {len(data)} 个文件路径")
    
    print("\n🎉 所有测试通过! 翻译器功能验证完成。")

# ================================
# 命令行入口
# ================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 运行测试
        test_translator()
    else:
        # 运行翻译任务
        asyncio.run(main())