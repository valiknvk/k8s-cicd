# K8s CI/CD Demo (Final)
###
## Flow
GitHub → Jenkins → DockerHub → k3s → NodePort → nginx → Internet

## Namespace
kubectl create namespace demo

## Jenkins setup

sudo -u jenkins KUBECONFIG=/var/lib/jenkins/.kube/config kubectl get ns

If it fails, fix kubeconfig ownership/path first (k3s example):

sudo mkdir -p /var/lib/jenkins/.kube
sudo cp /etc/rancher/k3s/k3s.yaml /var/lib/jenkins/.kube/config
sudo chown -R jenkins:jenkins /var/lib/jenkins/.kube
sudo chmod 600 /var/lib/jenkins/.kube/config

Then verify permissions for your service account:

sudo -u jenkins KUBECONFIG=/var/lib/jenkins/.kube/config kubectl auth can-i create deployments -n demo
sudo -u jenkins KUBECONFIG=/var/lib/jenkins/.kube/config kubectl auth can-i create services -n demo

Optional Jenkinsfile hardening (to bypass OpenAPI validation call):

kubectl apply --validate=false -f k8s/service.yaml
kubectl apply --validate=false -f k8s/postgres.yaml
kubectl apply --validate=false -f k8s/redis.yaml
kubectl apply --validate=false -f k8s/backend.yaml

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

## Cluster setup via ansible

ansible-playbook -i inventory.ini ansible/fix-k8s-access-and-jenkins.yml -b \
    -e jenkinsfile_path=/path/to/Jenkinsfile
