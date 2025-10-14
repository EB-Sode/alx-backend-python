#!/bin/bash

# kurbeScript.sh
# Script to start a local Kubernetes cluster using Minikube
# and verify that it's running.

set -e  # Exit on any error

echo "=== Starting Kubernetes cluster setup ==="

# 1. Check if minikube is installed
if ! command -v minikube &> /dev/null
then
    echo "Minikube not found. Installing Minikube..."
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
        sudo install minikube-linux-amd64 /usr/local/bin/minikube
        rm -f minikube-linux-amd64
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install minikube
    else
        echo "Unsupported OS. Please install Minikube manually."
        exit 1
    fi
else
    echo "Minikube is already installed ✅"
fi

# 2. Start Minikube cluster
echo "Starting Minikube cluster..."
minikube start

# 3. Verify the cluster is running
echo "Verifying cluster status..."
kubectl cluster-info

# 4. Retrieve available pods
echo "Retrieving pods in all namespaces..."
kubectl get pods --all-namespaces

echo "=== Kubernetes cluster setup complete! 🚀 ==="
