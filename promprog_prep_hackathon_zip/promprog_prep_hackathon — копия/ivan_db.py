import os
import json
import pathlib
import shutil

tovars_data = {}
users_base = {}
email = 'placeholder'

def return_image(path, placeholder):
    if os.path.exists(f"{pathlib.Path(__file__).parent.resolve()}/static/images/{path}.jpg"):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs(kwargs):
    if (email in users_base):
        return kwargs | {'username': users_base[email][1], 'userimg': return_image(f'users/{email}', 'user_placeholder')}
    else:
        return kwargs | {'username': 'Log in', 'userimg': return_image(f'users/{email}', 'user_placeholder')}

def getTovarsData(folder_path):
    total = dict()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            d = json.loads(content)
            total |= d
            for i in d:
                d[i] |= {"tovars": {}}
            way = f"{pathlib.Path(__file__).parent.resolve()}/tovars/{filename[:-5]}"
            for tovar in os.listdir(way):
                tovar_path = os.path.join(way, tovar)
                with open(tovar_path, 'r', encoding='utf-8') as f1:
                    info = f1.read()
                    tov = json.loads(info)
                    for i in d:
                        d[i]["tovars"] |= tov
    return total