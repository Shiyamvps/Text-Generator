import streamlit as st

from summarizer import (
    summarize_text,
    extract_document_text,
    describe_image,
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
            label="Original Content Word Count",
            value=original_count
        )

    with right:

        st.metric(
            label="Summary Word Count",
            value=summary_count
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

st.subheader("Summarization Type")

# Summary length for all three input methods
summary_length = st.selectbox(
    "Select Summary Length",
    ["Short", "Medium", "Detailed"]
)

# Format selection for all three input methods
summary_format = st.radio(
    "How would you like your summary?",
    ["Bulleted Points", "Paragraph"],
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

            # Extract document content
            extracted_text = extract_document_text(
                uploaded_file
            )

            if extracted_text and extracted_text.strip():

                st.subheader(
                    "Extracted Document Content"
                )

                # Display extracted content
                st.text_area(
                    "Content extracted from your document",

                    value=extracted_text,

                    height=300,

                    disabled=True,

                    key="extracted_document_content"
                )

                # Generate document summary
                if st.button(
                    "Generate Summary",
                    key="document_summary_button"
                ):

                    with st.spinner(
                        "Summarizing your document..."
                    ):

                        summary = summarize_text(
                            extracted_text,
                            summary_length,
                            summary_format
                        )

                    st.subheader(
                        "Generated Summary"
                    )

                    st.markdown(summary)

                    # Calculate word counts
                    original_count = count_words(
                        extracted_text
                    )

                    summary_count = count_words(
                        summary
                    )

                    # Display comparison at the bottom
                    st.divider()

                    show_word_count_comparison(
                        original_count,
                        summary_count
                    )

                    # Download summary
                    st.download_button(
                        label="Download Summary",

                        data=summary,

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

        # Display uploaded image
        st.image(
            uploaded_image,

            caption="Uploaded Image",

            use_container_width=True
        )

        # Generate image description
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

                st.subheader(
                    "Detailed Image Description"
                )

                # Display description in selected format
                st.markdown(image_description)

                # Calculate description word count
                description_count = count_words(
                    image_description
                )

                st.divider()

                st.subheader("Word Count")

                st.metric(
                    label="Description Word Count",

                    value=description_count
                )

                # Download image description
                st.download_button(
                    label="Download Image Description",

                    data=image_description,

                    file_name="image_description.txt",

                    mime="text/plain",

                    key="image_download"
                )

            except Exception as e:

                st.error(
                    f"Unable to describe the image: {e}"
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

    # Generate pasted text summary
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

                st.subheader(
                    "Generated Summary"
                )

                st.markdown(summary)

                # Calculate word counts
                original_count = count_words(
                    pasted_text
                )

                summary_count = count_words(
                    summary
                )

                # Display comparison at the bottom
                st.divider()

                show_word_count_comparison(
                    original_count,
                    summary_count
                )

                # Download summary
                st.download_button(
                    label="Download Summary",

                    data=summary,

                    file_name="text_summary.txt",

                    mime="text/plain",

                    key="paste_download"
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

        else:

            st.warning(
                "Please enter some content before summarizing."
            )
