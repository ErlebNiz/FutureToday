import os
from flask import Flask, request, redirect, url_for, send_file, render_template
import pandas as pd
import requests
from io import BytesIO


app = Flask(__name__)


ACCESS_TOKEN = ''

# Функция для сокращения ссылки через VK API
def shorten_url(long_url):
    api_url = "https://api.vk.com/method/utils.getShortLink"

    params = {
        'url': long_url,  
        'access_token': ACCESS_TOKEN,  
        'v': '5.131'  
    }
    
    response = requests.get(api_url, params=params).json()
    
    if 'response' in response:
        return response['response']['short_url'] 
    else:
        return None  

@app.route('/')
def upload_file():
    return render_template('upload.html')  # Отображаем HTML-шаблон для загрузки

# Обработчик загрузки файла
@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        # Получаем загруженный файл
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            input_df = pd.read_excel(file)
             # Получаем ссылки из первого столбца .xlsx файла
            urls = input_df.iloc[:, 0].tolist()
            
            # Список для хранения сокращенных ссылок
            short_urls = []
            
            # Проходим по каждой ссылке и сокращаем её
            for url in urls:
                short_url = shorten_url(url)
                short_urls.append(short_url)
            
            # Создаем DataFrame с оригинальными и сокращенными ссылками
            output_df = pd.DataFrame({
                'Original URL': urls,
                'Short URL': short_urls
            })
            
            # Сохраняем результат в новый .xslx файл в памяти (без записи на диск)
            output = BytesIO()
            output_df.to_excel(output, index=False)
            output.seek(0)
            
            # Отправляем файл пользователю для скачивания
            return send_file(output, as_attachment=True, download_name='output.xlsx')
    
    # Если файл не был загружен или формат не поддерживается, возвращаем на главную страницу
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True) 