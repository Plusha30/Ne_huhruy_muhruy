import os
import re

# Поиск всех HTML файлов
for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r"url_for\('compare_page'", content)
                if matches:
                    print(f"В файле {path} найдено {len(matches)} неправильных ссылок:")
                    for i, match in enumerate(matches, 1):
                        print(f"  {i}. {match}")