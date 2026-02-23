import os
import streamlit as st
from chains import EmailGenerator
from langchain_community.document_loaders import WebBaseLoader

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

st.set_page_config(layout="wide", page_title="AI Cold Email Gen", page_icon="📧")

# --- Enhanced Modern SaaS CSS ---

# st.markdown("""
# <style>
# /* 1. Page Background */
# .stApp {
#     background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
#     color: #f8fafc;
# }

# /* 2. Compact Chat Container - Reduced width to 500px */
# .chat-container {
#     max-width: 500px; /* This makes the interface "Small" */
#     margin: 20px auto;
#     padding: 15px;
#     background: rgba(255, 255, 255, 0.05);
#     backdrop-filter: blur(12px);
#     border: 1px solid rgba(255, 255, 255, 0.1);
#     border-radius: 20px;
#     box-shadow: 0 15px 35px rgba(0,0,0,0.4);
# }

# /* 3. User Bubble - Smaller padding and font */
# .user-bubble {
#     padding: 10px 15px;
#     margin: 8px 0 8px auto;
#     border-radius: 18px 18px 0px 18px;
#     background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
#     color: white;
#     max-width: 85%; /* Allows it to take more space relative to the small container */
#     font-size: 13px;
#     display: block;
# }

# /* 4. Bot Bubble - Compact and Clean */
# .bot-bubble {
#     padding: 15px;
#     margin: 8px auto 8px 0;
#     border-radius: 18px 18px 18px 0px;
#     background: #ffffff;
#     color: #1e293b;
#     max-width: 90%;
#     font-size: 13px;
#     line-height: 1.5;
#     display: block;
#     border-left: 4px solid #3b82f6;
# }

# /* 5. Compact Button */
# .stButton>button {
#     background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
#     color: white;
#     font-weight: bold;
#     border-radius: 10px;
#     padding: 8px 20px;
#     border: none;
#     width: 100%;
#     font-size: 14px;
# }

# /* 6. Textarea refinement */
# textarea {
#     background-color: #1e293b !important;
#     color: #f8fafc !important;
#     border: 1px solid #334155 !important;
#     border-radius: 12px !important;
#     font-size: 13px !important;
# }
# </style>
# """, unsafe_allow_html=True)


def main():
    st.markdown("<h1 style='text-align: center; color: black; font-size: 20px'> AI Cold Email Generator</h1>", unsafe_allow_html=True)
    # st.markdown("<p style='text-align: center; color: #94a3b8;'>AtliQ Technologies Sales Acceleration Tool</p>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        tone = st.selectbox("Select Email Tone", ["Professional", "Witty", "Urgent"])
        use_url = st.checkbox("Scrape Job Description from URL")
        st.info("Uses RAG to match portfolio case studies.")

    # Job description input
    job_desc = ""
    if use_url:
        url_input = st.text_input("Enter Job Posting URL:")
        if url_input:
            try:
                with st.spinner("Scraping job details..."):
                    loader = WebBaseLoader(url_input)
                    page_data = loader.load().pop().page_content
                    job_desc = st.text_area("Scraped Content:", value=page_data, height=150)
            except Exception as e:
                st.error(f"Scraping failed: {e}")
    else:
        job_desc = st.text_area("Paste Job Description here:", height=150)

    # Execution
    if st.button("🚀 Generate Personalized Email"):
        if job_desc.strip():
            try:
                with st.spinner("Searching and drafting..."):
                    gen = EmailGenerator()
                    email_content = gen.generate_email(job_desc, tone)

                    # Wrap bubbles in the container
                    st.markdown('<div class="chat-container chat-box">', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="user-bubble"><strong>Target Role:</strong><br>{job_desc[:200]}...</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="bot-bubble"><strong>Generated Draft:</strong><br><br>{email_content}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Download Email",
                        data=email_content,
                        file_name="atliq_cold_email.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please provide a job description.")

if __name__ == "__main__":
    main()