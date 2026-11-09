#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json


def parse_amount(amount):
    if isinstance(amount, (int, float)):
        return float(amount)
    if isinstance(amount, str):
        return float(amount.replace(",", "").strip())
    return float(amount)


latest_events = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except Exception:
            # Ignore lines that can't be read
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            # Ignore events without a txn_id
            continue

        # Only the latest attempt for each txn_id counts
        existing = latest_events.get(txn_id)
        if existing is None or event.get("ts", "") > existing.get("ts", ""):
            latest_events[txn_id] = event

total = 0.0
count = 0

for event in latest_events.values():
    if event.get("status") == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt", "r", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
