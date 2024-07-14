---
draft: false
date: 2024-07-11
categories:
    - Kubernetes
    - Deep Learning
    - Project
    - EKS
    - Terraform
    - Helm
authors:
    - junho
---

## System overview

| <img src="https://d17pwbfgewyq5y.cloudfront.net/AWS_EKS.drawio.png?" alt="simpledl architecture" width="750"> |
| :--: |
| *Kubernetes architecture (EKS)* |

The final architecture of my application, which I will be explaining in the following post.

<!-- more -->

## Application Demo

| <img src="https://imgur.com/CAgwA5H.gif" alt="pods" width="680"> |
|:--:| 
| *web application* |

[↑ Back to top](#)
<br><br>

* <a href="https://github.com/jnuho/simpledl" target="_blank">`Github`</a>

- [`Why Kuberenetes`](#why-kubernetes)
- [`Skill Sets`](#skill-sets)
- [`Microservices`](#microservices)
    - [`1.Frontend - Nginx`](#frontend-nginx)
    - [`2. Backend - Golang`](#backend-golang-web-server)
    - [`3. Backend - Python`](#backend-python-web-server)
- [`Dockerize`](#dockerize)
- [`EKS implementation`](#eks-implementation)
    - [`AWS LoadBalancer Controller`](#aws-loadbalancer-controller)
    - [`Traffic Flow in AWS EKS`](#traffic-flow-in-aws-eks)
    - [`Terraform`](#terraform)
- [`Appendix`](#appendix)


## Why Kubernetes

docker-compose has many limitations in `Scalability`, `Load balancing`, and `Cloud-native integration`.

Even in local development environment, minikube was a better choice due to the aspect of `Kubernetes Consistency`.

Kubernetes provides an extensive set of APIs that effectively address these challenges.

| | docker-compose | Kubernetes
--|--|--
Scalability              | Limited to a single host             | Simulates multi-node scaling
Load Balancing           | Requires manual setup (e.g., HAProxy)| Built-in Kubernetes Service load balancing
Cloud-Native Integration | Minimal cloud integration      | Supports Kubernetes-native cloud integrations
Kubernetes Consistency   | Not applicable                     | Mirrors production Kubernetes environments


| <img src="https://imgur.com/j0RI7lF.png" alt="simpledl architecture" width="550"> |
| :--: |
|  *docker-compose vs. Kubernetes* |

### Scalability

docker-compose is limited to deploying containers on a single host. In contrast, Kubernetes offers orchestration and management of containerized applications across a cluster of nodes, ensuring high availability and resource efficiency.


| <img src="https://imgur.com/Cc5oFFZ.png" alt="simpledl architecture" width="500"> |
| :--: |
|  *docker-compose vs. Kubernetes* |


- `HPA` implements control loop with interval set by kube-controller-manager.
    - based on `CPU` and `Memory` usage
    - pre-requisite:
        - metric-server
        - `deployment.spec.template.spec.containers[i].resources`
        - `hpa.spec.metrics[i].resouce` CPU and Memory

- hpa.yaml
    - uses `name: fe-nginx` to identify target
    - in order to enable HPA to work on another metrics, you need to define addtional component.

```yaml
# ...
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fe-nginx
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

- deployment.yaml

```yaml
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 100m
              memory: 256Mi
```


- metric-server scrapes from kublet and publish metrics to `metrics.k8s.io/v1beta` Kubernetes api.
    - install metric-server with helm!

### Load Balancing

docker-compose lacks built-in load balancing capabilities. It requires to set up HAProxy manually to achieve many functionalities that Load balancer provides.
Kubernetes, on the other hand, provides advanced, native support for load balancing and traffic routing through `Ingress`, `Ingress Controller`, and `AWS Load Balancer Controller`.

1. Layer 4 implementation
2. Layer 7 inplementation

### Cloud-Native Integration

Kubernetes natively supports cloud environments, enabling seamless integration with services like AWS. It allows for:

- Use of cloud-specific ingress controllers
- Automatic provisioning of cloud resources (e.g., load balancers)
- Alignment with cloud-native services for optimized deployment and scalability

This integration enhances operational efficiency in cloud environments, embodying key cloud-native principles of automation and scalability.

### Kubernetes Consistency

Simulates Production Environment: Minikube runs a single-node Kubernetes cluster on your local machine.

Feature Parity: Allows developers to use the same Kubernetes features and resources locally as they would in a production environment (e.g., Deployments, Services, ConfigMaps, Secrets).

## About the App

My initial goal was to revisit the [`skills`](#skill-sets) by creating a simple web application which uses above skill sets.

I had to spend some time trouble shooting on constructing the Infrastructure for both On-premise and AWS cloud envionment.

The application should analyze images and determines whether they depict Cats or Non-cats, although the project is not finished yet.

I've yet to use pytorch (CNN) to create a model that can recognize Cat vs. Non-cat. For now I only experimented with numpy for binary classification.



## Skill Sets

- `Kubernetes`
    - AWS: EKS cluster with 3 worker nodes. Terraform to deploy EKS and AWS Load Balancer Controller and Ingress for exposing the app.
    - Local: 3-node cluster w/ [microk8s](https://microk8s.io/docs/getting-started).
- `Terraform` iac to create:
    - [`LINK`](https://blogd.org/blog/2024/07/01/eks-with-terraform-and-helm)
    - AWS network resources
    - IAM Role and policy association with serviceaccount
    - EKS cluster, node group, addons
- `Helm Chart`
    - [`LINK`](helm.pdf)
- `Docker` and `Dockerfile` for building images
- `Github Actions` for CI
    - Github repository -> Dockerhub image repository
- `Microservices Architecture`
    - Frontend : Nginx (with html, css, js) as a reverse proxy server
    - Backend : Python (uvicorn), Golang (go-gin) as backend web server
- `Deep learning` algorithm for binary classification using `numpy` and `pytorch`
    - Forward/[backward propagation](https://en.wikipedia.org/wiki/Backpropagation) and Gradient Descent for parameter tuning.
    - TODO: `pytorch` for cat/non-cat recognizer (In progress)
- `Virtualbox` (with cli) to test configure 3 microk8s Kubernetes master nodes (ubuntu) in local environment
- `Golang Concurrency`
    - used context, channel, goroutine for concurrent programming



[↑ Back to top](#)
<br><br>


## Microservices

- `Frontend - Nginx`
   - Nginx serves as the static content server, handling HTML, CSS, and JavaScript files.
   - It ensures efficient delivery of frontend resources to users' browsers.
- `Backend - Go-Gin web-server`
   - The Go-Gin server acts as an intermediary between the frontend and backend services.
   - It receives requests from the frontend, including requests for cat-related information.
   - Additionally, it performs utility functions, such as fetching weather data for three cities using goroutine concurrency (3-worker).

- `Backend - Python uvicorn + fast api web-server`
    - The Python backend worker is responsible for image classification.
    - TODO (not complete):
    - Given an image URL, it uses PyTorch (and possibly NumPy) to perform binary classification (cat vs. non-cat).
    - The result of the classification is then relayed back to the Go-Gin server.

- `How it works?`
    - When a user submits an image URL via the frontend(browser), the Go-Gin server receives the request.
    - It forwards the request to the Python backend.
    - The Python backend processes the image using the deep learning algorithm.
    - Finally, the result (whether the image contains a cat or not) is sent back to the frontend.

- `Next Goal`
    - Enhance the Python backend by incorporating a deep learning algorithm using pytorch.
    - I initially did a Numpy implementation with 5-Layer and 2,500 iterations for training parameters.
    - Now, I'm exploring the use of PyTorch for training the model and performing predictions



[↑ Back to top](#)
<br><br>



## Frontend nginx

- Vanilla Javascript
- HTML/CSS - bootstrap
- Nginx server that serves static files: /usr/share/nginx/html
- Dockerized with `nginx:alpine` Image


[↑ Back to top](#)
<br><br>



## Backend Python web server

- Use FastAPI + Unicorn
    - FastAPI is an ASGI (<b>Asynchronous</b> Server Gateway Interface) framework which requires an ASGI server to run.
    - Unicorn is a lightning-fast ASGI server implementation

- install python (download .exe from python.org)
    - check Add to PATH option (required)


- Run the python web server

```sh
uvicorn main:app --port 3002
```


[↑ Back to top](#)
<br><br>


## Dockerize

**NOTE**: It is crucial to optimize Docker images to be as compact as possible.
One strategy to achieve this is by utilizing base images that are minimalistic, such as the Alpine image.

- [NOTE on defining backend endpoint in frontend](https://stackoverflow.com/a/56375180/23876187)
    - frontend app is not in any container, but the javascript is served from container as a js script file to <b>your browser</b>!

- frontend nginx service



[↑ Back to top](#)
<br><br>


## EKS implementation



[↑ Back to top](#)
<br><br>

### AWS LoadBalancer Controller

- [`AWS document`](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html)
- [`AWS LoadBalancer Controller`](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.8/how-it-works/)


- Controller 
    - In Kubernetes, controllers are control loops that watch the state of your cluster, then make or request changes where needed.
    - Each controller tries to move the current cluster state closer to the desired state.
    - The Load Balancer Controller watches for Kubernetes Ingress or Service resources.
 
- The `AWS Load Balancer Controller` (pods in kube-system namespace) watches for changes in Kubernetes `Ingress` resources.
    - When an Ingress resource is created or updated, the controller translates the Ingress resource into configurations for AWS ALBs or NLBs.
    - It ensures that the ALB/NLB is configured correctly to route traffic based on the rules specified in the Ingress resource.

- In order for this Kubernetes pod to be able to create AWS resources like ALBs(based on Kubernetes Ingress), and NLBs(based on Service resources),
    - it needs `IAM Role` with proper policies attached to use AWS API to create and configure an ALB.
    - The AWS Load Balancer Controller, running as a pod in the `kube-system` namespace,
    - monitors for new or updated Ingress resources with the alb ingress class.


### Traffic Flow in AWS EKS

- `Client Request to ALB`
    - The client (e.g., browser) sends a request to the AWS Application Load Balancer (ALB).
    - The ALB serves as the entry point into the Kubernetes cluster.
- `ALB to Ingress Controller`
    - The ALB forwards the request directly to the Kubernetes cluster based on the rules defined in the ALB's configuration.
    - The AWS Load Balancer Controller is responsible for creating and configuring the ALB based on the Ingress resource
    - It is deployed in your cluster and runs in the kube-system namespace.
    - It watches for Ingress resources that are annotated to use an AWS ALB and automatically creates and configures the ALB based on these resources.
- `Ingress Controller (e.g., NGINX Ingress)`
    - The Ingress Controller (e.g., NGINX Ingress Controller) is responsible for implementing the rules defined in the Ingress resource.
    - It receives requests from the ALB via the AWS Load Balancer Controller and routes them to the appropriate Kubernetes Services(ClusterIP) based on the Ingress rules.
- `Service to Pods`
    - Finally, the Service routes the request to one or more Pods that belong to the targeted Kubernetes workload (Deployment, StatefulSet, etc.).
    - The Pods process the request and generate responses, which flow back through the same path to reach the client.
    - The Service forwards the request to the appropriate Pods, which are the application instances.
    - The Pods process the request and generate a response, which is sent back through the same path.
    - Kubernetes Services, specifically those of type ClusterIP, provide a stable virtual IP address to access a set of Pods.
    - The Ingress Controller routes traffic to the corresponding Service based on the Ingress rules.

- Recap
    - **Client** sends requests to the AWS ALB.

    - **AWS ALB**: This is created and managed by the AWS Load Balancer Controller based on the Ingress resource definitions. It handles incoming traffic from clients.
    - **Ingress Controller**: It interprets the Ingress resource rules and routes the traffic to the appropriate Kubernetes backend services.
    - **Service (ClusterIP)**: It provides a stable IP address and DNS name to access the Pods and internal load balancing across Pods.
    - **Pods**: These are the application instances that handle the actual processing of requests.

The AWS Load Balancer Controller's role is to manage the lifecycle and configuration of AWS ALBs/NLBs based on Kubernetes Ingress resources. It does not handle the traffic directly. Instead, it ensures that the ALB is correctly set up to route traffic to the Kubernetes cluster, where the Ingress Controller then takes over to route the traffic within the cluster to the appropriate services and pods.actual instances of your application that handle requests and generate responses.


```
Client (Browser)
   |
   v
AWS ALB (Application Load Balancer)  <-- Created and managed by AWS Load Balancer Controller
   |
   v
Ingress Controller (e.g., NGINX)     <-- Routes traffic within the cluster based on Ingress rules
   |
   v
Service (ClusterIP)
   |
   v
Pods (Application Instances)

```

Requests from clients are efficiently routed to the appropriate Kubernetes workloads
based on the defined rules and configurations managed by the AWS Load Balancer Controller
and Ingress resources within an AWS EKS cluster.


[↑ Back to top](#)
<br><br>

| <img src="https://imgur.com/YpjRWc6.png" alt="pods" width="700"> |
|:--:| 
| *ingress resource* |

| <img src="https://imgur.com/Ymkj2PH.png" alt="pods" width="400"> |
|:--:| 
| *aws load-balancer controller pod in `kube-system` namespace* |


[↑ Back to top](#)
<br><br>






## Appendix

- [`Binary classification`](#binary-classification)
- [`Mathematical background`](#mathematical-background)
- [`Image Classification`](#image-classification)
- [`vite for development`](#vite-for-development)
- [`Virtualbox network architecture`](#virtualbox-network-architecture)
- [`Virtualbox setup`](#virtualbox-setup)
- [`CORS issue`](#cors-issue)
- [`Minikube implementation`](#minikube-implementation)
- [`Microk8s implemntation`](#microk8s-implemntation)
- [`Golang ini setting`](#golang-ini-setting)

### Binary classification

It is a basic deep learning image recognizers, one of which was covered in Andrew Ng's coursera course. I plan to test two simple deep learning models to identify cat images and hand-written digits (0-9), respectively and return the result of identification to the browser.

[↑ Back to top](#)
<br><br>


### Mathematical background

The basic operations for forward and backward propagations in deep learning algorithm are as follows:

|<img src="https://imgur.com/ZJ94x9B.png" alt="propagation" width="450">|
|:--:| 
| *Forward and Backward propagation* |

<!-- - Forward propagation for layer $l$: $a^{[l-1]}\rightarrow a^{[l]}, z^{[l]}, w^{[l]}, b^{[l]}$

    $Z^{[l]} = W^{[l]} A^{[l-1]} + b^{[l]}$

    $A^{[l]} = g^{[l]} (Z^{[l]})$

    (for $i=1,\dots,L$ with initial value $A^{[0]} = X$)

<br>

- Backward propagation for layer $l$: $da^{[l]} \rightarrow da^{[l-1]},dW^{[l]}, db^{[l]}$

    $dZ^{[l]} = dA^{[l]} * {g^{[l]}}^{'}(Z^{[l]})$

    $dW^{[l]} = \frac{1}{m}dZ^{[l]}{A^{[l-1]}}^T$

    $db^{[l]} = \frac{1}{m}np.sum(dZ^{[l]}, axis=1, keepdims=True)$

    $dA^{[l-1]} = {W^{[l]}}^T dZ^{[l]} = \frac{dJ}{dA^{[l-1]}} = \frac{dZ^{[l]}}{dA^{[l-1]}} \frac{dJ}{dZ^{[l]}} = \frac{dZ^{[l]}}{dA^{[l-1]}} dZ^{[l]}$

    (with initial value $dZ^{[L]} = A^{[L]}-Y$) -->


[↑ Back to top](#)
<br><br>

### Image Classification

- cat vs.non-cat image classification and hand-written digits recognition
- https://www.youtube.com/watch?v=JgtWVML4Ykg&ab_channel=SheldonVon
- https://detexify.kirelabs.org/classify.html
- https://mco-mnist-draw-rwpxka3zaa-ue.a.run.app/
- pytorch
    - https://youtu.be/EMXfZB8FVUA?si=XL8SckGQi9xQDgtc
    - https://pytorch.org/get-started/locally/

- CPU (Without Nvidia CUDA) only

```sh
pip3 install torch torchvision torchaudio

# requirements.txt
torch==2.3.0
torchaudio==2.3.0
torchvision==0.18.0

# install using requirements.txt
python install -r requirements.txt
```

```python
import torch

x = torch.rand(3)
# tensor([.5907, .0781, .3094])
print(x)

print(torch.cuda.is_available())
```

[↑ Back to top](#)
<br><br>



### vite for development

- Download & install nodejs 20.12.2
    - for local development using `vite`

```sh
npm create vite@latest
    ? Project name: lesson11
    > choose Vanilla, TypeScript
```

- Edit `package.json` to edit port and dependencies

```json
    "scripts": {
        "dev": "vite --host 0.0.0.0 --port 8080",
        "build": "tsc && vite build",
        "preview": "vite preview"
    },

    "dependencies": {
        "axios": "^1.6.8"
    }
```

I used nodejs vite for local development environment.
I will be using nginx in production environment.

```sh
# install dependencies specified in package.json
# install if package.json changes e.g. project name
npm i
npm run dev
    VITE v5.2.9    ready in 180 ms

    ➜    Local:     http://localhost:4200/
    ➜    Network: use --host to expose
    ➜    press h + enter to show help
```

- Edit code
    - Write `index.html`
    - Create directory: `./model`, `./templates`
    - Define models and templates
    - Edit `main.ts`



[↑ Back to top](#)
<br><br>

## Backend Golang web server

- `go.mod`, `go.sum` must be in github repo root directory
- sources:
    - `cmd/backend-server/main.go`
    - `backend/web/handler.go`
    - `backend/web/server.go`
    - `backend/web/util.go`
    - `backend/pkg/weatherapi.go`

```sh
cd simpledl
go mod init github.com/jnuho/simpledl
go mod tidy
```


### Virtualbox network architecture

I had to construct a virtualbox environment in which my kubernetes cluster and application will be deployed. 🔥


|<img src="https://i.imgur.com/w8PxxXk.png" alt="simpledl architecture" width="400">|
|:--:| 
| *kubernetes architecture (Local VirtualBox)* |


|<img src="https://imgur.com/tyhjPsG.png" alt="pods" width="520">|
|:--:| 
| *NAT network* |



[↑ Back to top](#)
<br><br>

### Virtualbox Setup

- Download ubuntu iso image
- Run vm instacne using iso image
- Install ubuntu

- Hosts: 10.0.2.3, 10.0.2.4, 10.0.2.5
- OS: Ubuntu 24.04 server


```bat
vboxmanage list dhcpservers
vboxmanage list natnetworks
vboxmanage list vms

VBoxManage dhcpserver remove --netname k8snetwork
VBoxManage natnetwork remove --netname k8snetwork

VBoxManage unregistervm ubuntu-1 --delete
VBoxManage unregistervm ubuntu-2 --delete
VBoxManage unregistervm ubuntu-3 --delete

./vb-create.bat > log.txt 2>&1
```


```bat
VBoxManage natnetwork add --netname k8snetwork --network "10.0.2.0/24" --enable --dhcp on
VBoxManage dhcpserver add --netname k8snetwork --server-ip "10.0.2.2" --netmask "255.255.255.0" --lower-ip "10.0.2.3" --upper-ip "10.0.2.254" --enable

vboxmanage dhcpserver restart --network=k8snetwork

for /L %%i in (1, 1, 3) do (
    REM Create VM
    VBoxManage createvm --name ubuntu-%%i --register --ostype Ubuntu_64
    REM ...
    REM ...
)

REM Set up port forwarding rules
VBoxManage natnetwork modify --netname k8snetwork --port-forward-4 "Rule 1:tcp:[127.0.0.1]:22021:[10.0.2.3]:22"
VBoxManage natnetwork modify --netname k8snetwork --port-forward-4 "Rule 2:tcp:[127.0.0.1]:22022:[10.0.2.4]:22"
VBoxManage natnetwork modify --netname k8snetwork --port-forward-4 "Rule 3:tcp:[127.0.0.1]:22023:[10.0.2.5]:22"

REM application port
VBoxManage natnetwork modify --netname k8snetwork --port-forward-4 "Http:tcp:[127.0.0.1]:80:[10.0.2.3]:80"
```

```sh
# ethernet device info
nmcli d

nmcli d show enp0s3

ip a dev enp0s3

sudo ip link set enp0s3 down
sudo ip link set enp0s3 up
```


[↑ Back to top](#)
<br><br>

### CORS issue

- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

When a web application tries to make a request to a server that’s on a different domain, protocol, or port,
it encounters a CORS (Cross-Origin Resource Sharing) issue. Add headers to backend server accordingly

```
For security reasons, browsers restrict cross-origin HTTP requests initiated from scripts.
For example, fetch() and XMLHttpRequest follow the same-origin policy.

This means that a web application using those APIs can only request resources
from the same origin the application was loaded from unless the response
from other origins includes the right CORS headers.

=> Add appropriate headers in golang server.
```


[↑ Back to top](#)
<br><br>


### Minikube implementation

To set up your Nginx, Golang, and Python microservices on Minikube, you'll need to create Kubernetes Deployment and Service YAML files for each of your microservices. You'll also need to set up an Ingress controller to expose your services to the public. Here's a high-level overview of the steps:

1. **Install Minikube**: If you haven't already, you'll need to install Minikube on your machine. Minikube is a tool that lets you run Kubernetes locally.

- ubuntu 24.04 install minikube

```sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb

# unintstall
#sudo dpkg -r minikube
```


[↑ Back to top](#)
<br><br>

2. **Start Minikube**: Once installed, you can start a local Kubernetes cluster with the command `minikube start`.

```sh
# As a TROUBLE SHOOTING:
docker context use default
    default
    Current context is now "default"

minikube start
```


[↑ Back to top](#)
<br><br>

3. **Create secret**

3-1. Login to docker hub

```
docker login --username YOUR_USERNAME
```

3-2. Create secret

```
k create secret docker-registry regcred \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=USER \
    --docker-password=PW \
    --docker-email=EMAIL

k get secret
```



[↑ Back to top](#)
<br><br>

4. **Create Deployment and Service YAML Files**: For each of your microservices (Nginx, Golang, Python), you'll need to create a Deployment and a Service. The Deployment defines your application and the Docker image it uses, while the Service defines how your application is exposed to the network

4-1. deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
    name: fe-nginx-deployment
spec:
    replicas: 1
    # Deployement manages pods with label 'app: fe-nginx
    selector:
        matchLabels:
            app: fe-nginx
    # define labels for the Pods:
    #     must be matched by service.yaml > spec.selector
    template:
        metadata:
            labels:
                app: fe-nginx
        spec:
            containers:
            - name: fe-nginx
                image: jnuho/fe-nginx:latest
                ports:
                - containerPort: 80
            imagePullSecrets:
            - name: regcred

```


[↑ Back to top](#)
<br><br>

4-2. service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
    name: fe-nginx-service
    namespace: simple
spec:
    # must match deployment.yaml > spec.template.metadata.labels
    selector:
        app: fe-nginx
    ports:
        - protocol: TCP
            port: 8080
            targetPort: 80
    type: ClusterIP
```



[↑ Back to top](#)
<br><br>

5. **Apply the YAML Files**: Once you've created your YAML files, you can apply them to your Kubernetes cluster with the command `kubectl apply -f <filename.yaml>`.


[↑ Back to top](#)
<br><br>


6. **Enable Ingress Controller**:

6-1. NGINX ingress controller using Minikube addons: you can use the command `minikube addons enable ingress`

```sh
minikube addons enable ingress
```


[↑ Back to top](#)
<br><br>

6-2. Nginx ingress controller

- [setting up an NGINX ingress controller](https://medium.com/@amirhosseineidy/how-to-set-up-nginx-ingress-controller-in-local-server-6cc4bd7d6a6b) in a bare metal or local server:


Ingress is an API in Kubernetes that routes traffic to different services, making applications accessible to clients from the Kubernetes cluster. Among multiple choices like HAProxy or Envoy for setting up an ingress controller, NGINX is the most popular one. It is powered by the NGINX web server and is a fast and secure controller that delivers your applications to the clients easily.

- Install NGINX ingress controller with `helm`

```sh
# inside cmd or powershell
winget install Helm.Helm

# RESTART terminal and do:
helm upgrade --install ingress-nginx ingress-nginx \
    --repo https://kubernetes.github.io/ingress-nginx \
    --namespace ingress-nginx --create-namespace
```

- Check if ingress controller is working:

```sh
helm list
    NAME                        NAMESPACE             REVISION                UPDATED                                                                 STATUS                    CHART                                     APP VERSION
    ingress-nginx     default                 1                             2024-04-30 14:26:18.9350713 +0900 KST     deployed                ingress-nginx-4.10.1        1.10.1

k get ClusterRole | grep ingress
    ingress-nginx                                                                                                                    2024-04-30T07:01:05Z

k get all
    NAME                                                                                     READY     STATUS        RESTARTS     AGE
    pod/ingress-nginx-controller-cf668668c-zvkd9     1/1         Running     0                    44s

    NAME                                                                                 TYPE                     CLUSTER-IP             EXTERNAL-IP     PORT(S)                                            AGE
    service/ingress-nginx-controller                         LoadBalancer     10.100.168.236     <pending>         80:32020/TCP,443:31346/TCP     44s
    service/ingress-nginx-controller-admission     ClusterIP            10.107.208.79        <none>                443/TCP                                            44s
    service/kubernetes                                                     ClusterIP            10.96.0.1                <none>                443/TCP                                            4m8s

    NAME                                                                             READY     UP-TO-DATE     AVAILABLE     AGE
    deployment.apps/ingress-nginx-controller     1/1         1                        1                     44s

    NAME                                                                                                 DESIRED     CURRENT     READY     AGE
    replicaset.apps/ingress-nginx-controller-cf668668c     1                 1                 1             44s
```


[↑ Back to top](#)
<br><br>

7. **Create an Ingress YAML File**: The Ingress YAML file will define the rules for routing external traffic to your services. You'll need to specify the host and path for each service, and the service that should handle traffic to each host/path


[↑ Back to top](#)
<br><br>

8. **Apply the Ingress YAML File**: Just like with the Deployment and Service files, you can apply the Ingress file with `kubectl apply -f <ingress-filename.yaml>`.

- Ingress rules
    - Ingress rules are resources that help route services to your desired domain name or prefix. They are divided into prefix and DNS.
    - .yaml mainifest for ingress rules

```sh
k apply ingress.yaml
k get ingress
    NAME                             CLASS     HOSTS                                ADDRESS                PORTS     AGE
    fe-nginx-ingress     nginx     my-app.example.com     192.168.49.2     80            4m35s
```


[↑ Back to top](#)
<br><br>


9. **Access Your Services**: With the Ingress set up, you should be able to access your services from outside your Kubernetes cluster. You can get the IP address of your Minikube cluster with the command `minikube ip`, and then access your services at that IP


- Accessing application
    - For accessing these applications in a local cluster, you should access it through node port (30000 ports) or use a reverse proxy to send them.
    - But is there any way to access app on port 80 or 443?
        - use Port-forward or `MetalLB` to allow access to app on port 80 or 443.

- port forward

```sh
k get svc -n ingress-nginx
NAME                                                                 TYPE                CLUSTER-IP         EXTERNAL-IP     PORT(S)                                            AGE
ingress-nginx-controller                         NodePort        10.107.26.28     <none>                80:32361/TCP,443:31064/TCP     3h9m
ingress-nginx-controller-admission     ClusterIP     10.106.14.66     <none>                443/TCP                                            3h9m

kubectl port-forward -n <namespace> svc/<service-name> <local-port>:<service-port>
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 80:80 3001:3001 3002:3002

```


[↑ Back to top](#)
<br><br>

- Installing Metallb

```sh
# strictARP to true
kubectl edit configmap -n kube-system kube-proxy

    apiVersion: kubeproxy.config.k8s.io/v1alpha1
    kind: KubeProxyConfiguration
    mode: "ipvs"
    ipvs:
        strictARP: true

kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.10/config/manifests/metallb-frr.yaml

kubectl get pods -n metallb-system
    NAME                                                    READY     STATUS        RESTARTS     AGE
    controller-596589985b-jrnmk     1/1         Running     0                    34m
    speaker-hdrmc                                 4/4         Running     0                    34m
```

- Now set a range IPs for your local load balancer by creating a configMap. 
    - Remember that the set of IP addresses you apply must be in the same range as your nodes IPs

The range of IP addresses you choose for MetalLB should be in the same subnet as your nodes' IPs. These IP addresses are used by MetalLB to assign to services of type LoadBalancer.
Using command, `k get node -o wide`, the INTERNAL-IP of my node is 192.168.49.2. So, choose a range of IP addresses in the 192.168.49.x range for MetalLB. For example, 192.168.49.100-192.168.49.110 as my range.

The IP addresses you choose for MetalLB should be reserved for MetalLB's use and should not conflict with any other devices on your network.

```yaml
# to see ip range for node
kubectl get nodes -o wide
    NAME             STATUS     ROLES                     AGE     VERSION     INTERNAL-IP        EXTERNAL-IP     OS-IMAGE                         KERNEL-VERSION                                             CONTAINER-RUNTIME
    minikube     Ready        control-plane     41m     v1.30.0     192.168.49.2     <none>                Ubuntu 22.04.4 LTS     5.15.146.1-microsoft-standard-WSL2     docker://26.0.1

cat > configmap.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
    name: nat
    namespace: metallb-system
spec:
    addresses:
        - 192.168.49.100-192.168.49.110
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
    name: empty
    namespace: metallb-system


k apply -f configmap.yaml

kubectl rollout restart deployment controller -n metallb-system

# check EXTERNAL-IP for nginx-controller is assigned!!!
# the external IPS is assigned to your NGINX load balancer service and all other load balancer typed services.
k get svc
    NAME                                                                 TYPE                     CLUSTER-IP             EXTERNAL-IP            PORT(S)                                            AGE
    ingress-nginx-controller                         LoadBalancer     10.100.168.236     192.168.49.100     80:32020/TCP,443:31346/TCP     68m
```


[↑ Back to top](#)
<br><br>

- DNS Setup
    - Finally, you need to set the domain names defined in the ingress rules in your DNS server or hosts file
    - edit hosts file, `C:\Windows\System32\drivers\etc\hosts`

```
192.168.49.100 my-app.example.com
```


[↑ Back to top](#)
<br><br>


### Using Minikube for image build and local development

- https://www.youtube.com/watch?v=_1uWY1GdDVY&ab_channel=GoogleOpenSource


```sh
minikube docker-env
        W0502 10:17:02.728250     12636 main.go:291] Unable to resolve the current Docker CLI context "default": context "default": context not found: open C:\Users\user\.docker\contexts\meta\37a8eec1ce19687d132fe29051dca629d164e2c4958ba141d5f4133a33f0688f\meta.json: The system cannot find the path specified.
        export DOCKER_TLS_VERIFY="1"
        export DOCKER_HOST="tcp://127.0.0.1:57853"
        export DOCKER_CERT_PATH="C:\Users\user\.minikube\certs"
        export MINIKUBE_ACTIVE_DOCKERD="minikube"

# To point your shell to minikube's docker-daemon, run:
# eval $(minikube -p minikube docker-env)


# Now your PC directs to minikube's docker
# From now, Any image you build will be directory on built on minikube's docker

# list images inside minikube cluster
docker images -a

cd dockerfiles
docker build -f dockerfiles/Dockerfile-nginx -t fe-nginx .

```


[↑ Back to top](#)
<br><br>

- deployment.yaml

```yaml
spec:
    templates:
        spec:
            containers:
            - name: fe-nginx
                image: fe-nginx:latest
                ports:
                - containerPort: 80
```

```sh
k apply -f deployment.yaml
```


[↑ Back to top](#)
<br><br>

- suppose source changed -> change image

```sh
docker rmi fe-nginx:latest
docker build -f dockerfiles/Dockerfile-nginx -t fe-nginx .
k delete -f deployment.yaml
k apply -f deployment.yaml
```


[↑ Back to top](#)
<br><br>

- mount data to minikube cluster
    - suppose golang docker container source does:


```go
var version = "0.0.2"
func indexHandler(w http.ResponseWriter, req *http.Request){ 
        // after deployment.yaml volumeMount, this will printout
        // NOTE:
        localFile, err := os.ReadFile("/tmp/data/hello-world.txt")
        if err != nil {
                fmt.Printf("couldn't read file %v\n", err)
        }
        // before deployment.yaml volumeMount, this will printout
        fmt.FPrintf(w,"<h1>hello world :) </h1> \n Version %s\n File Content:%s", version, localFile)
}
```


```sh
minikube mount    {localdir}:{minikube hostdir}

# mount a volume to minikube cluster (persistant storage)
# mount files to minikube cluster
minikube mount    /c/Users/user/Downloads/tmp:/tmp/data
```

```yaml
spec:
    templates:
        spec:
            containers:
            - name: fe-nginx
                image: fe-nginx:latest
                ports:
                - containerPort: 80
                # target dir inside pod: /tmp/data
                volumeMounts:
                - mountPath: /tmp/data
                    name: test-volume
            volumes:
                - name: test-volume
                    # host is kubernetes host(vm)
                    hostPath:
                        # directory location on host
                        path: /tmp/data
```


[↑ Back to top](#)
<br><br>

- apply the changes:

```sh
docker rmi fe-nginx:latest
docker build -f dockerfiles/Dockerfile-nginx -t fe-nginx .
k delete -f deployment.yaml
k apply -f deployment.yaml

# deploy the app
minikube service my-fe-nginx
```

- now edit local hello-world.txt file
- then refresh browser to check the change is immediately applied




[↑ Back to top](#)
<br><br>


- dashboard

```sh
minikube ip
minikube dashboard --url
        http://127.0.0.1:45583/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/
```


[↑ Back to top](#)
<br><br>

- minikube ingress

https://stackoverflow.com/a/73735009

```sh
# minikube start --cpus 4 --memory 4096
minikube start
minikube addons enable ingress
minikube addons enable ingress-dns

# Wait until you see the ingress-nginx-controller-XXXX is up and running using Kubectl get pods -n ingress-nginx
# Create an ingress using the K8s example yaml file
# Update the service section to point to the NodePort Service that you already created
# Append 127.0.0.1 hello-world.info to your /etc/hosts file on MacOS (NOTE: Do NOT use the Minikube IP)

# ( Keep the window open. After you entered the password there will be no more messages, and the cursor just blinks)
minikube tunnel

# Hit the hello-world.info ( or whatever host you configured in the yaml file) in a browser and it should work
```


[↑ Back to top](#)
<br><br>

Here's a high-level overview of the traffic flow when you access `http://localhost` in your setup:

1. **Browser Request**: When you type `http://localhost` into your browser and hit enter, your browser sends a HTTP request to `localhost`, which is resolved to the IP address `127.0.0.1`.

2. **Port Forwarding**: Since you've set up port forwarding with the command `kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 80:80`, the request to `localhost` on port 80 is forwarded to port 80 on the `ingress-nginx-controller` service.


```sh
 k get svc -n ingress-nginx
    NAME                                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)
        AGE
    ingress-nginx-controller             NodePort    10.109.183.14    <none>        80:31078/TCP,443:31420/TCP   6m17s
    ingress-nginx-controller-admission   ClusterIP   10.110.101.115   <none>        443/TCP                      6m17s

# k port-forward deployment/fe-nginx-deployment 80
# localhost:8080 -> ingress controller on 80
k port-forward -n ingress-nginx svc/ingress-nginx-controller 80:80
```

The need for port-forwarding arises due to the way Kubernetes networking and Minikube are structured. Here's a breakdown of why you might need to use port-forwarding and why direct access might not work without it:

### Why Direct Access Might Not Work

2-1. **Network Isolation:**
   - **Kubernetes Networking:** Kubernetes clusters are designed to have an isolated network. Services within the cluster communicate with each other via internal cluster IPs that are not accessible from the outside world directly.
   - **Minikube Networking:** Minikube sets up a local virtual machine (VM) on your computer. This VM has its own network namespace, separate from your host machine's network. The services running inside Minikube are isolated from your host machine by default.

2-2. **ClusterIP Services:**
   - **ClusterIP Type:** The services you've listed (`be-go-service`, `be-py-service`, `fe-nginx-service`, and `kubernetes`) are of type `ClusterIP`. This means they are only accessible within the cluster. External traffic from your host machine cannot reach these services directly.

2-3. **Minikube IP Address:**
   - Minikube typically runs on a virtual IP address, such as `192.168.49.2` in your case. Accessing this IP directly from your host might not be straightforward due to network isolation.

### Why Port-Forwarding is Needed

Port-forwarding provides a bridge between your host machine and the Kubernetes cluster, allowing you to access cluster services from your local machine as if they were running locally.

- **Accessing Cluster Services:**
   - Port-forwarding allows you to map a port on your local machine to a port on a pod or service within the cluster. This makes it possible to access cluster services using `localhost` on your host machine.

- **Bypassing Network Isolation:**
   - By forwarding a port, you bypass the network isolation of the cluster, making it possible to communicate with services running inside Minikube directly from your host.

### Alternative Approaches

If you prefer not to use port-forwarding, there are other approaches you can consider:

- **Minikube Tunnel:**
   - Minikube provides a `minikube tunnel` command that can create a network tunnel to your cluster, making services of type `LoadBalancer` accessible from your host machine.

   ```sh
   minikube tunnel
   ```

- **NodePort Services:**
   - Change the service type to `NodePort`, which exposes the service on a port on each node of the cluster. You can then access the service using the Minikube IP and the NodePort.

   Example of changing a service to NodePort:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: fe-nginx-service
   spec:
     type: NodePort
     ports:
       - port: 8080
         targetPort: 8080
         nodePort: 30080  # Example NodePort
     selector:
       app: fe-nginx
   ```

- **Ingress with Minikube IP:**
   - You can use the Minikube IP address and configure your `/etc/hosts` file to point `localhost` to the Minikube IP.

### Summary

Using `kubectl port-forward` is a convenient and straightforward way to access your services without altering service types or cluster configurations. It helps bridge the network isolation between your host machine and the Kubernetes cluster set up by Minikube.




3. **Ingress Controller**: The Ingress Controller, which is part of the `ingress-nginx-controller` service, receives the request. The Ingress Controller is responsible for routing the request based on the rules defined in your Ingress resource.

4. **Ingress Rules**: In your case, you've set up an Ingress rule to route traffic to the `nginx-service` service on port 80 when the host is `simple-app.com`. However, since you're accessing `localhost` and not `simple-app.com`, this rule does not apply.

5. **Service**: If there were a matching Ingress rule, the Ingress Controller would forward the request to the `nginx-service` service on port 80.

6. **Pod**: The service then load balances the request to one of the pods that match its selector. In your case, this would be the pod running the Nginx application.

Please note that since you're accessing `localhost` and not `simple-app.com`, the Ingress rule does not apply, and the request will not be routed to your Nginx application. To access your application, you need to either use `simple-app.com` as the host or modify your Ingress rule to match `localhost`.



[↑ Back to top](#)
<br><br>

### Microk8s implemntation

- install microk8s (Ubuntu)

```sh
# 1.27/stable version ERROR -> install --classic
sudo snap install microk8s --classic

# 일반유저에게 microk8s 커맨드 권한 부여
# NOTE: root유저로만 microk8s 커맨드 사용시 아래 커맨드 필요 X
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube

microk8s.status --wait-ready
microk8s kubectl get no
microk8s kubectl get svc

cat >> ~/.bashrc <<-EOF

alias k='microk8s.kubectl'
EOF

source ~/.bashrc


microk8s start

# Join node (All 3 are master nodes)
sudo su -
vim /etc/hosts

cat >> /etc/hosts <<-EOF

10.0.2.3 ubuntu-1
10.0.2.4 ubuntu-2
10.0.2.5 ubuntu-3
EOF

# On each vms
ssh foo@10.0.2.3
ssh foo@10.0.2.4
ssh foo@10.0.2.5


# in first node
microk8s add-node

# in other 2 nodes
microk8s join [TOKEN]

# Trouble shoot
# https://microk8s.io/docs/restore-quorum
vim /var/snap/microk8s/current/var/kubernetes/backend/cluster.yaml

- Address: 172.16.9.201:19001
    ID: 3297041220608546238
    Role: 0
- Address: 172.16.9.202:19001
    ID: 13629670026737620399
    Role: 0
- Address: 172.16.9.203:19001
    ID: 10602814967080190144
    Role: 0
```

[↑ Back to top](#)
<br><br>

- Trouble-shooting
    - diagnosis:
        - deployed pods with count of 2 replicas, one on node1 and another on node3
        - calling endpoint seems to have different result for each time of calling.
    - cause:
        - microk8s ctr images import was done only one node1.
        - node3 tries to pull image from public docker hub instead of local repository.
        - in result, two pods have different images: one from local repository, another from public docker repository.


|<img src="https://imgur.com/KAUbhcq.png" alt="pods" width="700">|
|:--:| 
| *pod resources* |



```
k describe pod fe-nginx-deployment-7b9c5bb8f8-xlrs2
        Containers:
            fe-nginx:
                Image:                    jnuho/fe-nginx:latest
                Image ID:             sha256:2544d68d372793a21b627c360def55e648ad2cfbbf330a65ba567dbced1985f2

k describe pod fe-nginx-deployment-7b9c5bb8f8-q6d6m
        Containers:
            fe-nginx:
                Image:                    jnuho/fe-nginx:latest
                Image ID:             docker.io/jnuho/fe-nginx@sha256:48e8995cc2c86a3759ac1156cd954d8f90a1c054ae1fcd67181a77df2ff5492f

```


[↑ Back to top](#)
<br><br>

- Local docker registory
    - https://microk8s.io/docs/registry-images

```sh
git clone https://github.com/jnuho/simpledl.git

cd simpledl/script
./1.build-image.sh
./1-1.import-microk8s.sh

docker save jnuho/fe-nginx > fe-nginx.tar
docker save jnuho/be-go > be-go.tar
docker save jnuho/be-py > be-py.tar

microk8s ctr image import fe-nginx.tar
microk8s ctr image import be-go.tar
microk8s ctr image import be-py.tar

rm fe-nginx.tar
rm be-go.tar
rm be-py.tar

microk8s ctr image ls | grep jnuho
```


```sh
microk8s kubectl get pods -A | grep ingress


telnet localhost 8080
telnet localhost 3001
```


[↑ Back to top](#)
<br><br>

- Port forwarding

```
host -> virtualbox vm
```


[↑ Back to top](#)
<br><br>

- ufw setting

```
open port 3001
```


[↑ Back to top](#)
<br><br>


### Golang ini setting

In software development, managing configurations across different environments—such as development (dev), staging (stg), and production (prd)—is crucial. 

Each environment often requires distinct settings, such as API endpoint URLs, database connections, and environment variables.

Hard-coding these values directly into the application code can lead to maintenance challenges and potential errors during deployment.

- Environment-Specific Values Files
    - 

```yaml
# One can also set different namespace for each environment on values.xxx.yaml

# 1. Development envionment
helm install tst-release ./tst-chart -f ./tst-chart/values.dev.yaml

# 2. Stage envionment
helm install tst-release ./tst-chart -f ./tst-chart/values.stg.yaml

# 3. Production envionment
helm install tst-release ./tst-chart -f ./tst-chart/values.prd.yaml
```



[↑ Back to top](#)
<br><br>

