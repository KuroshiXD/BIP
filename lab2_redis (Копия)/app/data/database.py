from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        # Импортируем модели для создания таблиц
        from .models import NoteModel  # noqa
        Base.metadata.create_all(bind=self.engine)

    def session(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()