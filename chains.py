# import os
# import pandas as pd
# import chromadb
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_core.prompts import PromptTemplate

# # Load the API key from your .env file for security
# load_dotenv()

# class EmailGenerator:
#     def __init__(self):
#         # 1. Initialize LLM (Llama 3.3 via Groq) 
#         # Using os.getenv ensures your key isn't hardcoded
#         self.llm = ChatGroq(
#             temperature=0, 
#             groq_api_key=os.getenv("GROQ_API_KEY"), 
#             model_name="llama-3.3-70b-versatile"
#         )
        
#         # 2. Initialize Embedding Model (The "Translator") 
#         self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
#         # 3. Initialize Vector Database (The "Memory") 
#         self.chroma_client = chromadb.PersistentClient(path="./vectorstore")
#         self.collection = self.chroma_client.get_or_create_collection(name="portfolio")
        
#         # 4. Load portfolio data if the database is empty [cite: 20, 29]
#         if self.collection.count() == 0:
#             self._load_portfolio_data()

#     def _load_portfolio_data(self):
#         """Helper to populate the vector database from portfolio.csv."""
#         df = pd.read_csv("portfolio.csv")
#         for index, row in df.iterrows():
#             # Create a searchable string combining tech and use case [cite: 22, 23]
#             search_content = f"Tech: {row['Tech Stack']}, Use Case: {row['Use Case']}"
            
#             self.collection.add(
#                 documents=[search_content],
#                 metadatas=[{
#                     "link": row['Link'], 
#                     "results": row['Results']
#                 }],
#                 ids=[str(index)]
#             )

#     def generate_email(self, job_description, tone="Professional"):
#         # 1. Semantic Search for matching project [cite: 16]
#         # n_results=1 ensures we find the "single most relevant case study" [cite: 14]
#         results = self.collection.query(
#             query_texts=[job_description],
#             n_results=1
#         )
        
#         # 2. Cold Start Handling 
#         # Check if the match is relevant enough (lower distance = higher similarity)
#         if not results['documents'][0] or results['distances'][0][0] > 1.5:
#             match_context = "General expertise in software development and problem solving."
#             link = "atliq.com"
#         else:
#             match_context = results['documents'][0][0]
#             link = results['metadatas'][0][0]['link']

#         # 3. Prompt Engineering [cite: 16]
#         template = """
#         ### JOB DESCRIPTION:
#         {job_description}

#         ### RELEVANT EXPERIENCE:
#         AtliQ Technologies project: {match_context}
#         Evidence of success: {link}

#         ### INSTRUCTION:
#         You are the CTO of AtliQ Technologies. Write a cold email to the hiring manager.
#         - Use a {tone} tone[cite: 37].
#         - Explicitly mention the relevant experience above as proof of capability[cite: 16].
#         - Keep the email concise and under 150 words.
#         - Do not include any fake projects or hallucinated links.
#         """
        
#         prompt = PromptTemplate.from_template(template)
        
#         # 4. Orchestration (The "Manager") 
#         chain = prompt | self.llm
#         response = chain.invoke({
#             "job_description": job_description, 
#             "match_context": match_context, 
#             "link": link,
#             "tone": tone
#         })
        
#         return response.content




import os
import pandas as pd
import chromadb
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader

# Load environment variables
load_dotenv()

# Set User Agent for scraping
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# --- Backend: EmailGenerator Class ---
class EmailGenerator:
    def __init__(self):
        # 1. Initialize LLM (Llama 3.3 via Groq)
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_API_KEY"), 
            model_name="llama-3.3-70b-versatile"
        )
        
        # 2. Initialize Embedding Model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 3. Initialize Vector Database
        self.chroma_client = chromadb.PersistentClient(path="./vectorstore")
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")
        
        # 4. Load portfolio data if empty
        if self.collection.count() == 0:
            self._load_portfolio_data()

    def _load_portfolio_data(self):
        df = pd.read_csv("portfolio.csv")
        for index, row in df.iterrows():
            search_content = f"Tech: {row['Tech Stack']}, Use Case: {row['Use Case']}"
            self.collection.add(
                documents=[search_content],
                metadatas=[{"link": row['Link'], "results": row['Results']}],
                ids=[str(index)]
            )

    def generate_email(self, job_description, tone="Professional"):
        # Semantic Search
        results = self.collection.query(query_texts=[job_description], n_results=1)
        
        if not results['documents'][0] or results['distances'][0][0] > 1.5:
            match_context = "General expertise in software development and problem solving."
            link = "atliq.com"
        else:
            match_context = results['documents'][0][0]
            link = results['metadatas'][0][0]['link']

        template = """
        ### JOB DESCRIPTION:
        {job_description}

        ### RELEVANT EXPERIENCE:
        AtliQ Technologies project: {match_context}
        Evidence of success: {link}

        ### INSTRUCTION:
        You are the CTO of AtliQ Technologies. Write a cold email to the hiring manager.
        - Use a {tone} tone.
        - Explicitly mention the relevant experience above as proof of capability.
        - Keep the email concise and under 150 words.
        - Do not include any fake projects or hallucinated links.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        response = chain.invoke({
            "job_description": job_description, 
            "match_context": match_context, 
            "link": link,
            "tone": tone
        })
        return response.content

# --- Frontend: Streamlit App ---
def main():
    st.set_page_config(layout="wide", page_title="AI Code Email Gen")

    # Dark, Bold Title, 48px, No Icon
    st.markdown("""
        <h1 style='text-align: center; color: #1E293B; font-size: 48px; font-weight: 800; margin-bottom: 0px;'>
            AI Cold Email Generator
        </h1>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 18px; margin-top: 0px;'>AtliQ Technologies Sales Acceleration Tool</p>", unsafe_allow_html=True)
    st.write("---")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        tone = st.selectbox("Select Email Tone", ["Professional", "Witty", "Urgent"])
        use_url = st.checkbox("Scrape Job Description from URL")
        st.info("Uses RAG to match portfolio case studies.")

    # Input handling
    job_desc = ""
    if use_url:
        url_input = st.text_input("Enter Job Posting URL:")
        if url_input:
            try:
                with st.spinner("Scraping job details..."):
                    loader = WebBaseLoader(url_input)
                    page_data = loader.load().pop().page_content
                    job_desc = st.text_area("Scraped Content:", value=page_data, height=200)
            except Exception as e:
                st.error(f"Scraping failed: {e}")
    else:
        job_desc = st.text_area("Paste Job Description here:", height=200)

    # Execution
    if st.button("🚀 Generate Personalized Email"):
        if job_desc.strip():
            try:
                with st.spinner("Drafting your email..."):
                    generator = EmailGenerator()
                    email_content = generator.generate_email(job_desc, tone)

                    st.subheader("Generated Email")
                    st.text_area("Result:", value=email_content, height=350)
                    
                    st.download_button(
                        label="Download Email",
                        data=email_content,
                        file_name="cold_email.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please provide a job description.")

if __name__ == "__main__":
    main()