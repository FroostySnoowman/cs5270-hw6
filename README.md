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

Notes:
- Handles **create** only for HW6; logs a warning for update/delete (reserved for HW7).
- Request JSON must follow the schema in the assignment handout.
- Keep and submit your logs per the homework. 

## Host B Test
python3 consumer.py \
  --req-bucket "usu-cs5270-beal-requests" \
  --target s3 \
  --out-bucket "usu-cs5270-beal-web" \
  --key-prefix "widgets/" \
  --region "us-east-1" \
  --profile "cs5270" \
  --sleep-ms 100

## Host A Test
java -jar producer.jar \
  -p "cs5270" \
  -r "us-east-1" \
  -rb "usu-cs5270-beal-requests" \
  -mrt 30000 \
  -ird 100