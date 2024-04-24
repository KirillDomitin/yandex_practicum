Как запускать:  
1. Заполнить example.env и переименовать в .env
2. Создать сеть:  
`docker network create --driver bridge main-network`
3. Развернуть контейнеры:  
`docker-compose up -d --build`  
или  
`docker-compose down -v 
&& docker-compose up -d --build`
4. Проверить, что всё работает:  
`http://localhost:80/api/openapi`
_____
`docker exec -it fastapi_solution bash`  
`while read -r line; do echo "$line"; done < "logs.log"`  
`docker-compose up -d --no-deps --build fastapi_solution`  