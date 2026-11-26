import streamlit as st

from summarizer import (
    summarize_text,
    extract_document_text,
    describe_image,
    translate_summary_to_english,
    count_words
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Text Generator",
    page_icon="📝",
    layout="wide"
)

st.title("AI Text Generator")

st.write(
    "Summarize documents, describe images, "
    "or summarize pasted content."
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

state_defaults = {
    "document_summary": None,
    "document_translation": None,
    "paste_summary": None,
    "paste_translation": None
}

for key, value in state_defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# WORD COUNT COMPARISON
# --------------------------------------------------

def show_word_count_comparison(
    original_count,
    summary_count
):

    st.subheader("Word Count Comparison")

    left, right = st.columns(2)

    with left:

        st.metric(
            "Original Content Word Count",
            original_count
        )

    with right:

        st.metric(
            "Summary Word Count",
            summary_count
        )

# --------------------------------------------------
# DISPLAY TRANSLATION
# --------------------------------------------------

def display_translation(
    summary,
    translation,
    original_key,
    translation_key,
    summary_format
):

    st.subheader("Original Language Summary")

    st.markdown(summary)

    st.metric(
        "Original Summary Word Count",
        count_words(summary)
    )

    if st.button(
        "Translate to English",
        key=translation_key
    ):

        try:

            with st.spinner("Translating summary into English..."):

                english_translation = translate_summary_to_english(
                    summary,
                    summary_format
                )

            st.session_state[original_key + "_translation"] = (
                english_translation
            )

        except Exception as e:

            st.error(f"Translation failed: {e}")

    saved_translation = st.session_state.get(
        original_key + "_translation"
    )

    if saved_translation:

        st.divider()

        st.subheader("English Translation")

        st.markdown(saved_translation)

        st.metric(
            "English Translation Word Count",
            count_words(saved_translation)
        )

        st.download_button(
            "Download English Translation",
            data=saved_translation,
            file_name="english_translation.txt",
            mime="text/plain",
            key=translation_key + "_download"
        )

# --------------------------------------------------
# INPUT METHOD
# --------------------------------------------------

input_method = st.radio(
    "Choose your input method",

    [
        "Upload a Document",
        "Upload an Image",
        "Paste Content"
    ],

    horizontal=True
)

# --------------------------------------------------
# SUMMARY SETTINGS
# --------------------------------------------------

st.subheader("Summary Settings")

summary_length = st.selectbox(
    "Select Summary Length",

    [
        "Short",
        "Medium",
        "Detailed"
    ]
)

summary_format = st.radio(
    "How would you like your summary?",

    [
        "Bulleted Points",
        "Paragraph"
    ],

    horizontal=True
)

# --------------------------------------------------
# OPTION 1: DOCUMENT UPLOAD
# --------------------------------------------------

if input_method == "Upload a Document":

    st.subheader("Upload Your Document")

    uploaded_file = st.file_uploader(
        "Choose a document",

        type=[
            "pdf",
            "csv",
            "xlsx",
            "xls",
            "docx",
            "pptx",
            "txt",
            "md"
        ],

        key="document_uploader"
    )

    if uploaded_file is not None:

        try:

            extracted_text = extract_document_text(
                uploaded_file
            )

            if extracted_text and extracted_text.strip():

                st.subheader("Extracted Document Content")

                st.text_area(
                    "Content extracted from your document",

                    value=extracted_text,

                    height=300,

                    disabled=True,

                    key="extracted_document_content"
                )

                if st.button(
                    "Generate Summary",
                    key="document_summary_button"
                ):

                    try:

                        with st.spinner(
                            "Summarizing your document..."
                        ):

                            summary = summarize_text(
                                extracted_text,
                                summary_length,
                                summary_format
                            )

                        st.session_state.document_summary = summary
                        st.session_state.document_translation = None

                    except Exception as e:

                        st.error(
                            f"Unable to summarize document: {e}"
                        )

                # Display saved summary
                if st.session_state.document_summary:

                    st.divider()

                    display_translation(
                        st.session_state.document_summary,
                        st.session_state.document_translation,
                        "document_summary",
                        "document_translate_button",
                        summary_format
                    )

                    original_count = count_words(extracted_text)

                    summary_count = count_words(
                        st.session_state.document_summary
                    )

                    st.divider()

                    show_word_count_comparison(
                        original_count,
                        summary_count
                    )

                    st.download_button(
                        "Download Original Summary",

                        data=st.session_state.document_summary,

                        file_name="document_summary.txt",

                        mime="text/plain",

                        key="document_download"
                    )

            else:

                st.warning(
                    "No readable text was found in this document."
                )

        except Exception as e:

            st.error(
                f"Unable to process the document: {e}"
            )

# --------------------------------------------------
# OPTION 2: IMAGE UPLOAD
# --------------------------------------------------

elif input_method == "Upload an Image":

    st.subheader("Upload Your Image")

    uploaded_image = st.file_uploader(
        "Choose an image",

        type=[
            "jpg",
            "jpeg",
            "png"
        ],

        key="image_uploader"
    )

    if uploaded_image is not None:

        st.image(
            uploaded_image,

            caption="Uploaded Image",

            use_container_width=True
        )

        if st.button(
            "Describe Image",
            key="describe_image_button"
        ):

            try:

                with st.spinner(
                    "Analyzing your image..."
                ):

                    image_description = describe_image(
                        uploaded_image.getvalue(),
                        uploaded_image.type,
                        summary_format,
                        summary_length
                    )

                st.session_state.image_description = image_description

            except Exception as e:

                st.error(
                    f"Unable to describe the image: {e}"
                )

        if st.session_state.get("image_description"):

            st.subheader("Detailed Image Description")

            st.markdown(
                st.session_state.image_description
            )

            st.divider()

            st.subheader("Word Count")

            st.metric(
                "Description Word Count",

                count_words(
                    st.session_state.image_description
                )
            )

            st.download_button(
                "Download Image Description",

                data=st.session_state.image_description,

                file_name="image_description.txt",

                mime="text/plain",

                key="image_download"
            )

# --------------------------------------------------
# OPTION 3: PASTE CONTENT
# --------------------------------------------------

elif input_method == "Paste Content":

    st.subheader("Paste Your Content")

    pasted_text = st.text_area(
        "Enter or paste your text here",

        height=300,

        placeholder="Paste your content here...",

        key="pasted_content"
    )

    if st.button(
        "Generate Summary",
        key="paste_summary_button"
    ):

        if pasted_text and pasted_text.strip():

            try:

                with st.spinner(
                    "Generating your summary..."
                ):

                    summary = summarize_text(
                        pasted_text,
                        summary_length,
                        summary_format
                    )

                st.session_state.paste_summary = summary
                st.session_state.paste_translation = None

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

        else:

            st.warning(
                "Please enter some content before summarizing."
            )

    # Display saved summary
    if st.session_state.paste_summary:

        st.divider()

        display_translation(
            st.session_state.paste_summary,
            st.session_state.paste_translation,
            "paste_summary",
            "paste_translate_button",
            summary_format
        )

        original_count = count_words(pasted_text)

        summary_count = count_words(
            st.session_state.paste_summary
        )

        st.divider()

        show_word_count_comparison(
            original_count,
            summary_count
        )

        st.download_button(
            "Download Original Summary",

            data=st.session_state.paste_summary,

            file_name="text_summary.txt",

            mime="text/plain",

            key="paste_download"
        )
