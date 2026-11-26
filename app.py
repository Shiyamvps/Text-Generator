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
    "document_language": None,
    "document_translation": None,
    "document_source": None,

    "paste_summary": None,
    "paste_language": None,
    "paste_translation": None,
    "paste_source": None,

    "image_description": None
}

for key, value in state_defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# WORD COUNT DISPLAY
# --------------------------------------------------

def show_word_counts(
    original_count,
    summary_count,
    translation=None
):

    st.divider()
    st.subheader("Word Count Comparison")

    if translation:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Length of Content",
                original_count
            )

        with col2:
            st.metric(
                "Length of Summary",
                summary_count
            )

        with col3:
            st.metric(
                "English Summary",
                count_words(translation)
            )

    else:

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Original Content",
                original_count
            )

        with col2:
            st.metric(
                "Summary",
                summary_count
            )

# --------------------------------------------------
# DISPLAY SUMMARY AND OPTIONAL TRANSLATION
# --------------------------------------------------

def display_summary(
    summary,
    language,
    translation_key,
    summary_format
):

    st.subheader("Summarization")

    st.markdown(summary)

    translation = None

    # Show translation option only for non-English content
    if language.strip().lower() not in [
        "english",
        "english (us)",
        "english (uk)"
    ]:

        if st.button(
            "Translate to English",
            key=translation_key
        ):

            try:

                with st.spinner(
                    "Translating summary into English..."
                ):

                    translation = translate_summary_to_english(
                        summary,
                        summary_format
                    )

                st.session_state[
                    translation_key + "_result"
                ] = translation

            except Exception as e:

                st.error(
                    f"Translation failed: {e}"
                )

        translation = st.session_state.get(
            translation_key + "_result"
        )

        if translation:

            st.divider()

            st.subheader("English Translation")

            st.markdown(translation)

            st.download_button(
                "Download English Translation",

                data=translation,

                file_name="english_translation.txt",

                mime="text/plain",

                key=translation_key + "_download"
            )

    return translation

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
                            "Detecting language and summarizing your document..."
                        ):

                            summary, language = summarize_text(
                                extracted_text,
                                summary_length,
                                summary_format
                            )

                        st.session_state.document_summary = summary
                        st.session_state.document_language = language
                        st.session_state.document_source = extracted_text
                        st.session_state.document_translation = None
                        st.session_state.document_translate_button_result = None

                    except Exception as e:

                        st.error(
                            f"Unable to summarize document: {e}"
                        )

                # Display summary only when it belongs to current document
                if (
                    st.session_state.document_summary
                    and st.session_state.document_source == extracted_text
                ):

                    st.divider()

                    translation = display_summary(
                        st.session_state.document_summary,
                        st.session_state.document_language,
                        "document_translate_button",
                        summary_format
                    )

                    st.download_button(
                        "Download Original Summary",

                        data=st.session_state.document_summary,

                        file_name="document_summary.txt",

                        mime="text/plain",

                        key="document_download"
                    )

                    show_word_counts(
                        count_words(extracted_text),
                        count_words(st.session_state.document_summary),
                        translation
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
                    "Detecting language and generating your summary..."
                ):

                    summary, language = summarize_text(
                        pasted_text,
                        summary_length,
                        summary_format
                    )

                st.session_state.paste_summary = summary
                st.session_state.paste_language = language
                st.session_state.paste_source = pasted_text
                st.session_state.paste_translation = None
                st.session_state.paste_translate_button_result = None

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

        else:

            st.warning(
                "Please enter some content before summarizing."
            )

    # Display summary only when it belongs to current pasted content
    if (
        st.session_state.paste_summary
        and st.session_state.paste_source == pasted_text
    ):

        st.divider()

        translation = display_summary(
            st.session_state.paste_summary,
            st.session_state.paste_language,
            "paste_translate_button",
            summary_format
        )

        st.download_button(
            "Download Original Summary",

            data=st.session_state.paste_summary,

            file_name="text_summary.txt",

            mime="text/plain",

            key="paste_download"
        )

        show_word_counts(
            count_words(pasted_text),
            count_words(st.session_state.paste_summary),
            translation
        )
