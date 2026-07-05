import os
import pickle
import jieba
import __main__  # <--- 新增這行：引入系統最底層的主程式空間

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# --- 引入 LangChain 核心與檢索套件 ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("找不到 GOOGLE_API_KEY，請確認 .env 檔案是否設定正確！")

# ==========================================
# 魔法指令：把函數強行塞進 Uvicorn 的主程式空間，騙過 pickle！
def chinese_tokenizer(text):
    return list(jieba.cut(text))

__main__.chinese_tokenizer = chinese_tokenizer  # <--- 關鍵就是這行！
# ==========================================

app = FastAPI(title="電梯 AI 專家系統 API", version="1.0.0")

# ... 下面的 @app.on_event("startup") 等程式碼維持原樣不動 ...


# 全域變數，用來存放混合檢索器
global_retriever = None

# --- 1. 伺服器啟動時：預先掛載知識庫 ---
@app.on_event("startup")
async def startup_event():
    global global_retriever
    print("====== 正在掛載本地知識庫 ======")
    try:
        # A. 載入 Embedding 模型
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=API_KEY)
        
        # B. 載入 FAISS 向量庫
        faiss_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        faiss_retriever = faiss_db.as_retriever(search_kwargs={"k": 2}) 
        
        # C. 載入 BM25 關鍵字庫
        with open("bm25_retriever.pkl", "rb") as f:
            bm25_retriever = pickle.load(f)
        bm25_retriever.k = 2
        
        # D. 建立混合檢索器
        global_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever], 
            weights=[0.4, 0.6]
        )
        print("✅ 知識庫掛載成功！AI 已經準備好讀取手冊了。")
    except Exception as e:
        print(f"❌ 知識庫掛載失敗: {e}")

# --- 2. 定義防爆重試的 AI 呼叫邏輯 ---
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=8))
def invoke_expert_ai(user_query: str):
    if not global_retriever:
        raise Exception("知識庫尚未載入完成，請稍後再試。")

    # 檢索資料庫
    retrieved_docs = global_retriever.invoke(user_query)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    print(f"\n[後台檢索結果] 找到以下參考資料：\n{context_text}\n")

            
    # ✅ 換成這行最新世代的模型
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=API_KEY)
    
    prompt_template = ChatPromptTemplate.from_template(
        "你是一位資深的電梯維修專家。請『嚴格根據以下提供的手冊參考資料』，回答維修人員的問題。\n"
        "如果參考資料中沒有提到，請回答「手冊中未提及此狀況，請聯絡原廠支援」，不要自己瞎猜。\n\n"
        "【手冊參考資料】：\n{context}\n\n"
        "【現場狀況】：\n{question}"
    )

    
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"context": context_text, "question": user_query})

# --- 3. 定義 API 路由 ---
class RepairRequest(BaseModel):
    error_code: str = Field(..., description="電梯故障代碼", example="E32")
    symptoms: str = Field(default="", description="現場異常現象", example="門無法完全關閉")
    machine_model: str = Field(default="Hitachi-V2", description="電梯型號")

class RepairResponse(BaseModel):
    advice: str
    status: str

@app.post("/api/v1/repair-advice", response_model=RepairResponse)
async def get_repair_advice(request: RepairRequest):
    try:
        user_query = f"機型：{request.machine_model}，故障碼：{request.error_code}，症狀：{request.symptoms}"
        ai_response = invoke_expert_ai(user_query)
        return RepairResponse(advice=ai_response, status="success")
    except Exception as e:
        # 修正重點：強制在終端機印出詳細的錯誤紅字，不讓 FastAPI 隱藏它
        import traceback
        traceback.print_exc() 
        
        raise HTTPException(status_code=500, detail=f"系統錯誤：{str(e)}")
