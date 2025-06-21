from app import app, db
from models import Subject

def create_initial_data():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created.")

        # Перевіряємо, чи предмети вже існують
        if Subject.query.first() is None:
            print("Adding initial subjects...")
            
            ukrainian = Subject(
                name="Українська мова",
                slug="ukrainian-language",
                description="Курс з української мови, що охоплює основні правила граматики, синтаксису та лексикології. Готуємося до ЗНО та покращуємо свої знання разом!"
            )
            
            math = Subject(
                name="Математика",
                slug="mathematics",
                description="Всебічний курс з математики: від алгебри та геометрії до початків аналізу. Розв'язуємо задачі, вивчаємо теореми та розвиваємо логічне мислення."
            )
            
            history = Subject(
                name="Історія України",
                slug="history-of-ukraine",
                description="Подорож у часі від стародавніх племен на території України до сучасності. Вивчаємо ключові події, видатних постатей та культурні досягнення."
            )
            
            db.session.add(ukrainian)
            db.session.add(math)
            db.session.add(history)
            
            db.session.commit()
            print("Initial subjects added.")
        else:
            print("Subjects already exist. Skipping.")

if __name__ == '__main__':
    create_initial_data()