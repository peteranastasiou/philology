

if docker volume does not already exist:
   docker volume create neo4jdata


docker run -it --rm \
   --volume neo4jdata:/data \
   -p7474:7474 \
   -p7687:7687 \
   -d \
   -e NEO4J_AUTH=neo4j/secretgraph \
   neo4j:latest

