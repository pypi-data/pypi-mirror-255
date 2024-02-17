import json, re

class ParseJSONException(json.JSONDecodeError):
    def __init__(self, original_text, message="Unable to parse 1c data"):
        self.original_text = original_text
        self.message = message
        super().__init__(self.message)

def lts(lts_file):

    str_original = ''
    with open(lts_file,encoding='utf-8') as cfg:
        str_original = cfg.read().replace("\r\n",'\n').replace('\n','').replace('\uFEFF','').replace('{','[').replace('}',']')
    str_original = re.sub(r"([0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12})",wrap_by_quotes,str_original)
    str_original = re.sub(r"[^,\[](\"\")",replace_double_quotes,str_original)
    str_original = re.sub(r",(0\d+)",wrap_by_quotes,str_original)
    str_original = re.sub(r"(\\)[^\"]",wrap_backslash,str_original)
    
    try:
        data = json.loads(str_original)
    except:
        raise ParseJSONException(str_original)

    return data

def wrap_by_quotes(match_obj):
    environment = match_obj.group()
    value = match_obj.group(1)
    replacement = environment.replace(value,f'"{value}"')
    if value is not None:
        return replacement

def wrap_backslash(match_obj):
    environment = match_obj.group()
    value = match_obj.group(1)
    replacement = environment.replace(value,f'\\\\')
    if value is not None:
        return replacement

def replace_double_quotes(match_obj):
    value = match_obj.group()
    if value is not None:
        return value.replace('""','\\"')