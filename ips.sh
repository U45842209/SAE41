#!/bin/bash

# Récupérer tous les ID et noms de conteneurs Docker en cours d'exécution
containers=$(docker ps --format "{{.ID}} {{.Names}}")

# Parcourir tous les conteneurs et afficher leurs adresses IP avec les noms
while read -r container_id container_name
do
    container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_id)
    echo "Conteneur $container_name : $container_ip"
done <<< "$containers"

