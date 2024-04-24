from pydantic import BaseModel

from models.genre import Genre
from models.person import Person


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float
    description: str | None
    directors: list[Person] | None
    actors: list[Person] | None
    writers: list[Person] | None
    genres: list[Genre] | None
    directors_names: list[str] | None
    writers_names: list[str] | None
    actors_names: list[str] | None


class FilmShort(BaseModel):
    id: str
    title: str
    imdb_rating: float
