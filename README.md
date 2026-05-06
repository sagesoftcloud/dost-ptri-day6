# CI/CD & Infrastructure as Code Lab

## DOST PTRI - AWS Fundamentals Training Program

Hands-on labs covering Git/GitHub, AWS CodePipeline with real EC2 deployment, and CloudFormation from basic to advanced — culminating in a production-like deployment workflow.

### CI/CD Labs

| # | Lab | What You'll Do | Time |
|---|-----|---------------|:----:|
| 1 | [Clone & Push to GitHub](./01-github-push-lab.md) | Clone project, push to your own repo | 30 min |
| 2 | [Build Pipeline & Deploy to EC2](./02-build-pipeline-deploy-ec2.md) | Create full pipeline: GitHub → Build → Deploy to live EC2 | 60 min |

### CloudFormation Labs

| # | Lab | Difficulty | Time |
|---|-----|:----------:|:----:|
| 3 | [Basic: S3 Bucket](./03-cloudformation-basic.md) | ⭐ | 20 min |
| 4 | [Intermediate: VPC Stack](./04-cloudformation-intermediate.md) | ⭐⭐ | 30 min |
| 5 | [Advanced: Serverless API](./05-cloudformation-advanced.md) | ⭐⭐⭐ | 40 min |

### Final Lab

| # | Lab | What You'll Do | Time |
|---|-----|---------------|:----:|
| 6 | [CI/CD + CloudFormation: Deploy EC2](./06-final-cicd-cloudformation.md) | Provision EC2 via CFN, then deploy app via pipeline | 60 min |

---

### Prerequisites

- AWS account with AdministratorAccess
- Region: **ap-southeast-1** (Singapore)
- GitHub account (free) — https://github.com/signup
- Git installed on your machine

### ⚠️ Cost

Labs use `t2.micro` (free tier eligible). **Delete all resources after each lab** to avoid charges.

---

**Start here → [01 - Clone & Push to GitHub](./01-github-push-lab.md)**
