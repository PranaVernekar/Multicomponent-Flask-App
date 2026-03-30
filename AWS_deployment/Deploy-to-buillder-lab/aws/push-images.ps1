param(
    [Parameter(Mandatory = $true)]
    [string]$Region,
    [Parameter(Mandatory = $true)]
    [string]$AccountId,
    [Parameter(Mandatory = $false)]
    [string]$ImageTag = "v1"
)

$ErrorActionPreference = "Stop"

$GatewayRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-gateway"
$InvsysRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/flask-app-invsys"
$Registry = "$AccountId.dkr.ecr.$Region.amazonaws.com"

aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $Registry

docker build -t "${GatewayRepo}:$ImageTag" .\gateway
docker push "${GatewayRepo}:$ImageTag"

docker build -t "${InvsysRepo}:$ImageTag" .\invsys
docker push "${InvsysRepo}:$ImageTag"
