import json

with open("q-vercel-latency.json") as f:
    records = json.load(f)

def handler(request):
    try:
        body = json.loads(request.body.decode())

        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 0)

        result = {}

        for region in regions:
            subset = [r for r in records if r["region"] == region]

            latencies = [r["latency_ms"] for r in subset]
            uptimes = [r["uptime"] for r in subset]

            if latencies:
                avg_latency = sum(latencies)/len(latencies)
                p95_latency = sorted(latencies)[int(0.95*len(latencies))-1]
            else:
                avg_latency = 0
                p95_latency = 0

            avg_uptime = sum(uptimes)/len(uptimes) if uptimes else 0
            breaches = sum(l > threshold for l in latencies)

            result[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            }

        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
