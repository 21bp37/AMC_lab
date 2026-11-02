import os
import sys
import time

import duckdb

UA = "(?i)(\u0443\u043a\u0440\u0430\u0438\u043d|\u0443\u043a\u0440\u0430\u0457\u043d)"
PL = "(?i)(\u043f\u043e\u043b\u044c\u0448|\u043f\u043e\u043b\u044c\u0449|\u043f\u043e\u043b\u044f\u043a|\u043f\u043e\u043b\u044f\u0446|\u043f\u043e\u043b\u044c\u0441\u044c\u043a|\u0432\u0430\u0440\u0448\u0430\u0432)"

parts = [int(a) for a in sys.argv[1:]] or list(range(1, 9))
os.makedirs("data/telegram", exist_ok=True)
for i in parts:
    url = f"https://zenodo.org/records/16949193/files/post_texts_part_{i}.csv?download=1"
    out = f"data/telegram/posts_2022_part_{i}.csv"
    if os.path.exists(out):
        print(f"part {i}: już jest, pomijam", flush=True)
        continue
    for attempt in range(1, 6):
        try:
            con = duckdb.connect()
            con.execute("SET TimeZone = 'UTC'")
            con.execute("INSTALL httpfs; LOAD httpfs;")
            print(f"part {i}: start (próba {attempt})", flush=True)
            tmp = out + ".tmp"
            con.execute(f"""
                COPY (
                  SELECT id, peer_id, date, message, views, forwards
                  FROM read_csv('{url}', header = true, all_varchar = true, ignore_errors = true)
                  WHERE TRY_CAST(date AS TIMESTAMPTZ) >= TIMESTAMPTZ '2022-02-24 00:00:00+00'
                    AND TRY_CAST(date AS TIMESTAMPTZ) <  TIMESTAMPTZ '2023-01-01 00:00:00+00'
                    AND regexp_matches(COALESCE(message, ''), ?)
                    AND regexp_matches(COALESCE(message, ''), ?)
                ) TO '{tmp}' (HEADER)
            """, [UA, PL])
            os.replace(tmp, out)
            n = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{out}')").fetchone()[0]
            print(f"part {i}: gotowe, {n} postów -> {out}", flush=True)
            break
        except Exception as e:
            print(f"part {i}: błąd: {e}", flush=True)
            time.sleep(10)
    else:
        print(f"part {i}: NIE UDAŁO SIĘ, uruchom ponownie: python filtr_telegram.py {i}", flush=True)
