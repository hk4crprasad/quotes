# Medical PDF Analyzer - Extract Diagnoses and Procedures
# Dependencies:
# pip install google-genai PyMuPDF Pillow
import base64
import os
import fitz  # PyMuPDF
from google import genai
from google.genai import types

# Set up your Google Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBIsDN1738uvZIxHnZw-00U3cY3eL6nxPI"

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text += page_text + "\n"
    doc.close()
    return text.strip()

def extract_medical_info(pdf_path):
    """Extract diagnoses and procedures from medical PDF using Gemma (text-only)."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    if not pdf_text:
        print("No extractable text found in PDF.")
        return

    medical_prompt = """
You are a medical document analyzer. Carefully analyze the following medical document and extract only the following information:

**DIAGNOSES:**
- List all diagnosis names mentioned (primary and secondary), one per line.
- IMPORTANT: Remove any text in parentheses. Only output the main diagnosis name, without any codes or extra details in parentheses or brackets.

**PROCEDURES:**
- List all procedure names performed or mentioned, one per line.
- IMPORTANT: Remove any text in parentheses. Only output the main procedure name, without any codes or extra details in parentheses or brackets.

**CODES:**
- List all ICD-10 codes found in the document, one per line, without diagnosis names.
- List all CPT codes found in the document, one per line, without procedure names.

Format your response exactly as follows:

## DIAGNOSES
1. [Diagnosis name]
2. ...

## PROCEDURES
1. [Procedure name]
2. ...

## ICD-10 CODES
1. [ICD-10 code]
2. ...

## CPT CODES
1. [CPT code]
2. ...

If any section is not found in the document, indicate "Not specified in document".

Do not include chief complaint, medications, follow-up, or any other information.

Medical Document Text:
""" + pdf_text

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=medical_prompt)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        temperature=0.1,
    )

    print("Analyzing medical document...")
    print("=" * 50)

    try:
        model = "gemma-3n-e4b-it"  # Text-only model
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        print("Please ensure your PDF is a valid medical document and try again.")

def main():
    pdf_path = "/home/tecosys/Nutaan-ICD-HCC-Finder/Medical_Claim_Diagnosis_Review.pdf"
    if not os.path.exists(pdf_path):
        print("Error: File not found. Please check the path and try again.")
        return
    if not pdf_path.lower().endswith('.pdf'):
        print("Error: Please provide a PDF file.")
        return
    extract_medical_info(pdf_path)

if __name__ == "__main__":
    main()