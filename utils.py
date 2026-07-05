import jieba
import re

def chinese_tokenizer(text):
    """專為電梯手冊 BM25 設計的混合斷詞函數 (保留英數故障碼)"""
    
    # 1. 用正規表達式強制抓出所有英數字組合 (支援包含橫線的格式，如 E32, ERR-01, INV-40)
    # 這確保故障碼絕對不會被切碎
    error_codes = re.findall(r'[A-Za-z0-9\-]+', text)
    
    # 2. 正常使用 jieba 切割中文
    chinese_words = list(jieba.cut(text))
    
    # 3. 合併兩者的結果，並統一轉為小寫
    # 轉小寫很重要！這樣技師輸入 "e32" 也能匹配手冊裡的 "E32"
    combined_tokens = error_codes + chinese_words
    return [token.lower() for token in combined_tokens if token.strip()]
