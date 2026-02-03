import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup Google API Key securely from secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Using 'gemini-pro' for maximum compatibility
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error("API Key not found. Please set GOOGLE_API_KEY in your secrets.")
    st.stop()

# 2. Function to extract text from the PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# --- Streamlit UI ---
st.set_page_config(page_title="GenAI Resume Assistant", page_icon="😁")
st.title("GenAI Resume Assistant")

# Input Section
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
job_desc = st.text_area("Paste the Job Description here:", height=200)

if st.button("Improve My Resume"):
    if uploaded_file and job_desc:
        with st.spinner("Analyzing with Gemini..."):
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
                
                prompt = f"""
                You are an expert Career Coach. 
                I am providing you with a Resume and a Job Description. 
                Please:
                1. Identify the top 3 missing keywords from the resume based on the job description.
                2. Rewrite the 'Professional Experience' section to be more impact-oriented.
                3. Give me an 'ATS Compatibility' score out of 100.
                
                Resume: {resume_text}
                Job Description: {job_desc}
                """
                
                response = model.generate_content(prompt)
                
                st.success("Analysis Complete!")
                st.subheader("AI Suggestions:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a resume and provide a job description.")
