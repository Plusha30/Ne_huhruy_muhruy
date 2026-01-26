import pandas as pd
from io import BytesIO
import json
import os
from datetime import datetime

def generate_users_report(users_dir_path):
    """
    Генерирует Excel отчет со всеми пользователями из JSON файлов
    Возвращает BytesIO объект с Excel файлом
    """
    # Список для хранения данных пользователей
    users_list = []
    
    # Проверяем существует ли директория
    if not os.path.exists(users_dir_path):
        # Если папки нет, возвращаем отчет с демо-данными
        return _generate_demo_report()
    
    # Сканируем все JSON файлы в папке users
    for filename in os.listdir(users_dir_path):
        if filename.endswith('.json'):
            filepath = os.path.join(users_dir_path, filename)
            
            try:
                # Читаем JSON файл
                with open(filepath, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                
                # Добавляем email из имени файла
                user_email = filename.replace('.json', '')
                user_data['email'] = user_email
                
                # Добавляем в список
                users_list.append(user_data)
                
            except Exception as e:
                print(f"Ошибка при чтении файла {filename}: {e}")
                continue
    
    # Если нет пользователей, возвращаем демо-отчет
    if not users_list:
        return _generate_demo_report()
    
    # Создаем DataFrame из списка пользователей
    df = pd.DataFrame(users_list)
    
    # Преобразуем числовые права в текстовые
    rights_map = {
        0: 'Гость',
        1: 'Пользователь', 
        2: 'Модератор',
        3: 'Администратор'
    }
    
    if 'rights' in df.columns:
        df['Права доступа'] = df['rights'].map(rights_map)
    
    # Переименовываем колонки
    column_mapping = {
        'email': 'Email',
        'username': 'Имя',
        'phone': 'Телефон',
        'money': 'Баланс',
        'description': 'Описание'
    }
    
    # Применяем переименование, если колонки существуют
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Определяем порядок колонок для отчета
    desired_columns = ['Email', 'Имя', 'Телефон', 'Права доступа', 'Баланс', 'Описание']
    report_columns = [col for col in desired_columns if col in df.columns]
    
    # Создаем финальный DataFrame с нужными колонками
    df_report = df[report_columns]
    
    # Создаем Excel файл в памяти
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Записываем данные в лист "Пользователи"
        df_report.to_excel(writer, sheet_name='Пользователи', index=False)
        
        # Получаем объект листа
        worksheet = writer.sheets['Пользователи']
        
        # Автоматически настраиваем ширину колонок
        for column in worksheet.columns:
            column_letter = column[0].column_letter
            max_length = 0
            
            for cell in column:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            
            # Устанавливаем ширину (+2 для отступов)
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Перемещаем указатель в начало потока
    output.seek(0)
    
    return output

def _generate_demo_report():
    """
    Создает демо-отчет для тестирования
    """
    # Демо-данные
    demo_data = [
        {
            'Email': 'admin@example.com',
            'Имя': 'Администратор Системы',
            'Телефон': '+7 (999) 123-45-67',
            'Права доступа': 'Администратор',
            'Баланс': 5000,
            'Описание': 'Главный администратор'
        },
        {
            'Email': 'user@example.com',
            'Имя': 'Иван Иванов',
            'Телефон': '+7 (987) 654-32-10',
            'Права доступа': 'Пользователь',
            'Баланс': 1500,
            'Описание': 'Обычный пользователь'
        }
    ]
    
    df = pd.DataFrame(demo_data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Пользователи (демо)', index=False)
        
        # Автоширина колонок
        worksheet = writer.sheets['Пользователи (демо)']
        for column in worksheet.columns:
            column_letter = column[0].column_letter
            max_length = 0
            for cell in column:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    output.seek(0)
    return output