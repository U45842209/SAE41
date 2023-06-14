#!/bin/bash

# Récupérer tous les ID de conteneurs Docker en cours d'exécution
container_ids=$(docker ps -q)

# Parcourir tous les conteneurs et afficher leurs adresses IP
for container_id in $container_ids
do
    container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_id)
    echo "Conteneur $container_id : $container_ip"
done
