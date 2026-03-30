# Deploy Flask Microservices to AWS ECS

This guide explains how to deploy the two-service Flask application in this project to AWS using Amazon ECS.

Services in this project:

- `gateway`: public entrypoint running on port `5001`
- `invsys`: internal inventory API running on port `5000`

AWS services used:

- Amazon ECR for container images
- Amazon ECS for running containers
- Application Load Balancer for public access to `gateway`
- CloudWatch Logs for container logs
- Cloud Map or ECS Service Connect for internal service discovery

## Project structure

Relevant deployment files:

- `AWS_deployment/Deploy-to-buillder-lab/gateway`
- `AWS_deployment/Deploy-to-buillder-lab/invsys`
- `AWS_deployment/Deploy-to-buillder-lab/aws/gateway-task-definition.json`
- `AWS_deployment/Deploy-to-buillder-lab/aws/invsys-task-definition.json`
- `AWS_deployment/Deploy-to-buillder-lab/aws/push-images.ps1`

## Step 1: Open the deployment folder

Run all commands from:

```powershell
cd "C:\Users\verne\PycharmProjects\(AWS) Building a multicomponent Flask app\AWS_deployment\Deploy-to-buillder-lab"
```

## Step 2: Configure AWS variables

Set your AWS values in PowerShell:

```powershell
$Region = "us-east-1"
$AccountId = "123456789012"
$ImageTag = "v1"
$ClusterName = "flask-app-cluster"
$GatewayRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-gateway"
$InvsysRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-invsys"
$ExecutionRoleArn = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
$TaskRoleArn = "arn:aws:iam::123456789012:role/flaskAppTaskRole"
```

## Step 3: Create ECR repositories

Create one repository for each service:

```powershell
aws ecr create-repository --repository-name flask-app-gateway --region $Region
aws ecr create-repository --repository-name flask-app-invsys --region $Region
```

## Step 4: Authenticate Docker with ECR

```powershell
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"
```

## Step 5: Build and push the images

Use the helper script already included in the repo:

```powershell
.\aws\push-images.ps1 -Region $Region -AccountId $AccountId -ImageTag $ImageTag
```

Manual commands if needed:

```powershell
docker build -t "${GatewayRepo}:$ImageTag" .\gateway
docker push "${GatewayRepo}:$ImageTag"

docker build -t "${InvsysRepo}:$ImageTag" .\invsys
docker push "${InvsysRepo}:$ImageTag"
```

## Step 6: Create CloudWatch log groups

Create log groups for both ECS tasks:

```powershell
aws logs create-log-group --log-group-name /ecs/flask-app-gateway --region $Region
aws logs create-log-group --log-group-name /ecs/flask-app-invsys --region $Region
```

## Step 7: Create an ECS cluster

If you do not already have a cluster:

```powershell
aws ecs create-cluster --cluster-name $ClusterName --region $Region
```

## Step 8: Prepare service discovery

The `gateway` container needs an internal URL for `invsys`.

Recommended internal DNS name:

```text
http://invsys.services.local:5000
```

This requires either:

- AWS Cloud Map namespace `services.local`, or
- ECS Service Connect with matching service name

## Step 9: Update the ECS task definition files

Edit these files:

- `aws/invsys-task-definition.json`
- `aws/gateway-task-definition.json`

Replace these placeholders:

- `ACCOUNT_ID`
- `AWS_REGION`
- `IMAGE_TAG`
- `ECS_TASK_EXECUTION_ROLE_ARN`
- `ECS_TASK_ROLE_ARN`

In the gateway task definition, also set:

```json
{
  "name": "INVSYS_BASE_URL",
  "value": "http://invsys.services.local:5000"
}
```

Example image value:

```json
"image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/flask-app-gateway:v1"
```

## Step 10: Register the ECS task definitions

```powershell
aws ecs register-task-definition --cli-input-json file://aws/invsys-task-definition.json --region $Region
aws ecs register-task-definition --cli-input-json file://aws/gateway-task-definition.json --region $Region
```

## Step 11: Create the load balancer for the gateway

Create an ALB target group for the gateway service. The health check path should be:

```text
/health
```

The gateway container listens on:

```text
5001
```

If using the AWS Console:

1. Create an Application Load Balancer.
2. Create a target group using IP targets.
3. Set protocol to HTTP.
4. Set port to `5001`.
5. Set health check path to `/health`.
6. Attach the target group to the ALB listener.

## Step 12: Create the ECS services

Create `invsys` first, then `gateway`.

### Create the `invsys` service

Recommended settings:

- no public load balancer
- internal-only networking
- service discovery name `invsys`
- container port `5000`

Example CLI shape:

```powershell
aws ecs create-service `
  --cluster $ClusterName `
  --service-name flask-app-invsys `
  --task-definition flask-app-invsys `
  --desired-count 1 `
  --launch-type EC2 `
  --region $Region
```

### Create the `gateway` service

Recommended settings:

- attach to the ALB target group
- container name `gateway`
- container port `5001`
- desired count `1`

Example CLI shape:

```powershell
aws ecs create-service `
  --cluster $ClusterName `
  --service-name flask-app-gateway `
  --task-definition flask-app-gateway `
  --desired-count 1 `
  --launch-type EC2 `
  --region $Region
```

Note:
Add your VPC, subnet, security group, and load balancer settings according to your AWS lab environment.

## Step 13: Verify the deployment

Once the ECS services are stable, test the ALB DNS name:

```text
http://<alb-dns>/
http://<alb-dns>/health
http://<alb-dns>/items
```

Expected results:

- `/` returns the gateway welcome response
- `/health` returns status JSON
- `/items` returns inventory data from the internal API through the gateway

## Step 14: Useful AWS CLI checks

Check ECS clusters:

```powershell
aws ecs list-clusters --region $Region
```

Check services:

```powershell
aws ecs list-services --cluster $ClusterName --region $Region
```

Describe tasks:

```powershell
aws ecs list-tasks --cluster $ClusterName --region $Region
aws ecs describe-tasks --cluster $ClusterName --tasks <task-arn> --region $Region
```

Check logs:

```powershell
aws logs describe-log-groups --region $Region
aws logs tail /ecs/flask-app-gateway --follow --region $Region
aws logs tail /ecs/flask-app-invsys --follow --region $Region
```

## Troubleshooting

If `gateway` is healthy but `/items` fails:

- check `INVSYS_BASE_URL`
- check service discovery configuration
- check security groups between ECS tasks

If ECS cannot pull images:

- check that the image exists in ECR
- check the execution role permissions
- check the region in the image URI

If the ALB target stays unhealthy:

- confirm the target group uses port `5001`
- confirm the gateway exposes `/health`
- confirm the ALB can reach the ECS task security group

## Deployment summary

The overall workflow is:

1. Build Docker images
2. Push images to ECR
3. Register ECS task definitions
4. Create the `invsys` ECS service
5. Create the `gateway` ECS service
6. Attach the gateway to an ALB
7. Verify application access through the ALB
