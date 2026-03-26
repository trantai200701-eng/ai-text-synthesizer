import streamlit as st
from google import genai # Đã đổi sang thư viện mới

# ==========================================
# MODULE 1: DATA PROCESSING & ERROR HANDLING
# ==========================================
def process_uploaded_files(uploaded_files):
    valid_data = []
    error_logs = []

    for file in uploaded_files:
        try:
            bytes_data = file.read()
            text_content = bytes_data.decode("utf-8")
            
            if not text_content.strip():
                error_logs.append(f"Warning: File '{file.name}' is empty and was skipped.")
                continue
                
            valid_data.append({
                "filename": file.name,
                "content": text_content.strip()
            })
            
        except UnicodeDecodeError:
            error_logs.append(f"Error: File '{file.name}' is not a valid UTF-8 text file.")
        except Exception as e:
            error_logs.append(f"Unexpected error with file '{file.name}': {str(e)}")

    return valid_data, error_logs

# ==========================================
# MODULE 2: AI SUMMARIZATION ENGINE (CẬP NHẬT)
# ==========================================
def synthesize_with_ai(parsed_data, api_key):
    if not parsed_data:
        return "No valid text data to synthesize."

    combined_text = "\n\n".join([f"--- Nguồn {data['filename']} ---\n{data['content']}" for data in parsed_data])
    
    prompt = f"""
    Bạn là một trợ lý tổng hợp thông tin chuyên nghiệp. 
    Dưới đây là các đoạn văn bản được trích xuất từ nhiều file khác nhau.
    Nhiệm vụ của bạn là:
    1. Đọc và hiểu toàn bộ nội dung.
    2. Viết một đoạn tóm tắt ngắn gọn, mạch lạc bằng tiếng Việt, gom nhóm các thông tin có liên quan lại với nhau.
    3. Trích xuất 3-5 từ khóa quan trọng nhất từ các văn bản này.

    Văn bản cần xử lý:
    {combined_text}
    """

    try:
        # Sử dụng cú pháp của thư viện google-genai mới
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Lỗi khi gọi API AI: {str(e)}\nVui lòng kiểm tra lại API Key hoặc kết nối mạng."

# ==========================================
# MODULE 3: STREAMLIT USER INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="AI Text Synthesizer", page_icon="🧠", layout="centered")
    
    with st.sidebar:
        st.header("⚙️ Cấu hình AI")
        api_key = st.text_input("Nhập Gemini API Key của bạn:", type="password")
        st.markdown("[Lấy API Key tại đây](https://aistudio.google.com/app/apikey)")

    st.title("🧠 AI Multi-File Text Synthesizer")
    st.markdown("Tải lên các file `.txt`. Hệ thống sẽ dùng **Google Gemini AI** để đọc hiểu và tổng hợp nội dung.")

    uploaded_files = st.file_uploader("Chọn tệp .txt", type=["txt"], accept_multiple_files=True)

    if uploaded_files:
        st.info(f"Đã chọn {len(uploaded_files)} tệp.")
        
        if st.button("Tổng hợp bằng AI", type="primary"):
            if not api_key:
                st.error("Vui lòng nhập API Key ở thanh công cụ bên trái (Sidebar) trước khi chạy.")
                return

            with st.spinner("AI đang đọc và tổng hợp dữ liệu..."):
                parsed_data, error_logs = process_uploaded_files(uploaded_files)
                
                if error_logs:
                    for error in error_logs:
                        st.warning(error)
                
                if parsed_data:
                    final_result = synthesize_with_ai(parsed_data, api_key)
                    
                    st.success("Tổng hợp hoàn tất!")
                    st.subheader("Kết quả từ AI:")
                    st.markdown(final_result) 
                    
                    st.download_button(
                        label="Tải kết quả xuống",
                        data=final_result,
                        file_name="ai_synthesized_output.txt",
                        mime="text/plain"
                    )

if __name__ == "__main__":
    main()