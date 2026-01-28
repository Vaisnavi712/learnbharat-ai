import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from syllabus_data import SYLLABUS

# -------------------------
# OpenAI Client (SAFE)
# -------------------------
client = OpenAI()  # Reads OPENAI_API_KEY from Streamlit Secrets

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="LearnBharat AI", page_icon="📚")

st.title("LearnBharat AI 📚")
st.subheader("Your AI Study Assistant for Indian Universities")
st.markdown("---")

# -------------------------
# User Inputs
# -------------------------
course_code = st.text_input("Enter course code (e.g., CS301)")

focus = st.multiselect(
    "What do you want?",
    ["Notes", "Videos", "Exam Questions", "Project Ideas"]
)

language = st.selectbox(
    "Preferred Language",
    ["English", "Hindi", "Tamil", "Telugu"]
)

st.markdown("---")

# -------------------------
# Load Syllabus
# -------------------------
syllabus = ""
course_name = ""

if course_code:
    if course_code in SYLLABUS:
        course_name = SYLLABUS[course_code]["name"]
        syllabus = "\n".join(SYLLABUS[course_code]["units"])
        st.success(f"Loaded syllabus for {course_name}")
    else:
        course_name = course_code
        st.warning("Course not found. Using course code as topic.")

# -------------------------
# AI Generator
# -------------------------
def ai_generate(course, focus, language, syllabus):
    prompt = f"""
You are an expert Indian university professor and exam coach.

Course Name: {course}
Requested Outputs: {", ".join(focus)}
Preferred Language: {language}

Official Syllabus:
{syllabus}

Instructions:
- If Notes are requested, generate unit-wise easy explanations
- If Videos are requested, recommend NPTEL + Indian YouTube channels
- If Exam Questions are requested, generate GATE + university-style questions
- If Project Ideas are requested, suggest 3–5 practical projects with difficulty levels
- Also recommend remaining learning modes not selected

Format clearly with headings and bullet points.
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    # Safe text extraction
    return response.output[0].content[0].text

# -------------------------
# Exam Readiness Score
# -------------------------
def calculate_readiness(focus):
    score = 0
    if "Notes" in focus:
        score += 35
    if "Exam Questions" in focus:
        score += 35
    if "Project Ideas" in focus:
        score += 20
    if "Videos" in focus:
        score += 10
    return min(score, 100)

# -------------------------
# PDF Helpers
# -------------------------
def clean_text_for_pdf(text):
    return text.encode("latin-1", "ignore").decode("latin-1")

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    clean_text = clean_text_for_pdf(text)
    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 8, line)

    return pdf

# -------------------------
# Generate Button
# -------------------------
if st.button("Generate 🚀"):

    if not course_code:
        st.warning("Please enter a course code")

    elif not focus:
        st.warning("Please select at least one option")

    else:
        with st.spinner("Generating personalized study content..."):
            try:
                output = ai_generate(course_name, focus, language, syllabus)

                st.success("Done!")
                st.markdown("## 📘 Generated Study Material")
                st.markdown(output)

                # -------------------------
                # Exam Readiness Display
                # -------------------------
                score = calculate_readiness(focus)

                st.markdown("## 📊 Exam Readiness Score")
                st.progress(score / 100)
                st.metric("Readiness Level", f"{score}%")

                if score < 50:
                    st.warning("Focus more on notes and exam questions.")
                elif score < 80:
                    st.info("Good progress! Add projects or more practice.")
                else:
                    st.success("Excellent! You are exam-ready 🚀")

                # -------------------------
                # PDF Download
                # -------------------------
                pdf = create_pdf(output)
                pdf.output("study_material.pdf")

                with open("study_material.pdf", "rb") as f:
                    st.download_button(
                        "📄 Download as PDF",
                        f,
                        file_name="LearnBharat_AI_Notes.pdf"
                    )

            except Exception as e:
                st.error("AI error:")
                st.code(str(e))
                st.stop()


