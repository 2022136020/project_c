import requests, json

API_KEY    = "AIzaSyCVs6DgBwIFNA0a0BSvxkCz86MxrRfnVCs"
PROJECT_ID = "portfolio-tracker-d3939"
EMAIL      = "demo@portfolio-tracker.app"
PASSWORD   = "demo1234!"

# 1. 로그인 → idToken, uid 획득
auth_res = requests.post(
    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
    json={"email": EMAIL, "password": PASSWORD, "returnSecureToken": True}
)
auth_res.raise_for_status()
data  = auth_res.json()
token = data["idToken"]
uid   = data["localId"]
print(f"로그인 성공: uid={uid}")

BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
HDR  = {"Authorization": f"Bearer {token}"}

def list_docs(path):
    url = f"{BASE}/{path}"
    res = requests.get(url, headers=HDR)
    if res.status_code == 404:
        return []
    res.raise_for_status()
    return res.json().get("documents", [])

def delete_doc(name):
    url = f"https://firestore.googleapis.com/v1/{name}"
    res = requests.delete(url, headers=HDR)
    if res.status_code not in (200, 204):
        print(f"  삭제 실패: {name} ({res.status_code})")

# 2. positions 삭제
positions = list_docs(f"users/{uid}/positions")
print(f"포지션 {len(positions)}개 삭제 중...")
for doc in positions:
    delete_doc(doc["name"])
    print(f"  삭제: {doc['name'].split('/')[-1]}")

# 3. accounts + transactions 삭제
accounts = list_docs(f"users/{uid}/accounts")
print(f"계좌 {len(accounts)}개 삭제 중...")
for acc in accounts:
    acc_id = acc["name"].split("/")[-1]
    # transactions 먼저
    txs = list_docs(f"users/{uid}/accounts/{acc_id}/transactions")
    for tx in txs:
        delete_doc(tx["name"])
    print(f"  계좌 {acc_id}: 거래내역 {len(txs)}개 삭제")
    delete_doc(acc["name"])
    print(f"  계좌 삭제 완료")

print("\n✅ 데모 계정 초기화 완료 — 완전히 새 계정 상태입니다.")
