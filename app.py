from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import google.generativeai as genai

app = Flask(__name__)

# Secret key (güvenlik için)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Veritabanı yapılandırması
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "site.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flask-Login yapılandırması
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'info'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Project Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    github_link = db.Column(db.String(500))
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return f'<Project {self.title}>'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Veritabanını oluştur ve seed data ekle - Uygulama başladığında otomatik çalışır
with app.app_context():
    # instance klasörünü oluştur
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Veritabanı tablolarını oluştur
    db.create_all()
    
    # Varsayılan admin kullanıcısı oluştur (eğer yoksa)
    if User.query.count() == 0:
        admin_user = User(
            username='admingh645ghf',
            password_hash=generate_password_hash('admin123ghfj')  # Üretimde değiştirin!
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin kullanıcısı oluşturuldu: admingh645ghf / admin123ghfj")
    
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız!', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    projects = Project.query.all()
    return render_template('admin.html', projects=projects)

@app.route('/admin/project/add', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    github_link = request.form.get('github_link', '')
    image_url = request.form.get('image_url', '')
    
    if title and description:
        project = Project(
            title=title,
            description=description,
            github_link=github_link,
            image_url=image_url
        )
        db.session.add(project)
        db.session.commit()
        flash('Proje başarıyla eklendi!', 'success')
    else:
        flash('Başlık ve açıklama zorunludur!', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/project/<int:project_id>/edit', methods=['POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    project.title = request.form.get('title', project.title)
    project.description = request.form.get('description', project.description)
    project.github_link = request.form.get('github_link', project.github_link)
    project.image_url = request.form.get('image_url', project.image_url)
    
    db.session.commit()
    flash('Proje başarıyla güncellendi!', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Proje başarıyla silindi!', 'success')
    
    return redirect(url_for('admin'))

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

