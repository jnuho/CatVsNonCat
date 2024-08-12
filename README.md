---
draft: false
date: 2024-08-01
categories:
  - Linux
authors:
  - junho
---

I configured a Kubernetes cluster with `kubeadm` using 3 Raspberry pis.

<img src="https://upload.wikimedia.org/wikipedia/commons/3/39/Kubernetes_logo_without_workmark.svg" alt="k8s" width="50">
<img src="https://kubernetes.io/images/kubeadm-stacked-color.png" alt="kubeadm" width="45">
<img src="https://raw.githubusercontent.com/cncf/artwork/master/projects/containerd/horizontal/color/containerd-horizontal-color.png" alt="containerd" width="100">
<img src="https://www.f5.com/content/dam/www/global-assets/partner-logos/ce-partner-logo/NGINX-Part-of-F5-horiz-black-type-525x208@2x.png" alt="nginx" width="110">
<img src="https://imagej.net/media/icons/pi.svg" alt="pi" width="30">
<img src="https://www.tigera.io/app/uploads/2020/03/Calico-logo.svg" alt="calico" width="110">      

<img src="https://i.imgur.com/Av7PzuR.jpg" alt="pi-cluster" width="500">

<!-- more -->

Kubernetes is a complex distributed system. By setting it up in home network, I explore inner workings of Kubernetes.

<br>

# Table of Contents

- [Raspberry Pi Setup](#raspberry-pi-setup)
    - [Enable the external PCI Express port](#enable-the-external-pci-express-port)
    - [Set NVMe early in the boot order](#set-nvme-early-in-the-boot-order)
    - [Network settings](#network-settings)
- [Kubernetes](#kubernetes)
    - [Prerequisite](#prerequisite)
    - [Container runtime](#container-runtime)
        - [CRI-O](#cri-o)
        - [containerd](#containerd)
    - [Installing kubeadm, kubelet and kubectl](#installing-kubeadm-kubelet-and-kubectl)
    - [Creating a cluster with kubeadm](#creating-a-cluster-with-kubeadm)
    - [Troubleshooting kubeadm](#troubleshooting-kubeadm)
    - [CNI: Calico](#cni-calico)
    - [Control your cluster from other machines](#controlling-your-cluster-from-other-machines)
- [Metrics server](#metrics-server)
- [Nginx Ingress Controller](#nginx-ingress-controller)
- [Metallb](#metallb)
- [Docker Registry](#docker-registry)
- [Argo CD](#argo-cd)
- [Reference](#reference)


## Raspberry Pi Setup <a class="headerlink" href="#raspberry-pi-setup" title="Permanent link"> ¶</a>


You need to have minimum 1 master node and 1 worker node. To make the cluster highly available, odd number of master node (1, 3, 5 ...) and more than 2 worker nodes are ideal. I chose SSD over microSD card which seemed to have poor performance and lack durability. Installing NVME SSD requires M.2 HAT+ and additional configuration in Linux.

- Hardware
    - 3 x Raspberry pi 5 (1 master, 2 workers)
        - 8GB Memory, 4-core CPU
    - 3 x Raspberry Pi M.2 HAT+  (1 master, 2 workers)
    - 3 x Raspberry Pi Active Cooler
    - 3 x SSD: SK Hynix BC901 256GB
    - 3 x Ethernet cable
    - 3 x Usb-C cable (power adapter ideally >= 25W = 5A x 5V)
    - 1 x TP LINK Switch Hub TL-SG105

Now, configure NVMD SSD Boot! [LINK](https://www.jeffgeerling.com/blog/2023/nvme-ssd-boot-raspberry-pi-5).

### Enable the external PCI Express port


```sh
sudo vim /boot/firmware/config.txt

# Add to bottom of /boot/firmware/config.txt
dtparam=pciex1

# Note: You could also just add the following (it is an alias to the above line)
# dtparam=nvme

# Optionally, you can control the PCIe lane speed using this parameter
# dtparam=pciex1_gen=3
```

### Set NVMe early in the boot order

```sh
# Edit the EEPROM on the Raspberry Pi 5.
sudo EDITOR=vim rpi-eeprom-config --edit

# Change the BOOT_ORDER line to the following:
BOOT_ORDER=0xf416

# Add the following line if using a non-HAT+ adapter:
PCIE_PROBE=1

# Press Ctrl-O, then enter, to write the change to the file.
# Press Ctrl-X to exit nano (the editor).
```

### Network settings

Check [linux set-up](https://blogd.org/blog/2024/07/01/linux/#time-sync)

- Time sync
- Change Hostname
- SSH access


[↑ Back to top](#)
<br><br>


## Kubernetes <a class="headerlink" href="#kubernetes" title="Permanent link"> ¶</a>

We will configure Kubernetes v1.30.3.

- [Prerequisite](#prerequisite)
- [Container runtime](#container-runtime)
- [Installing kubeadm, kubelet and kubectl](#installing-kubeadm-kubelet-and-kubectl)
- [Creating a cluster with kubeadm](#creating-a-cluster-with-kubeadm)

### Prerequisite

- Swap memory off
  - The default behavior of a kubelet was to fail to start if swap memory was detected on a node. 
  - You MUST disable swap if the kubelet is not properly configured to use swap.

```sh
# disable swapping temporarily.
sudo swapoff -a
# To make this change persistent across reboots, make sure swap is disabled in config files. Comment out swap

# Disable swap permanently
# vim /etc/fstab
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# check Swap is disabled
free -h
                   total        used        free      shared  buff/cache   available
    Mem:           7.8Gi       900Mi       2.1Gi       5.2Mi       5.0Gi       6.9Gi
->  Swap:             0B          0B          0B
```

- Required ports
  - Check required ports for both control plane and worker nodes
  - https://kubernetes.io/docs/reference/networking/ports-and-protocols/

```sh
nc 127.0.0.1 6443 -v
```

- Configuring a cgroup driver
  - https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/configure-cgroup-driver/

```sh
#   On Linux, control groups are used to constrain resources that are allocated to processes.
#   Both the `KUBELET` and the underlying `CONTAINER RUNTIME` need to interface with control groups
#   to enforce resource management for pods and containers and set resources such as cpu/memory requests and limits.
#   There are two cgroup drivers available: cgroupfs-default cgroup driver in the kubelet, systemd.
#   The Container runtimes page explains that the systemd driver is recommended for kubeadm based setups
#   instead of the kubelet's default cgroupfs driver, because kubeadm manages the kubelet as a systemd service.

cat << EOF > kubeadm-config.yaml
kind: ClusterConfiguration
apiVersion: kubeadm.k8s.io/v1beta3
kubernetesVersion: v1.30.3
---
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
cgroupDriver: systemd
EOF
```

[↑ Back to top](#)
<br><br>


### Container runtime

Kubernetes 1.30 requires that you use a runtime that conforms with the Container Runtime Interface (CRI); containerd, CRI-O, Docker Engine. You need to install a container runtime into each node in the cluster so that Pods can run there. (kubelet deprecated Docker support since Kubernetes>=1.24)

#### CRI-O

- [instruction](https://github.com/cri-o/packaging/blob/main/README.md#usage)

```sh
```


[↑ Back to top](#)
<br><br>


#### containerd

- Getting started with [containerd](https://github.com/containerd/containerd/blob/main/docs/getting-started.md)

- Install and configure prerequisites
  - 1. Enable IPv4 packet forwarding
  - 2. cgroup drivers: systemd
  - 3. container runtime - containerd


```sh
# 1. Enable IPv4 packet forwarding
#   By default, the Linux kernel does not allow IPv4 packets to be routed between interfaces.
#   sysctl params required by setup, params persist across reboots
cat << EOF | sudo tee /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

# Verify that net.ipv4.ip_forward is set to 1 with:
sysctl net.ipv4.ip_forward

# 2. cgroup drivers
#   On Linux, control groups are used to constrain resources that are allocated to processes.

# 3. container runtime - containerd
# https://github.com/containerd/containerd/blob/main/docs/getting-started.md
# Step 3-1: Installing containerd
wget https://github.com/containerd/containerd/releases/download/v1.7.20/containerd-1.7.20-linux-arm64.tar.gz
sudo tar Cxzvf /usr/local containerd-1.7.20-linux-arm64.tar.gz

# If you intend to start containerd via systemd, you should also download
#   the containerd.service unit file into /usr/local/lib/systemd/system/containerd.service
sudo mkdir -p /usr/local/lib/systemd/system/
sudo wget -O /usr/local/lib/systemd/system/containerd.service https://raw.githubusercontent.com/containerd/containerd/main/containerd.service

sudo systemctl daemon-reload
sudo systemctl enable --now containerd
sudo systemctl status containerd

# Step 3-2: Installing runc
wget https://github.com/opencontainers/runc/releases/download/v1.1.13/runc.arm64
sudo install -m 755 runc.arm64 /usr/local/sbin/runc

# Step 3-3: Installing CNI plugins
wget https://github.com/containernetworking/plugins/releases/download/v1.5.1/cni-plugins-linux-arm64-v1.5.1.tgz
sudo mkdir -p /opt/cni/bin
sudo tar Cxzvf /opt/cni/bin cni-plugins-linux-arm64-v1.5.1.tgz

# 4. You can find this file under the path /etc/containerd/config.toml.
# generate default config
sudo mkdir -p /etc/containerd
sudo su -
sudo containerd config default > /etc/containerd/config.toml
sudo cat /etc/containerd/config.toml

# 5. Configuring the systemd cgroup driver
#   To use the systemd cgroup driver in /etc/containerd/config.toml with runc, set
sudo sed -i 's/SystemdCgroup \= false/SystemdCgroup = true/g' /etc/containerd/config.toml

cat /etc/containerd/config.toml
[plugins]
  # ...
  [plugins."io.containerd.grpc.v1.cri"]
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            SystemdCgroup = true

sudo systemctl restart containerd
sudo systemctl status containerd
```

### nerdctl

"`nerdctl` is a Docker-compatible CLI for `containerd`"

[Why nerdctl?](https://blog.devgenius.io/k8s-why-use-nerdctl-for-containerd-f4ea49bcf900)

- Pre-requisite
  - containerd is installed, enabled, and running
  - cni plugins is installed (previously `cni-plugins-linux-arm64-v1.5.1.tgz`)
  - Configure [rootlesskit](https://rootlesscontaine.rs/getting-started/containerd/)
  - [Install Guide](https://www.techrepublic.com/article/deploy-container-nerdctl/)

```sh
# uidmap
sudo apt-get install uidmap -y

# RootlessKit
sudo apt-get install rootlesskit -y

wget https://github.com/containerd/nerdctl/releases/download/v2.0.0-rc.0/nerdctl-2.0.0-rc.0-linux-arm64.tar.gz
sudo tar Cxzvvf /usr/local/bin nerdctl-2.0.0-rc.0-linux-arm64.tar.gz

which nerdctl
  /usr/local/bin/nerdctl

#sudo sh -c "echo 1 > /proc/sys/kernel/unprivileged_userns_clone"
sudo vim /etc/sysctl.d/99-rootless.conf
kernel.unprivileged_userns_clone=1

# apply in 99-rootless.conf to system
sudo sysctl --system
# check if it is applied to system
sudo sysctl kernel.unprivileged_userns_clone

# DO NOT RUN AS `root` !!!
containerd-rootless-setuptool.sh install

# Now, you can run without root privilege!
nerdctl version
nerdctl
```


[↑ Back to top](#)
<br><br>


### Installing kubeadm, kubelet and kubectl

- For Kubernetes v1.30, you will install these packages on <b>ALL OF YOUR MACHINES</b>:
  - `kubeadm`: the command to bootstrap the cluster.
  - `kubelet`: the component that runs on all of the machines in your cluster and does things like starting pods and containers.
  - [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
  <!-- - [`helm`](https://helm.sh/docs/intro/install/) -->

```sh
# 1. Update the apt package index and install packages needed to use the Kubernetes apt repository:
sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl gpg

# 2. Download the public signing key for the Kubernetes package repositories. The same signing key is used for all repositories so you can disregard the version in the URL:
# If the directory `/etc/apt/keyrings` does not exist, it should be created before the curl command, read the note below.
# sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# 3. Add the appropriate Kubernetes apt repository. 
# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# 4. Update the apt package index, install kubelet, kubeadm and kubectl, and pin their version:
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# kublet : set node ip
sudo su -
local_ip="$(ip --json addr show eth0 | jq -r '.[0].addr_info[] | select(.family == "inet") | .local')"
echo $local_ip
cat > /etc/default/kubelet << EOF
KUBELET_EXTRA_ARGS=--node-ip=$local_ip
EOF
cat /etc/default/kubelet
exit

# 5. (Optional) Enable the kubelet service before running kubeadm:
sudo systemctl enable --now kubelet
```

[↑ Back to top](#)
<br><br>


### Creating a cluster with kubeadm

- Initializing your `control-plane node` (master node)

```sh
# --pod-network-cidr
# your Pod network must not overlap with any of the host networks (192.168.0.0/24)

# on master node:

POD_CIDR="10.100.0.0/16"
NODENAME=$(hostname -s)
MASTER_PRIVATE_IP=$(ip addr show eth0 | awk '/inet / {print $2}' | cut -d/ -f1)

sudo kubeadm init \
    --apiserver-advertise-address="$MASTER_PRIVATE_IP" \
    --apiserver-cert-extra-sans="$MASTER_PRIVATE_IP" \
    --pod-network-cidr="$POD_CIDR" \
    --controller-manager-extra-args "allocate-node-cidrs=false" \
    --node-name "$NODENAME" \
    -v=5

# NOTE: --controller-manager-extra-args "allocate-node-cidrs=false"
# prevent `kube-controller-manager-master` from trying to allocate podCidr.
# Calico will do it instead :)

# [addons] Applied essential addon: CoreDNS
# [addons] Applied essential addon: kube-proxy
# Your Kubernetes control-plane has initialized successfully!
# To start using your cluster, you need to run the following as a regular user:

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Alternatively, if you are the root user, you can run:
#   export KUBECONFIG=/etc/kubernetes/admin.conf
# You should now deploy a pod network to the cluster.
# Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
#   https://kubernetes.io/docs/concepts/cluster-administration/addons/
# Then you can join any number of worker nodes by running the following on each as root:

sudo kubeadm join 192.168.0.10:6443 --token mjgw9s.d29kh7dtjqig5owf \
        --discovery-token-ca-cert-hash sha256:f3516dba4e89b3530a044ed531ab07ed00fea6a44104aae1d0ec1ab87357e14a
```

- Worker nodes

```sh
# set `node-role`
kubectl label node worker1 node-role.kubernetes.io/worker=worker
kubectl label node worker2 node-role.kubernetes.io/worker=worker


kubectl get no -o wide
NAME      STATUS     ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE           KERNEL-VERSION     CONTAINER-RUNTIME
master    NotReady   control-plane   58s   v1.30.3   192.168.0.10   <none>        Ubuntu 24.04 LTS   6.8.0-1008-raspi   containerd://1.7.20
worker1   NotReady   worker          19s   v1.30.3   192.168.0.11   <none>        Ubuntu 24.04 LTS   6.8.0-1008-raspi   containerd://1.7.20
worker2   NotReady   worker          25s   v1.30.3   192.168.0.12   <none>        Ubuntu 24.04 LTS   6.8.0-1008-raspi   containerd://1.7.20
```


### Troubleshooting kubeadm

- `coredns` is stuck in the Pending state. This is expected and part of the design. 
    - [troubleshooting-kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/troubleshooting-kubeadm/)

```sh
k get pod -n kube-system
  NAME                             READY   STATUS    RESTARTS        AGE
  coredns-7db6d8ff4d-sv6bv         0/1     Pending   0               4h54m
  coredns-7db6d8ff4d-vtc4p         0/1     Pending   0               4h54m

k describe pod coredns-7db6d8ff4d-sv6bv -n kube-system
    # Warning  FailedScheduling  7m50s (x6 over 4h45m)  default-scheduler  0/3 nodes are available: 3 node(s) had untolerated taint {node.kubernetes.io/not-ready: }. preemption: 0/3 nodes are available: 3 Preemption is not helpful for scheduling.

```

- CIDR allocation failed

```sh
k logs kube-controller-manager-master -nkube-system
    E0807 07:33:10.824783       1 controller_utils.go:262]
    Error while processing Node Add/Delete: failed to allocate cidr from cluster cidr at idx:0:
    CIDR allocation failed; there are no remaining CIDRs left to allocate in the accepted range

kubectl describe pod kube-controller-manager-master -n kube-system | grep cluster-cidr
kubectl describe pod kube-controller-manager-master -n kube-system | grep allocate-node-cidrs

# The --cluster-cidr=10.100.0.0/16 should match the pod network CIDR
# and is used by the controller manager to allocate pod CIDRs to nodes.
# So this seems to be a correct set-up of cidr
sudo cat /etc/kubernetes/manifests/kube-controller-manager.yaml | grep cidr
    - --allocate-node-cidrs=true
    - --cluster-cidr=10.100.0.0/16
sudo vim /etc/kubernetes/manifests/kube-controller-manager.yaml
    - --allocate-node-cidrs=false

# Error message is resolved!
kubectl describe nodes
    Events:
      Type    Reason            Age                   From             Message
      ----    ------            ----                  ----             -------
      Normal  CIDRNotAvailable  7m53s (x17 over 14h)  cidrAllocator    Node worker1 status is now: CIDRNotAvailable
 ->   Normal  RegisteredNode    4m1s                  node-controller  Node worker1 event: Registered Node worker1 in Controller


# https://devops.stackexchange.com/questions/17032/what-is-the-meaning-of-the-podcidr-field-in-the-node-spec-in-kubenretes
# https://github.com/kubernetes/kubernetes/issues/76761
# When using Calico, the podCIDR field on the node objects is not used or required.
# Calico handles IP allocation without needing this field to be set.
kubectl get nodes -o custom-columns=NAME:.metadata.name,CIDR:.spec.podCIDR
    NAME      CIDR
    master    <none>
    worker1   <none>
    worker2   <none>
# Instead of using podCIDR, Calico uses its own IPPool resource to manage the available IP ranges. You can view this with:
kubectl get ippool -o yaml

kubectl get blockaffinities -A
    NAME                        AGE
    master-10-100-219-64-26     20h
    worker1-10-100-235-128-26   20h
    worker2-10-100-189-64-26    20h
kubectl get ipamblocks -A
    NAME                AGE
    10-100-189-64-26    20h
    10-100-219-64-26    20h
    10-100-235-128-26   20h
k get pod -A -o wide | grep -v 192.168. | grep -v Completed | grep worker2
        10.100.189.xx
k get pod -A -o wide | grep -v 192.168. | grep -v Completed | grep master
        10.100.219.xx
k get pod -A -o wide | grep -v 192.168. | grep -v Completed | grep worker1
        10.100.235.xx

kubectl get ippool default-ipv4-ippool -o yaml
    apiVersion: crd.projectcalico.org/v1
    kind: IPPool
    metadata:
      annotations:
        projectcalico.org/metadata: '{"creationTimestamp":"2024-08-07T03:17:23Z"}'
      creationTimestamp: "2024-08-07T03:17:23Z"
      generation: 1
      name: default-ipv4-ippool
      resourceVersion: "935"
      uid: 04c9c442-e0a4-4a42-b481-2609ccde7bda
    spec:
      allowedUses:
      - Workload
      - Tunnel
      blockSize: 26
      cidr: 10.100.0.0/16
      ipipMode: Always

➜  ~ k get pod -A -o wide
NAMESPACE        NAME                                       READY   STATUS      RESTARTS   AGE   IP               NODE      NOMINATED NODE   READINESS GATES
default          be-go-6b6f5fc88d-mxxbg                     1/1     Running     0          13m   10.100.235.131   worker1   <none>           <none>
default          be-py-6bc85fcb56-cn8cc                     1/1     Running     0          13m   10.100.235.132   worker1   <none>           <none>
default          be-py-6bc85fcb56-lb4rk                     1/1     Running     0          13m   10.100.189.68    worker2   <none>           <none>
default          fe-nginx-d7f6d6449-rzmll                   1/1     Running     0          13m   10.100.189.67    worker2   <none>           <none>
ingress-nginx    ingress-nginx-admission-create-g4qqd       0/1     Completed   0          14m   10.100.235.129   worker1   <none>           <none>
ingress-nginx    ingress-nginx-admission-patch-znfw5        0/1     Completed   0          14m   10.100.189.66    worker2   <none>           <none>
ingress-nginx    ingress-nginx-controller-666487-z5td9      1/1     Running     0          14m   10.100.235.130   worker1   <none>           <none>
kube-system      calico-kube-controllers-77d59654f4-ctfst   1/1     Running     0          17m   10.100.219.66    master    <none>           <none>
kube-system      calico-node-d9nj8                          1/1     Running     0          17m   192.168.0.10     master    <none>           <none>
kube-system      calico-node-mslzt                          1/1     Running     0          17m   192.168.0.12     worker2   <none>           <none>
kube-system      calico-node-vzlk5                          1/1     Running     0          17m   192.168.0.11     worker1   <none>           <none>
kube-system      coredns-7db6d8ff4d-pm4v9                   1/1     Running     0          19m   10.100.219.65    master    <none>           <none>
kube-system      coredns-7db6d8ff4d-zz9h5                   1/1     Running     0          19m   10.100.219.67    master    <none>           <none>
kube-system      etcd-master                                1/1     Running     0          19m   192.168.0.10     master    <none>           <none>
kube-system      kube-apiserver-master                      1/1     Running     0          19m   192.168.0.10     master    <none>           <none>
kube-system      kube-controller-manager-master             1/1     Running     0          19m   192.168.0.10     master    <none>           <none>
kube-system      kube-proxy-6rlhv                           1/1     Running     0          19m   192.168.0.12     worker2   <none>           <none>
kube-system      kube-proxy-6zrf8                           1/1     Running     0          19m   192.168.0.10     master    <none>           <none>
kube-system      kube-proxy-mz96w                           1/1     Running     0          19m   192.168.0.11     worker1   <none>           <none>
kube-system      kube-scheduler-master                      1/1     Running     0          19m   192.168.0.10     master    <none>           <none>
kube-system      metrics-server-5df54c66b8-pzj84            1/1     Running     0          15m   10.100.189.65    worker2   <none>           <none>
metallb-system   controller-6dd967fdc7-2c8fg                1/1     Running     0          11m   10.100.189.69    worker2   <none>           <none>
metallb-system   speaker-4bm8l                              1/1     Running     0          11m   192.168.0.10     master    <none>           <none>
metallb-system   speaker-9kmcf                              1/1     Running     0          11m   192.168.0.12     worker2   <none>           <none>
metallb-system   speaker-qnw8v                              1/1     Running     0          11m   192.168.0.11     worker1   <none>           <none>

ps aux | grep cluster-cidr
    --cluster-cidr=10.100.0.0/16

helm install --dry-run cat-release ./cat-chart -f ./cat-chart/values.pi.yaml
# change CIDR blocks 
```


- [Force delete](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)

```sh
k delete --grace-period=0 --force -nkube-system pod/coredns-7db6d8ff4d-5dv6d
```


### CNI: Calico

Install Calico CNI (Container Network Interface) plugin to enable Pod networking!

You must deploy a `Container Network Interface` (CNI) based Pod network add-on such as `Calico`, `flannel`, `weavenet` so that your Pods can communicate with each other. Cluster DNS (CoreDNS) will not start up before a network is installed. Without CNI, the coredns pods are `pending` and `podSubnet` is not specified in the cluster configuration.


- 1-1. Install with manifest

```sh
# Check Pod Subnet is missing
kubectl get configmap -n kube-system kubeadm-config -o yaml
    ...
    networking:
      dnsDomain: cluster.local
      #podSubnet: 10.100.0.0/16
      serviceSubnet: 10.96.0.0/12
    scheduler: {}
    ...
```

```sh
curl -O https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/calico.yaml
vim calico.yaml
# Match POD_CIDR and CALICO_IPV4POOL_CIDR

kind: DaemonSet
apiVersion: apps/v1
metadata:
  name: calico-node
  namespace: kube-system
  labels:
    k8s-app: calico-node
spec:
  template:
    spec:
      containers:
        - name: calico-node
          env:
            # The default IPv4 pool to create on startup if none exists. Pod IPs will be
            # chosen from this range. Changing this value after installation will have
            # no effect. This should fall within `--cluster-cidr`.
            - name: CALICO_IPV4POOL_CIDR
              value: "10.100.0.0/16"
---

kubectl apply -f calico.yaml

# Verify Calico installation in your cluster.
kubectl get pods -nkube-system

    NAME                                       READY   STATUS     RESTARTS   AGE
    calico-kube-controllers-77d59654f4-59qlx   1/1     Running    0          21s
    calico-node-mn2kl                          1/1     Running   0          21s
    calico-node-sndg4                          1/1     Running   0          21s
    calico-node-wmwpm                          1/1     Running   0          21s
```


- 1-2. Install with Calico Operator - tigera-operator

```sh
# Install the operator on your cluster.
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/tigera-operator.yaml

```

- `custom-resources.yaml`

```yaml
# This section includes base Calico installation configuration.
# For more information, see: https://docs.tigera.io/calico/latest/reference/installation/api#operator.tigera.io/v1.Installation
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  # Configures Calico networking.
  calicoNetwork:
    ipPools:
    - name: default-ipv4-ippool
      blockSize: 26
      cidr: 10.100.0.0/16
      encapsulation: VXLANCrossSubnet
      natOutgoing: Enabled
      nodeSelector: all()

---

# This section configures the Calico API server.
# For more information, see: https://docs.tigera.io/calico/latest/reference/installation/api#operator.tigera.io/v1.APIServer
apiVersion: operator.tigera.io/v1
kind: APIServer
metadata:
  name: default
spec: {}
```

- Custom Resource

```sh
curl https://raw.githubusercontent.com/projectcalico/calico/v3.28.1/manifests/custom-resources.yaml -O
kubectl create -f custom-resources.yaml

# Verify Calico installation in your cluster.
watch kubectl get pods -n calico-system

NAME                                       READY   STATUS    RESTARTS   AGE
calico-kube-controllers-5857c9dccf-f6bh2   1/1     Running   0          6m43s
calico-node-l65nq                          1/1     Running   0          6m43s
calico-node-wtftp                          1/1     Running   0          6m43s
calico-node-xj2kn                          1/1     Running   0          6m43s
calico-typha-68cbb57dc7-752ch              1/1     Running   0          6m43s
calico-typha-68cbb57dc7-b49rn              1/1     Running   0          6m40s
csi-node-driver-5pt8r                      2/2     Running   0          6m43s
csi-node-driver-gqps8                      2/2     Running   0          6m43s
csi-node-driver-lkthq                      2/2     Running   0          6m43s
```

- To determine the pod network CIDR, you can inspect the configuration of the CNI plugin installed in your cluster.
- Here’s how you can check for some common CNI plugins:

```sh
# 1. `calico` CNI plugin
kubectl get ippools.crd.projectcalico.org -o yaml

    apiVersion: v1
    items:
    - apiVersion: crd.projectcalico.org/v1
      kind: IPPool
      spec:
        blockSize: 26
        cidr: 10.100.0.0/16
```

[↑ Back to top](#)
<br><br>


### Control your cluster from other machines

```sh
scp root@<control-plane-host>:/etc/kubernetes/admin.conf .
scp mobb@192.168.0.10:/home/mobb/.kube/config .

# `cluster` `context` `user` -> add this to existing `~/.kube/config`
# change names to 'pi' which can be identified by you...
kubectl --kubeconfig ./config get nodes
  clusters:
  - cluster: ...
  contexts:
  - context: ...
  users:
  - name: ...

kubectl config get-contexts
kubectl config use-context pi


kubectl get no
    NAME      STATUS   ROLES           AGE   VERSION
    master    Ready    control-plane   36m   v1.30.3
    worker1   Ready    worker          33m   v1.30.3
    worker2   Ready    worker          33m   v1.30.3

kubectl top no
    NAME      CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
    master    137m         3%     846Mi           10%
    worker1   56m          1%     528Mi           6%
    worker2   68m          1%     501Mi           6%

kubectl top pod -nkube-system
    NAME                                       CPU(cores)   MEMORY(bytes)
    calico-kube-controllers-77d59654f4-59qlx   2m           12Mi
    calico-node-mn2kl                          25m          117Mi
    calico-node-sndg4                          27m          117Mi
    calico-node-wmwpm                          24m          117Mi
    coredns-7db6d8ff4d-kvzq2                   2m           13Mi
    coredns-7db6d8ff4d-mqmj9                   2m           13Mi
    etcd-master                                20m          44Mi
    kube-apiserver-master                      48m          261Mi
    kube-controller-manager-master             12m          56Mi
    kube-proxy-7st54                           1m           13Mi
    kube-proxy-gcb6c                           1m           12Mi
    kube-proxy-wt555                           1m           13Mi
    kube-scheduler-master                      3m           18Mi
    metrics-server-5df54c66b8-zhr7h            4m           18Mi
```


[↑ Back to top](#)
<br><br>


## Metrics server <a class="headerlink" href="#metrics-server" title="Permanent link"> ¶</a>

```sh
curl -L https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml -o metrics-server.yaml

vim metrics-server.yaml
      - args:
        - --kubelet-insecure-tls=true

kubectl apply -f metrics-server.yaml 

k get pod -nkube-system

    NAME                                       READY   STATUS    RESTARTS   AGE
    ...
    metrics-server-5df54c66b8-zhr7h            1/1     Running   0          35s
```


[↑ Back to top](#)
<br><br>

## Nginx Ingress Controller <a class="headerlink" href="#nginx-ingress-controller" title="Permanent link"> ¶</a>

- Method 1. Install with yaml manifest

```sh
curl -L https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.1/deploy/static/provider/cloud/deploy.yaml -o ingress-nginx.yaml

kubectl apply -f ingress-nginx.yaml
```



- Method 2. Install `helm`

```sh
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

- Install `Nginx Ingress Controller`
    - [quick start](https://kubernetes.github.io/ingress-nginx/deploy/#quick-start)
    - [Guide](#https://medium.com/@tonylixu/devops-in-k8s-nginx-ingress-controller-0a09f48458e2)


```sh
helm upgrade --install ingress-nginx ingress-nginx \
    --repo https://kubernetes.github.io/ingress-nginx \
    --namespace ingress-nginx --create-namespace

kubectl get pods -ningress-nginx

kubectl get svc -ningress-nginx
    NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
    ingress-nginx-controller             LoadBalancer   10.102.120.211   <pending>     80:31362/TCP,443:32684/TCP   52s
    ingress-nginx-controller-admission   ClusterIP      10.99.130.218    <none>        443/TCP                      52s
```


## Metallb <a class="headerlink" href="#metallb" title="Permanent link"> ¶</a>

<img src="https://kubernetes.github.io/ingress-nginx/images/baremetal/baremetal_overview.jpg" alt="A pure software solution: MetalLB" width="400">

- [A pure software solution for Nginx ingress controller: MetalLB](https://kubernetes.github.io/ingress-nginx/deploy/baremetal/)
- [installation](https://metallb.universe.tf/installation/)

- Preparation
    - If you’re using kube-proxy in IPVS mode, since Kubernetes v1.14.2 you have to enable strict ARP mode.

```sh
# kubectl edit configmap -n kube-system kube-proxy
# OR
# see what changes would be made, returns nonzero returncode if different
kubectl get configmap kube-proxy -n kube-system -o yaml | \
    sed -e "s/strictARP: false/strictARP: true/" | \
    kubectl diff -f - -n kube-system

# actually apply the changes, returns nonzero returncode on errors only
kubectl get configmap kube-proxy -n kube-system -o yaml | \
    sed -e "s/strictARP: false/strictARP: true/" | \
    kubectl apply -f - -n kube-system
```

- Installation by manifest

```sh
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.8/config/manifests/metallb-native.yaml

kubectl get pod -nmetallb-system
    NAME                          READY   STATUS    RESTARTS   AGE
    controller-6dd967fdc7-xwmnn   1/1     Running   0          40s
    speaker-876fv                 1/1     Running   0          40s
    speaker-s6xzp                 1/1     Running   0          40s
    speaker-wwtrm                 1/1     Running   0          40s

```


- Configuration
    - https://metallb.universe.tf/configuration/

```sh
k get no

NAME      STATUS   ROLES           AGE   VERSION
master    Ready    control-plane   41m   v1.30.3
worker1   Ready    worker          38m   v1.30.3
worker2   Ready    worker          38m   v1.30.3

k get svc -ningress-nginx
    NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
    ingress-nginx-controller             LoadBalancer   10.102.120.211   <pending>     80:31362/TCP,443:32684/TCP   26m
    ingress-nginx-controller-admission   ClusterIP      10.99.130.218    <none>        443/TCP                      26m

k get ingress
    NAME               CLASS   HOSTS       ADDRESS   PORTS   AGE
    fe-nginx-ingress   nginx   localhost             80      81m


# NOTE: Setting no IPAddressPool selector in an L2Advertisement instance is interpreted
#       as that instance being associated to all the IPAddressPools available.

# DO NOT OVERLAP with POD_CIDR (10.100.0.0/16), and NODE_IPs (192.168.0.10 ~ 12) (master and worker nodes)

cat << EOF > metallb.yaml
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.0.201-192.168.0.220
  autoAssign: true
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - first-pool
EOF

kubectl apply -f metallb.yaml

kubectl get svc -ningress-nginx
    NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP     PORT(S)                      AGE
    ingress-nginx-controller             LoadBalancer   10.102.120.211   192.168.0.201   80:31362/TCP,443:32684/TCP   164m
    ingress-nginx-controller-admission   ClusterIP      10.99.130.218    <none>          443/TCP                      164m

```

- Edit Windows hosts File
    - C:\Windows\System32\drivers\etc\hosts

```
192.168.0.201 catornot.com

curl -D- http://192.168.0.201 -H 'Host: catornot.com'
```

## Application

```sh
helm install ...


kubectl get pod -o wide
    NAME                       READY   STATUS    RESTARTS   AGE   IP               NODE      NOMINATED NODE   READINESS GATES
    be-go-6b6f5fc88d-mxxbg     1/1     Running   0          10m   10.100.235.131   worker1   <none>           <none>
    be-py-6bc85fcb56-cn8cc     1/1     Running   0          10m   10.100.235.132   worker1   <none>           <none>
    be-py-6bc85fcb56-lb4rk     1/1     Running   0          10m   10.100.189.68    worker2   <none>           <none>
    fe-nginx-d7f6d6449-rzmll   1/1     Running   0          10m   10.100.189.67    worker2   <none>           <none>
```

## Docker Registry <a class="headerlink" href="#docker-registry" title="Permanent link"> ¶</a>

### Local Registry

Set up local docker registry that Kubernetes Pods will pull images from. I used `worker1` node to set up a temporary docker registry. I will set-up another raspberry-pi machine in the future.

- Self-signed Certificate

```sh
mkdir -p certs
# Generate SSL Certificates:
openssl req -newkey rsa:4096 -nodes -sha256 -x509 \
  -keyout certs/domain.key \
  -days 365 \
  -out certs/domain.crt \
  -subj "/CN=192.168.0.11"


# Run the Registry Container with HTTPS:
docker run -d -p 5000:5000 \
  --restart=always \
  --name registry \
  -v $(pwd)/certs:/certs \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:5000 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  registry:2

# Distribute the CA Certificate:
sudo mkdir -p /etc/docker/certs.d/192.168.0.11:5000
sudo cp certs/domain.crt /etc/docker/certs.d/192.168.0.11:5000/ca.crt

docker tag your-image 192.168.0.11:5000/your-image
docker push 192.168.0.11:5000/your-image
```

- Configure Containerd to Use the Secure Registry

```
# Edit the containerd Configuration:
sudo vim /etc/containerd/config.toml

[plugins."io.containerd.grpc.v1.cri".registry]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors."192.168.0.10:5000"]
      endpoint = ["https://192.168.0.10:5000"]
  [plugins."io.containerd.grpc.v1.cri".registry.configs]
    [plugins."io.containerd.grpc.v1.cri".registry.configs."192.168.0.10:5000".tls]
      ca_file = "/etc/docker/certs.d/192.168.0.10:5000/ca.crt"

sudo systemctl restart containerd
```

[↑ Back to top](#)
<br><br>

### Dockerhub

- Authenticate to dockerhub to increase image pull rate limit.
- [increase-rate-limits](https://www.docker.com/increase-rate-limits/)

```sh
sudo vim /etc/containerd/config.toml
      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."registry-1.docker.io".auth]
          username = "jnuho"
          password = "******"

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."registry-1.docker.io"]
          endpoint = ["https://registry-1.docker.io"]

sudo systemctl restart containerd
```

[↑ Back to top](#)
<br><br>

## Argo CD <a class="headerlink" href="#argo-cd" title="Permanent link"> ¶</a>

"Argo CD is implemented as a Kubernetes controller which continuously monitors running applications and compares the current, live state against the desired target state (as specified in the Git repo)"


### Install Argo CD

```sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```


### Argo CD CLI

```sh
cat << EOF > install-argocd-cli.sh
VERSION=$(curl -L -s https://raw.githubusercontent.com/argoproj/argo-cd/stable/VERSION)
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/download/v$VERSION/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
EOF

chmod +x install-argocd-cli.sh
./install-argocd-cli.sh

# NOTE: INITIAL PASSWORD!
argocd admin initial-password -n argocd

argocd account update-password --server "https://localhost:8080"
```


### Configure TLS

This default installation will have a self-signed certificate and cannot be accessed without a bit of extra work. Do one of:

```sh
# default self-signed certificate
kubectl get secret argocd-secret -nargocd -o yaml

    apiVersion: v1
    data:
      admin.password: PASSWORD_HERE
      admin.passwordMtime: PASSWORD_HERE
      server.secretkey: SECRETKEY_HERE
      tls.crt: CERT_HERE
      tls.key: KEY_HERE
    kind: Secret
    metadata:
      name: argocd-secret
      namespace: argocd
    type: Opaque
```

#### Create self-signed TLS certificate

-  I referred to a book, [`Bulletproof SSL and TLS`](https://www.amazon.com/Bulletproof-SSL-TLS-Understanding-Applications/dp/1907117040).

```sh
# 1. Generate an RSA private key
openssl genrsa -out argocd.key 2048


# 2. Public key: have just the public part of a key separately
openssl rsa -in argocd.key -pubout -out argocd-public.key


# 3. Certificate Signing Request (CSR).
# This is a formal request asking a CA to sign a certificate, and it contains the public key of the
# entity requesting the certificate and some information about the entity.
# A CSR is always signed with the private key corresponding to the public key it carries.
# openssl req -new -key argocd.key -out argocd.csr
# Here, I did Unattended CSR Generation (non-interactive). it requires creating argocd.cnf beforehand.
cat << EOF > argocd.cnf
[req]
prompt = no
distinguished_name = dn
req_extensions = ext
[dn]
CN = www.catornot.com
emailAddress = cactoos555@gmail.com
O = CatOrNot Ltd
L = Seoul
C = KR

[ext]
subjectAltName = @alt_names

[alt_names]
DNS.1   = *.catornot.com
DNS.2   = catornot.com
DNS.3   = argocd-repo-server
DNS.4   = argocd-repo-server.argo-cd.svc
DNS.5   = argocd-dex-server
DNS.6   = argocd-dex-server.argo-cd.svc
IP.1    = 192.168.0.202
EOF

openssl req -new -config argocd.cnf -key argocd.key -out argocd.csr
# double-check that the CSR is correct
# openssl req -text -in argocd.csr -noout


# 4. Signing Your Own Certificates
# After a CSR is generated, use it to sign your own certificate and/or send it to a public CA
# and ask him or her to sign the certificate
# If you’re installing a TLS server for your own use, you probably don’t want to go to a CA to
# get a publicly trusted certificate. It’s much easier to sign your own. 

# (Required for) Creating Certificates Valid for Multiple Hostnames
cat << EOF > argocd.ext
subjectAltName = @alt_names
[alt_names]
DNS.1   = *.catornot.com
DNS.2   = catornot.com
DNS.3   = argocd-repo-server
DNS.4   = argocd-repo-server.argo-cd.svc
DNS.5   = argocd-dex-server
DNS.6   = argocd-dex-server.argo-cd.svc
IP.1    = 192.168.0.202
EOF

openssl x509 -req -days 3650 -in argocd.csr -signkey argocd.key -out argocd.crt -extfile argocd.ext

# examine the created certificate
openssl x509 -text -in argocd.crt -noout
```

#### Create secrets using Self-signed certificate

- [TLS configuration](https://argo-cd.readthedocs.io/en/stable/operator-manual/tls/)

"Argo CD provides three inbound TLS endpoints that can be configured:"

- argocd-server
    - `argocd-server-tls` (higher priority) or `argocd-secret` (deprecated) secret that stores tls.crt and tls.key
    - if tls.crt and tls.key are found in neither of above secrets, a self-signed certificate is generated into `argocd-secret`

```sh
# To create this secret manually from an existing key pair, you can use kubectl:
# Argo CD will pick up changes to the argocd-server-tls secret automatically
# and will not require restart of the pods to use a renewed certificate.
cd argocd_certs
```

kubectl create secret tls catornot-tls \
  --cert=./argocd.crt \
  --key=./argocd.key

- argocd-repo-server

```sh
kubectl create -n argocd secret tls argocd-repo-server-tls \
  --cert=./argocd.crt \
  --key=./argocd.key

k get deploy/argocd-repo-server -nargocd
    NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
    argocd-repo-server                 1/1     1            1           16h

k rollout restart deploy/argocd-repo-server -nargocd
k get pod -nargocd
```

- argocd-dex-server
    - NOTE: as opposed to argocd-server, the argocd-repo-server is not able to pick up changes
    - to this secret automatically. If you create (or update) this secret,
    - the argocd-repo-server pods need to be `restarted`.

```sh
kubectl create -n argocd secret tls argocd-dex-server-tls \
  --cert=./argocd.crt \
  --key=./argocd.key

k get deploy/argocd-dex-server -nargocd
    NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
    argocd-dex-server                 1/1     1            1           16h

k rollout restart deploy/argocd-dex-server -nargocd
k get pod -nargocd
```

##### Configuring TLS between Argo CD components

- Configuring TLS to argocd-repo-server
    - Modify the pod startup parameters for argocd-server and argocd-application-controller
    - to include the `--repo-server-strict-tls` parameter.

```sh
kubectl get deploy/argocd-server -nargocd
    NAME            READY   UP-TO-DATE   AVAILABLE   AGE
    argocd-server   1/1     1            1           17h
kubectl edit deployment argocd-server -n argocd
    spec:
      containers:
      - args:
        - /usr/local/bin/argocd-server
        - --repo-server-strict-tls
        name: argocd-server


kubectl get statefulsets/argocd-application-controller -n argocd
    NAME                            READY   AGE
    argocd-application-controller   1/1     17h
kubectl edit statefulset argocd-application-controller -n argocd
    spec:
      containers:
      - args:
        - /usr/local/bin/argocd-application-controller
        - --repo-server-strict-tls
```

- Configuring TLS to argocd-dex-server
    - Modify the pod startup parameters for argocd-server to include the --dex-server-strict-tls parameter.

```sh
kubectl get deploy/argocd-server -nargocd
    NAME            READY   UP-TO-DATE   AVAILABLE   AGE
    argocd-server   1/1     1            1           17h
kubectl edit deployment argocd-server -n argocd
    spec:
      containers:
      - args:
        - /usr/local/bin/argocd-server
        - --repo-server-strict-tls
        - --dex-server-strict-tls
        name: argocd-server
```


#### Check argocd-server pods if it correctly uses the created certificate!

```sh
kubectl exec -it argocd-server-66688f65d6-xdcl8 -nargocd /bin/bash
ls /app/config/server/tls

openssl x509 -text -in /app/config/server/tls/tls.crt -noout
```

#### Register A Cluster To Deploy Apps To (Optional)

In case, argocd need to deploy application to a different Kubernetes cluster than the cluster that argocd is running in.
When deploying internally (to the same cluster that Argo CD is running in),
`https://kubernetes.default.svc` should be used as the application's K8s API server address.


```sh
argocd cluster list
    SERVER                          NAME        VERSION  STATUS   MESSAGE                                                  PROJECT
    https://kubernetes.default.svc  in-cluster           Unknown  Cluster has no applications and is not being monitored.


    arn:aws:eks:ap-northeast-2:094833749257:cluster/my-cluster
kubectl config get-contexts -o name
    minikube
    pi
argocd cluster add pi

argocd cluster list
    SERVER                          NAME        VERSION  STATUS      MESSAGE                                                  PROJECT
    https://192.168.0.10:6443       pi          1.30     Successful
    https://kubernetes.default.svc  in-cluster           Unknown     Cluster has no applications and is not being monitored.
```

.kube/config
    server: https://192.168.0.10:6443

### Ingress Configuration

- [Kubernetes/ingress-nginx](https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#kubernetesingress-nginx)
    - [Option 1: SSL-Passthrough](https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#option-1-ssl-passthrough)
    - [Option 2: SSL Termination at Ingress Controller](https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#option-2-ssl-termination-at-ingress-controller)


```sh
# **TEST** with port-forward just for testing
kubectl port-forward svc/argocd-server -n argocd 8080:443

# TEST use of Service of type Load Balancer and ROLLBACK to use ingress instead
kubectl get svc/argocd-server -n argocd
    NAME            TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
    argocd-server   ClusterIP   10.98.233.38   <none>        80/TCP,443/TCP   15h

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
kubectl get svc/argocd-server -n argocd
    NAME            TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)                      AGE
    argocd-server   LoadBalancer   10.98.233.38   192.168.0.202   80:32216/TCP,443:32427/TCP   15h

# Access available: http://192.168.0.202

# ROLLBACK
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "ClusterIP"}}'
```



[↑ Back to top](#)
<br><br>

## Reference <a class="headerlink" href="#reference" title="Permanent link"> ¶</a>

- [kubernetes.io](https://kubernetes.io/docs/home/)
- [server world](https://www.server-world.info/en/note?os=Ubuntu_24.04&p=download)
- [networking-terminology](https://www.digitalocean.com/community/tutorials/an-introduction-to-networking-terminology-interfaces-and-protocols)
- [understanding-ip-subnets-and-cidr](https://www.digitalocean.com/community/tutorials/understanding-ip-addresses-subnets-and-cidr-notation-for-networking)
- [Calico](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises#install-calico)
- [Argo CD](https://argo-cd.readthedocs.io/en/stable/)

