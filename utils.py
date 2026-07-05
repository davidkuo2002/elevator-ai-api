import jieba
import re

def chinese_tokenizer(text):
    """專為電梯手冊 BM25 設計的混合斷詞函數 (保留英數故障碼)"""
    error_codes = re.findall(r'[A-Za-z0-9\-]+', text)
    chinese_words = list(jieba.cut(text))
    combined_tokens = error_codes + chinese_words
    return [token.lower() for token in combined_tokens if token.strip()]
