import PyPDF2
import requests
from io import BytesIO
def read_pdf(pdf_url=None):
    print("URL"+str(pdf_url))
    if pdf_url:
        try:
            # Get the PDF content from the URL
            response = requests.get(pdf_url)
            response.raise_for_status()  # Check if the request was successful

            # Open the PDF using BytesIO
            pdf_file = BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            text_content = ''

            # Iterate through all pages and extract text
            for page in reader.pages:
                text_content += page.extract_text() + '\n'

            # Assign the extracted content to the variable
            return text_content

        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF from URL: {e}")
            return None

    return None
