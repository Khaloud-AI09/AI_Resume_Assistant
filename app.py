import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup API Key with extra safety
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ GOOGLE_API_KEY not found! Check your .streamlit/secrets.toml file.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Using 'gemini-1.5-flash-latest' to avoid 404 version errors
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
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

# --- Streamlit UI ---
st.set_page_config(page_title="AI Resume Assistant", page_icon="😁")
st.title("GenAI Resume Assistant")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
job_desc = st.text_area("Paste the Job Description here:", height=200)

if st.button("Improve My Resume"):
    if uploaded_file and job_desc:
        with st.spinner("Analyzing with Gemini..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                prompt = f"""
                You are an expert Career Coach. 
                Resume: {resume_text}
                Job Description: {job_desc}

                Please:
                1. Identify the top 3 missing keywords.
                2. Rewrite the 'Professional Experience' section to be more impact-oriented.
                3. Give an 'ATS Compatibility' score out of 100.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("Analysis Complete!")
                    st.markdown("### AI Suggestions:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI Generation Error (likely 404 or quota): {e}")
    else:
        st.warning("Please upload a resume and paste a job description!")
