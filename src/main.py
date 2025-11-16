import csv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Movie(BaseModel):
    movieId: str
    title: str
    genres: str

class Link(BaseModel):
    movieId: str
    imdbId: str
    tmdbId: str

class Rating(BaseModel):
    userId: str
    movieId: str
    rating: float
    timestamp: str

class Tag(BaseModel):
    userId: str
    movieId: str
    tag: str
    timestamp: str

@app.get("/movies", response_model=List[dict])
def get_movies():
    movies = []
    with open('database/movies.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            movie = Movie(**row)
            movies.append(movie.__dict__) 
    return movies


@app.get("/links", response_model=List[dict])
def get_links():
    links = []
    with open('database/links.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            link = Link(**row)
            links.append(link.__dict__)
    return links


@app.get("/ratings", response_model=List[dict])
def get_ratings():
    ratings = []
    with open('database/ratings.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['rating'] = float(row['rating'])
            rating = Rating(**row)
            ratings.append(rating.__dict__)
    return ratings


@app.get("/tags", response_model=List[dict])
def get_tags():
    tags = []
    with open('database/tags.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tag = Tag(**row)
            tags.append(tag.__dict__)
    return tags


@app.get("/")
def read_root():
    return {"hello": "world"}
