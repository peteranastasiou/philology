
# Check if already running
docker ps | grep neo4j && echo -e "\nAlready Running\n" && exit 0

# Create the volume if it doesn't already exist
docker volume ls | grep neo4jdata || docker volume create neo4jdata

# Start the container
docker run -it --rm \
   --volume neo4jdata:/data \
   -p7474:7474 \
   -p7687:7687 \
   -d \
   -e NEO4J_AUTH=neo4j/secretgraph \
   neo4j:latest

