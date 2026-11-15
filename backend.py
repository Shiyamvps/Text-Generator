
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load API key
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API key is missing. Check your .env file.")

# Step 1: Initialize the LLM

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=api_key
)

# Step 2: Create the prompt template

prompt = PromptTemplate.from_template("""

You are an expert text summarizer.

Summarize the following text in a {length} format.

Instructions:

1. Identify the important points.
2. Avoid unnecessary details.
3. Keep the summary easy to understand.

Text:

{text}

Summary:

""")

# Step 3: Initialize output parser

parser = StrOutputParser()

# Step 4: Create LangChain chain

summarizer_chain = prompt | llm | parser

# Step 5: Create a function to summarize text

def summarize_text(text, length):

    result = summarizer_chain.invoke({
        "text": text,
        "length": length
    })

    return result