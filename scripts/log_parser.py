#!/usr/bin/env python3
import argparse
import re
from collections import Counter, defaultdict
from datetime import datetime
import html
import sys

# regex for combined log format
LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<req>[^"]+)" (?P<status>\d{3}) (?P<size>\S+)(?: "(?P<ref>[^"]*)" "(?P<ua>[^"]*)")?'
)

def parse_line(line):
    m = LOG_RE.match(line)
    if not m:
        return None
    return m.groupdict()

def generate_html(report, out_path):
    html_content = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Log report</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;padding:20px}}
table{{border-collapse:collapse;width:100%;margin-bottom:20px}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f4f4f4}}
</style>
</head>
<body>
<h1>Log report</h1>
<p>Generated: {datetime.now().isoformat()}</p>
<h2>Top IPs</h2>
<table><tr><th>IP</th><th>Hits</th></tr>
{''.join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k,v in report['ips'])}
</table>

<h2>Top User-Agents</h2>
<table><tr><th>User-Agent</th><th>Count</th></tr>
{''.join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k,v in report['uas'])}
</table>

<h2>HTTP Status Codes</h2>
<table><tr><th>Status</th><th>Count</th></tr>
{''.join(f"<tr><td>{s}</td><td>{c}</td></tr>" for s,c in report['status'].items())}
</table>

</body></html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description="Parse Apache/Nginx logs and generate HTML report.")
    parser.add_argument("logfile", help="Path to log file (can be - for stdin)")
    parser.add_argument("-n", "--top", type=int, default=20, help="Top N IPs and UAs")
    parser.add_argument("-o", "--output", default="report.html", help="HTML output file")
    args = parser.parse_args()

    ip_counter = Counter()
    ua_counter = Counter()
    status_counter = Counter()
    total = 0
    fh = sys.stdin if args.logfile == "-" else open(args.logfile, "r", encoding="utf-8", errors="ignore")
    with fh:
        for line in fh:
            parsed = parse_line(line)
            if not parsed:
                continue
            total += 1
            ip_counter[parsed['ip']] += 1
            if parsed.get('ua'):
                ua_counter[parsed['ua']] += 1
            status_counter[parsed['status']] += 1

    report = {
        'total': total,
        'ips': ip_counter.most_common(args.top),
        'uas': ua_counter.most_common(args.top),
        'status': dict(status_counter.most_common()),
    }
    generate_html(report, args.output)
    print(f"Processed {total} lines. Report written to {args.output}")

if __name__ == "__main__":
    main()
