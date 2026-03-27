# K8s CI/CD Demo (Final)

## Flow
GitHub → Jenkins → DockerHub → k3s → NodePort → nginx → Internet

## Replace:
DOCKERHUB_USERNAME in:
- Jenkinsfile
- k8s/deployment.yaml

## Namespace
kubectl create namespace demo

## nginx config
/etc/nginx/sites-available/k8s:

server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:30080;
    }
}

Enable:
ln -s /etc/nginx/sites-available/k8s /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

## Test
curl http://SERVER_IP

## Versioning

kubectl rollout history deployment/demo-nginx -n demo
kubectl rollout undo deployment/demo-nginx -n demo
kubectl rollout status deployment/demo-nginx -n demo