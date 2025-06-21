from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Subject, Lesson

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key-for-sessions'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prepaire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

# app.py

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Користувач з таким іменем вже існує!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)

        # ↓↓↓ ОНОВЛЕНА ЛОГІКА ПРИЗНАЧЕННЯ РОЛЕЙ ↓↓↓
        if username.startswith('moderator_ukr_'):
            new_user.role = 'moderator_ukr'
        elif username.startswith('moderator_mat_'):
            new_user.role = 'moderator_mat'
        elif username.startswith('moderator_ist_'):
            new_user.role = 'moderator_ist'
        elif username.startswith('moderator_'): # Цю перевірку ставимо останньою
            new_user.role = 'moderator'
        else:
            new_user.role = 'user'
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Вхід успішний!', 'success')
            return redirect(url_for('base'))
        else:
            flash('Неправильне ім\'я користувача або пароль.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('base'))

@app.route('/subjects')
def subjects():
    all_subjects = Subject.query.all()
    return render_template('subjects.html', subjects=all_subjects)

def check_permission(user_role, subject_slug):
    if user_role == 'moderator':
        return True
    if user_role == 'moderator_ukr' and subject_slug == 'ukrainian-language':
        return True
    if user_role == 'moderator_mat' and subject_slug == 'mathematics':
        return True
    if user_role == 'moderator_ist' and subject_slug == 'history-of-ukraine':
        return True
    return False

@app.route('/subject/<slug>')
def subject_page(slug):
    subject = Subject.query.filter_by(slug=slug).first_or_404()
    user_role = session.get('role', 'guest') # Отримуємо роль, або 'guest' якщо не залогінений
    # ↓↓↓ Передаємо в шаблон інформацію, чи може користувач редагувати ↓↓↓
    can_edit = check_permission(user_role, subject.slug)
    return render_template('subject_page.html', subject=subject, can_edit=can_edit)


@app.route('/add_lesson/<subject_slug>', methods=['POST'])
def add_lesson(subject_slug):
    user_role = session.get('role')
    # ↓↓↓ Використовуємо нашу нову функцію для перевірки ↓↓↓
    if not check_permission(user_role, subject_slug):
        flash('У вас немає прав для додавання уроків до цього предмету!', 'danger')
        return redirect(url_for('subject_page', slug=subject_slug))
    
    # ... (решта логіки функції залишається без змін) ...
    subject = Subject.query.filter_by(slug=subject_slug).first_or_404()
    
    title = request.form['title']
    slug = request.form['slug']
    content = request.form['content']

    if not title or not content or not slug:
        flash('Всі поля (назва, URL, зміст) є обов\'язковими.', 'warning')
        return redirect(url_for('subject_page', slug=subject_slug))

    if Lesson.query.filter_by(slug=slug).first():
        flash('Урок з такою URL-адресою вже існує. Виберіть іншу.', 'danger')
        return redirect(url_for('subject_page', slug=subject_slug))
        
    new_lesson = Lesson(title=title, slug=slug, content=content, subject_id=subject.id)
    db.session.add(new_lesson)
    db.session.commit()
    
    flash('Новий урок успішно додано!', 'success')
    return redirect(url_for('subject_page', slug=subject.slug))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/lesson/<lesson_slug>')
def lesson_page(lesson_slug):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()
    return render_template('lesson_page.html', lesson=lesson)

if __name__ == '__main__':
    app.run(debug=True)