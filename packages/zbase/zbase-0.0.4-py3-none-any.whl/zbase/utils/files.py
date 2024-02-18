import json,os

def read_lines(file:str, parse_json = False, skip_empty=True):
    with open(file , 'r') as f:
        for line in f:
            if skip_empty:
                if line.strip()=="":
                    continue
            if parse_json:
                yield json.loads(line)
            else:
                yield line.strip()


def get_ext(filename:str)->str:
    """
    Get file extension.
    """
    if "." not in filename:
        return ""
    filename = os.path.basename(filename)
    filename = filename.rstrip().lower()
    if filename.endswith(".tar.gz"):
        return "tar.gz"
    return os.path.splitext(filename)[-1].lstrip(".")



def get_filename_without_ext(filename:str)->str:
    """
    Get filename without extension.
    """
    if "." not in filename:
        return filename
    filename = os.path.basename(filename)
    return os.path.splitext(filename)[0]