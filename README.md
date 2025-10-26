# CS5270 HW6 Consumer

Reads one Widget Request at a time from an S3 "request bucket" (Bucket 2).
If it's a **create** request, writes the widget to either:
- S3 (Bucket 3) as JSON at `widgets/{owner-slug}/{widgetId}`, or
- DynamoDB table with flattened attributes.

## Install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Run (S3 target)
python3 consumer.py \
  --req-bucket BUCKET2 \
  --target s3 \
  --out-bucket BUCKET3 \
  --region us-east-1

## Run (DynamoDB target)
python3 consumer.py \
  --req-bucket BUCKET2 \
  --target dynamodb \
  --table widgets \
  --region us-east-1

Flags:
  --sleep-ms 100        poll delay when empty
  --profile default     optional AWS profile
  --log-file consumer.log
  --key-prefix widgets/ key prefix in Bucket 3

## Setup AWS Credentials
```
aws configure --profile cs5270
```

## S3
### Host B Test (Second)
```python
python3 consumer.py \
  --req-bucket "usu-cs5270-beal-requests" \
  --target s3 \
  --out-bucket "usu-cs5270-beal-web" \
  --key-prefix "widgets/" \
  --region "us-east-1" \
  --profile "cs5270" \
  --sleep-ms 100
```

### Host A Test (First)
```bash
java -jar producer.jar \
  -p "cs5270" \
  -r "us-east-1" \
  -rb "usu-cs5270-beal-requests" \
  -mrt 30000 \
  -ird 100
```

## DynamoDB
### General Setup
```bash
aws dynamodb create-table \
  --table-name "widgets" \
  --attribute-definitions AttributeName=widgetId,AttributeType=S \
  --key-schema AttributeName=widgetId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "us-east-1" \
  --profile "cs5270"
```

```bash
aws dynamodb describe-table \
  --table-name "widgets" \
  --region "us-east-1" \
  --profile "cs5270" \
  --query 'Table.TableStatus'
```

### Host B Test (Second)
```python
python3 consumer.py \
  --req-bucket "usu-cs5270-beal-requests" \
  --target dynamodb \
  --table "widgets" \
  --region "us-east-1" \
  --profile "cs5270" \
  --sleep-ms 100
```

### Host A Test (First)
```bash
java -jar producer.jar \
  -p "cs5270" \
  -r "us-east-1" \
  -rb "usu-cs5270-beal-requests" \
  -mrt 30000 \
  -ird 100
```

## Mixed
```python
python3 consumer.py \
  --req-bucket "usu-cs5270-beal-requests" \
  --target dynamodb \
  --table "widgets" \
  --region "us-east-1" \
  --profile "cs5270" \
  --sleep-ms 100
```

## Screenshots
- 1.X - S3 -> S3
- 2.X - S3 -> DynamoDB