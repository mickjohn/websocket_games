docker run --name websocket-games \
    --rm \
    -v $(pwd)/frontend_projects/homepage/build:/usr/share/nginx/html:ro \
    -p 80:80 \
    -d nginx
