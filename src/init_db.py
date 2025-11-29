import csv
from sqlalchemy.orm import Session
from database import engine
from models import Base, Movie, Link, Rating, Tag

Base.metadata.create_all(engine)

with Session(engine) as session:

    if session.query(Movie).first():
        print("Database already initialized. Skipping CSV load.")
    else:
        print("Loading CSV data into the database...")

        with open("database/movies.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                session.add(Movie(
                    movieId=int(row["movieId"]),
                    title=row["title"],
                    genres=row["genres"]
                ))

        with open("database/links.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                session.add(Link(
                    movieId=int(row["movieId"]),
                    imdbId=row["imdbId"],
                    tmdbId=row["tmdbId"]
                ))

        with open("database/ratings.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                session.add(Rating(
                    userId=int(row["userId"]),
                    movieId=int(row["movieId"]),
                    rating=float(row["rating"]),
                    timestamp=row["timestamp"]
                ))

        with open("database/tags.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                session.add(Tag(
                    userId=int(row["userId"]),
                    movieId=int(row["movieId"]),
                    tag=row["tag"],
                    timestamp=row["timestamp"]
                ))

        session.commit()
