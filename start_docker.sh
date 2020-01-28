docker run --name websocket-games \
    --rm \
    -v $(pwd)/frontend/frontend/build:/usr/share/nginx/html:ro \
    -v $(pwd)/frontend/nginx.conf:/etc/nginx/nginx.conf:ro \
    -p 80:80 \
    -d nginx
