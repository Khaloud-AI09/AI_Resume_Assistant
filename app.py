import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup API Key with extra safety
# This looks for the key in .streamlit/secrets.toml locally 
# OR in the 'Secrets' dashboard on Streamlit Cloud
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ GOOGLE_API_KEY not found! Please check your secrets.toml or Cloud settings.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # If gemini-1.5-flash gives a 404, try 'gemini-1.5-flash-latest' or 'gemini-pro'
    model = genai.GenerativeModel('gemini-1.5-flash')
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
st.set_page_config(page_title="AI Resume Assistant", page_icon="📄")
st.title("📄 GenAI Resume Assistant")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
job_description = st.text_area("Paste the Job Description here:", height=200)

if st.button("Improve My Resume"):
    if uploaded_file and job_description:
        with st.spinner("Analyzing with Gemini..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                # Fixed a common NameError by ensuring variable name matches
                prompt = f"""
                You are an expert Career Coach. 
                I am providing you with a Resume and a Job Description. 
                Please:
                1. Identify the top 3 missing keywords from the resume based on the job description.
                2. Rewrite the 'Professional Experience' section to be more impact-oriented.
                3. Give me an 'ATS Compatibility' score out of 100.
                
                Resume: {resume_text}
                Job Description: {job_description}
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("Done!")
                    st.markdown("### AI Suggestions:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI Generation Error: {e}")
    else:
        st.warning("Please upload a resume and paste a job description!")
