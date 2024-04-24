from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Query

from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter()


ELASTICSEARCH_INDEX = 'persons'


@router.get('/{person_id:uuid}', response_model=Person)
async def get_person_by_id(request: Request,
                           person_id: UUID,
                           person_service: PersonService = Depends(get_person_service), ) -> Person:
    request_url = f"{request.url.path}?{request.url.query}"
    elem = await person_service.get_by_id(request_url=request_url, _id=str(person_id),
                                          index=ELASTICSEARCH_INDEX, model=Person)
    if not elem:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')
    return elem


@router.get('/search', response_model=list[Person])
async def search_persons(request: Request,
                         query_string: str,
                         page: Annotated[int, Query(ge=1, le=10)],
                         page_size: int = 10,
                         person_service: PersonService = Depends(get_person_service), ) -> list[Person]:
    request_url = f"{request.url.path}?{request.url.query}"
    elems = await person_service.search_persons(request_url=request_url, model=Person, index=ELASTICSEARCH_INDEX,
                                                query_string=query_string,
                                                page=page, page_size=page_size)
    if not elems:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='not found')
    return elems
