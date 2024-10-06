import PyPDF2
def read_pdf(pdf_file=None):

    if pdf_file:
        # Open the PDF file
        with pdf_file.open('rb') as f:
            reader = PyPDF2.PdfReader(f)
            text_content = ''

            # Iterate through all pages and extract text
            for page in reader.pages:
                text_content += page.extract_text() + '\n'

        # Assign the extracted content to the variable
        return text_content
    return None
