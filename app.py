import os
import pickle
import streamlit as st
from dotenv import load_dotenv
import utils 
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers import EnsembleRetriever 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 載入環境變數
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# 網頁基本設定（手機優化寬度）
st.set_page_config(page_title="電梯維修 AI 專家", page_icon="🛗", layout="centered")

# --- 狀態管理 (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'machine_model' not in st.session_state:
    st.session_state.machine_model = "CHIMAX"
if 'error_code' not in st.session_state:
    st.session_state.error_code = ""
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = ""

# --- 快取載入知識庫 ---
@st.cache_resource
def load_knowledge_base():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=API_KEY)
        faiss_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        faiss_retriever = faiss_db.as_retriever(search_kwargs={"k": 4}) # k=4 提供更多上下文 [cite: 3, 14]
        
        with open("bm25_retriever.pkl", "rb") as f:
            bm25_retriever = pickle.load(f)
        bm25_retriever.k = 4         
        
        # 權重調整：BM25 佔 0.7，強化精準故障碼匹配 [cite: 4]
        retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.7, 0.3])
        return retriever
    except Exception as e:
        st.error(f"知識庫載入失敗: {e}")
        return None

global_retriever = load_knowledge_base()

# --- AI 核心處理邏輯 ---
def invoke_expert_ai(user_query: str, retriever):
    retrieved_docs = retriever.invoke(user_query)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=API_KEY)
    prompt_template = ChatPromptTemplate.from_template( 
        "你是一位具備 20 年經驗的資深電梯維修專家。請『嚴格根據以下提供的手冊參考資料』，詳細、專業且有條理地協助現場維修人員。\n"
        "如果參考資料中沒有提到，請回答「手冊中未提及此狀況，請聯絡原廠支援」，絕不能自行編造內容。\n\n"
        "請『務必』依照以下結構詳細回覆：\n"
        "1. 🚨 **安全確認**：執行此維修前，必須注意的安全事項。\n"
        "2. 🔍 **故障確診與原因**：請先明確指出該故障碼在手冊中的「正式定義」，接著列出所有可能原因。\n"
        "3. 🛠️ **逐步檢查與排除流程**：提供具體、按順序的維修與測試步驟。\n"
        "4. 💡 **後續觀察建議**：維修完成後，應如何進行測試以確認問題解決。\n\n"
        "【手冊參考資料】：\n{context}\n\n"
        "【現場狀況】：\n{question}"
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"context": context_text, "question": user_query})


# --- UI 介面：分步導覽 (Wizard) ---
st.title("🛗 電梯 AI 專家系統")
st.progress(st.session_state.step / 3, text=f"目前進度：第 {st.session_state.step} / 3 步")

# 步驟 1：選擇電梯機型
if st.session_state.step == 1:
    st.header("步驟 1：選擇電梯機型")
    AVAILABLE_MODELS = ["CHIMAX", "HPM", "IDE"]
    current_model = st.session_state.machine_model
    
    # 防呆機制：若暫存機型不在選單中，fallback 至 index 0 [cite: 13]
    default_index = AVAILABLE_MODELS.index(current_model) if current_model in AVAILABLE_MODELS else 0
        
    selected_model = st.selectbox("電梯機型", AVAILABLE_MODELS, index=default_index)
    if st.button("下一步：輸入故障資訊 ➡️", use_container_width=True):
        st.session_state.machine_model = selected_model
        st.session_state.step = 2
        st.rerun()

# 步驟 2：現場狀況回報
elif st.session_state.step == 2:
    st.header("步驟 2：現場狀況回報")
    error_code_input = st.text_input("主機板/變頻器故障碼", value=st.session_state.error_code)
    symptoms_input = st.text_area("現場情況描述", value=st.session_state.symptoms)
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 回上一步", use_container_width=True):
            st.session_state.step = 1  
            st.rerun()
    with col2:
        if st.button("🚀 開始診斷", type="primary", use_container_width=True):
            st.session_state.error_code = error_code_input
            st.session_state.symptoms = symptoms_input
            st.session_state.step = 3
            st.rerun()

# 步驟 3：AI 診斷結果
elif st.session_state.step == 3:
    st.header("步驟 3：AI 診斷結果")
    if global_retriever is None:   
        st.error("知識庫未載入。")
    else:
        with st.spinner("AI 專家正在診斷中..."):
            try:
                user_query = f"機型：{st.session_state.machine_model}，故障碼：{st.session_state.error_code}，症狀：{st.session_state.symptoms}"
                advice = invoke_expert_ai(user_query, global_retriever)
                st.success("✅ 診斷完成")               
                st.info(advice)
            except Exception as e:
                # 終極防護：轉大寫後比對是否有流量限制錯誤碼
                error_msg = str(e).upper()
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.warning("⚠️ 目前系統使用人數較多 (已達免費 AI 額度上限)，請稍等 30 秒後再試一次！")
                else:
                    st.error("❌ 診斷過程發生錯誤")
                    st.code(str(e))
                    
    if st.button("🔄 處理下一台電梯", use_container_width=True):
        st.session_state.error_code = ""
        st.session_state.symptoms = ""
        st.session_state.step = 1
        st.rerun()
