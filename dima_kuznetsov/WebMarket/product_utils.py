import os


CATEGORIES = {
    'supercars': {'name': 'Суперкары', 'icon': '🏎️'},
    'sportscars': {'name': 'Спорт-кары', 'icon': '🚗'},
    'motorcycles': {'name': 'Топ-мотоциклы', 'icon': '🏍️'}
}

PRODUCTS_PATH = "products_data"
UPLOAD_PATH = "static/images"
MAX_UPLOAD_SIZE = 64 * 1024 * 1024  # 64MB лимит
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def load_products_from_files():

    # простой парсер файлов БД, мини аналог json в txt; 
    # функция извлекает все продукты, без этого никак

    products = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_dir, PRODUCTS_PATH)
    
    for product_file in os.listdir(base_path):
        if product_file.endswith('.txt'):
            with open(os.path.join(base_path, product_file), 'r', encoding='utf-8') as f:
                product_data = {}
                for line in f:
                    if not (':' in line):
                        continue
                    key, value = line.strip().split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'images':
                        product_data[key] = [img.strip() for img in value.split(',')]
                    elif key == 'specs':
                        specs = {}
                        for spec in value.split('|'):
                            if not (':' in spec): 
                                continue
                            spec_key, spec_value = spec.split(':', 1)
                            specs[spec_key.strip()] = spec_value.strip()
                        product_data[key] = specs
                    elif key in ['price', 'stock', 'bestseller']:
                        try:
                            product_data[key] = int(value)
                        except:
                            product_data[key] = 0
                    else:
                        product_data[key] = value
                
                products.append(product_data)

    return products


def get_products_by_category(category, need_specs):
    # вернуть продукты какой-то категории; по надобности - пункты сравнения товаров
    all_products = load_products_from_files()
    ans = [p for p in all_products if p['category'] == category]
    ans.sort(key=lambda x: x['bestseller'], reverse=True)

    if not need_specs:
        return ans
    all_specs = set().union(*(product.get('specs', {}).keys() for product in all_products))
    return ans, all_specs


def product_page_template_data(product_id):
    # вернуть информацию о товаре
    products = load_products_from_files()
    product = None
    for p in products:
        if p['id'] == product_id:
            product = p
            break
    
    if not product:
        return 404
    
    template_data = {
        'product': product,
        'category_name': CATEGORIES[product['category']]['name'],
        'category_url': product['category']
    }
    return template_data


def allowed_file(filename):
    # проверка расширения
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_new_product_file(data, files):
    # создать файл с новым продуктом
    image_filename = 'default.jpg'

    if 'image' in files:
        file = files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = file.filename
            
            product_id = data['id']
            ext = filename.rsplit('.', 1)[1].lower()
            image_filename = f"{product_id}.{ext}"
            
            file.save(os.path.join(UPLOAD_PATH, image_filename))

    product_data = f"""id: {data['id']}
    name: {data['name']}
    category: {data['category']}
    price: {data['price']}
    stock: {data['stock']}
    images: {image_filename}
    description: {data['description']}
    specs: Мощность: {data.get('power', 'N/A')}|Разгон 0-100: {data.get('acceleration', 'N/A')}|Тип: {data.get('type', 'N/A')}
    bestseller: 0
    brand: {data['brand']}"""
        
    filename = f"{data['id']}.txt"
    os.makedirs(f'{PRODUCTS_PATH}/', exist_ok=True)
    
    with open(f'{PRODUCTS_PATH}/{filename}', 'w', encoding='utf-8') as f:
        f.write(product_data)
