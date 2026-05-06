# Lab 01 — Clone & Push to Your GitHub

## Objective

Clone this project, create your own GitHub repository, and push the code — simulating the first step of a CI/CD workflow.

---

## Step 1: Install & Configure Git (5 min)

### Check if Git is installed

```bash
git --version
```

If not installed:
- **Mac:** `xcode-select --install`
- **Windows:** Download from https://git-scm.com/downloads

### Configure your identity

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 2: Create YOUR GitHub Repository (5 min)

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `dost-ptri-day6-cicd`
   - **Description:** `Day 6 CI/CD Sample — DOST PTRI Training`
   - **Visibility:** Public
   - ❌ Do NOT check "Add a README file"
3. Click **Create repository**
4. Keep this tab open — you'll need the URL

---

## Step 3: Clone This Project (5 min)

### Clone only the CI/CD folder (not the entire repo)

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/sagesoftcloud/dost-ptri.git
cd dost-ptri
git sparse-checkout set cicd-deployment
```

### Copy to your own project folder

```bash
cp -r cicd-deployment ~/dost-ptri-day6-cicd
cd ~/dost-ptri-day6-cicd
```

### Verify the files

```bash
ls
```

You should see:

```
README.md              app.py                 buildspec.yml
appspec.yml            requirements.txt       test_app.py
pipeline-template.yaml lab-s3-versioning.yaml scripts/
```

---

## Step 4: Create Your Own Repo from These Files (10 min)

### Initialize a fresh Git repository

```bash
git init
git add .
git commit -m "Initial commit: Day 6 CI/CD sample project"
git branch -M main
```

### Connect to YOUR GitHub repo

Replace `YOUR-USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR-USERNAME/dost-ptri-day6-cicd.git
```

### Push

```bash
git push -u origin main
```

> 💡 If prompted for credentials, use a **Personal Access Token**:
> GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate with `repo` scope

---

## Step 5: Verify on GitHub (5 min)

1. Refresh your repository page on GitHub
2. You should see all files uploaded
3. Click on these key files and read them:
   - `buildspec.yml` — what CodeBuild does (build & test)
   - `appspec.yml` — what CodeDeploy does (deploy to EC2)
   - `pipeline-template.yaml` — the entire pipeline as CloudFormation IaC

---

## Step 6: Make a Change & Push (Bonus)

### Edit `app.py` — add a new endpoint

```python
@app.route("/version")
def version():
    return jsonify({"version": "1.1.0", "day": "Day 6"})
```

### Commit and push

```bash
git add app.py
git commit -m "feat: add version endpoint"
git push
```

### Check GitHub

Refresh your repo — the new commit appears. In a real pipeline, this push would **automatically trigger a build**.

---

## How This Connects to AWS CodePipeline

```
┌──────────┐         ┌──────────────┐         ┌───────────┐
│  GitHub  │ ──────→ │ CodePipeline │ ──────→ │ CodeBuild │
│  (push)  │ webhook │   (Source)   │ trigger │  (Build)  │
└──────────┘         └──────────────┘         └───────────┘
```

1. You `git push` → GitHub sends a webhook to AWS
2. CodePipeline pulls the latest code (Source stage)
3. CodeBuild reads `buildspec.yml` → installs deps, runs tests, packages
4. CodeDeploy reads `appspec.yml` → deploys to EC2 using lifecycle scripts

> ⚠️ We are NOT deploying the pipeline today — this is conceptual understanding.

---

## ✅ Lab Complete!

You've successfully:
- Cloned a project from GitHub
- Created your own repository
- Pushed code with Git
- Understood how `git push` triggers CI/CD pipelines

---

**Next → [Lab 02: Build Pipeline & Deploy to EC2](./02-build-pipeline-deploy-ec2.md)**
