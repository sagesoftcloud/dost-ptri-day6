# Lab 06 — Final: CI/CD + CloudFormation — Deploy to EC2 (Production-Like)

## Difficulty: ⭐⭐⭐ Final Challenge

## Objective

Combine everything from Day 6: use **CloudFormation** to provision the infrastructure (EC2 + IAM + Security Group), then use **CodePipeline** to automatically deploy your app to that EC2 instance. This is how production deployments work — infrastructure as code + automated delivery.

**The full picture:**

```
CloudFormation (provisions infra)     CodePipeline (deploys app)
─────────────────────────────────     ──────────────────────────
EC2 Instance                          GitHub → Build → Deploy
IAM Roles                                              ↓
Security Group                                    EC2 (live app)
CodeDeploy App + Deployment Group
```

**Time:** ~60 min

---

## Prerequisites

- Completed Labs 01–02 (you have a GitHub repo and understand pipelines)
- Completed Labs 03–05 (you understand CloudFormation)
- Region: **ap-southeast-1**

---

## Part A: Write the Infrastructure Template (20 min)

This single template provisions everything the pipeline needs to deploy to.

Create `cfn-ec2-deploy-infra.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 06 Final - EC2 infrastructure for CI/CD deployment'

Parameters:
  ProjectName:
    Type: String
    Default: dost-ptri-final

  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Existing EC2 key pair for SSH access

  InstanceType:
    Type: String
    Default: t2.micro
    AllowedValues:
      - t2.micro
      - t3.micro

Resources:
  # --- Security Group ---
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow HTTP (8080) and SSH
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
          Description: SSH - restrict to your IP in production
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0
          Description: Application port
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-sg

  # --- IAM Role for EC2 (CodeDeploy agent) ---
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub ${ProjectName}-ec2-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforAWSCodeDeploy
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref EC2Role

  # --- IAM Role for CodeDeploy service ---
  CodeDeployRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub ${ProjectName}-codedeploy-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: codedeploy.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole

  # --- EC2 Instance ---
  AppServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !FindInMap [RegionAMI, !Ref 'AWS::Region', AMI]
      KeyName: !Ref KeyPairName
      IamInstanceProfile: !Ref EC2InstanceProfile
      SecurityGroupIds:
        - !Ref AppSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-server
        - Key: DeployGroup
          Value: !Ref ProjectName
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          sudo yum update -y
          sudo yum install -y python3 python3-pip ruby wget
          sudo pip3 install flask
          # Install CodeDeploy Agent
          cd /home/ec2-user
          sudo wget https://aws-codedeploy-${AWS::Region}.s3.${AWS::Region}.amazonaws.com/latest/install
          sudo chmod +x ./install
          sudo ./install auto
          sudo systemctl start codedeploy-agent
          sudo systemctl enable codedeploy-agent

  # --- CodeDeploy Application ---
  CodeDeployApp:
    Type: AWS::CodeDeploy::Application
    Properties:
      ApplicationName: !Sub ${ProjectName}-app
      ComputePlatform: Server

  # --- CodeDeploy Deployment Group ---
  DeploymentGroup:
    Type: AWS::CodeDeploy::DeploymentGroup
    Properties:
      ApplicationName: !Ref CodeDeployApp
      DeploymentGroupName: !Sub ${ProjectName}-deploy-group
      ServiceRoleArn: !GetAtt CodeDeployRole.Arn
      DeploymentConfigName: CodeDeployDefault.AllAtOnce
      Ec2TagFilters:
        - Key: DeployGroup
          Value: !Ref ProjectName
          Type: KEY_AND_VALUE

Mappings:
  RegionAMI:
    ap-southeast-1:
      AMI: ami-0c1907b2b7c73d03c
    us-east-1:
      AMI: ami-0c02fb55956c7d316

Outputs:
  ServerPublicIP:
    Description: Public IP of the EC2 instance
    Value: !GetAtt AppServer.PublicIp

  ServerPublicDNS:
    Description: Public DNS of the EC2 instance
    Value: !GetAtt AppServer.PublicDnsName

  AppURL:
    Description: Application URL
    Value: !Sub http://${AppServer.PublicIp}:8080

  CodeDeployAppName:
    Description: CodeDeploy application name
    Value: !Ref CodeDeployApp

  DeploymentGroupName:
    Description: CodeDeploy deployment group name
    Value: !Sub ${ProjectName}-deploy-group

  SecurityGroupId:
    Value: !Ref AppSecurityGroup
```

### What this template creates:

| Resource | Purpose |
|----------|---------|
| Security Group | Opens port 22 (SSH) and 8080 (app) |
| IAM Role (EC2) | Allows EC2 to talk to CodeDeploy + SSM |
| Instance Profile | Attaches role to EC2 |
| IAM Role (CodeDeploy) | Allows CodeDeploy service to manage deployments |
| EC2 Instance | Your app server with CodeDeploy agent installed |
| CodeDeploy Application | The deployment target definition |
| Deployment Group | Links CodeDeploy to your EC2 (via tag) |

---

## Part B: Deploy the Infrastructure (10 min)

### B1. Create a Key Pair first

1. Go to **EC2 Console** → **Key Pairs** → **Create key pair**
2. Name: `dost-ptri-final-key`
3. Type: RSA, Format: `.pem`
4. Download and save it

### B2. Deploy the CloudFormation stack

1. **CloudFormation Console** → **Create stack** → Upload `cfn-ec2-deploy-infra.yaml`
2. Fill in:
   - Stack name: `day6-final-YOURNAME`
   - ProjectName: `dost-ptri-final`
   - KeyPairName: Select `dost-ptri-final-key`
   - InstanceType: `t2.micro`
3. ⚠️ Check "I acknowledge that CloudFormation might create IAM resources with custom names"
4. Submit → wait for `CREATE_COMPLETE` (~3 min)

### B3. Verify

- Check **Outputs** tab → note the `AppURL` and `CodeDeployAppName`
- Go to **EC2 Console** → instance is running ✅
- Go to **CodeDeploy** → application and deployment group exist ✅

### B4. Wait for CodeDeploy agent

The EC2 UserData script takes ~2 minutes to install everything. Wait before proceeding.

SSH in to verify (optional):

```bash
chmod 400 dost-ptri-final-key.pem
ssh -i dost-ptri-final-key.pem ec2-user@YOUR-PUBLIC-IP
sudo systemctl status codedeploy-agent
```

Should show: `active (running)` ✅

---

## Part C: Create the Pipeline (15 min)

### C1. Create CodeBuild Project

1. **CodeBuild** → **Create build project**

**Project configuration:**

| Setting | Value |
|---------|-------|
| Project name | `dost-ptri-final-build` |
| Project type | **Default project** |

**Source:**

| Setting | Value |
|---------|-------|
| Source provider | **GitHub** |

2. You'll see: *"You have not connected to GitHub. Manage account credentials."*
   - Click **Manage account credentials**
   - **Manage default source credential** dialog:
     - Source Provider: **GitHub**
     - Credential type: **GitHub App**
     - Connection: Click **Create a new GitHub connection**
     - Connection name: `dost-ptri-github`
     - Click **Connect to GitHub** → Authorize → Select account → Only select repositories → `dost-ptri-day6-cicd` → Install & Authorize
     - Back in AWS → **Connect** → Status: **Available** ✅ → **Save**

3. You'll see: *"Your account is successfully connected by using an AWS managed GitHub App."*

| Setting | Value |
|---------|-------|
| Connection | Select your connection ARN |
| Repository | **Repository in my GitHub account** → `dost-ptri-day6-cicd` |
| Source version | Leave blank |
| Webhook | ❌ **UNCHECK** "Rebuild every time a code change is pushed" |
| Build type | **Single build** |

> ⚠️ Leave webhook unchecked or you'll get "Failed to create webhook" error.

**Environment:**

| Setting | Value |
|---------|-------|
| Provisioning model | **On-demand** |
| Environment image | **Managed image** |
| Compute | **EC2** |
| Running mode | **Container** |
| Operating system | **Amazon Linux** |
| Runtime | **Standard** |
| Image | `aws/codebuild/amazonlinux-x86_64-standard:6.0` |
| Service role | **New service role** |

**Buildspec:**

| Setting | Value |
|---------|-------|
| Build specifications | **Use a buildspec file** |

**Artifacts:**

| Setting | Value |
|---------|-------|
| Type | **No artifacts** |

4. Click **Create build project**

### C2. Create CodePipeline

1. **CodePipeline** → **Create pipeline**

**Step 1: Choose creation option**
- Category: **Build custom pipeline** → **Next**

**Step 2: Choose pipeline settings**
- Pipeline name: `dost-ptri-final-pipeline`
- Execution mode: **Superseded**
- Service role: **New service role**
- Click **Next**

**Step 3: Add source stage**
- Source provider: **GitHub (Version 2)**
- Connection: Select `dost-ptri-github`
- Repository: your `dost-ptri-day6-cicd` repo
- Branch: `main`
- Click **Next**

**Step 4: Add build stage**
- Click **Other build providers** (not "Commands")
- Provider: **AWS CodeBuild**
- Region: **Asia Pacific (Singapore)**
- Project name: `dost-ptri-final-build`
- Click **Next**

**Step 5: Add test stage**
- Click **Skip test stage** → Confirm

**Step 6: Add deploy stage**
- Deploy provider: **AWS CodeDeploy**
- Region: **Asia Pacific (Singapore)**
- Application name: `dost-ptri-final-app`
- Deployment group: `dost-ptri-final-deploy-group`
- Click **Next**

**Step 7: Review**
- Review all stages → **Create pipeline**

---

## Part D: Watch the Full Flow (10 min)

Pipeline triggers automatically:

```
Source ✅ → Build ✅ → Deploy ✅
```

### What happens on the EC2 during Deploy:

1. CodeDeploy agent receives deployment
2. Runs `stop_server.sh` → kills old app
3. Copies files to `/opt/dost-ptri-app`
4. Runs `install_dependencies.sh` → `pip install flask`
5. Runs `start_server.sh` → starts app on port 8080
6. Runs `validate_service.sh` → curls `/health` → confirms success

### Test your live app:

```bash
curl http://YOUR-EC2-IP:8080/
```

```json
{"message": "DOST PTRI Day 6 — CI/CD Sample App", "status": "running"}
```

```bash
curl http://YOUR-EC2-IP:8080/health
```

```json
{"status": "healthy"}
```

---

## Part E: Push a Change — Full Cycle (5 min)

```bash
# Edit app.py — add endpoint
# (add this to app.py)
# @app.route("/deployed-by")
# def deployed_by():
#     return jsonify({"method": "CloudFormation + CodePipeline", "lab": "Final"})

git add app.py
git commit -m "feat: add deployed-by endpoint"
git push
```

Watch pipeline → all green → test:

```bash
curl http://YOUR-EC2-IP:8080/deployed-by
```

```json
{"method": "CloudFormation + CodePipeline", "lab": "Final"}
```

---

## Summary: What You Built

```
┌─────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE (CloudFormation)            │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐ │
│  │ Security │  │ IAM Roles│  │    EC2    │  │ CodeDeploy│ │
│  │  Group   │  │ (2 roles)│  │  Instance │  │  App +    │ │
│  │ 22+8080  │  │          │  │  + Agent  │  │  Group    │ │
│  └──────────┘  └──────────┘  └───────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    DELIVERY (CodePipeline)                    │
│                                                              │
│  GitHub ──→ CodeBuild ──→ CodeDeploy ──→ EC2 (live app)     │
│  (push)     (test)        (deploy)       (running)          │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Tool | What it does |
|-------|------|-------------|
| Infrastructure provisioning | CloudFormation | Creates EC2, IAM, SG, CodeDeploy — repeatable, deletable |
| Source control | GitHub | Stores code, triggers pipeline |
| Build & test | CodeBuild | Runs tests, packages app |
| Deployment | CodeDeploy | Ships code to EC2, runs lifecycle scripts |
| Orchestration | CodePipeline | Connects all stages automatically |

---

## Clean Up

1. **Delete the pipeline** → CodePipeline → Delete
2. **Delete CodeBuild project** → CodeBuild → Delete
3. **Delete the CloudFormation stack** → this removes EC2, IAM roles, SG, CodeDeploy app — everything
4. **Delete S3 artifact bucket** (created by pipeline) → empty then delete
5. **Delete GitHub connection** → CodePipeline → Settings → Connections → Delete `dost-ptri-github`

> 💡 Because we used CloudFormation, most cleanup is just deleting one stack.

---

## ✅ Final Lab Complete!

You've demonstrated a **production-level deployment workflow**:

- ✅ Infrastructure defined as code (CloudFormation)
- ✅ Server provisioned automatically with all dependencies
- ✅ CI/CD pipeline deploys on every push
- ✅ Health checks validate each deployment
- ✅ One-click teardown of everything

**This is how real companies deploy software on AWS.**

---

**← [Back to Lab Overview](./README.md)**
