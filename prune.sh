docker stop $(docker ps -aq)

docker container prune

docker image prune -a

docker volume prune
