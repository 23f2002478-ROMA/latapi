import json
import numpy as np
from http.server import BaseHTTPRequestHandler

with open("q-vercel-latency.json") as f:
    records = json.load(f)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        request = json.loads(body)

        regions = request["regions"]
        threshold = request["threshold_ms"]

        result = {}

        for region in regions:
            subset = [r for r in records if r["region"] == region]

            latencies = [r["latency_ms"] for r in subset]
            uptimes = [r["uptime"] for r in subset]

            avg_latency = float(np.mean(latencies)) if latencies else 0
            p95_latency = float(np.percentile(latencies, 95)) if latencies else 0
            avg_uptime = float(np.mean(uptimes)) if uptimes else 0
            breaches = sum(l > threshold for l in latencies)

            result[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            }

        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","POST")
        self.end_headers()

        self.wfile.write(json.dumps(result).encode())
