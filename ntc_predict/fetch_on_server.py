#!/usr/bin/env python3
"""在服务器上运行，从本地 ES 拉取数据到 JSON 文件"""
import requests
import json
import sys

ES_URL = "http://localhost:9200"
OUTPUT = "/tmp/ntc_data.jsonl"
SCROLL_SIZE = 5000

resp = requests.post(
    f"{ES_URL}/logs-onenet-2026.06.*/_search?scroll=2m",
    json={
        "query": {"bool": {"must": [
            {"exists": {"field": "data.params.N4_T.value"}},
            {"exists": {"field": "data.params.OT4_C.value"}}
        ]}},
        "size": SCROLL_SIZE,
        "_source": ["data.params", "@timestamp", "deviceName"]
    },
    headers={"Content-Type": "application/json"}
)
data = resp.json()
scroll_id = data.get("_scroll_id")
hits = data["hits"]["hits"]
total = data["hits"]["total"]["value"]
print(f"Total: {total}", flush=True)

count = 0
with open(OUTPUT, "w") as f:
    while hits:
        for hit in hits:
            params = hit["_source"].get("data", {}).get("params", {})
            n4 = params.get("N4_T", {}).get("value")
            ot4 = params.get("OT4_C", {}).get("value")
            if n4 is not None and ot4 is not None:
                row = {
                    "N4_T": float(n4),
                    "OT4_C": float(ot4),
                    "ts": params.get("N4_T", {}).get("time_iso", hit["_source"].get("@timestamp", ""))
                }
                # 只保留数值字段，减小体积
                for k in ["AT", "humi", "temp", "P1_V", "H1_PW", "N4_R", "L_4"]:
                    v = params.get(k, {}).get("value")
                    if v is not None:
                        try:
                            row[k] = float(v) if v not in ("ON", "OFF", "stop", "start") else v
                        except:
                            pass
                row["deviceName"] = hit["_source"].get("deviceName", "")
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1

        if count % 20000 == 0:
            print(f"Progress: {count}", flush=True)

        resp = requests.post(
            f"{ES_URL}/_search/scroll",
            json={"scroll": "2m", "scroll_id": scroll_id},
            headers={"Content-Type": "application/json"}
        )
        data = resp.json()
        scroll_id = data.get("_scroll_id")
        hits = data["hits"]["hits"]

requests.delete(f"{ES_URL}/_search/scroll", json={"scroll_id": scroll_id})
print(f"Done: {count} rows saved to {OUTPUT}")
