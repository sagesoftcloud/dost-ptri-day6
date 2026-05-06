# Lab 03 — CloudFormation Basic: S3 Bucket with Versioning

## Difficulty: ⭐ Basic

## Objective

Write your first CloudFormation template from scratch, deploy it, and verify the resource was created correctly.

**What you'll create:** 1 S3 Bucket with versioning, encryption, and public access blocked

**Time:** ~20 min

---

## Step 1: Write the Template (10 min)

Create a file called `cfn-basic.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 03 - Basic: S3 Bucket with Versioning'

Parameters:
  BucketName:
    Type: String
    Description: Globally unique bucket name (lowercase, no spaces)

  Environment:
    Type: String
    Default: training
    AllowedValues:
      - training
      - development
      - production

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

Outputs:
  BucketName:
    Description: Name of the bucket
    Value: !Ref MyBucket

  BucketARN:
    Description: ARN of the bucket
    Value: !GetAtt MyBucket.Arn
```

### Key concepts:

| Concept | Example | Purpose |
|---------|---------|---------|
| `Parameters` | `BucketName`, `Environment` | Inputs you provide at deploy time |
| `!Ref` | `!Ref BucketName` | References a parameter or resource |
| `!GetAtt` | `!GetAtt MyBucket.Arn` | Gets an attribute of a resource |
| `Outputs` | `BucketARN` | Values shown after stack creation |

---

## Step 2: Deploy (5 min)

1. **CloudFormation Console** → **Create stack** → Upload `cfn-basic.yaml`
2. Stack name: `day6-basic-YOURNAME`
3. BucketName: `dost-ptri-basic-YOURNAME`
4. Environment: `training`
5. Submit → wait for `CREATE_COMPLETE`

---

## Step 3: Verify (3 min)

1. **S3 Console** → find your bucket → Properties:
   - ✅ Versioning: Enabled
   - ✅ Encryption: AES-256
2. Permissions → ✅ Block all public access: On
3. CloudFormation **Outputs** tab → ✅ BucketName and BucketARN

---

## Step 4: Clean Up (2 min)

Select stack → **Delete** → confirm → bucket gone ✅

---

## ✅ Lab Complete!

**Concepts practiced:** Parameters, Resources, Outputs, `!Ref`, `!GetAtt`, Tags

---

**Next → [Lab 04: CloudFormation Intermediate — VPC Stack](./04-cloudformation-intermediate.md)**
