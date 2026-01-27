import os

USER_DATA_PATH = 'user_data'
AVATARS_PATH = 'static/images/avatars'


def user_exists(email):
    return os.path.exists(f"{USER_DATA_PATH}/{email}.txt")


def validate_pass_and_email(new_email, password, confirm_password):
    if user_exists(new_email):
        return False, "Пользователь с таким email уже существует"
    if password != confirm_password:
        return False, "Пароли не совпадают"
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    return True, ""


def create_user_text(email, password, user_data, avatar_filename):
    return f"""email: {email}
password: {password}
first_name: {user_data.get('first_name', '')}
last_name: {user_data.get('last_name', '')}
phone: {user_data.get('phone', '')}
birthdate: {user_data.get('birthdate', '')}
gender: {user_data.get('gender', 'male')}
avatar: {avatar_filename}"""


def save_avatar(avatar_file, email):
    avatar_filename = 'default_avatar.jpg'
    if avatar_file and avatar_file.filename != '':
        filename = avatar_file.filename
        if filename:
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
            avatar_filename = f"{email}.{ext}"
            avatar_file.save(os.path.join(AVATARS_PATH, avatar_filename))
    return avatar_filename


def save_user(user_data, avatar_file):
    os.makedirs(USER_DATA_PATH, exist_ok=True)
    os.makedirs(AVATARS_PATH, exist_ok=True)
    email = user_data['email']
    avatar_filename = save_avatar(avatar_file, email)
    user_content = create_user_text(email, user_data['password'], user_data, avatar_filename)

    with open(f"{USER_DATA_PATH}/{email}.txt", 'w', encoding='utf-8') as f:
        f.write(user_content)


def get_user(email):
    filepath = f"{USER_DATA_PATH}/{email}.txt"
    if not os.path.exists(filepath):
        return None
    user_data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                user_data[key.strip()] = value.strip()
    return user_data


def authenticate_user(email, password):
    user = get_user(email)
    if not user:
        return False, "Пользователь с таким email не найден"
    if user.get('password') != password:
        return False, "Неверный пароль"
    return True, user


def update_user(email, user_data, avatar_file):
    os.makedirs(USER_DATA_PATH, exist_ok=True)
    os.makedirs(AVATARS_PATH, exist_ok=True)
    
    current_user = get_user(email)
    if not current_user:
        return False, "Пользователь не найден"
    
    password = user_data.get('password', current_user.get('password'))
    if user_data.get('new_password'):
        if user_data.get('new_password') != user_data.get('confirm_password', ''):
            return False, "Новые пароли не совпадают"
        password = user_data['new_password']
    
    avatar_filename = current_user.get('avatar', 'default_avatar.jpg')
    if avatar_file and avatar_file.filename != '':
        # удаление старой аватарки
        if avatar_filename and avatar_filename != 'default_avatar.jpg':
            old_path = os.path.join(AVATARS_PATH, avatar_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        # сохранение новой
        avatar_filename = save_avatar(avatar_file, email)
    
    updated_content = create_user_text(email, password, user_data, avatar_filename)

    with open(f"{USER_DATA_PATH}/{email}.txt", 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return True, "Данные успешно обновлены"