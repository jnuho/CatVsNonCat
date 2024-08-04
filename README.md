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

<img src="https://imgur.com/DwRBYMd.png" alt="EKS architecture" width="600">

The CatVsNonCat image classifier uses a deep learning model to determine whether an image from a given URL contains a cat or not.

I focused on implementing Kubernetes in an AWS environment. I used Nginx Ingress Controller to configure external access to the application.

<!-- more -->


<img src="https://imgur.com/VbKBWdO.gif" alt="demo" width="650">

[↑ Back to top](#)
<br>

Github Repository : [CatVsNonCat](https://github.com/jnuho/CatVsNonCat)

# Table of Content

- [Motivation](#motivation)
- [Why Kuberenetes?](#why-kubernetes)
    - [Scalability](#scalability)
    - [Load Balancing](#load-balancing)
        - [Nginx Ingress Controller](#nginx-ingress-controller)
        - [AWS Load Balancer Controller](#aws-load-balancer-controller)
- [Skill Used](#skill-used)
- [Microservices](#microservices)
    - [1.Frontend - Nginx](#frontend-nginx)
    - [2. Backend - Golang](#backend-golang-web-server)
    - [3. Backend - Python](#backend-python-web-server)
- [Dockerize](#dockerize)
    - [Multi-stage builds](multi-stage-builds)
    - [minikube docker-env](#minikube-docker-env)
- [IaC](#iac)
    - [Terraform](#terraform)
    - [Helm Chart](#helm-chart)
- [ArgoCD](#argocd)
- [TLS](#tls)
- [Kubernetes for MLOps](#kubernetes-for-mlops)
- [Appendix](#appendix)


## Motivation

My initial goal was to revisit the [`skills`](#skills-used) I've learned.

With my recent interest on deep learning, I decided to create a Cat image classifying application on Kubernetes environment.

The prediction model uses the following steps to train a Neural Network:

- Forward Propagation
    - <small>$a^{[l]}  = ReLU(z^{[l]})$ for $l=1,...L-1$</small>
    - <small>$a^{[l]}  = \sigma(z^{[l]})$ for $l=L$</small>
- Compute cost
- Backward Propagation
- Gradient descent (Update parameters -  $\omega$, $b$)

<img src="https://miro.medium.com/v2/resize:fit:640/format:webp/1*iNPHcCxIvcm7RwkRaMTx1g.jpeg" alt="gradient descent" width="300">

<sub>Original image credited to towardsdatascience.com</sub>

- jupyter [notebook](https://blogd.org/blog/2024/05/31/deep-neural-network-for-image-classification)

```python
def L_layer_model(
        parameters = init_params(layers_dims: List[int]),
        X: np.ndarray,
        Y: np.ndarray,
        layers_dims: List[int],
        learning_rate: float = 0.0075,
        num_iterations: int = 3000)
    # RETURNS Updated `parameters` and `costs`
    -> Tuple[dict, List[float]]:
```


[↑ Back to top](#)
<br><br>


## Why Kubernetes?

- While docker and docker-compose <img src="https://i0.wp.com/codeblog.dotsandbrackets.com/wp-content/uploads/2016/10/compose-logo.jpg?w=27"> can be used for deploying a web application, it falls short in terms of scalability, load balancing, IaC support (Terraform, Helm), and seamless cloud-native integration.
- Kubernetes offers a rich set of APIs to address above challenges to manage Microservices.
- For local development, I chose <img src="https://blog.radwell.codes/wp-content/uploads/2021/05/minikube-logo-full.png" alt="minikube logo" width="75"> to align with Kuberentes best practices. This `consistency` ensures a smoother transition to <img src="https://diagrams.mingrammer.com/img/resources/aws/compute/elastic-kubernetes-service.png" alt="EKS logo" width="25"> EKS production.


| | docker-compose | Kubernetes
--|--|--
Scalability              | Limited to a Single host             | Multi-node scaling
Load Balancing           | Requires manual setup (e.g., HAProxy)| Support [Load Balancing](#load-balancing) in various ways
IaC Support | Resticted to docker compose cli | Terraform, Helm for fast and reliable resource provisioning (*< ~15 minutes*)


| <img src="https://imgur.com/qqDsoa2.png" alt="dc vs k8s" width="500"> |
| :--: |
|  *docker-compose vs. Kubernetes* |

[↑ Back to top](#)
<br><br>

### Scalability

Kubernetes offers orchestration of containerized applications across a cluster of nodes, ensuring scalability and high availability.


<img src="https://imgur.com/KxETYaG.png" alt="ingress" width="720">

#### Horizonal Pod Autoscaling

HPA control loop checks `CPU` and `Memory` usage via api-server's metric api  and scales accordingly.

<img src="https://imgur.com/rvtBRlL.png" alt="metric-server" width="500">


- Pre-requisite to implement HPA:
    - Install `metric-server` on the worker nodes (kube-system namespace) with helm!
        - → scrapes metrics from kublet
        - → publish to `metrics.k8s.io/v1beta` Kuberentes API
        - → consumed by HPA!
    - deployment.yaml: `spec.template.spec.containers[i].resources` must be specified.
    - deployment.yaml: `spec.replicas` is to be omitted.

<!-- - `Vertical Pod Autoscaling`: [LINK](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources) -->

- hpa.yaml
    - `spec.metrics[i].resource` to specify CPU and Memory threshold
    - `spec.scaleTargetRef.name` to identify the target
    - in order to enable HPA to work on another metrics, you need to define addtional component.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fe-nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fe-nginx-deployment
  minReplicas: 1
  maxReplicas: 1
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
    - Omit `spec.replica: xx` in order to use HPA functionality.

```yaml
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 100m
              memory: 256Mi
```

#### Metric server

<img src="https://imgur.com/7RHqdu8.png" alt="hpa" width="720">

#### HPA monitoring

<img src="https://imgur.com/1EiedmA.png" alt="hpa" width="720">



[↑ Back to top](#)
<br><br>


### Load Balancing

Kubernetes provides native support for load balancing and traffic routing through `Ingress`, `Ingress Controller`, and `AWS Load Balancer Controller`. I will be exploring two ways for exposing the Kuberentes application to the outside world:

- [`Nginx Ingress Controller`](#nginx-ingress-controller)
- [`AWS Load Balancer Controller`](#aws-load-balancer-controller)

#### Nginx Ingress Controller

Nginx Ingress Controller is a 3rd party implementation of Ingress controller.

- Install with Helm or kubectl. (in `ingress` namespace)
- it provisions `NLB` upon installation.
    - the Service of type LoadBalancer triggers the NLB creation during installation
- it monitors `Ingress` resource:
    - for each Ingress being created, it is converted to Nignx native `Lua` configuration and routes to the target service! The controller acts as a proxy and redirects traffic into services.
- Monitoring tools like `Prometheus` <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Prometheus_software_logo.svg" width=28> can scrape metrics (traffic, latency, errors for all Ingresses) from the nginx ingress controller pod without implementing anything on the Application side!
    <!-- - must specify `ingressClassName` as the name of Ingress Nginx controller. (helm installing using Terraform, specify same name as this)
    - When you create an Ingress resource with the specified ingressClassName, the NGINX Ingress Controller reads the Ingress rules and updates its configuration accordingly. -->
    <!-- - Traffic flow: `AWS NLB ->  Nginx ingress controller ->(Ingres Rule) Service -> Pod` -->
    <!-- - All the Ingresses use the same Load Balancer! COST and MAINTENANCE saved! -->

<img src="https://imgur.com/7QR1Wpn.png" alt="nginx-ingress-controller" width="480">


<img src="https://imgur.com/DwRBYMd.png" alt="EKS architecture" width="750">

<div align="center">*<b>NLB</b> with Nginx Ingress Controller*</div>


<img src="https://kubernetes.io/docs/images/ingress.svg" alt="ingress" width="520">

<sub>Original image credited to kubernetes.io</sub>

```sh
kubectl get ingressclass -A
# NAME            CONTROLLER            PARAMETERS  AGE
# alb             ingress.k8s.aws/alb   <none>      20m
# external-nginx  k8s.io/ingress-nginx  <none>      20m
```


| <img src="https://imgur.com/pSGCLP9.png" alt="ingress" width="720"> |
| :--: |


- Baremetal (To-be-tested)
    - [Link](https://kubernetes.github.io/ingress-nginx/deploy/baremetal)
    - A pure software solution: MetalLB
    - Over a NodePort Service

<img src="https://kubernetes.github.io/ingress-nginx/images/baremetal/baremetal_overview.jpg" alt="ingress" width="500">

<sub>Original image credited to kubernetes.github.io</sub>


#### AWS Load Balancer Controller

- The controller (in `kube-system` namespace) watches for Kubernetes Ingress or Service resources. In response, it creates the appropriate AWS Elastic Load Balancing resources. 
    - The LBC provisions `ALB` when you create an *Ingress*.
    - The LBC provisions `NLB` when you create a *Service* of type *LoadBalancer*.
    - ALB is slower than NLB and more expensive.


| <img src="https://imgur.com/UaF1vHK.png" alt="aws-lbc" width="520"> |
| :--: |
|  *AWS Load Balancer Controller - L4 or L7* |


| <img src="https://imgur.com/tg4GAzA.png" alt="EKS architecture" width="750"> |
| :--: |
| *<b>ALB</b> with AWS Load Balancer Controller* |



[↑ Back to top](#)
<br><br>


<!-- ### Cloud-Native Integration

Kubernetes natively supports cloud environments, enabling seamless integration with services like AWS. It allows for:

- Use of cloud-specific ingress controllers
- Automatic provisioning of cloud resources (e.g., load balancers)


[↑ Back to top](#)
<br><br> -->


## Skills used

- `Kubernetes`
    - AWS: EKS cluster with 3 worker nodes. Terraform to deploy EKS and AWS Load Balancer Controller and Ingress for exposing the app.
    - Local: 3-node cluster with [microk8s](https://microk8s.io/docs/getting-started).
- `Terraform` iac to create:
    - [`LINK`](https://blogd.org/blog/2024/07/01/eks-with-terraform-and-helm)
    - IAM Role and policy association with serviceaccount
    - Networks, EKS cluster, node group, addons
- `Helm Chart`
    - deploy application using templates
    - [`LINK`](https://blogd.org/blog/helm.pdf)
- `Docker` and `Dockerfile` for building images
- `Github Actions` for CI
    - Github repository -> Dockerhub image repository
- `Microservices Architecture`
    - Frontend : Nginx (with html, css, js)
    - Backend : Golang (go-gin), Python (uvicorn) as backend web server
- `Deep learning` algorithm for training and predicting Cat images using `numpy` and `pytorch` (in-progress)
- `Virtualbox` (with cli) to test configure 3 microk8s Kubernetes master nodes (ubuntu) in local environment
- `Golang Concurrency`
    - used context, channel, goroutine for concurrent programming


[↑ Back to top](#)
<br><br>


## Microservices

- Kubelet configures Pods' DNS so that running containers can lookup Services by name rather than IP.



| <img src="https://imgur.com/KxETYaG.png" alt="ingress" width="680"> |<img src="https://imgur.com/b69kvRA.png" alt="demo" width="300"> |
|--| --
| *applications diagram* |
    
- `Frontend - Nginx`
   - Nginx serves as the static content server, handling HTML, CSS, and JavaScript files.
   - It ensures efficient delivery of frontend resources to users' browsers.

- `Backend - Go-Gin web-server`
   - The Go-Gin server acts as an intermediary between the frontend and backend services.
   - It receives requests from the frontend, including requests for cat-related information.
   - Additionally, it performs utility functions, such as fetching weather data for three cities using goroutine concurrency (5-worker).
   - [main.go](https://github.com/jnuho/CatVsNonCat/blob/main/cmd/backend-web-server/main.go#L50)
   - [weatherapi.go](https://github.com/jnuho/CatVsNonCat/blob/main/pkg/weatherapi.go#L160)
     - Implemented with `Fan-out/Fan-in pattern`
     - Another possible pattern: [`Worker-pool pattern`](https://blogd.org/blog/2024/05/29/golang-worker-pool-pattern/)

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

**NOTE**: It is crucial to optimize Docker images to be as compact as possible. To achieve this is by utilizing base images that are minimalistic, such as the Alpine image and using [Multi-stage builds](#multi-stage-builds).

<!-- - [NOTE on defining backend endpoint in frontend](https://stackoverflow.com/a/56375180/23876187)
    - frontend app is not in any container, but the javascript is served from container as a js script file to <b>your browser</b>! -->

###  Multi-stage builds

- Reference [LINK](https://docs.docker.com/build/building/multi-stage)

```Dockerfile
# Use an golang alpine as the base image
FROM golang:1.22.3-alpine as build

# Set the temporary working directory in the container in the first stage
WORKDIR /

# # Copy package.json and package-lock.json into the working directory
COPY go.mod go.sum ./
COPY backend/web ./backend/web
COPY cmd/backend-web-server/main.go ./cmd/backend-web-server/main.go
COPY pkg ./pkg

# Copy the .env file into the working directory
COPY .env .env

# # Install the app dependencies inside the docker image
RUN go mod download && go mod verify

# Set GOARCH and GOOS for the build target
ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64

# # Define the command to run your app using CMD which defines your runtime
RUN go build -o backend-web-server ./cmd/backend-web-server

RUN rm -rf /var/cache/apk/* /tmp/*

# Use a smaller base image for the final image
FROM alpine:latest

# Copy the binary from the build stage
COPY --from=build /backend-web-server /usr/local/bin/backend-web-server

# Copy the .env file from the build stage
# put in root directory / becasuse running CMD "backend-web-server" is ru
COPY --from=build /.env /.env

EXPOSE 3001

# When you specify CMD ["go-app"], Docker looks for an executable named go-app in the system’s $PATH.
# The $PATH includes common directories where executables are stored, such as /usr/local/bin, /usr/bin, and others.
CMD ["backend-web-server", "-web-host=:3001"]
```

[↑ Back to top](#)
<br><br>


### minikube docker-env

- To point your shell to minikube's docker-daemon, run:
- Build docker images in local and minikube Pods can refer to it

```sh
eval $(minikube -p minikube docker-env)
```

- To Unset

```sh
# unset DOCKER_TLS_VERIFY
# unset DOCKER_HOST
# unset DOCKER_CERT_PATH
# unset MINIKUBE_ACTIVE_DOCKERD
eval $(minikube -p minikube docker-env --unset)
```

- Apply changes in local development
1. Edit file
2. build image - `./build-nginx.sh`
3. restart pod - `./rstart-nginx.sh`

[↑ Back to top](#)
<br><br>


## IaC

### Terraform

- [.gitignore practice](https://developer.hashicorp.com/terraform/language/style#gitignore)

- [terraform scripts](https://github.com/jnuho/CatVsNonCat/tree/main/script/terraform)
- VPC, Subnet, igw, nat, route table, etc.
- IAM role with assume-role-policy
    - attach the required Amazon EKS IAM managed policy to it.
- Attach AmazonEKSClusterPolicy policy to IAM role: `6-eks.tf`


- Download terraform.exe
    - Environment variable > Add Path: C:\Program Files\terraform_1.8.5_windows_amd64


```sh
# Navigate to your Terraform configuration directory
# cd path/to/your/terraform/configuration
cd terraform

# Initialize Terraform
terraform init

# Validate the configuration
terraform validate

# Format the Configuration
terraform fmt

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply

# With DEBUGGING enabled
TF_LOG=DEBUG terraform apply

# Destroy
# terraform destroy
```

- Check ingressClass

```sh
kubectl get ingressclass -A
# NAME            CONTROLLER            PARAMETERS  AGE
# alb             ingress.k8s.aws/alb   <none>      20m
# external-nginx  k8s.io/ingress-nginx  <none>      20m
```

| <img src="https://imgur.com/YpjRWc6.png" alt="pods" width="700"> |
|:--:| 
| *ingress resource* |

| <img src="https://imgur.com/Ymkj2PH.png" alt="pods" width="400"> |
|:--:| 
| *aws load-balancer controller pod in `kube-system` namespace* |


```sh
git clone https://github.com/jnuho/terraform-aws-vpc.git
cd terraform-aws-vpc
git add .
git commit -m 'create vpc module'
git tag 0.1.0
git push origin main --tags
```

### Helm Chart


- [helm chart scripts in repository](https://github.com/jnuho/CatVsNonCat/tree/main/script/tst-chart)

- Configure `kubectl`
    - Check context : `kubectl config current-context`
    - Update `.kube/config`

```sh
# TO LOCAL
kubectl config use-context minikube

# TO EKS
aws eks update-kubeconfig --region ap-northeast-2 --name my-cluster --profile terraform
```

- Install `helm` on the same client PC as `kubectl`

```sh
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

- Create

```sh
# Create helm chart
helm create tst-chart
```


- Validate

```sh
cd CatVsNonCat/script
tree
    tst-chart
       ├── Chart.yaml
       ├── charts
       ├── templates
       │   ├── _helpers.tpl
       │   ├── deployment.yaml
       │   ├── hpa.yaml
       │   ├── ingress.yaml
       │   └── service.yaml
       ├── values.dev.yaml
       ├── values.prd.AWS.L4.lbc.yaml
       ├── values.prd.AWS.L7.lbc.yaml
       └── values.prd.AWS.L4.ingress.controller.yaml

helm lint tst-chart
helm template tst-chart --debug
# check results without installation
# helm install --dry-run tst-chart --generate-name
helm install --dry-run tst-release ./tst-chart -f ./tst-chart/values.prd.AWS.L4.ingress.controller.yaml
```

- Install

```sh
helm install tst-release ./tst-chart -f ./tst-chart/values.prd.AWS.L4.ingress.controller.yaml
```

- Upgrade
    - Helm will perform a rolling update for the affected resources (e.g., Deployments, StatefulSets).
    - Pods are replaced one by one, ensuring zero-downtime during the update.
    - Helm manages this process transparently.
    - Edit `values.dev.yaml` and apply `helm upgrade` command

```yaml
kubectl patch deployment my-app --type='json' -p='[{"op":"replace","path":"/spec/replicas","value":5}]'

services: 
  - name: fe-nginx
    replicaCount: 3
```

```sh
helm list
    NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART              APP VERSION
    tst-release     default         1               2024-07-09 14:25:50.410043621 +0900 KST deployed        tst-chart-0.1.0    1.16.0

helm upgrade tst-release ./tst-chart -f ./tst-chart/values.prd.AWS.L4.ingress.controller.yaml
    Release "tst-release" has been upgraded. Happy Helming!
    NAME: tst-release
    LAST DEPLOYED: Tue Jul  9 14:35:35 2024
    NAMESPACE: default
    STATUS: deployed
    REVISION: 2
    TEST SUITE: None

helm list
    NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART              APP VERSION
    tst-release     default         2               2024-07-09 14:35:35.404055879 +0900 KST deployed        tst-chart-0.1.0    1.16.0
```

- Rollback

```sh
helm rollback tst-release VERSION_NO
```

- Uninstall (Helm v3)
    - `helm delete --purge` in Helm V2

```sh
helm uninstall tst-release
```

- Helm Repository
    - While you can deploy a Helm chart directly from the filesystem,
    - it’s recommended to use Helm repositories.
    - Helm repositories allow versioning, collaboration, and easy distribution of charts
    - [`LINK`](https://www.kubernet.dev/getting-started-with-helm-simplifying-kubernetes-application-deployments)


[↑ Back to top](#)
<br><br>


## ArgoCD


```sh
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm search repo argocd
helm show values argo/argo-cd --version 3.35.4 > argocd-defaults.yaml
# Edit variables and apply
vim argocd-defaults.yaml
kubectl apply -f argocd-defaults.yaml
```

- You can use Terraform as well.

```sh
# Use Terraform for equivalent command as the following:
# helm install argocd -n argocd --create-namespace argo/argo-cd --version 3.35.4 -f terraform/values/argocd.yaml
terraform apply

helm status argocd -n argocd
# check for failing install
helm list  --pending -A

helm list -A
k get pod -n argocd
k get secrets -n argocd
k get secrets argocd-intitial-admin-secret -o yaml -n argocd 
echo -n "PASSWORKDKDKD" | base64 -d

kubectl port-forward svc/argocd-server -n argocd 8080:80
    http://localhost:8080
    login with admin/password
```


- Create Git Repository for `yaml` and `helm` chart templates.

```sh
git clone new-repo
```

- Setup Dockerhub Account (and Create Repository only for private repo)

```sh
docker login --username jnuho
docker pull nginx:1.23.3

docker tag nginx:1.23.3 jnuho/nginx:v0.1.0
docker push jnuho/nginx:v0.1.0

# Write yaml/helm and push to repo
git add .
git commit -m 'add yaml/helm'
git push origin main
```

- Configure argocd to watch for Git Repo (yaml/helm)
    - Create `Application` CRDs for ArgoCD

```sh
kubectl apply -f script/argocd/application.yaml
```


- Workflow
    - docker tag
    - docker push
    - Edit deployment.yaml's image tag
        - git push to `cvn-yaml` Git Repo
    - Argocd detects in 5 minutes
        - manually `Sync` or
        - edit application.yaml to automatically `Sync`
    - Create `upgrade.sh`
        - Run: ./upgrade.sh v0.1.3



[↑ Back to top](#)
<br><br>


## TLS

Self-signed SSL/TLS Certificate vs. CA Certificate

The difference between a CA certificate and a self-signed certificate is the issuer of the certificate. 

[↑ Back to top](#)
<br><br>


## Kubernetes for MLOps


<img src="https://coffeewhale.com/assets/images/mlops/hidden-model.png" alt="pods" width="580">

<sub>Original image credited to papers.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf and coffeewhale.com</sub>

<img src="https://www.determined.ai/assets/images/blogs/kubernetes-bad/kubeflow-unicorns.png" alt="pods" width="480">

<sub>Original image credited to .determined.ai</sub>


- Challenges of Using Kubernetes-Based ML Tools
    - Containerizing Code (Docker Image Build and Execution):
    - Writing Kubernetes Manifests (YAML Files):

[↑ Back to top](#)
<br><br>


## Appendix

- [Appendix](https://blogd.org/blog/2024/01/01/catvsnoncat-appendix/)


### References

- [ingress-nginx doc 1](https://kubernetes.github.io/ingress-nginx/deploy)
- [ingress-nginx doc 2](https://docs.nginx.com/nginx-ingress-controller/overview/design/#the-nginx-ingress-controller-pod)


[↑ Back to top](#)
<br><br>
