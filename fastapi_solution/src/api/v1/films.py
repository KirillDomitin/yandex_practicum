from http import HTTPStatus
from typing import Annotated, Literal
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Query

from models.film import Film, FilmShort
from services.film import FilmService, get_film_service


router = APIRouter()


ELASTICSEARCH_INDEX = 'movies'


@router.get('/{film_id:uuid}', response_model=Film)
async def get_film_by_id(request: Request,
                         film_id: UUID,
                         film_service: FilmService = Depends(get_film_service),) -> Film:
    request_url = f"{request.url.path}?{request.url.query}"
    elem = await film_service.get_by_id(request_url=request_url, _id=str(film_id), index=ELASTICSEARCH_INDEX, model=Film)
    if not elem:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')
    return elem


@router.get('/search', response_model=list[FilmShort])
async def search_films(request: Request,
                       query_string: Annotated[str, Query(max_length=256)],
                       page: Annotated[int, Query(ge=1, le=10)] = 1,
                       page_size: Annotated[int, Query(ge=5, le=20)] = 10,
                       film_service: FilmService = Depends(get_film_service)) -> list[FilmShort]:
    request_url = f"{request.url.path}?{request.url.query}"
    logging.info(f"request_url = {request_url}")
    elems = await film_service.search_films(request_url=request_url, model=FilmShort, index=ELASTICSEARCH_INDEX,
                                            query_string=query_string,
                                            page=page, page_size=page_size)
    if not elems:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')

    return elems


@router.get('/', response_model=list[FilmShort])
async def get_films_by_filter(request: Request,
                              page: Annotated[int, Query(ge=1, le=10)] = 1,
                              page_size: Annotated[int, Query(ge=5, le=20)] = 10,
                              sort_by: Literal['imdb_rating'] = 'imdb_rating',
                              sort_order: Literal['desc', 'asc'] = 'desc',
                              genre: UUID = None,
                              director: UUID = None,
                              writer: UUID = None,
                              actor: UUID = None,
                              film_service: FilmService = Depends(get_film_service)) -> list[FilmShort]:
    request_url = f"{request.url.path}?{request.url.query}"
    logging.info(f"request_url = {request_url}")
    elems = await film_service.get_films_by_filter(request_url=request_url, model=FilmShort, index=ELASTICSEARCH_INDEX,
                                                   genre=genre, director=director,
                                                   writer=writer, actor=actor,
                                                   page=page, page_size=page_size,
                                                   sort_by=sort_by, sort_order=sort_order)
    if not elems:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')

    return elems

