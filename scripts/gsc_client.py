#!/usr/bin/env python3
"""
gsc_client.py — pull Search Console query+page data. OAuth (installed-app flow) or
service account. Credentials path comes from config/arg; tokens cached locally.

Requires: pip install google-api-python-client google-auth-oauthlib ; live network +
a verified GSC property. Gated: exits cleanly if creds are missing so callers degrade.

Usage:
  python gsc_client.py --site "https://driftroast.com/" --creds path/to/creds.json \
     --start 2026-04-01 --end 2026-06-30 --dims query,page --out data/gsc/pull.json
"""
from __future__ import annotations
import argparse, json, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--creds", required=True)
    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True)
    ap.add_argument("--dims", default="query,page")
    ap.add_argument("--row-limit", type=int, default=25000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not os.path.exists(a.creds):
        sys.stderr.write(f"[gsc] creds file {a.creds} not found — GSC disabled; caller should degrade.\n")
        print(json.dumps({"disabled": True, "reason": "no creds"})); return
    try:
        from google.oauth2.service_account import Credentials as SA
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except Exception as e:
        sys.stderr.write(f"[gsc] libraries missing ({e}); pip install google-api-python-client google-auth-oauthlib\n")
        print(json.dumps({"disabled": True, "reason": "libs missing"})); return

    SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
    creds_obj = json.load(open(a.creds))
    if creds_obj.get("type") == "service_account":
        creds = SA.from_service_account_file(a.creds, scopes=SCOPES)
    else:
        tok = a.creds + ".token.json"
        flow = InstalledAppFlow.from_client_secrets_file(a.creds, SCOPES)
        creds = flow.run_local_server(port=0)
        json.dump(json.loads(creds.to_json()), open(tok, "w"))
    svc = build("searchconsole", "v1", credentials=creds)
    body = {"startDate": a.start, "endDate": a.end,
            "dimensions": a.dims.split(","), "rowLimit": a.row_limit}
    resp = svc.searchanalytics().query(siteUrl=a.site, body=body).execute()
    rows = []
    dims = a.dims.split(",")
    for r in resp.get("rows", []):
        row = dict(zip(dims, r["keys"]))
        row.update({"clicks": r.get("clicks"), "impressions": r.get("impressions"),
                    "ctr": r.get("ctr"), "position": r.get("position"),
                    "provenance": "measured", "source": "gsc"})
        rows.append(row)
    json.dump({"site": a.site, "start": a.start, "end": a.end, "dims": dims,
               "count": len(rows), "rows": rows}, open(a.out, "w"), indent=2)
    print(json.dumps({"out": a.out, "rows": len(rows)}))

if __name__ == "__main__":
    main()
