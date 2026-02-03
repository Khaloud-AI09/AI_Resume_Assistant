import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import time

# 1. Setup API Key with extra safety
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ GOOGLE_API_KEY not found! Check your .streamlit/secrets.toml file.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Updating to Gemini 3 Flash
    model = genai.GenerativeModel('gemini-3-flash')
except Exception as e:
    st.error(f"Failed to initialize Gemini: {e}")
    st.stop()

# 2. PDF Extraction Function
def extract_text_from_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# 3. AI Generation with Rate-Limit Handling
def generate_analysis(prompt):
    max_retries = 3
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                st.warning(f"Quota hit! Retrying in {5 * (i+1)} seconds...")
                time.sleep(5 * (i+1)) # Exponential backoff
                continue
            else:
                raise e

# --- Streamlit UI ---
st.set_page_config(page_title="Gemini 3 Resume Assistant", page_icon="🚀")
st.title("🚀 Gemini 3 Resume Assistant")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
job_description = st.text_area("Paste the Job Description here:", height=200)

if st.button("Improve My Resume"):
    if uploaded_file and job_description:
        with st.spinner("Gemini 3 is analyzing..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                prompt = f"""
                You are an expert Career Coach. 
                Resume: {resume_text}
                Job Description: {job_description}

                Please:
                1. Identify the top 3 missing keywords.
                2. Rewrite the 'Professional Experience' section to be impact-oriented.
                3. Give an 'ATS Compatibility' score out of 100.
                """
                
                try:
                    result = generate_analysis(prompt)
                    st.success("Analysis Complete!")
                    st.markdown("### AI Suggestions:")
                    st.write(result)
                except Exception as e:
                    st.error(f"AI Generation Error: {e}")
    else:
        st.warning("Please upload a resume and paste a job description!")
