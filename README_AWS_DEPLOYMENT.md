# AWS ECS Deployment README

This document explains how to deploy the Flask microservices application in this project to AWS ECS.

Application services:

- `gateway`: public-facing Flask service on port `5001`
- `invsys`: internal inventory API on port `5000`

AWS services used:

- Amazon ECR
- Amazon ECS
- Application Load Balancer
- CloudWatch Logs
- Cloud Map or ECS Service Connect

## Step 1: Go to the deployment folder

```powershell
cd "C:\Users\verne\PycharmProjects\(AWS) Building a multicomponent Flask app\AWS_deployment\Deploy-to-buillder-lab"
```

## Step 2: Set AWS variables

```powershell
$Region = "us-east-1"
$AccountId = "123456789012"
$ImageTag = "v1"
$ClusterName = "flask-app-cluster"
$GatewayRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-gateway"
$InvsysRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-invsys"
```

## Step 3: Create ECR repositories

```powershell
aws ecr create-repository --repository-name flask-app-gateway --region $Region
aws ecr create-repository --repository-name flask-app-invsys --region $Region
```

## Step 4: Login to ECR

```powershell
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"
```

## Step 5: Build and push Docker images

Use the included script:

```powershell
.\aws\push-images.ps1 -Region $Region -AccountId $AccountId -ImageTag $ImageTag
```

Or run manually:

```powershell
docker build -t "${GatewayRepo}:$ImageTag" .\gateway
docker push "${GatewayRepo}:$ImageTag"

docker build -t "${InvsysRepo}:$ImageTag" .\invsys
docker push "${InvsysRepo}:$ImageTag"
```

## Step 6: Create CloudWatch log groups

```powershell
aws logs create-log-group --log-group-name /ecs/flask-app-gateway --region $Region
aws logs create-log-group --log-group-name /ecs/flask-app-invsys --region $Region
```

## Step 7: Create ECS cluster

```powershell
aws ecs create-cluster --cluster-name $ClusterName --region $Region
```

## Step 8: Configure internal service discovery

The `gateway` service should call:

```text
http://invsys.services.local:5000
```

Set this up using Cloud Map or ECS Service Connect.

## Step 9: Update task definition files

Files:

- `AWS_deployment/Deploy-to-buillder-lab/aws/gateway-task-definition.json`
- `AWS_deployment/Deploy-to-buillder-lab/aws/invsys-task-definition.json`

Replace these placeholders:

- `ACCOUNT_ID`
- `AWS_REGION`
- `IMAGE_TAG`
- `ECS_TASK_EXECUTION_ROLE_ARN`
- `ECS_TASK_ROLE_ARN`

In the gateway task definition, set:

```json
{
  "name": "INVSYS_BASE_URL",
  "value": "http://invsys.services.local:5000"
}
```

## Step 10: Register task definitions

```powershell
aws ecs register-task-definition --cli-input-json file://aws/invsys-task-definition.json --region $Region
aws ecs register-task-definition --cli-input-json file://aws/gateway-task-definition.json --region $Region
```

## Step 11: Create the ALB

Create an Application Load Balancer for the `gateway` service.

Use:

- target type: `ip`
- protocol: `HTTP`
- target port: `5001`
- health check path: `/health`

## Step 12: Create ECS services

Create `invsys` first, then `gateway`.

Example:

```powershell
aws ecs create-service `
  --cluster $ClusterName `
  --service-name flask-app-invsys `
  --task-definition flask-app-invsys `
  --desired-count 1 `
  --launch-type EC2 `
  --region $Region
```

```powershell
aws ecs create-service `
  --cluster $ClusterName `
  --service-name flask-app-gateway `
  --task-definition flask-app-gateway `
  --desired-count 1 `
  --launch-type EC2 `
  --region $Region
```

Add your actual subnet, security group, load balancer, and service discovery settings based on your AWS environment.

## Step 13: Verify deployment

Test:

```text
http://<alb-dns>/
http://<alb-dns>/health
http://<alb-dns>/items
```

Expected:

- `/` returns gateway response
- `/health` returns healthy JSON
- `/items` returns inventory data through the gateway

## Troubleshooting

If `/items` fails:

- verify `INVSYS_BASE_URL`
- verify service discovery
- verify security groups

If image pull fails:

- verify ECR repo and tag
- verify execution role permissions
- verify AWS region

If ALB health checks fail:

- verify target port `5001`
- verify `/health` endpoint
- verify network access from ALB to ECS tasks
