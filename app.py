from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import google.generativeai as genai

app = Flask(__name__)

# Veritabanı yapılandırması
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "site.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Project Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    github_link = db.Column(db.String(500))
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return f'<Project {self.title}>'

# Veritabanını oluştur ve seed data ekle - Uygulama başladığında otomatik çalışır
with app.app_context():
    # instance klasörünü oluştur
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Veritabanı tablolarını oluştur
    db.create_all()
    
    # Eğer veritabanı boşsa seed data ekle
    if Project.query.count() == 0:
        projects = [
            Project(
                title="Brain Tumor Detection",
                description="Derin öğrenme kullanarak beyin tümörü tespiti ve görüntü analizi projesi. CNN mimarisi ile yüksek doğruluk oranı elde edildi.",
                github_link="https://github.com/burakyalinat/brain-tumor-detection",
                image_url=""
            ),
            Project(
                title="NLP Sentiment Analysis",
                description="Doğal dil işleme teknikleri kullanarak metin duygu analizi yapan model. LSTM ve Transformer mimarileri ile geliştirildi.",
                github_link="https://github.com/burakyalinat/nlp-sentiment-analysis",
                image_url=""
            ),
            Project(
                title="GAN Image Generation",
                description="Generative Adversarial Networks kullanarak gerçekçi görüntü üretimi. StyleGAN ve DCGAN mimarileri ile çalışıldı.",
                github_link="https://github.com/burakyalinat/gan-image-generation",
                image_url=""
            )
        ]
        
        for project in projects:
            db.session.add(project)
        
        db.session.commit()
        print("Seed data başarıyla eklendi!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Mesaj boş olamaz'}), 400
        
        # Gemini API anahtarını ortam değişkeninden al
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'error': 'GEMINI_API_KEY ortam değişkeni ayarlanmamış'}), 500
        
        # Gemini API'yi yapılandır
        genai.configure(api_key=api_key)
        
        # Generation config - daha tutarlı ve hızlı cevaplar için
        generation_config = {
            'temperature': 0.7,  # Düşük değer daha tutarlı cevaplar verir (0.0-1.0)
            'top_p': 0.95,        # Nucleus sampling
            'top_k': 40,          # Top-k sampling
            'max_output_tokens': 1024,  # Maksimum token sayısı
        }
        
        # Gemini 1.5 Flash modelini kullan (güncel ve hızlı)
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=generation_config
        )
        
        # Sistem mesajı ile birlikte kullanıcı mesajını gönder
        system_prompt = "Sen Burak'ın asistanısın. Burak bir Deep Learning mühendisi. Zeki, kısa ve hafif esprili cevaplar ver."
        full_prompt = f"{system_prompt}\n\nKullanıcı: {user_message}\nAsistan:"
        
        response = model.generate_content(full_prompt)
        
        return jsonify({'response': response.text})
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': 'Bir hata oluştu'}), 500

if __name__ == '__main__':
    app.run(debug=True)

