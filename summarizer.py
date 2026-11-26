import os
import base64

from io import BytesIO, StringIO

import pandas as pd

from dotenv import load_dotenv
from openai import OpenAI

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from pypdf import PdfReader
from docx import Document
from pptx import Presentation

load_dotenv()

# --------------------------------------------------
# OPENAI CLIENT
# --------------------------------------------------

def get_openai_client():

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. "
            "Please check your .env file."
        )

    return OpenAI(api_key=api_key)

# --------------------------------------------------
# 1. TEXT SUMMARIZATION
# --------------------------------------------------

def summarize_text(text, length, summary_format):

    if not text or not text.strip():
        raise ValueError("Please provide some text to summarize.")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    prompt = PromptTemplate(
        input_variables=[
            "text",
            "length",
            "summary_format"
        ],
        template="""
You are an expert multilingual text summarization assistant.

LANGUAGE INSTRUCTIONS:

1. Identify the language of the original content.
2. Write the summary in the SAME language as the original.
3. Tamil content must produce a Tamil summary.
4. Hindi content must produce a Hindi summary.
5. English content must produce an English summary.
6. Do not translate the content into English.
7. Preserve important facts, names and technical terms.
8. For mixed-language content, use its dominant language.

SUMMARY LENGTH:
{length}

SUMMARY FORMAT:
{summary_format}

FORMATTING:
- Bulleted Points: use clear bullet points.
- Paragraph: use connected paragraphs.
- Do not mix both formats.
- Do not invent information.

ORIGINAL CONTENT:
{text}

Generate the summary:
"""
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "text": text,
        "length": length,
        "summary_format": summary_format
    })

# --------------------------------------------------
# 2. TRANSLATE SUMMARY INTO ENGLISH
# --------------------------------------------------

def translate_summary_to_english(summary, summary_format):

    if not summary or not summary.strip():
        raise ValueError("No summary is available to translate.")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    prompt = PromptTemplate(
        input_variables=["summary", "summary_format"],
        template="""
You are an expert multilingual translator.

Translate the following summary into English.

IMPORTANT INSTRUCTIONS:

1. Translate the complete summary into English.
2. Preserve the original meaning and important details.
3. Do not add new information.
4. Do not remove important information.
5. Preserve names, numbers and technical terms.
6. Maintain the original structure and formatting.

OUTPUT FORMAT:
{summary_format}

If the original is in bullet points, return English
bullet points.

If the original is in paragraphs, return English paragraphs.

SUMMARY TO TRANSLATE:
{summary}

Return only the English translation.
"""
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "summary": summary,
        "summary_format": summary_format
    })

# --------------------------------------------------
# 3. DOCUMENT TEXT EXTRACTION
# --------------------------------------------------

def extract_document_text(uploaded_file):

    file_name = uploaded_file.name
    extension = file_name.rsplit(".", 1)[-1].lower()

    file_bytes = uploaded_file.getvalue()

    if extension == "pdf":

        reader = PdfReader(BytesIO(file_bytes))

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = page.extract_text() or ""

            pages.append(
                f"--- Page {page_number} ---\n{page_text}"
            )

        return "\n\n".join(pages)

    elif extension == "csv":

        dataframe = pd.read_csv(
            StringIO(file_bytes.decode("utf-8-sig")),
            dtype=str
        ).fillna("")

        return dataframe.to_string(index=False)

    elif extension in ["xlsx", "xls"]:

        excel_file = pd.ExcelFile(BytesIO(file_bytes))

        all_sheets = []

        for sheet_name in excel_file.sheet_names:

            dataframe = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                dtype=str
            ).fillna("")

            all_sheets.append(
                f"--- Sheet: {sheet_name} ---\n"
                f"{dataframe.to_string(index=False)}"
            )

        return "\n\n".join(all_sheets)

    elif extension == "docx":

        document = Document(BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        for table in document.tables:

            for row in table.rows:

                paragraphs.append(
                    " | ".join(
                        cell.text for cell in row.cells
                    )
                )

        return "\n".join(paragraphs)

    elif extension == "pptx":

        presentation = Presentation(BytesIO(file_bytes))

        slides_text = []

        for slide_number, slide in enumerate(
            presentation.slides,
            start=1
        ):

            slide_content = []

            for shape in slide.shapes:

                if (
                    hasattr(shape, "text")
                    and shape.text.strip()
                ):

                    slide_content.append(shape.text)

            slides_text.append(
                f"--- Slide {slide_number} ---\n"
                + "\n".join(slide_content)
            )

        return "\n\n".join(slides_text)

    elif extension in ["txt", "md"]:

        return file_bytes.decode(
            "utf-8-sig",
            errors="replace"
        )

    else:

        raise ValueError(
            f"The .{extension} file format is not supported."
        )

# --------------------------------------------------
# 4. IMAGE DESCRIPTION
# --------------------------------------------------

def describe_image(
    image_bytes,
    mime_type,
    summary_format,
    summary_length
):

    client = get_openai_client()

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data_url = (
        f"data:{mime_type};base64,{encoded_image}"
    )

    if summary_format == "Bulleted Points":

        formatting_instruction = """
Use clear and informative bullet points.
Do not write long paragraphs.
"""

    else:

        formatting_instruction = """
Write the description in connected paragraphs.
Do not use bullet points.
"""

    if summary_length == "Short":

        length_instruction = """
Give a brief description covering only the most important
visible details.
"""

    elif summary_length == "Medium":

        length_instruction = """
Give a moderately detailed description covering the main
subjects, actions, appearance and surroundings.
"""

    else:

        length_instruction = """
Give a comprehensive description covering subjects,
appearance, clothing, expressions, actions, background,
objects and overall atmosphere.
"""

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",

                "content": f"""
You are an advanced visual image analysis assistant.

Analyze the uploaded image carefully.

Describe visible subjects, clothing, expressions,
actions, objects, background and surroundings.

For movie-like or superhero-like scenes, describe
visible costumes, colours, symbols and visual themes.

Do not identify real people or name fictional movie
characters from their appearance.

Do not invent details that cannot be established
from the image.

DESCRIPTION LENGTH:
{length_instruction}

DESCRIPTION FORMAT:
{formatting_instruction}

Write the description in English.
"""
            },

            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text": """
Describe this image according to the selected
summary length and format.

Explain the main subjects, their visible appearance,
actions, expressions, clothing, objects, background
and overall atmosphere.
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {
                            "url": image_data_url,
                            "detail": "high"
                        }
                    }

                ]
            }

        ],

        max_tokens=1500,
        temperature=0
    )

    return response.choices[0].message.content

# --------------------------------------------------
# 5. WORD COUNT
# --------------------------------------------------

def count_words(text):

    if not text or not text.strip():
        return 0

    return len(text.split())
