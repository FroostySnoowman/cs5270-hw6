import logging
import argparse
import boto3
import time
from typing import Optional
from botocore.config import Config

from helpers import (
    parse_request,
    build_widget_for_s3,
    build_ddb_item,
    s3_key_for,
)

def make_s3(profile: Optional[str], region: str):
    sess = boto3.session.Session(profile_name=profile, region_name=region) if profile else boto3.session.Session(region_name=region)
    return sess.client("s3", config=Config(retries={"max_attempts": 10, "mode": "standard"}))

def make_ddb_resource(profile: Optional[str], region: str):
    sess = boto3.session.Session(profile_name=profile, region_name=region) if profile else boto3.session.Session(region_name=region)
    return sess.resource("dynamodb", config=Config(retries={"max_attempts": 10, "mode": "standard"}))

def get_next_key(s3, bucket: str) -> Optional[str]:
    resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
    objs = resp.get("Contents", [])
    if not objs:
        return None
    return objs[0]["Key"]

def pop_request(s3, bucket: str) -> Optional[tuple[str, dict]]:
    key = get_next_key(s3, bucket)
    if not key:
        return None
    obj = s3.get_object(Bucket=bucket, Key=key)
    body_bytes = obj["Body"].read()
    s3.delete_object(Bucket=bucket, Key=key)
    body = body_bytes.decode("utf-8", errors="ignore").strip()
    if not body:
        logging.getLogger("hw6").warning("Skipping empty request object: %s", key)
        return None
    try:
        req = parse_request(body)
    except Exception as e:
        logging.getLogger("hw6").warning("Skipping malformed request %s: %s", key, e)
        return None
    return key, req

def handle_create_s3(s3, out_bucket: str, req: dict, prefix: str):
    widget = build_widget_for_s3(req)
    key = s3_key_for(req["owner"], req["widgetId"], prefix=prefix)
    s3.put_object(Bucket=out_bucket, Key=key, Body=(__import__("json").dumps(widget)).encode("utf-8"), ContentType="application/json")
    return key

def handle_create_ddb(ddb_table, req: dict):
    item = build_ddb_item(req)
    ddb_table.put_item(Item=item)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--req-bucket", required=True)
    ap.add_argument("--target", choices=["s3", "dynamodb"], required=True)
    ap.add_argument("--out-bucket")
    ap.add_argument("--table")
    ap.add_argument("--key-prefix", default="widgets/")
    ap.add_argument("--sleep-ms", type=int, default=100)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--log-file", default="consumer.log")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(args.log_file), logging.StreamHandler()],
    )
    log = logging.getLogger("hw6")

    s3 = make_s3(args.profile, args.region)
    ddb = None
    table = None

    if args.target == "s3":
        if not args.out_bucket:
            log.error("--out-bucket required for target=s3")
            return
    else:
        if not args.table:
            log.error("--table required for target=dynamodb")
            return
        ddb = make_ddb_resource(args.profile, args.region)
        table = ddb.Table(args.table)

    while True:
        popped = pop_request(s3, args.req_bucket)
        if not popped:
            time.sleep(max(args.sleep_ms, 0) / 1000.0)
            continue

        key, req = popped
        t = (req.get("type") or "").lower()
        if t == "create":
            try:
                if args.target == "s3":
                    out_key = handle_create_s3(s3, args.out_bucket, req, args.key_prefix)
                    log.info("CREATE -> S3: %s", out_key)
                else:
                    handle_create_ddb(table, req)
                    log.info("CREATE -> DynamoDB: widgetId=%s owner=%s", req["widgetId"], req["owner"])
            except Exception as e:
                log.error("Failed to process %s: %s", key, e)
        elif t in ("update", "delete"):
            log.warning("Ignoring %s (out of scope for HW6)", t)
        else:
            log.warning("Unknown request type: %r", req.get("type"))

if __name__ == "__main__":
    main()