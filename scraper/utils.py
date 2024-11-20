import re


def convert_to_filename(title):
    filename = re.sub(r'[<>:"/\\|?*]', "_", title)
    filename = re.sub(r"\s+", " ", filename).strip()
    filename = filename.replace(" ", "_")
    return filename
