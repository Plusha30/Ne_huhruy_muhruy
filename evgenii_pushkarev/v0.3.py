from flask import Flask, render_template, send_from_directory, abort, request
import os
import glob

app = Flask(__name__)


# Функция для загрузки данных товаров из txt файлов
def load_products():
    products = []
    if not os.path.exists('products'):
        os.makedirs('products')
        print("Создана папка products. Добавьте туда txt файлы с товарами.")
        return products

    product_files = glob.glob('products/*.txt')
    print(f"Найдено файлов товаров: {len(product_files)}")

    for file_path in product_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            print(f"Обрабатываем файл: {file_path}, строк: {len(lines)}")

            if len(lines) >= 10:  # Уменьшил минимальное количество полей
                product = {
                    'id': os.path.basename(file_path).replace('.txt', ''),
                    'name': lines[0],
                    'category': lines[1],
                    'category_name': lines[2],
                    'price': int(lines[3].replace('₽', '').replace(' ', '')) if lines[3].replace('₽', '').replace(' ',
                                                                                                                  '').isdigit() else 0,
                    'manufacturer': lines[4],
                    'year': lines[5],
                    'image': lines[6],
                    'in_stock': int(lines[7]) if lines[7].isdigit() else 1,
                    'description': lines[8] if len(lines) > 8 else 'Описание отсутствует',
                    'features': lines[9] if len(lines) > 9 else ''
                }
                products.append(product)
                print(f"Добавлен товар: {product['name']}, категория: {product['category']}")
            else:
                print(f"Файл {file_path} содержит недостаточно данных: {len(lines)} строк")

        except Exception as e:
            print(f"Ошибка загрузки файла {file_path}: {e}")

    return products


# Функция для фильтрации товаров
def filter_products(products, filters):
    filtered_products = products.copy()

    # Фильтр по цене
    min_price = filters.get('min_price')
    max_price = filters.get('max_price')
    if min_price and min_price.isdigit():
        filtered_products = [p for p in filtered_products if p['price'] >= int(min_price)]
    if max_price and max_price.isdigit():
        filtered_products = [p for p in filtered_products if p['price'] <= int(max_price)]

    # Фильтр по брендам
    selected_brands = filters.getlist('brand')
    if selected_brands:
        filtered_products = [p for p in filtered_products if p['manufacturer'] in selected_brands]

    # Фильтр по наличию
    in_stock_only = filters.get('in_stock')
    if in_stock_only:
        filtered_products = [p for p in filtered_products if p['in_stock'] > 0]

    # Фильтр по году (новый фильтр)
    min_year = filters.get('min_year')
    max_year = filters.get('max_year')
    if min_year and min_year.isdigit():
        filtered_products = [p for p in filtered_products if int(p['year']) >= int(min_year)]
    if max_year and max_year.isdigit():
        filtered_products = [p for p in filtered_products if int(p['year']) <= int(max_year)]

    # Фильтр по состоянию (новый фильтр)
    condition_filter = filters.get('condition')
    if condition_filter:
        if condition_filter == 'excellent':
            filtered_products = [p for p in filtered_products if p['in_stock'] > 0 and p['price'] > 50000]
        elif condition_filter == 'good':
            filtered_products = [p for p in filtered_products if p['in_stock'] > 0 and 30000 <= p['price'] <= 50000]

    return filtered_products


# Главная страница
@app.route('/')
def index():
    products = load_products()
    return render_template('index.html', products=products)


# Страницы категорий с поддержкой фильтров
@app.route('/<page_name>')
def show_page(page_name):
    if not page_name.endswith('.html'):
        page_name += '.html'

    category_map = {
        'classic.html': 'classic',
        'pinball.html': 'pinball',
        'racing.html': 'racing'
    }

    if page_name in category_map:
        target_category = category_map[page_name]
        products = load_products()
        category_products = [p for p in products if p['category'] == target_category]

        print(f"Категория: {target_category}, найдено товаров: {len(category_products)}")
        for p in category_products:
            print(f" - {p['name']} (категория: {p['category']})")

        # Применяем фильтры из GET-параметров
        filtered_products = filter_products(category_products, request.args)

        # Получаем уникальные бренды для текущей категории
        available_brands = list(set(p['manufacturer'] for p in category_products))

        # Получаем диапазон годов для фильтра
        years = [int(p['year']) for p in category_products if p['year'].isdigit()]
        min_year = min(years) if years else 1970
        max_year = max(years) if years else 2024

        category_name = category_products[0]['category_name'] if category_products else "Категория"

        return render_template(page_name,
                               products=filtered_products,
                               all_products=category_products,
                               category_name=category_name,
                               available_brands=available_brands,
                               min_year=min_year,
                               max_year=max_year,
                               current_filters=request.args)

    template_path = os.path.join(app.template_folder, page_name)
    if os.path.exists(template_path):
        return render_template(page_name)
    else:
        return render_template('404.html'), 404

# ... остальные маршруты остаются без изменений