from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, ForeignKey

class Base(DeclarativeBase):
    pass

class Movie(Base):
    __tablename__ = "movies"
    movieId: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    genres: Mapped[str] = mapped_column(String)

class Link(Base):
    __tablename__ = "links"
    movieId: Mapped[int] = mapped_column(ForeignKey("movies.movieId"), primary_key=True)
    imdbId: Mapped[str] = mapped_column(String)
    tmdbId: Mapped[str] = mapped_column(String)

class Rating(Base):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    userId: Mapped[int]
    movieId: Mapped[int] = mapped_column(ForeignKey("movies.movieId"))
    rating: Mapped[float]
    timestamp: Mapped[int]

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    userId: Mapped[int]
    movieId: Mapped[int] = mapped_column(ForeignKey("movies.movieId"))
    tag: Mapped[str] = mapped_column(String)
    timestamp: Mapped[int]
