import os


def safe_file_open_w(path):
    """ 
    Open "path"/file for writing, creating any parent directories as needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    return open(path, 'w', newline='')


def safe_file_open_wb(path):
    """ 
    Open binary "path"/file for writing, creating any parent directories as needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    return open(path, 'wb')


def parse_content_disposition_header(cd_header: str):
    """
    Extract the filename out of a Content-Disposition header string
    """
    header_chunks = cd_header.split(';')
    filename = "".join([chunk.split("=")[1].strip(' ').strip('\"') for chunk in header_chunks if "filename" in chunk])

    return filename
