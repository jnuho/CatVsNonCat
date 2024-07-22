docker rmi jnuho/fe-nginx:latest

docker build -f ../dockerfiles/Dockerfile-nginx -t jnuho/fe-nginx:latest ..

sleep 2

docker image prune -f

