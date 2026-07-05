import os
import pickle
import streamlit as st
from dotenv import load_dotenv
import utils 

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
# 確保使用我們剛剛修正的正確套件路徑
from langchain_classic.retrievers import EnsembleRetriever 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. 初始化與環境變數 ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="電梯維修 AI 專家", page_icon="🛗", layout="centered")

# --- 2. 狀態管理 (Session State) ---
# 用來記住目前在哪一頁，以及使用者輸入的資料
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
        
        retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.7, 0.3])
        return retriever
    except Exception as e:
        st.error(f"知識庫載入失敗: {e}")
        return None

global_retriever = load_knowledge_base()

# --- 4. AI 核心處理邏輯 ---
def invoke_expert_ai(user_query: str, retriever):
    retrieved_docs = retriever.invoke(user_query)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=API_KEY)
    prompt_template = ChatPromptTemplate.from_template(
        "你是一位具備 20 年經驗的資深電梯維修專家。請『嚴格根據以下提供的手冊參考資料』，詳細、專業且有條理地協助現場維修人員。\n"
        "如果參考資料中沒有提到相關資訊，請回答「手冊中未提及此狀況，請聯絡原廠支援」，絕不能自行編造內容（禁止幻覺）。\n\n"
        "為了讓現場技師能快速且安全地執行，請『務必』依照以下結構詳細回覆：\n"
        "1. 🚨 **安全確認**：執行此維修前，必須注意的安全事項（例如：是否需先切斷主電源、確認車廂位置等）。\n"
        "2. 🔍 **故障確診與原因**：請先明確指出該故障碼在手冊中的「正式定義」，接著詳細列出導致此故障的所有可能原因。\n" # <--- 這裡微調了
        "3. 🛠️ **逐步檢查與排除流程**：提供具體、按順序（Step-by-Step）的維修與測試步驟。請盡量詳細說明該量測哪個接點、期待的數值為何等細節。\n"
        "4. 💡 **後續觀察建議**：維修完成後，應如何進行測試以確認問題已徹底解決。\n\n"
        "【手冊參考資料】：\n{context}\n\n"
        "【現場狀況】：\n{question}"
    )



    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"context": context_text, "question": user_query})

# ==========================================
# --- 5. UI 介面：分步導覽 (Wizard) 邏輯 ---
# ==========================================

st.title("🛗 電梯 AI 專家系統")

# 顯示進度條
progress_text = f"目前進度：第 {st.session_state.step} / 3 步"
st.progress(st.session_state.step / 3, text=progress_text)

# ------------------------------------------
# 第一頁：選擇系統 (機型)
# ------------------------------------------
if st.session_state.step == 1:
    st.header("步驟 1：選擇電梯機型")
    st.markdown("請確認您目前正在維修的電梯系統。")
    
    selected_model = st.selectbox(
        "電梯機型", 
        ["CHIMAX", "HPM", "IDE"],
        index=["CHIMAX", "HPM", "IED"].index(st.session_state.machine_model)
    )
    
    # 佔滿寬度的大按鈕，方便戴手套點擊
    if st.button("下一步：輸入故障資訊 ➡️", use_container_width=True):
        st.session_state.machine_model = selected_model
        st.session_state.step = 2
        st.rerun() # 強制重新整理畫面進入下一頁

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
    
    # 顯示使用者剛剛輸入的摘要
    with st.expander("📝 檢視您輸入的查詢條件", expanded=False):
        st.write(f"- **機型：** {st.session_state.machine_model}")
        st.write(f"- **故障碼：** {st.session_state.error_code or '無'}")
        st.write(f"- **症狀：** {st.session_state.symptoms or '無'}")
    
    # 開始呼叫 AI 進行診斷
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
            except Exception as e:
                st.error("❌ 診斷過程發生錯誤")
                st.code(str(e))
    
    st.divider() # 分隔線
    if st.button("🔄 處理下一台電梯 (重新開始)", use_container_width=True):
        # 清空資料並回到第一頁
        st.session_state.error_code = ""
        st.session_state.symptoms = ""
        st.session_state.step = 1
        st.rerun()
