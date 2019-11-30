docker run --name websocket-games \
    --rm \
    -v $(pwd)/frontend/homepage/build:/usr/share/nginx/html:ro \
    -p 80:80 \
    -d nginx
