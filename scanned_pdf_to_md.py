#掃描檔專用轉換腳本 (scanned_pdf_to_md.py)#

import os
import glob
import time
import base64
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ 錯誤：找不到 GOOGLE_API_KEY，請檢查 .env 檔案！")
    exit()

def convert_scanned_pdf_to_md_langchain():
    print("====== 開始使用 LangChain 架構解析掃描檔 ======")
    
    pdf_files = glob.glob("pdfs/*.pdf")
    if not pdf_files:
        print("❌ 找不到任何 PDF 檔案，請確認檔案是否放置於 pdfs/ 資料夾中。")
        return

    os.makedirs("manuals", exist_ok=True)
    
    # 嚴格依照技術手冊的套件呼叫方式，避開 $discovery 臭蟲
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=API_KEY
    )

    for pdf_path in pdf_files:
        print(f"🔄 正在解析: {pdf_path} ...")
        
        try:
            doc = fitz.open(pdf_path)
            full_md = []
            
            for page_num in range(len(doc)):
                # 將 PDF 每頁轉為高解析度圖片
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                base64_image = base64.b64encode(img_data).decode("utf-8")
                
                # 組裝 LangChain 支援的多模態訊息 (文字 + Base64圖片)
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": "這是一份電梯維修手冊/報告的掃描檔。請仔細閱讀圖片中的文字，並將其完整轉錄為 Markdown 格式。要求：1. 保留原有的標題結構。2. 故障碼與解決方法盡量用清單整理。3. 不要自行添加文件中沒有的資訊。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                    ]
                )
                
                # 呼叫 AI 進行視覺解析
                response = llm.invoke([message])
                full_md.append(response.content)
                time.sleep(3) # 防爆冷卻
            
            # 合併分頁並存檔
            base_name = os.path.basename(pdf_path)
            md_filename = base_name.replace(".pdf", ".md")
            output_path = os.path.join("manuals", md_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(full_md))
                
            print(f"✅ 成功產出: {output_path}")
            
        except Exception as e:
            print(f"⚠️ 轉換 {pdf_path} 時發生錯誤: {e}")

if __name__ == "__main__":
    convert_scanned_pdf_to_md_langchain()
