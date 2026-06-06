#!/usr/bin/env python3
"""
从 Elasticsearch 拉取 OneNET 饮水机数据，提取 N4_T 和 OT4_C
"""
import requests
import json
import time
import os

ES_URL = "http://101.35.135.63:9200"
INDEX = "logs-onenet-2026.06.*"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "raw_data.jsonl")
SCROLL_SIZE = 5000
SCROLL_KEEP = "2m"

def fetch_all():
    # 第一步：初始查询
    body = {
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "data.params.N4_T.value"}},
                    {"exists": {"field": "data.params.OT4_C.value"}}
                ]
            }
        },
        "size": SCROLL_SIZE,
        "_source": [
            "@timestamp",
            "data.params.N4_T.value",
            "data.params.N4_T.time_iso",
            "data.params.OT4_C.value",
            "data.params.OT4_C.time_iso",
            "data.params.Exp.value",
            "data.params.DEV_STS.value",
            "data.params.AT.value",
            "data.params.humi.value",
            "data.params.temp.value",
            "data.params.P1_V.value",
            "data.params.H1_PW.value",
            "data.params.N4_R.value",
            "data.params.L_4.value",
            "deviceName",
            "productId"
        ]
    }

    resp = requests.post(
        f"{ES_URL}/{INDEX}/_search?scroll={SCROLL_KEEP}",
        json=body,
        headers={"Content-Type": "application/json"}
    )
    data = resp.json()

    if "error" in data:
        print(f"ES 错误: {data['error']}")
        return

    scroll_id = data.get("_scroll_id")
    hits = data["hits"]["hits"]
    total = data["hits"]["total"]["value"]

    print(f"共 {total} 条数据，开始拉取...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        count = 0
        while hits:
            for hit in hits:
                src = hit["_source"]
                row = {
                    "@timestamp": src.get("@timestamp"),
                    "deviceName": src.get("deviceName", ""),
                }

                params = src.get("data", {}).get("params", {})

                # N4_T
                n4 = params.get("N4_T", {})
                if "value" in n4:
                    row["N4_T"] = n4["value"]
                    row["N4_T_time"] = n4.get("time_iso", "")

                # OT4_C
                ot4 = params.get("OT4_C", {})
                if "value" in ot4:
                    row["OT4_C"] = ot4["value"]
                    row["OT4_C_time"] = ot4.get("time_iso", "")

                # 环境参数
                for key in ["AT", "humi", "temp", "P1_V", "H1_PW", "N4_R", "L_4", "Exp", "DEV_STS"]:
                    p = params.get(key, {})
                    if "value" in p:
                        row[key] = p["value"]

                if "N4_T" in row and "OT4_C" in row:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    count += 1

            print(f"\r已拉取 {count} 条...", end="", flush=True)

            # 下一批
            resp = requests.post(
                f"{ES_URL}/_search/scroll",
                json={"scroll": SCROLL_KEEP, "scroll_id": scroll_id},
                headers={"Content-Type": "application/json"}
            )
            data = resp.json()
            scroll_id = data.get("_scroll_id")
            hits = data["hits"]["hits"]

    print(f"\n完成！共保存 {count} 条到 {OUTPUT_FILE}")

    # 清理 scroll
    try:
        requests.delete(f"{ES_URL}/_search/scroll", json={"scroll_id": scroll_id})
    except:
        pass


if __name__ == "__main__":
    fetch_all()
