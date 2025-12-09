#!/usr/bin/env python3
import argparse
import json
import csv
import time
import requests
from datetime import datetime
import os

def send_discord(webhook, content):
    payload = {"content": content}
    try:
        requests.post(webhook, json=payload, timeout=5)
    except Exception as e:
        print("Discord notify failed:", e)

def send_slack(webhook, text):
    payload = {"text": text}
    try:
        requests.post(webhook, json=payload, timeout=5)
    except Exception as e:
        print("Slack notify failed:", e)

def check_endpoint(url, timeout=10):
    start = time.time()
    try:
        r = requests.get(url, timeout=timeout)
        elapsed = time.time() - start
        return {
            "url": url,
            "status_code": r.status_code,
            "ok": r.ok,
            "response_time": round(elapsed, 3),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "url": url,
            "status_code": None,
            "ok": False,
            "error": str(e),
            "response_time": round(elapsed, 3),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

def append_json(path, obj):
    data = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    data.append(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_csv(path, obj):
    write_header = not os.path.exists(path)
    with open(path, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp","url","status_code","ok","response_time","error"])
        writer.writerow([obj.get("timestamp"), obj.get("url"), obj.get("status_code"), obj.get("ok"), obj.get("response_time"), obj.get("error","")])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+", help="Endpoints to check")
    parser.add_argument("--discord-webhook", default=os.environ.get("DISCORD_WEBHOOK"))
    parser.add_argument("--slack-webhook", default=os.environ.get("SLACK_WEBHOOK"))
    parser.add_argument("--json", default="api_results.json")
    parser.add_argument("--csv", default="api_results.csv")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--alert-threshold", type=float, default=2.0, help="response time seconds to trigger alert")
    args = parser.parse_args()

    for url in args.urls:
        res = check_endpoint(url, timeout=args.timeout)
        append_json(args.json, res)
        append_csv(args.csv, res)
        # Alert on failure or slow
        if not res.get("ok") or (res.get("response_time") is not None and res["response_time"] > args.alert_threshold):
            text = f"ALERT: {url} status={res.get('status_code')} ok={res.get('ok')} rt={res.get('response_time')}s"
            if args.discord_webhook:
                send_discord(args.discord_webhook, text)
            if args.slack_webhook:
                send_slack(args.slack_webhook, text)
            print("Alert sent for", url)
        else:
            print("OK:", url, res["status_code"], res["response_time"])

if __name__ == "__main__":
    main()
