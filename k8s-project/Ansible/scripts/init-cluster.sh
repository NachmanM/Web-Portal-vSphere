#!/bin/bash

if [ ! -d "/k8s-project" ]; then
    git clone -c core.sshCommand="ssh -o StrictHostKeyChecking=no" git@github.com:NachmanM/k8s-project.git /k8s-project
else
    echo "Directory /k8s-project already exists. Skipping clone."
fi


kubectl create secret docker-registry regcred \
--docker-server=992382545251.dkr.ecr.us-east-1.amazonaws.com \
--docker-username=AWS \
--docker-password=$(aws ecr get-login-password --region us-east-1) \
--namespace=default \
--dry-run=client -o yaml | kubectl apply -f -


helm repo add aws-ebs-csi-driver https://kubernetes-sigs.github.io/aws-ebs-csi-driver
helm repo update

helm upgrade --install aws-ebs-csi-driver \
  aws-ebs-csi-driver \
  --repo https://kubernetes-sigs.github.io/aws-ebs-csi-driver \
  --namespace kube-system \
  --version 2.55.1


kubectl apply -f /k8s-project/k8s/ingress-nginx/NameSpace.yaml
# Wait until the namespace is actually ready
kubectl wait --for=condition=Active namespace/ingress-nginx --timeout=3s

kubectl apply -R -f /k8s-project/k8s/


helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install the stack (creates the namespace automatically)
helm install prom-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f /k8s-project/Monitor/grafana-values.yaml

kubectl apply -f /k8s-project/Monitor/k8s/