from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

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

if __name__ == '__main__':
    app.run(debug=True)

