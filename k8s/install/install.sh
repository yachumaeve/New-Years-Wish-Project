#!/bin/bash
set -e # 遇到錯誤立即停止

# =======================================================
# 階段 1: 系統環境準備
# =======================================================
echo "--- 1. 禁用 Swap ---"
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

echo "--- 2. 配置核心網路模組 (重要！) ---"
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system

sudo apt install -y conntrack socat

# =======================================================
# 階段 2: 安裝 Containerd
# =======================================================
echo "--- 3. 安裝 Containerd ---"
sudo apt update
sudo apt install -y software-properties-common curl apt-transport-https ca-certificates gpg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y containerd.io

echo "--- 4. 配置 Containerd 使用 systemd Cgroup ---"
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd

# =======================================================
# 階段 3: 安裝 Kubeadm, Kubelet, Kubectl
# =======================================================
echo "--- 5. 安裝 K8s 工具 (v1.31) ---"
# 注意：這裡我將 v1.34 改為 v1.31，如果您堅持要最新版可以改回 v1.34
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

echo "--- K8s 基礎環境準備完成！ ---"