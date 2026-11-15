
import streamlit as st

from backend import summarize_text

# Step 1: Configure the page

st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="📝",
    layout="centered"
)

# Step 2: Display application heading

st.title("AI Text Summarizer")

st.write("Paste your text below and generate an AI-powered summary.")

# Step 3: Accept user input

text = st.text_area(
    "Enter your text",
    height=250,
    placeholder="Paste your article or paragraph here..."
)

# Step 4: Select summary length

length = st.selectbox(
    "Choose summary length",
    ["Short", "Medium", "Detailed"]
)

# Step 5: Generate summary

if st.button("Generate Summary"):

    if not text.strip():

        st.warning("Please enter some text.")

    else:

        with st.spinner("Generating summary..."):

            try:

                summary = summarize_text(text, length)

                st.subheader("Generated Summary")

                st.write(summary)

            except Exception as e:

                st.error(f"Something went wrong: {e}")