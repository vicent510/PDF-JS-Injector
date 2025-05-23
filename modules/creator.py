import os

def save_pdf(pdf, output_path, overwrite=True):
    """
    Saves the modified PDF to the specified path.

    Parameters:
        pdf: modified pikepdf.Pdf object.
        output_path: output file path.
        overwrite: if False, prevents overwriting an existing file.
    """
    try:
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(f"[!] File {output_path} already exists. Enable 'overwrite=True' to overwrite it.")

        pdf.save(output_path)
        print(f"[+] PDF successfully saved to: {output_path}")

    except FileExistsError as fe:
        print(str(fe))
        raise
    except PermissionError:
        print(f"[!] You do not have permission to write to the directory: {os.path.dirname(output_path)}")
        raise
    except Exception as e:
        print(f"[!] Unexpected error while saving PDF: {e}")
        raise
