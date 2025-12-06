#!/usr/bin/env python3
import argparse, requests, time, json, csv, sys
from datetime import datetime

def send_telegram_alert(token, chat_id, message):
    """Відправка повідомлення у Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=data, timeout=5)
        if r.status_code != 200:
            print("Помилка при відправці Telegram alert:", r.text)
    except Exception as e:
        print("Не вдалося відправити Telegram alert:", e)

def check_url(url, timeout=10):
    """Перевірка доступності одного URL."""
    start = time.time()
    try:
        r = requests.get(url, timeout=timeout)
        elapsed = time.time() - start
        return {"url": url, "status": r.status_code, "time": round(elapsed, 3)}
    except Exception as e:
        return {"url": url, "status": None, "time": None, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="API availability monitor")
    parser.add_argument("--endpoints", "-e", nargs="+", required=True, help="List of endpoints to check")
    parser.add_argument("--outjson", default="api_results.json")
    parser.add_argument("--outcsv", default="api_results.csv")
    parser.add_argument("--token", help="Telegram bot token")
    parser.add_argument("--chat", help="Telegram chat ID")
    args = parser.parse_args()

    results = []
    for url in args.endpoints:
        res = check_url(url)
        results.append(res)
        print(f"Checked {url}: {res['status']} ({res.get('time', '?')}s)")

        # Якщо є помилка — сповіщаємо у Telegram
        if (res.get("status") is None) or (res["status"] >= 400):
            if args.token and args.chat:
                msg = f"API ALERT:\nURL: {url}\nStatus: {res.get('status')}\nError: {res.get('error', 'N/A')}"
                send_telegram_alert(args.token, args.chat, msg)

    # Зберігаємо результати у JSON
    with open(args.outjson, "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.utcnow().isoformat(), "results": results}, f, indent=2)

    # Зберігаємо результати у CSV
    with open(args.outcsv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "status", "time", "error"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "url": r.get("url"),
                "status": r.get("status"),
                "time": r.get("time"),
                "error": r.get("error", "")
            })

    print("Monitoring complete. Results saved:", args.outjson, args.outcsv)

if __name__ == "__main__":
    main()
