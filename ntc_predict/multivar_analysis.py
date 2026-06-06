#!/usr/bin/env python3
"""多变量回归分析：N4_T + 其他参数 → OT4_C
"""
import json
import math
import random
import gzip
import os

DATA_FILE = "/tmp/ntc_data_multi.jsonl.gz"

# 所有可能相关的字段
ALL_FIELDS = ["N4_T", "OT4_C", "AT", "temp", "humi", "N1_T", "N2_T", "N3_T", "N4_R", "P1_V", "L_4"]


def pull_data():
    """从 ES 拉取多字段数据"""
    import urllib.request

    ES_URL = "http://localhost:9200"
    INDEX = "logs-onenet-2026.06.*"
    BATCH_SIZE = 10000
    MAX_TOTAL = 50000

    total = 0
    after = None

    with gzip.open(DATA_FILE, 'wt') as f:
        while total < MAX_TOTAL:
            body = {
                "size": BATCH_SIZE,
                "_source": ["data.params"],
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "data.params.N4_T.value"}},
                            {"exists": {"field": "data.params.OT4_C.value"}},
                        ]
                    }
                },
                "sort": [{"@timestamp": "asc"}]
            }
            if after:
                body["search_after"] = after

            req = urllib.request.Request(
                f"{ES_URL}/{INDEX}/_search",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"}
            )
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read())

            hits = result["hits"]["hits"]
            if not hits:
                break

            for hit in hits:
                params = hit["_source"].get("data", {}).get("params", {})
                row = {}
                for field in ALL_FIELDS:
                    if field in params and "value" in params[field]:
                        try:
                            row[field] = float(params[field]["value"])
                        except (ValueError, TypeError):
                            row[field] = None
                    else:
                        row[field] = None
                if row.get("N4_T") is not None and row.get("OT4_C") is not None:
                    f.write(json.dumps(row) + "\n")
                    total += 1

            after = hits[-1]["sort"]
            print(f"  已拉取 {total} 条...")

    print(f"共拉取 {total} 条有效数据")


def solve_ls(X, y):
    """最小二乘求解"""
    m = len(X[0])
    A = [[0.0] * m for _ in range(m)]
    B = [0.0] * m
    for i in range(len(X)):
        for r in range(m):
            for c in range(m):
                A[r][c] += X[i][r] * X[i][c]
            B[r] += X[i][r] * y[i]
    for col in range(m):
        pivot = A[col][col]
        if abs(pivot) < 1e-12:
            continue
        for j in range(col, m):
            A[col][j] /= pivot
        B[col] /= pivot
        for row in range(m):
            if row != col:
                factor = A[row][col]
                for j in range(col, m):
                    A[row][j] -= factor * A[col][j]
                B[row] -= factor * B[col]
    return B


def evaluate(predict_fn, test_data):
    errors = []
    for r in test_data:
        pred = predict_fn(r)
        actual = r["OT4_C"]
        errors.append(pred - actual)
    mae = sum(abs(e) for e in errors) / len(errors)
    rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
    mean_y = sum(r["OT4_C"] for r in test_data) / len(test_data)
    ss_res = sum(e * e for e in errors)
    ss_tot = sum((r["OT4_C"] - mean_y) ** 2 for r in test_data)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return mae, rmse, r2


def train_and_evaluate():
    rows = []
    with gzip.open(DATA_FILE, 'rt') as f:
        for line in f:
            rows.append(json.loads(line))

    N = len(rows)
    print(f"数据量: {N}")

    # 只保留所有字段完整的行
    complete = [r for r in rows if all(r.get(f) is not None for f in ALL_FIELDS)]
    print(f"完整数据: {len(complete)} 条")

    random.seed(42)
    random.shuffle(complete)
    split = int(len(complete) * 0.8)
    train = complete[:split]
    test = complete[split:]
    print(f"训练集: {len(train)}, 测试集: {len(test)}")

    results = {}

    # ===== 模型1: 纯多项式 N4_T → OT4_C =====
    n4_train = [r["N4_T"] for r in train]
    ot4_train = [r["OT4_C"] for r in train]

    X = [[1.0, r["N4_T"], r["N4_T"] ** 2, r["N4_T"] ** 3] for r in train]
    c1 = solve_ls(X, ot4_train)
    print(f"\n=== 模型1: 3阶多项式 (N4_T) ===")
    print(f"  N4_T^0 = {c1[0]:.6f}")
    print(f"  N4_T^1 = {c1[1]:.6f}")
    print(f"  N4_T^2 = {c1[2]:.8f}")
    print(f"  N4_T^3 = {c1[3]:.10f}")

    def predict1(r):
        n4 = r["N4_T"]
        return c1[0] + c1[1] * n4 + c1[2] * n4 * n4 + c1[3] * n4 * n4 * n4

    mae1, rmse1, r21 = evaluate(predict1, test)
    results["poly3"] = (mae1, rmse1, r21, c1)

    # ===== 模型2: 多变量线性 (核心4字段: N4_T + AT + temp + N4_R) =====
    fields2 = ["N4_T", "AT", "temp", "N4_R"]
    X = [[1.0] + [r[f] for f in fields2] for r in train]
    c2 = solve_ls(X, ot4_train)
    print(f"\n=== 模型2: 多变量线性 (N4_T + AT + temp + N4_R) ===")
    print(f"  bias = {c2[0]:.6f}")
    for i, f in enumerate(fields2, 1):
        print(f"  {f:6s} = {c2[i]:.6f}")

    def predict2(r):
        return c2[0] + sum(c2[i + 1] * r[f] for i, f in enumerate(fields2))

    mae2, rmse2, r22 = evaluate(predict2, test)
    results["linear4"] = (mae2, rmse2, r22, c2)

    # ===== 模型3: 多变量线性 (全8字段) =====
    fields3 = ["N4_T", "AT", "temp", "humi", "N1_T", "N2_T", "N3_T", "N4_R"]
    X = [[1.0] + [r[f] for f in fields3] for r in train]
    c3 = solve_ls(X, ot4_train)
    print(f"\n=== 模型3: 多变量线性 (全部8字段) ===")
    print(f"  bias = {c3[0]:.6f}")
    for i, f in enumerate(fields3, 1):
        print(f"  {f:6s} = {c3[i]:.6f}")

    def predict3(r):
        return c3[0] + sum(c3[i + 1] * r[f] for i, f in enumerate(fields3))

    mae3, rmse3, r23 = evaluate(predict3, test)
    results["linear8"] = (mae3, rmse3, r23, c3)

    # ===== 模型4: 多项式 N4_T + 线性其他 (最佳折中) =====
    # N4_T 用多项式展开 + AT/temp/N4_R 线性加入
    fields4_extra = ["AT", "temp", "N4_R"]
    X = []
    for r in train:
        n4 = r["N4_T"]
        row = [1.0, n4, n4 * n4, n4 * n4 * n4] + [r[f] for f in fields4_extra]
        X.append(row)
    c4 = solve_ls(X, ot4_train)
    print(f"\n=== 模型4: N4_T多项式 + AT/temp/N4_R 线性 (推荐) ===")
    print(f"  N4_T^0 = {c4[0]:.6f}")
    print(f"  N4_T^1 = {c4[1]:.6f}")
    print(f"  N4_T^2 = {c4[2]:.8f}")
    print(f"  N4_T^3 = {c4[3]:.10f}")
    for i, f in enumerate(fields4_extra, 4):
        print(f"  {f:6s} = {c4[i]:.6f}")

    def predict4(r):
        n4 = r["N4_T"]
        return (c4[0] + c4[1] * n4 + c4[2] * n4 * n4 + c4[3] * n4 * n4 * n4
                + c4[4] * r["AT"] + c4[5] * r["temp"] + c4[6] * r["N4_R"])

    mae4, rmse4, r24 = evaluate(predict4, test)
    results["hybrid"] = (mae4, rmse4, r24, c4)

    # ===== 汇总 =====
    print("\n" + "=" * 70)
    print("                    模型对比汇总 (测试集)")
    print("=" * 70)
    print(f"{'模型':30s} {'MAE':>8s} {'RMSE':>8s} {'R²':>8s} {'vs单变量':>10s}")
    print("-" * 70)
    base_mae = mae1
    for name, (mae, rmse, r2, coeffs) in results.items():
        imp = (base_mae - mae) / base_mae * 100
        label = {"poly3": "1. 仅N4_T (3阶多项式)",
                 "linear4": "2. N4_T+AT+temp+N4_R (线性)",
                 "linear8": "3. 全部8参数 (线性)",
                 "hybrid": "4. N4_T多项式+3辅助 (混合)"}[name]
        print(f"{label:30s} {mae:>7.3f}°C {rmse:>7.3f}°C {r2:>7.4f} {imp:>+9.1f}%")

    # ===== 输出实用公式 =====
    print("\n" + "=" * 70)
    print("                  Kibana Scripted Field 可用公式")
    print("=" * 70)

    # 模型4 的公式 (推荐)
    print("""
【推荐方案】混合模型 (MAE={:.3f}°C, R²={:.4f})
在 Kibana Index Pattern → Scripted Fields → 添加 "N4_T0"：
""".format(mae4, r24))

    print("""    Language: painless
    Type: number
    Script:""")
    script_lines = [
        "def n4 = doc['data.params.N4_T.value'].value;",
        "def at = doc['data.params.AT.value'].value;",
        "def tp = doc['data.params.temp.value'].value;",
        "def nr = doc['data.params.N4_R.value'].value;",
        "return {:.6f}".format(c4[0])
        + " + {:.6f} * n4".format(c4[1])
        + " + {:.8f} * n4 * n4".format(c4[2])
        + " + {:.10f} * n4 * n4 * n4".format(c4[3])
        + " + {:.6f} * at".format(c4[4])
        + " + {:.6f} * tp".format(c4[5])
        + " + {:.6f} * nr;".format(c4[6])
    ]
    for line in script_lines:
        print(f"    {line}")

    print("""
【简化方案】仅 N4_T 多项式 (MAE={:.3f}°C, R²={:.4f})
    Language: painless
    Type: number
    Script:""".format(mae1, r21))
    simple = "def n4 = doc['data.params.N4_T.value'].value; return {:.6f} + {:.6f} * n4 + {:.8f} * n4 * n4 + {:.10f} * n4 * n4 * n4;".format(
        c1[0], c1[1], c1[2], c1[3])
    print(f"    {simple}")

    # 保存模型到文件
    model_file = "/tmp/ntc_best_model.py"
    with open(model_file, "w") as f:
        f.write("""# NTC → 热电偶 最佳预测模型（多变量混合）
# 精度: MAE={mae:.3f}°C, RMSE={rmse:.3f}°C, R²={r2:.4f}
# 比单变量 N4_T 提升: {imp:.1f}%

def predict_ot4(n4_t: float, at: float, temp: float, n4_r: float) -> float:
    return {bias:.6f} \\
        + {c1:.6f} * n4_t \\
        + {c2:.8f} * n4_t**2 \\
        + {c3:.10f} * n4_t**3 \\
        + {cat:.6f} * at \\
        + {ctemp:.6f} * temp \\
        + {cnr:.6f} * n4_r


def predict_ot4_simple(n4_t: float) -> float:
    return {s_bias:.6f} \\
        + {s_c1:.6f} * n4_t \\
        + {s_c2:.8f} * n4_t**2 \\
        + {s_c3:.10f} * n4_t**3
""".format(
            mae=mae4, rmse=rmse4, r2=r24, imp=(base_mae - mae4) / base_mae * 100,
            bias=c4[0], c1=c4[1], c2=c4[2], c3=c4[3],
            cat=c4[4], ctemp=c4[5], cnr=c4[6],
            s_bias=c1[0], s_c1=c1[1], s_c2=c1[2], s_c3=c1[3],
        ))
    print(f"\n模型已保存到 {model_file}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "pull":
        pull_data()
    elif os.path.exists(DATA_FILE):
        train_and_evaluate()
    else:
        print("先运行: python3 multivar_analysis.py pull")
