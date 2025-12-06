#!/usr/bin/env python3
import argparse, re, html
from collections import Counter

APACHE_REGEX = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+) .*? "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) .* "(?P<ref>[^"]*)" "(?P<ua>[^"]*)"')

def parse_line(line):
    m = APACHE_REGEX.search(line)
    if not m:
        return None
    return m.groupdict()

def generate_html(output, top_ips, statuses, top_uas):
    html_doc = f"""
    <html><head><meta charset="utf-8"><title>Log Report</title></head><body>
    <h1>Log Analysis Report</h1>
    <h2>Top IPs</h2><ol>{"".join(f"<li>{ip} — {cnt}</li>" for ip,cnt in top_ips)}</ol>
    <h2>Status codes</h2><ul>{"".join(f"<li>{s} — {c}</li>" for s,c in statuses)}</ul>
    <h2>Top User-Agents</h2><ol>{"".join(f"<li>{html.escape(ua)} — {cnt}</li>" for ua,cnt in top_uas)}</ol>
    </body></html>
    """
    with open(output, "w", encoding="utf-8") as f:
        f.write(html_doc)

def main():
    parser = argparse.ArgumentParser(description="Parse Apache/Nginx logs and generate HTML report")
    parser.add_argument("logfile", help="Path to logfile")
    parser.add_argument("--output", "-o", default="report.html", help="Output HTML file")
    parser.add_argument("--top", "-t", type=int, default=10, help="Top N entries")
    args = parser.parse_args()

    ips = []
    statuses = []
    uas = []

    with open(args.logfile, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                ips.append(parsed["ip"])
                statuses.append(parsed["status"])
                uas.append(parsed["ua"])

    top_ips = Counter(ips).most_common(args.top)
    status_counts = Counter(statuses).most_common()
    top_uas = Counter(uas).most_common(args.top)

    generate_html(args.output, top_ips, status_counts, top_uas)
    print(f"Report saved to {args.output}")

if __name__ == "__main__":
    main()
