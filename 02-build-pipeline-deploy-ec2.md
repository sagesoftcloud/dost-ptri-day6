# Lab 02 — Build a CI/CD Pipeline that Deploys to EC2

## Objective

Build a complete, production-like CI/CD pipeline: push code to GitHub → CodeBuild tests it → CodeDeploy ships it to a real EC2 instance. This is how real-world deployments work.

**What you'll build:**

```
GitHub → CodePipeline → CodeBuild (test) → CodeDeploy → EC2 (live app)
```

**Time:** ~60 min

---

## Prerequisites

- Completed Lab 01 (your GitHub repo with the sample app)
- AWS Console access with AdministratorAccess
- Region: **ap-southeast-1** (Singapore)

---

## Part A: Launch an EC2 Instance (15 min)

You need a real server to deploy to.

### A1. Create an IAM Role for EC2

CodeDeploy needs the EC2 instance to have an agent that communicates with AWS.

1. Go to **IAM Console** → **Roles** → **Create role**
2. Trusted entity: **AWS service** → **EC2**
3. Add permissions:
   - Search and select: `AmazonEC2RoleforAWSCodeDeploy`
   - Search and select: `AmazonSSMManagedInstanceCore`
4. Role name: `dost-ptri-ec2-codedeploy-role`
5. Click **Create role**

### A2. Launch the EC2 Instance

1. Go to **EC2 Console** → **Launch instance**
2. Configure:

| Setting | Value |
|---------|-------|
| Name | `dost-ptri-day6-app-server` |
| AMI | **Amazon Linux 2023** |
| Instance type | `t2.micro` (free tier) |
| Key pair | Create new → `dost-ptri-day6-key` → Download |
| Network | Default VPC, public subnet |
| Auto-assign public IP | **Enable** |
| Security group | Create new: `dost-ptri-day6-sg` |
| Inbound rules | SSH (22) from **My IP**, HTTP (8080) from Anywhere |
| IAM instance profile | Select `dost-ptri-ec2-codedeploy-role` |

3. Under **Advanced details** → **User data**, paste:

```bash
#!/bin/bash
sudo yum update -y
sudo yum install -y python3 python3-pip ruby wget
sudo pip3 install flask

# Install CodeDeploy Agent
cd /home/ec2-user
sudo wget https://aws-codedeploy-ap-southeast-1.s3.ap-southeast-1.amazonaws.com/latest/install
sudo chmod +x ./install
sudo ./install auto
sudo systemctl start codedeploy-agent
sudo systemctl enable codedeploy-agent
```

4. Click **Launch instance**
5. Wait for instance state: **Running** ✅
6. Note the **Public IPv4 address** — you'll need it later

### A3. Add a Tag for CodeDeploy

1. Select your instance → **Tags** tab → **Manage tags**
2. Add tag:
   - Key: `DeployGroup`
   - Value: `dost-ptri-day6`
3. Save

> 💡 CodeDeploy uses this tag to find which instances to deploy to.

---

## Part B: Create CodeDeploy Application (10 min)

### B1. Create IAM Role for CodeDeploy Service

1. Go to **IAM** → **Roles** → **Create role**
2. Trusted entity: **AWS service** → **CodeDeploy**
3. Use case: **CodeDeploy**
4. Permission auto-selected: `AWSCodeDeployRole`
5. Role name: `dost-ptri-codedeploy-service-role`
6. Click **Create role**

### B2. Create the CodeDeploy Application

1. Go to **CodeDeploy Console** → **Applications** → **Create application**
2. Application name: `dost-ptri-day6-app`
3. Compute platform: **EC2/On-premises**
4. Click **Create application**

### B3. Create a Deployment Group

1. Inside your application → **Create deployment group**
2. Configure:

| Setting | Value |
|---------|-------|
| Deployment group name | `dost-ptri-day6-deploy-group` |
| Service role | Select `dost-ptri-codedeploy-service-role` |
| Deployment type | **In-place** |
| Environment configuration | **Amazon EC2 instances** |
| Tag group: Key | `DeployGroup` |
| Tag group: Value | `dost-ptri-day6` |
| Agent configuration | **Now and schedule updates** |
| Deployment settings | `CodeDeployDefault.AllAtOnce` |
| Load balancer | ❌ Uncheck "Enable load balancing" |

3. Click **Create deployment group**

---

## Part C: Create the Pipeline (15 min)

### C1. Create CodeBuild Project

1. Go to **CodeBuild** → **Create build project**

**Project configuration:**

| Setting | Value |
|---------|-------|
| Project name | `dost-ptri-day6-build` |
| Project type | **Default project** |

**Source:**

| Setting | Value |
|---------|-------|
| Source provider | **GitHub** |

2. You'll see: *"You have not connected to GitHub. Manage account credentials."*
   - Click **Manage account credentials**
   - **Manage default source credential** dialog appears:
     - Source Provider: **GitHub**
     - Credential type: **GitHub App**
     - Connection: Click **Create a new GitHub connection**
     - Connection name: `dost-ptri-github`
     - Click **Connect to GitHub**
     - A popup opens → Click **Authorize AWS Connector for GitHub**
     - Select your GitHub account
     - Choose **Only select repositories** → select `dost-ptri-day6-cicd`
     - Click **Install & Authorize**
     - Back in AWS → Click **Connect**
     - Status shows **Available** ✅ → Click **Save**

3. You'll now see: *"Your account is successfully connected by using an AWS managed GitHub App."*

| Setting | Value |
|---------|-------|
| Connection | Select your connection ARN from the dropdown |
| Repository | **Repository in my GitHub account** |
| Repository | Select `dost-ptri-day6-cicd` |
| Source version | Leave blank |

**Primary source webhook events:**

| Setting | Value |
|---------|-------|
| Webhook | ❌ **UNCHECK** "Rebuild every time a code change is pushed to this repository" |
| Build type | **Single build** |

> ⚠️ If you leave webhook checked, you'll get an error: "Failed to create webhook." Uncheck it — the pipeline will handle triggers instead.

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
| Image version | **Always use the latest image** |
| Service role | **New service role** |

**Buildspec:**

| Setting | Value |
|---------|-------|
| Build specifications | **Use a buildspec file** |

**Artifacts:**

| Setting | Value |
|---------|-------|
| Type | **No artifacts** |

**Logs:**

| Setting | Value |
|---------|-------|
| CloudWatch logs | ✅ Checked (default) |

4. Click **Create build project**

### C2. Create CodePipeline

1. Go to **CodePipeline** → **Create pipeline**

**Step 1: Choose creation option**

| Setting | Value |
|---------|-------|
| Category | **Build custom pipeline** |

2. Click **Next**

**Step 2: Choose pipeline settings**

| Setting | Value |
|---------|-------|
| Pipeline name | `dost-ptri-day6-pipeline` |
| Execution mode | **Superseded** |
| Service role | **New service role** |

3. Click **Next**

**Step 3: Add source stage**

| Setting | Value |
|---------|-------|
| Source provider | **GitHub (Version 2)** |
| Connection | Select `dost-ptri-github` (created earlier in CodeBuild) |
| Repository name | Your `dost-ptri-day6-cicd` repo |
| Branch name | `main` |
| Trigger | **Push to branch** |

4. Click **Next**

**Step 4: Add build stage**

| Setting | Value |
|---------|-------|
| Build provider | Click **Other build providers** |
| Provider | **AWS CodeBuild** |
| Region | **Asia Pacific (Singapore)** |
| Project name | `dost-ptri-day6-build` |
| Build type | **Single build** |
| Input artifacts | `SourceArtifact` |

> ⚠️ The default is "Commands" (inline shell). Click **Other build providers** to select your CodeBuild project.

5. Click **Next**

**Step 5: Add test stage (optional)**

6. Click **Skip test stage** → Confirm skip

**Step 6: Add deploy stage**

| Setting | Value |
|---------|-------|
| Deploy provider | **AWS CodeDeploy** |
| Region | **Asia Pacific (Singapore)** |
| Application name | `dost-ptri-day6-app` |
| Deployment group | `dost-ptri-day6-deploy-group` |

7. Click **Next**

**Step 7: Review**

8. Review all stages → Click **Create pipeline**

---

## Part D: Watch the Full Deployment (10 min)

The pipeline triggers immediately after creation.

### Watch each stage:

1. **Source** ✅ — pulls code from GitHub
2. **Build** ✅ — CodeBuild runs `buildspec.yml`:
   - Installs dependencies
   - Runs `pytest` (2 tests pass)
   - Packages app into ZIP
3. **Deploy** ✅ — CodeDeploy runs `appspec.yml` on your EC2:
   - `stop_server.sh` — stops old app
   - Copies files to `/opt/dost-ptri-app`
   - `install_dependencies.sh` — installs Flask
   - `start_server.sh` — starts the app
   - `validate_service.sh` — curls `/health` to confirm

### Test the live app:

```bash
curl http://YOUR-EC2-PUBLIC-IP:8080/
```

Response:
```json
{"message": "DOST PTRI Day 6 — CI/CD Sample App", "status": "running"}
```

```bash
curl http://YOUR-EC2-PUBLIC-IP:8080/health
```

Response:
```json
{"status": "healthy"}
```

> 🎉 **Your app is live on EC2, deployed automatically via CI/CD!**

---

## Part E: Push a Change — See Auto-Deploy (10 min)

### Edit `app.py` locally — add a version endpoint:

```python
@app.route("/version")
def version():
    return jsonify({"version": "2.0.0", "deployed_by": "CodeDeploy"})
```

### Push to GitHub:

```bash
git add app.py
git commit -m "feat: add version endpoint"
git push
```

### Watch the pipeline:

1. Source ✅ → Build ✅ → Deploy ✅
2. Test:

```bash
curl http://YOUR-EC2-PUBLIC-IP:8080/version
```

```json
{"version": "2.0.0", "deployed_by": "CodeDeploy"}
```

**Zero manual intervention. Push code → live on server. That's CI/CD.**

---

## What's Happening Behind the Scenes

```
┌─────────┐     ┌──────────────┐     ┌───────────┐     ┌────────────┐     ┌─────┐
│  You    │────→│  GitHub      │────→│CodePipeline│────→│ CodeBuild  │────→│Code │
│git push │     │  (webhook)   │     │(orchestrate)│    │(build+test)│     │Deploy│
└─────────┘     └──────────────┘     └───────────┘     └───────────┘     └──┬──┘
                                                                              │
                                                                              ↓
                                                                     ┌──────────────┐
                                                                     │   EC2 Server  │
                                                                     │──────────────│
                                                                     │ 1. Stop old   │
                                                                     │ 2. Copy files  │
                                                                     │ 3. Install deps│
                                                                     │ 4. Start app   │
                                                                     │ 5. Health check│
                                                                     └──────────────┘
```

### The scripts in action:

| Script | What it does on EC2 | Why it matters |
|--------|--------------------|----|
| `stop_server.sh` | Kills the old process | Zero-downtime prep |
| `install_dependencies.sh` | `pip install` on the server | Fresh deps every deploy |
| `start_server.sh` | Starts app in background | App goes live |
| `validate_service.sh` | Curls `/health` | Confirms deploy succeeded |

If `validate_service.sh` fails → CodeDeploy marks deployment as **failed** → pipeline shows ❌ → you know immediately.

---

## Clean Up

Delete in this order:

1. **CodePipeline** → Delete pipeline
2. **CodeDeploy** → Delete deployment group → Delete application
3. **CodeBuild** → Delete project
4. **EC2** → Terminate instance
5. **S3** → Empty and delete artifact bucket
6. **IAM** → Delete both roles (`ec2-codedeploy-role`, `codedeploy-service-role`)
7. **CodePipeline** → Settings → Connections → Delete `dost-ptri-github`

---

## ✅ Lab Complete!

You built a real production-like CI/CD pipeline:

| Component | What it does |
|-----------|-------------|
| GitHub | Source control — triggers pipeline on push |
| CodePipeline | Orchestrates the entire workflow |
| CodeBuild | Builds, tests, packages (reads `buildspec.yml`) |
| CodeDeploy | Deploys to EC2 (reads `appspec.yml` + runs scripts) |
| EC2 | Your production server running the app |

**This is exactly how companies deploy software to production.**

---

**Next → [Lab 03: CloudFormation Basic — S3 Bucket](./03-cloudformation-basic.md)**
