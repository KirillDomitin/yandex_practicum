from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


ELASTICSEARCH_INDEX = 'genres'


@router.get('/{genre_id:uuid}', response_model=Genre)
async def get_genre_by_id(request: Request,
                          genre_id: UUID,
                          genre_service: GenreService = Depends(get_genre_service),) -> Genre:
    request_url = f"{request.url.path}?{request.url.query}"
    elem = await genre_service.get_by_id(request_url=request_url, _id=str(genre_id), index=ELASTICSEARCH_INDEX, model=Genre)
    if not elem:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')
    return elem


@router.get('/', response_model=list[Genre])
async def get_genres(request: Request,
                     genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    request_url = f"{request.url.path}?{request.url.query}"
    elems = await genre_service.get_genres(request_url=request_url, model=Genre, index=ELASTICSEARCH_INDEX)
    if not elems:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')
    return elems
