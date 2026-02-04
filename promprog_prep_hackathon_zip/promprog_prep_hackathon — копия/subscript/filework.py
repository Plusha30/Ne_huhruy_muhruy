#Выделенный файл для работы с файлами

import pathlib
import os
import json
from datetime import date, datetime

base_path = str(pathlib.Path(__file__).parent.resolve())[:-10]
SESSION_PATH = f'{base_path}/sessions'
#Осторожно, костыль. [:-10] возвращает корневую папку всего проекта, несмотря на то, что этот файл лежит в папке subscript
#Возможно есть решение покрасивее. Но это тоже работает.

def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs(email):
    if (getuser(email) != False):
        user = getuser(email)
        ans = dict()
        ans['userimg'] = return_image(f'users/{email}', 'user_placeholder')
        for u in user:
            if (u != 'password'):
                ans[u] = user[u]
        return ans
    else:
        return {'username': 'Log in', 'userimg': return_image(f'users/{email}', 'user_placeholder'), \
            'description': 'empty', 'phone': 'N/A', 'rights': 0, 'money': 0, 'abonement': 'null'}

def today_days():
    today = date.today()
    epoch_date = date(1970, 1, 1)
    return (today - epoch_date).days

def today_hour():
    return datetime.now().hour

def getuser(email):
    users_path = f"{base_path}/users/{email}.json"
    if os.path.exists(users_path):
        with open(users_path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    return False

def setuser(email, changes):
    users_path = f"{base_path}/users/{email}.json"
    with open(users_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(changes, indent = 4))

def settovar(id, to):
    users_path = f"{base_path}/tovars/{id}.json"
    with open(users_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(to, indent = 4))

def gettovar(id):
    tovars_path = f"{base_path}/tovars/{id}.json"
    if os.path.exists(tovars_path):
        with open(tovars_path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    return False

def setquerylist(name, to):
    users_path = f"{base_path}/queries/{name}"
    with open(users_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(to, indent = 4))

def getquerylist(name):
    tovars_path = f"{base_path}/queries/{name}"
    if os.path.exists(tovars_path):
        with open(tovars_path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    return False

def gettovarlist():
    with open(f"{base_path}/tovars/tovars.json", 'r', encoding='utf-8') as f:
        return json.loads(f.read())
