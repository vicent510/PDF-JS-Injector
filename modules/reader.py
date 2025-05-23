import pikepdf
import os

def read_pdf(path):
    """
    Reads a PDF file and returns a pikepdf.Pdf object if valid.
    Also checks that the file exists and is a valid PDF.
    """
    # Basic file validation
    if not os.path.exists(path):
        raise FileNotFoundError(f"[!] File does not exist: {path}")
    if not path.lower().endswith('.pdf'):
        raise ValueError(f"[!] File is not a PDF: {path}")

    try:
        pdf = pikepdf.open(path)
        print(f"[+] PDF successfully loaded: {path}")
        print_metadata(pdf)
        return pdf
    except pikepdf._qpdf.PasswordError:
        raise ValueError("[!] PDF is password-protected.")
    except pikepdf.PdfError as e:
        raise ValueError(f"[!] PDF format error: {e}")
    except Exception as e:
        raise RuntimeError(f"[!] Unexpected error while reading PDF: {e}")

def print_metadata(pdf):
    """
    Displays basic PDF metadata (number of pages, title, author).
    """
    try:
        num_pages = len(pdf.pages)
        info = pdf.docinfo
        print(f"    ├── Pages: {num_pages}")
        if info:
            print(f"    ├── Title: {info.get('/Title', 'Not specified')}")
            print(f"    ├── Author: {info.get('/Author', 'Not specified')}")
            print(f"    └── Producer: {info.get('/Producer', 'Not specified')}")
    except Exception:
        print("    └── [!] Could not read metadata.")
