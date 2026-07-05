import os
import glob
import pickle
import time  # <--- 新增這行：用來讓程式暫停休息
from dotenv import load_dotenv

# 從我們剛剛寫好的 utils 引入斷詞函數
from utils import chinese_tokenizer

# --- 引入 LangChain 知識庫與文本切割套件 ---
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def build_real_knowledge_base():
    print("====== 開始建置真實電梯維修知識庫 ======")
    
    # 1. 抓取 manuals 資料夾下所有的 .md 檔案
    md_files = glob.glob("manuals/*.md")
    
    if not md_files:
        print("❌ 錯誤：在 manuals/ 資料夾中找不到任何 .md 檔案！請確認檔案位置。")
        return

    print(f"📄 找到 {len(md_files)} 個 Markdown 手冊檔案，開始解析...")

    # 2. 定義 Markdown 標題切割規則
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    # 3. 定義內文的二次切割規則
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    all_splits = []

    # 4. 讀取並切割每個檔案
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        md_header_splits = markdown_splitter.split_text(md_text)
        splits = text_splitter.split_documents(md_header_splits)
        
        for split in splits:
            split.metadata["source"] = os.path.basename(file_path)
            
        all_splits.extend(splits)
        
    print(f"✂️ 文件切割完成！總共切出了 {len(all_splits)} 個知識區塊 (Chunks)。")

        # ==========================================
    # 5. 建置 FAISS 向量庫 (終極防爆與冷卻機制)
    # ==========================================
    print("🧠 正在呼叫 Gemini 建立 FAISS 向量索引 (免費版限制嚴格，請耐心等候約 5 分鐘)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=API_KEY)
    
    # 終極保守參數：每次只傳 10 塊，並加入自動重試機制
    # 這樣每分鐘頂多發送 60 次請求，絕對不會超過 100 次的上限！
    batch_size = 10 
    faiss_db = None

    for i in range(0, len(all_splits), batch_size):
        batch = all_splits[i:i + batch_size]
        print(f"🔄 正在上傳第 {i+1} 到 {min(i+batch_size, len(all_splits))} 個區塊...")

        try:
            if faiss_db is None:
                faiss_db = FAISS.from_documents(batch, embeddings)
            else:
                faiss_db.add_documents(batch)
        except Exception as e:
            # 如果還是不小心踩到雷，就直接強迫休息 60 秒 (API 提示需要等 52 秒)
            print(f"⚠️ 觸發 API 限制，強制冷卻 60 秒後自動重試...")
            time.sleep(60)
            if faiss_db is None:
                faiss_db = FAISS.from_documents(batch, embeddings)
            else:
                faiss_db.add_documents(batch)

        # 每個小批次處理完，穩定休息 10 秒
        if i + batch_size < len(all_splits):
            time.sleep(10)

    faiss_db.save_local("faiss_index")
    print("✅ FAISS 向量庫建置並儲存成功！")
    # ==========================================


    # 6. 建置 BM25 關鍵字庫
    print("🔍 正在進行中文斷詞並建置 BM25 檢索器...")
    bm25_retriever = BM25Retriever.from_documents(all_splits, preprocess_func=chinese_tokenizer)
    with open("bm25_retriever.pkl", "wb") as f:
        pickle.dump(bm25_retriever, f)
    print("✅ BM25 檢索器打包成功！")

    print("====== 真實知識庫建置全數完成！ ======")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ 錯誤：找不到 GOOGLE_API_KEY，請檢查 .env 檔案！")
    else:
        build_real_knowledge_base()
