from fastapi import FastAPI
from sqlalchemy.orm import Session
from .models import Movie, Link, Rating, Tag
from .database import engine, SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
get_db()

@app.get("/movies")
def get_movies():
    with SessionLocal() as db:
        return db.query(Movie).all()

@app.get("/links")
def get_links():
    with SessionLocal() as db:
        return db.query(Link).all()

@app.get("/ratings")
def get_ratings():
    with SessionLocal() as db:
        return db.query(Rating).all()

@app.get("/tags")
def get_tags():
    with SessionLocal() as db:
        return db.query(Tag).all()


@app.get("/")
def read_root():
    return {"hello": "world"}
