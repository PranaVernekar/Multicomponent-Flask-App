# AWS ECS deployment runbook

This folder contains a minimal ECS deployment setup for the two services in this task:

- `gateway`: public-facing Flask gateway on port `5001`
- `invsys`: internal inventory API on port `5000`

## 1. Prerequisites

- AWS CLI configured against your lab account
- Docker Desktop running locally
- An ECR repository for each image:
  - `flask-app-gateway`
  - `flask-app-invsys`
- An ECS cluster
- An ALB target group for the gateway service
- A Cloud Map namespace or ECS Service Connect name for the internal `invsys` service

## 2. Build and push images

Set these variables in PowerShell and replace the placeholders:

```powershell
$Region = "us-east-1"
$AccountId = "123456789012"
$GatewayRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-gateway"
$InvsysRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-invsys"
$ImageTag = "v1"
```

Authenticate Docker to ECR:

```powershell
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"
```

Build and push the gateway image:

```powershell
docker build -t "${GatewayRepo}:$ImageTag" .\gateway
docker push "${GatewayRepo}:$ImageTag"
```

Build and push the inventory image:

```powershell
docker build -t "${InvsysRepo}:$ImageTag" .\invsys
docker push "${InvsysRepo}:$ImageTag"
```

## 3. Register task definitions

Update both JSON files in this folder before registering them:

- replace `ACCOUNT_ID`
- replace `AWS_REGION`
- replace `IMAGE_TAG`
- replace `ECS_TASK_EXECUTION_ROLE_ARN`
- replace `ECS_TASK_ROLE_ARN`
- for the gateway, set `INVSYS_BASE_URL` to your internal ECS DNS name

Example internal URL when using Cloud Map:

```text
http://invsys.services.local:5000
```

Register the task definitions:

```powershell
aws ecs register-task-definition --cli-input-json file://aws/invsys-task-definition.json --region $Region
aws ecs register-task-definition --cli-input-json file://aws/gateway-task-definition.json --region $Region
```

## 4. Create ECS services

Recommended layout:

- `invsys` ECS service:
  - internal only
  - no public load balancer
  - service discovery name `invsys`
  - health check path `/health`
- `gateway` ECS service:
  - attached to the ALB target group
  - listener forwards HTTP traffic to container port `5001`
  - health check path `/health`

Create the `invsys` service first, then the `gateway` service.

## 5. Verify deployment

After both ECS services are stable:

- open the ALB DNS name in a browser and confirm `/` responds
- call `http://<alb-dns>/health`
- call `http://<alb-dns>/items`

If `/items` fails while `/health` works on the gateway, the usual cause is an incorrect `INVSYS_BASE_URL` value or missing ECS service discovery.
