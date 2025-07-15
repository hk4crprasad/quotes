docker kill ai-quote-generator
docker rm ai-quote-generator
docker rmi ai-quote-generator
docker image prune -a -f
docker build -t ai-quote-generator .
docker run -d --name ai-quote-generator -p 8091:8091 ai-quote-generator