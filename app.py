import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media_site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['MAX_CONTENT_LENGTH'] = None  # No file size limit

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv'}

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    media_files = db.relationship('MediaFile', backref='user', lazy=True)

class MediaFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # 'photo' or 'video'
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def allowed_file(filename, file_type):
    if file_type == 'photo':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS
    elif file_type == 'video':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    return False

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    media_files = MediaFile.query.filter_by(user_id=session['user_id']).order_by(MediaFile.upload_date.desc()).all()
    return render_template('index.html', media_files=media_files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor!', 'error')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı!', 'info')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash('Dosya seçilmedi!', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi!', 'error')
        return redirect(url_for('index'))
    
    # Determine file type
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    if file_extension in ALLOWED_PHOTO_EXTENSIONS:
        file_type = 'photo'
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')
    elif file_extension in ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
    else:
        flash('Desteklenmeyen dosya formatı!', 'error')
        return redirect(url_for('index'))
    
    if allowed_file(file.filename, file_type):
        # Generate unique filename
        original_filename = file.filename
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Save to database
        media_file = MediaFile(
            filename=unique_filename,
            original_filename=original_filename,
            file_type=file_type,
            file_size=file_size,
            user_id=session['user_id']
        )
        
        db.session.add(media_file)
        db.session.commit()
        
        flash('Dosya başarıyla yüklendi!', 'success')
    else:
        flash('Desteklenmeyen dosya formatı!', 'error')
    
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Bu sayfaya erişim izniniz yok!', 'error')
        return redirect(url_for('index'))
    
    all_media = MediaFile.query.order_by(MediaFile.upload_date.desc()).all()
    users = User.query.all()
    
    return render_template('admin.html', media_files=all_media, users=users)

@app.route('/admin/delete/<int:media_id>')
def admin_delete_media(media_id):
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Bu işlem için yetkiniz yok!', 'error')
        return redirect(url_for('index'))
    
    media = MediaFile.query.get_or_404(media_id)
    
    # Delete file from filesystem
    if media.file_type == 'photo':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', media.filename)
    else:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', media.filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from database
    db.session.delete(media)
    db.session.commit()
    
    flash('Medya dosyası silindi!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/uploads/<file_type>/<filename>')
def uploaded_file(file_type, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], file_type), filename)

@app.route('/download/<file_type>/<filename>')
def download_file(file_type, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_type, filename)
    return send_from_directory(os.path.dirname(file_path), filename, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin kullanıcı oluşturuldu: admin / admin123")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
