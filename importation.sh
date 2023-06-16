docker cp app/sae410.sql mysql:/database.sql

docker exec -it mysql bash -c "mysql -u user -p -e 'CREATE DATABASE IF NOT EXISTS SAE410;'"

docker exec -i mysql bash -c "mysql -u user -p SAE410 < /database.sql"

docker exec -it mysql mysql -u root -p SAE410 < /docker-entrypoint-initdb.d/schema.sql
