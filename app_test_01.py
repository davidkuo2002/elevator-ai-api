import os
import pickle
import streamlit as st
from dotenv import load_dotenv
import utils 

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# 就是這一行！請確保它是從 langchain.retrievers 引入
from langchain_classic.retrievers import EnsembleRetriever



from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ... 下面接著你的初始化與載入邏輯


# 1. 初始化與環境變數
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="電梯維修 AI 專家", page_icon="🛗")

# 2. 快取載入知識庫 (避免每次點擊都重新讀取，保護你的記憶體)
@st.cache_resource
def load_knowledge_base():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=API_KEY
        )
        faiss_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        faiss_retriever = faiss_db.as_retriever(search_kwargs={"k": 2}) 
        
        with open("bm25_retriever.pkl", "rb") as f:
            bm25_retriever = pickle.load(f)
        bm25_retriever.k = 2
        
        retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.4, 0.6])
        print("✅ Streamlit 知識庫掛載成功！")
        return retriever
    except Exception as e:
        st.error(f"知識庫載入失敗: {e}")
        return None

global_retriever = load_knowledge_base()

# 3. AI 核心處理邏輯 (移除 tenacity 重試，讓錯誤能直接顯示在網頁上)
def invoke_expert_ai(user_query: str, retriever):
    retrieved_docs = retriever.invoke(user_query)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=API_KEY)
    prompt_template = ChatPromptTemplate.from_template(
        "你是一位資深的電梯維修專家。請『嚴格根據以下提供的手冊參考資料』，回答維修人員的問題。\n"
        "如果參考資料中沒有提到，請回答「手冊中未提及此狀況，請聯絡原廠支援」，不要自己瞎猜。\n\n"
        "【手冊參考資料】：\n{context}\n\n"
        "【現場狀況】：\n{question}"
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"context": context_text, "question": user_query})

# 4. 前端 UI 介面
st.title("🛗 電梯 AI 專家系統")
st.markdown("資深維修人員的智慧輔助工具")

with st.form("repair_form"):
    machine_model = st.selectbox("機型", ["Hitachi-V2", "Mitsubishi-A1", "Generic-Standard"])
    error_code = st.text_input("故障碼", placeholder="例如：E32")
    symptoms = st.text_area("症狀描述", placeholder="例如：門無法完全關閉，且伴隨異音")
    submit_button = st.form_submit_button(label="🚀 開始分析")

if submit_button:
    if not error_code or not symptoms:
        st.warning("請至少輸入故障碼與症狀！")
    elif global_retriever is None:
        st.error("系統尚未準備好（知識庫未載入），請檢查後台設定。")
    else:
        with st.spinner("AI 專家正在翻閱手冊與診斷中..."):
            try:
                user_query = f"機型：{machine_model}，故障碼：{error_code}，症狀：{symptoms}"
                advice = invoke_expert_ai(user_query, global_retriever)
                st.success("診斷完成")
                st.markdown("### 🛠️ 維修建議")
                st.write(advice)
            except Exception as e:
                # 這裡如果出錯，會把最真實的錯誤直接印在網頁上，不再是看不懂的 RetryError
                st.error("❌ 診斷過程發生錯誤")
                st.code(str(e))
