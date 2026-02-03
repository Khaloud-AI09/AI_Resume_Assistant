import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup API Key with extra safety
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ GOOGLE_API_KEY not found! Please check your .streamlit/secrets.toml or Cloud settings.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # NEW: Let's try to find an available model automatically to avoid 404
    model_name = 'gemini-1.5-flash' # Primary choice
    model = genai.GenerativeModel(model_name)
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
st.set_page_config(page_title="GenAI Resume Assistant", page_icon="📄")
st.title("📄 GenAI Resume Assistant")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
# Fixed the name here to match the prompt below
job_description = st.text_area("Paste the Job Description here:", height=200)

if st.button("Improve My Resume"):
    if uploaded_file and job_description:
        with st.spinner("Analyzing with Gemini..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                # Prompt using the fixed variable 'job_description'
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
                    response = model.generate_content(prompt)
                    st.success("Analysis Complete!")
                    st.markdown("### AI Suggestions:")
                    st.write(response.text)
                except Exception as e:
                    # If 1.5-flash fails, we give a specific hint
                    st.error(f"AI Error: {e}")
                    st.info("Try changing model name to 'gemini-pro' in the code if this persists.")
    else:
        st.warning("Please provide both a resume and a job description.")
