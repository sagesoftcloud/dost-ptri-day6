# Lab 05 — CloudFormation Advanced: Serverless API Stack

## Difficulty: ⭐⭐⭐ Advanced

## Objective

Deploy a complete serverless application with a single template — DynamoDB + Lambda + API Gateway. Test it with real HTTP requests.

**What you'll create:** DynamoDB Table + Lambda Function + IAM Role + API Gateway REST API (6 resources)

**Time:** ~40 min

---

## Step 1: Write the Template (20 min)

Create `cfn-advanced.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 05 - Advanced: Serverless API (DynamoDB + Lambda + API Gateway)'

Parameters:
  ProjectName:
    Type: String
    Default: dost-ptri-day6

Resources:
  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${ProjectName}-items
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH

  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub ${ProjectName}-lambda-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: DynamoDBAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                  - dynamodb:GetItem
                  - dynamodb:Scan
                Resource: !GetAtt DataTable.Arn

  AppFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub ${ProjectName}-api
      Runtime: python3.12
      Handler: index.handler
      Role: !GetAtt LambdaRole.Arn
      Timeout: 10
      Environment:
        Variables:
          TABLE_NAME: !Ref DataTable
      Code:
        ZipFile: |
          import json, os, boto3
          from datetime import datetime

          table = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

          def handler(event, context):
              method = event.get('httpMethod', 'GET')
              if method == 'POST':
                  body = json.loads(event.get('body', '{}'))
                  item = {'id': context.aws_request_id, 'data': body.get('data',''), 'created': datetime.now().isoformat()}
                  table.put_item(Item=item)
                  return {'statusCode': 201, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(item)}
              result = table.scan()
              return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({'items': result.get('Items',[]), 'count': result.get('Count',0)})}

  ApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub ${ProjectName}-api

  ApiResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGateway
      ParentId: !GetAtt ApiGateway.RootResourceId
      PathPart: items

  ApiMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ApiResource
      HttpMethod: ANY
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AppFunction.Arn}/invocations

  ApiDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn: ApiMethod
    Properties:
      RestApiId: !Ref ApiGateway
      StageName: dev

  LambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref AppFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGateway}/*

Outputs:
  ApiUrl:
    Description: API endpoint
    Value: !Sub https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/dev/items
  TableName:
    Value: !Ref DataTable
  FunctionName:
    Value: !Ref AppFunction
```

### New concepts:

| Concept | Purpose |
|---------|---------|
| `${AWS::AccountId}` | Pseudo parameter — your account ID |
| `${AWS::Region}` | Pseudo parameter — current region |
| `ZipFile: \|` | Inline Lambda code in template |
| IAM inline policy | Grant Lambda → DynamoDB access |
| `AWS_PROXY` integration | API Gateway passes full request to Lambda |

---

## Step 2: Deploy (10 min)

1. Upload `cfn-advanced.yaml` → Stack name: `day6-advanced-YOURNAME`
2. ⚠️ Check "I acknowledge that CloudFormation might create IAM resources"
3. Wait for `CREATE_COMPLETE` (~2 min)

---

## Step 3: Test the API (5 min)

Copy the **ApiUrl** from Outputs tab.

```bash
# GET — list items (empty)
curl YOUR_API_URL

# POST — create an item
curl -X POST YOUR_API_URL -H "Content-Type: application/json" -d '{"data": "Hello from CloudFormation!"}'

# GET — see your item
curl YOUR_API_URL
```

---

## Step 4: Verify in Console (5 min)

| Service | Check |
|---------|-------|
| DynamoDB | Table exists, Items tab shows your data |
| Lambda | Function exists, env vars set |
| API Gateway | REST API with `/items`, deployed to `dev` |

---

## Clean Up

Delete stack → all resources removed ✅

---

## ✅ Lab Complete!

**6 resources, 1 template, 1 click deploy.** Concepts: pseudo parameters, inline Lambda, IAM policies, API Gateway proxy.

---

**Next → [Lab 06: Final — CI/CD + CloudFormation Deploy EC2](./06-final-cicd-cloudformation.md)**
