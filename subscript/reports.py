import pandas as pd
from io import BytesIO
import json
import os
from datetime import datetime

def generate_student_buys_report(json_path):
    """
    Генерирует Excel отчет со всеми пользователями из JSON файлов
    Возвращает BytesIO объект с Excel файлом
    """
    # Список для хранения данных пользователей
    users_list = []
    
    # Проверяем существует ли директория
    if not os.path.exists(json_path):
        # Если папки нет, возвращаем отчет с демо-данными
        return _generate_demo_report()
    
    # Читаем JSON файл
    with open(json_path, 'r', encoding='utf-8') as f:
        users_list = json.load(f)
    
    # Если нет пользователей, возвращаем демо-отчет
    if not users_list:
        return _generate_demo_report()
    
    # Создаем DataFrame из списка пользователей
    df = pd.DataFrame(users_list)
    
    # Преобразуем числовые права в текстовые
    complete_map = {
        False: 'Нет',
        True: 'Да'
    }
    
    if 'isCooked' in df.columns:
        df['Приготовлен'] = df['isCooked'].map(complete_map)

    if 'isComplete' in df.columns:
        df['Получен'] = df['isComplete'].map(complete_map)
    
    # Переименовываем колонки
    column_mapping = {
        'id': 'ID',
        'user': 'Пользователь',
        'class': 'Класс',
        'phone': 'Телефон',
        'money': 'Цена',
        'what': 'Список товаров',
        'time': 'Время',
        'date': 'Дата'
    }
    
    # Применяем переименование, если колонки существуют
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Определяем порядок колонок для отчета
    desired_columns = ['ID', 'Пользователь', 'Класс', 'Телефон', 'Цена', 'Список товаров', 'Время', 'Дата', 'Приготовлен', 'Получен']
    report_columns = [col for col in desired_columns if col in df.columns]
    
    # Создаем финальный DataFrame с нужными колонками
    df_report = df[report_columns]
    
    # Создаем Excel файл в памяти
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Записываем данные в лист "Пользователи"
        df_report.to_excel(writer, sheet_name='Покупки', index=False)
        
        # Получаем объект листа
        worksheet = writer.sheets['Покупки']
        
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

def generate_product_report(json_path):
    """
    Генерирует Excel отчет со всеми пользователями из JSON файлов
    Возвращает BytesIO объект с Excel файлом
    """
    # Список для хранения данных пользователей
    users_list = []
    
    # Проверяем существует ли директория
    if not os.path.exists(json_path):
        # Если папки нет, возвращаем отчет с демо-данными
        return _generate_demo_report()
    
    # Читаем JSON файл
    with open(json_path, 'r', encoding='utf-8') as f:
        users_list = json.load(f)
    
    # Если нет пользователей, возвращаем демо-отчет
    if not users_list:
        return _generate_demo_report()
    
    # Создаем DataFrame из списка пользователей
    df = pd.DataFrame(users_list)
    
    # Преобразуем числовые права в текстовые
    complete_map = {
        -1: "Отклонено",
        0: "Не согласовано",
        1: "Принято"
    }
    
    if 'status' in df.columns:
        df['Результат'] = df['status'].map(complete_map)

    # Переименовываем колонки
    column_mapping = {
        'id': 'ID',
        'prod': 'Продукт',
        'volume': 'Объём',
        'person': 'Повар',
        'when': 'Время',
        'cost': 'Цена',
        'desc': 'Описание'
    }
    
    # Применяем переименование, если колонки существуют
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Определяем порядок колонок для отчета
    desired_columns = ['ID', 'Продукт', 'Объём', 'Повар', 'Время', 'Цена', 'Результат', 'Описание']
    report_columns = [col for col in desired_columns if col in df.columns]
    
    # Создаем финальный DataFrame с нужными колонками
    df_report = df[report_columns]
    
    # Создаем Excel файл в памяти
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Записываем данные в лист "Пользователи"
        df_report.to_excel(writer, sheet_name='Покупки', index=False)
        
        # Получаем объект листа
        worksheet = writer.sheets['Покупки']
        
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
            'Данные отсутствуют': '0'
        }
    ]
    
    df = pd.DataFrame(demo_data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Пусто', index=False)
        
        # Автоширина колонок
        worksheet = writer.sheets['Пусто']
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