docker build --no-cache -f Docker/dockerfile-IMS-Backend -t ja-ims-backend:latest .
docker tag ja-ims-backend:latest darliedcjw/ja-ims-backend:latest
docker push darliedcjw/ja-ims-backend:latest