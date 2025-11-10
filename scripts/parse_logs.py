import argparse, re, collections

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True)
args = parser.parse_args()

with open(args.file) as f:
    logs = f.readlines()

ips = [re.split(r'\s+', line)[0] for line in logs]
statuses = [re.split(r'\s+', line)[8] for line in logs]

ip_counter = collections.Counter(ips).most_common(5)
status_counter = collections.Counter(statuses).most_common()

with open("report.html", "w") as out:
    out.write("<h1>Log Analysis Report</h1>")
    out.write("<h2>Top IPs</h2><ul>")
    for ip, count in ip_counter:
        out.write(f"<li>{ip}: {count}</li>")
    out.write("</ul>")
