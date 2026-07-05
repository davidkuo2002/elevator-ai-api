import os
import pickle
import streamlit as st
from dotenv import load_dotenv
import utils 

# 導入 Google API 例外處理模組 (用來攔截 429 錯誤)
import google.api_core.exceptions

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers import EnsembleRetriever 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. 初始化與環境變數 ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="電梯維修 AI 專家", page_icon="🛗", layout="centered")

# --- 2. 狀態管理 (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'machine_model' not in st.session_state:
    st.session_state.machine_model = "CHIMAX"
if 'error_code' not in st.session_state:
    st.session_state.error_code = ""
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = ""

# --- 3. 快取載入知識庫 ---
@st.cache_resource
def load_knowledge_base():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=API_KEY
        )
        faiss_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        faiss_retriever = faiss_db.as_retriever(search_kwargs={"k": 4}) 
        
        with open("bm25_retriever.pkl", "rb") as f:
            bm25_retriever = pickle.load(f)
        bm25_retriever.k = 4
        
        retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever], 
            weights=[0.7, 0.3] 
        )
        return retriever
    except Exception as e:
        st.error(f"知識庫載入失敗: {e}")
        return None

global_retriever = load_knowledge_base()

# --- 4. AI 核心處理邏輯 (極簡精準版 + 除錯模式) ---
def invoke_expert_ai(user_query: str, retriever):
    retrieved_docs = retriever.invoke(user_query)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 開發者除錯：印出 AI 實際拿到的手冊內容
    st.info(f"🕵️‍♂️ [開發者除錯] AI 拿到的手冊內容：\n{context_text}")
    
    # 溫度設為 0.1，讓 AI 回答極度精確、不加料
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=API_KEY,
        temperature=0.1 
    )
    
    prompt_template = ChatPromptTemplate.from_template(
        "你是一位極度講求效率的電梯維修專家。請『嚴格根據以下提供的手冊參考資料』，給出最扼要、精準的回答。\n"
        "如果參考資料沒有提到，只能回答「手冊未提及此狀況，請聯絡原廠支援」，絕不盲目猜測。\n\n"
        "【輸出嚴格規則】：\n"
        "1. 零廢話：不需要問候語、前言或結語，直接給答案。\n"
        "2. 極簡條列：只列出「核心原因」與「關鍵處置動作」。\n"
        "3. 數據優先：如果有提到電壓、接點編號或特定零件，必須優先列出。\n\n"
        "【手冊參考資料】：\n{context}\n\n"
        "【現場狀況】：\n{question}"
    )
    
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"context": context_text, "question": user_query})

# ==========================================
# --- 5. UI 介面：分步導覽 (Wizard) 邏輯 ---
# ==========================================

st.title("🛗 電梯 AI 專家系統")
progress_text = f"目前進度：第 {st.session_state.step} / 3 步"
st.progress(st.session_state.step / 3, text=progress_text)

# ------------------------------------------
# 第一頁：選擇系統 (機型)
# ------------------------------------------
if st.session_state.step == 1:
    st.header("步驟 1：選擇電梯機型")
    
    AVAILABLE_MODELS = ["CHIMAX", "HPM", "IDE"]
    current_model = st.session_state.machine_model
    default_index = AVAILABLE_MODELS.index(current_model) if current_model in AVAILABLE_MODELS else 0
    
    selected_model = st.selectbox(
        "電梯機型", 
        AVAILABLE_MODELS,
        index=default_index
    )
    
    if st.button("下一步：輸入故障資訊 ➡️", use_container_width=True):
        st.session_state.machine_model = selected_model
        st.session_state.step = 2
        st.rerun()

# ------------------------------------------
# 第二頁：輸入故障碼與現場狀況
# ------------------------------------------
elif st.session_state.step == 2:
    st.header("步驟 2：現場狀況回報")
    st.markdown(f"**目前機型：** `{st.session_state.machine_model}`")
    
    error_code_input = st.text_input("主機板/變頻器故障碼", value=st.session_state.error_code, placeholder="例如：E32")
    symptoms_input = st.text_area("現場情況描述", value=st.session_state.symptoms, placeholder="例如：門無法完全關閉，且伴隨異音")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 回上一步", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🚀 開始診斷", type="primary", use_container_width=True):
            if not error_code_input and not symptoms_input:
                st.error("⚠️ 請至少輸入故障碼或現場情況，AI 才能幫您診斷！")
            else:
                st.session_state.error_code = error_code_input
                st.session_state.symptoms = symptoms_input
                st.session_state.step = 3
                st.rerun()

# ------------------------------------------
# 第三頁：顯示查詢結果
# ------------------------------------------
elif st.session_state.step == 3:
    st.header("步驟 3：AI 診斷結果")
    
    with st.expander("📝 檢視您輸入的查詢條件", expanded=False):
        st.write(f"- **機型：** {st.session_state.machine_model}")
        st.write(f"- **故障碼：** {st.session_state.error_code or '無'}")
        st.write(f"- **症狀：** {st.session_state.symptoms or '無'}")
    
    if global_retriever is None:
        st.error("系統尚未準備好（知識庫未載入），請檢查後台設定。")
    else:
        with st.spinner("AI 專家正在翻閱手冊與診斷中..."):
            try:
                user_query = f"機型：{st.session_state.machine_model}，故障碼：{st.session_state.error_code}，症狀：{st.session_state.symptoms}"
                advice = invoke_expert_ai(user_query, global_retriever)
                
                st.success("✅ 診斷完成")
                st.markdown("### 🛠️ 維修建議")
                st.info(advice)
                
            # 專門攔截 Google API 額度用盡的錯誤
            except google.api_core.exceptions.ResourceExhausted:
                st.error("⏳ 系統目前查詢人數較多（API 頻率限制），請等待 1 分鐘後再重新點擊診斷！")
            # 攔截其他未知錯誤
            except Exception as e:
                st.error("❌ 診斷過程發生未知的系統錯誤")
                st.code(str(e))
    
    st.divider() 
    if st.button("🔄 處理下一台電梯 (重新開始)", use_container_width=True):
        st.session_state.error_code = ""
        st.session_state.symptoms = ""
        st.session_state.step = 1
        st.rerun()