# Lab 04 — CloudFormation Intermediate: VPC with Subnets & Security Group

## Difficulty: ⭐⭐ Intermediate

## Objective

Build a networking foundation using CloudFormation — VPC, subnets, Internet Gateway, route table, and security group. Introduces multi-resource templates and automatic dependency resolution.

**What you'll create:** VPC + Public Subnet + Private Subnet + IGW + Route Table + Security Group (8 resources)

**Time:** ~30 min

---

## Step 1: Write the Template (15 min)

Create `cfn-intermediate.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 04 - Intermediate: VPC with Subnets and Security Group'

Parameters:
  ProjectName:
    Type: String
    Default: dost-ptri-day6

  VpcCidr:
    Type: String
    Default: 10.0.0.0/16

  PublicSubnetCidr:
    Type: String
    Default: 10.0.1.0/24

  PrivateSubnetCidr:
    Type: String
    Default: 10.0.2.0/24

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-vpc

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-igw

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Ref PublicSubnetCidr
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Ref PrivateSubnetCidr
      AvailabilityZone: !Select [1, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-rt

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow HTTP and SSH
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
          Description: Restrict to your IP in production
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-web-sg

Outputs:
  VpcId:
    Value: !Ref VPC
  PublicSubnetId:
    Value: !Ref PublicSubnet
  PrivateSubnetId:
    Value: !Ref PrivateSubnet
  SecurityGroupId:
    Value: !Ref WebSecurityGroup
```

### New concepts:

| Concept | Example | Purpose |
|---------|---------|---------|
| `!Sub` | `!Sub ${ProjectName}-vpc` | String substitution |
| `!Select` | `!Select [0, !GetAZs '']` | Pick from a list |
| `!GetAZs` | `!GetAZs ''` | Get AZs in current region |
| `DependsOn` | `DependsOn: AttachGateway` | Explicit ordering |
| Multi-resource | 8 resources | They reference each other |

---

## Step 2: Deploy (10 min)

1. Upload `cfn-intermediate.yaml` → Stack name: `day6-vpc-YOURNAME`
2. Watch Events — notice the creation order (VPC first, then dependents)
3. Wait for `CREATE_COMPLETE`

---

## Step 3: Verify (5 min)

- **VPC Console** → new VPC with `10.0.0.0/16` ✅
- 2 subnets (public + private) ✅
- Internet Gateway attached ✅
- Route table with `0.0.0.0/0 → igw` ✅
- Security group with HTTP + SSH rules ✅

---

## Step 4: Clean Up

Delete stack → all 8 resources removed in correct reverse order ✅

---

## ✅ Lab Complete!

**Concepts practiced:** `!Sub`, `!Select`, `!GetAZs`, `DependsOn`, multi-resource dependencies, automatic ordering

---

**Next → [Lab 05: CloudFormation Advanced — Serverless API](./05-cloudformation-advanced.md)**
