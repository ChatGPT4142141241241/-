from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    nickname = Column(String)
    game_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    favorites = relationship("FavoriteHero", back_populates="user")
    builds = relationship("Build", back_populates="user")
    notes = relationship("Note", back_populates="user")

class Hero(Base):
    __tablename__ = 'heroes'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    role = Column(String)
    difficulty = Column(String)
    win_rate = Column(Float)
    image_path = Column(String)
    guide = Column(Text)
    tier = Column(String)
    favorites = relationship("FavoriteHero", back_populates="hero")

class FavoriteHero(Base):
    __tablename__ = 'favorite_heroes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hero_id = Column(Integer, ForeignKey('heroes.id'))
    user = relationship("User", back_populates="favorites")
    hero = relationship("Hero", back_populates="favorites")

class Build(Base):
    __tablename__ = 'builds'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hero_id = Column(Integer, ForeignKey('heroes.id'))
    name = Column(String)
    items = Column(Text)
    description = Column(Text)
    user = relationship("User", back_populates="builds")

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    content = Column(Text)
    user = relationship("User", back_populates="notes")

class Term(Base):
    __tablename__ = 'terms'
    id = Column(Integer, primary_key=True)
    term = Column(String, unique=True)
    category = Column(String)
    definition = Column(Text)
    example = Column(Text)

class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    correct_answer = Column(String)
    options = Column(Text)  # JSON string of options
    category = Column(String)

class ShopItem(Base):
    __tablename__ = 'shop_items'
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey('users.id'))
    category = Column(String)  # diamonds, skin, account, service
    title = Column(String)
    description = Column(Text)
    price = Column(Float)
    image_path = Column(String)
    status = Column(String)  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

# Создание базы данных
engine = create_engine('sqlite:///ml_helper.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session() 