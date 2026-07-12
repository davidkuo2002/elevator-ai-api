
#掃描檔視覺轉譯程式#

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
            
            # --- 具備防爆與智慧重試機制的迴圈 ---
            for page_num in range(len(doc)):
                # 將 PDF 每頁轉為高解析度圖片
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                base64_image = base64.b64encode(img_data).decode("utf-8")
                
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": "這是一份電梯維修手冊/報告的掃描檔。請仔細閱讀圖片中的文字，並將其完整轉錄為 Markdown 格式。要求：1. 保留原有的標題結構。2. 故障碼與解決方法盡量用清單整理。3. 不要自行添加文件中沒有的資訊。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                    ]
                )
                
                # 🛡️ 智慧重試機制 (最多重試 3 次)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        print(f"  👉 正在處理第 {page_num + 1}/{len(doc)} 頁...")
                        response = llm.invoke([message])
                        full_md.append(f"## Page {page_num + 1}\n\n" + response.content)
                        
                        # 基礎冷卻時間調高到 5 秒 (確保 60秒內不超過 12次，安全避開 15次上限)
                        time.sleep(5) 
                        break # 成功就跳出重試迴圈
                        
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "429" in error_msg or "quota" in error_msg or "resourceexhausted" in error_msg:
                            print(f"  ⚠️ 觸發 API 流量限制！強制冷卻 30 秒後重試 (第 {attempt + 1}/{max_retries} 次)...")
                            time.sleep(30)
                        else:
                            print(f"  ❌ 第 {page_num + 1} 頁發生未知錯誤: {e}")
                            full_md.append(f"\n\n## Page {page_num + 1}\n\n[ 系統提示：解析此頁時發生未知錯誤，請人工確認 ]\n\n")
                            break # 非流量問題，直接跳出不重試
                else:
                    # 如果重試 3 次都失敗，才真的放棄這頁
                    print(f"  🛑 第 {page_num + 1} 頁重試達上限，已跳過。")
                    full_md.append(f"\n\n## Page {page_num + 1}\n\n[ 系統提示：觸發流量限制重試達上限，此頁跳過 ]\n\n")
            
            # 合併分頁並存檔
            base_name = os.path.basename(pdf_path)
            md_filename = base_name.replace(".pdf", ".md")
            output_path = os.path.join("manuals", md_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(full_md))
                
            print(f"✅ 成功產出: {output_path}")
            
        # 這裡就是剛剛不小心被刪掉的 except 區塊！
        except Exception as e:
            print(f"⚠️ 轉換 {pdf_path} 時發生錯誤: {e}")

if __name__ == "__main__":
    convert_scanned_pdf_to_md_langchain()