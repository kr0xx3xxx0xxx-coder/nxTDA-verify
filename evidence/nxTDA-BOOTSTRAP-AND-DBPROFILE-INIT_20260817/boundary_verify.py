# -*- coding: utf-8 -*-
"""nxTDA DB 프로필 모듈 경계값 검증 — 실행 중인 JVM(포트 8098)에 실제 HTTP 요청을 보낸다.

각 케이스의 요청/응답 원문을 그대로 출력한다(비밀번호 값은 출력하지 않는다).
"""
import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8098"
API = BASE + "/api/dbprofile/profiles"

# 실 Oracle 접속정보 — nxDTV 프리셋 파일에서 읽는다(소스/로그에 비밀번호를 하드코딩하지 않는다).
ORA = json.load(open(r"X:\Projects\nxDTV\db_presets_src.json", encoding="utf-8"))
ORA = next(p for p in ORA if p.get("name") == "Oracle_asis")
ORA_PW = ORA.get("password") or ""


def call(method, path, body=None):
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def mask(body):
    """요청 본문 표시용 — 비밀번호 값은 길이만 남긴다."""
    if not isinstance(body, dict):
        return body
    d = dict(body)
    if "password" in d:
        pw = d["password"]
        d["password"] = f"<len={len(pw)}>" if pw else ""
    return d


CASES = []


def case(no, name, method, path, body, expect):
    CASES.append((no, name, method, path, body, expect))


ORA_BASE = {
    "profileName": "Oracle_asis_TDA",
    "dbmsType": "ORACLE",
    "host": ORA["host"],
    "port": ORA["port"],
    "databaseName": ORA["dbname"],
    "username": ORA["user"],
    "password": ORA_PW,
    "sslMode": "",
    "connectType": "service_name",
    "serviceName": ORA["dbname"],
    "sid": (ORA.get("advanced_options") or {}).get("sid", ""),
    "schemaName": (ORA.get("advanced_options") or {}).get("schema", ""),
}

# ── 정상 경로 ────────────────────────────────────────────────────────────────
case(1, "정상 등록(Oracle, SSL 미선택)", "POST", "/api/dbprofile/profiles", ORA_BASE, "200 created=true")
case(2, "프로필명 중복 재등록(같은 이름 재POST)", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, host=ORA["host"], schemaName="NXDNP"), "200 created=false (in-place 갱신)")
case(3, "빈 비밀번호로 기존 프로필 수정(기존 값 유지)", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, password=""), "200 + hasPassword=true 유지")

# ── 경계/거절 케이스 ─────────────────────────────────────────────────────────
case(4, "빈 비밀번호 + 신규 프로필", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="NEW_NO_PW", password=""), "400 PASSWORD_REQUIRED")
case(5, "프로필명 빈값", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="  "), "400 PROFILE_NAME_REQUIRED")
case(6, "프로필명 101자", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="A" * 101), "400 PROFILE_NAME_TOO_LONG")
case(7, "존재하지 않는 DBMS 타입(POSTGRESQL)", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="PG_NOT_SUPPORTED", dbmsType="POSTGRESQL"), "400 DBMS_TYPE_INVALID")
case(8, "DBMS 타입 미선택(빈값)", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="NO_DBMS", dbmsType=""), "400 DBMS_TYPE_INVALID")
case(9, "호스트 빈값", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="NO_HOST", host=""), "400 HOST_REQUIRED")
case(10, "포트 0", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="PORT_0", port=0), "400 PORT_INVALID")
case(11, "포트 70000", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="PORT_70000", port=70000), "400 PORT_INVALID")
case(12, "포트 null", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="PORT_NULL", port=None), "400 PORT_INVALID")
case(13, "계정 빈값", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="NO_USER", username=""), "400 USERNAME_REQUIRED")
case(14, "SSL 모드 오타(requre)", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="SSL_TYPO", sslMode="requre"), "400 SSL_MODE_INVALID")
case(15, "SSL 모드 정상값(require) 저장", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="Oracle_SSL_REQUIRE", sslMode="require"), "200 sslMode=require")
case(16, "Oracle connectType=sid + SID 빈값", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="SID_MISSING", connectType="sid", sid=""), "400 CONNECT_TARGET_REQUIRED")
case(17, "Oracle connectType 오타(servicename)", "POST", "/api/dbprofile/profiles",
     dict(ORA_BASE, profileName="CT_TYPO", connectType="servicename"), "400 CONNECT_TYPE_INVALID")
case(18, "스텁 DBMS(TIBERO) 프로필 등록", "POST", "/api/dbprofile/profiles",
     {"profileName": "Tibero_stub", "dbmsType": "TIBERO", "host": "192.168.0.99", "port": 8629,
      "databaseName": "tibero", "username": "sys", "password": "dummy-not-used",
      "sslMode": "", "connectType": "", "serviceName": "", "sid": "", "schemaName": ""},
     "200 (등록 자체는 가능)")

print("=" * 100)
print("nxTDA DB 프로필 경계값 검증 — 실행 중 JVM(http://127.0.0.1:8098) 대상")
print("=" * 100)

for no, name, method, path, body, expect in CASES:
    status, text = call(method, path, body)
    print(f"\n--- [케이스 {no}] {name}")
    print(f"    기대       : {expect}")
    print(f"    요청       : {method} {path}")
    print(f"    요청본문   : {json.dumps(mask(body), ensure_ascii=False)}")
    print(f"    응답상태   : {status}")
    print(f"    응답본문   : {text}")

# ── 접속 테스트 ──────────────────────────────────────────────────────────────
print("\n" + "=" * 100)
print("접속 테스트 (비밀번호는 클라이언트가 보내지 않는다 — 요청 본문 없음)")
print("=" * 100)

for no, name, prof, expect in [
    (19, "실 Oracle 접속 테스트", "Oracle_asis_TDA", "200 ok=true + DB 배너"),
    (20, "스텁 어댑터(TIBERO) 접속 테스트", "Tibero_stub", "400 ADAPTER_NOT_IMPLEMENTED"),
    (21, "존재하지 않는 프로필 접속 테스트", "NO_SUCH_PROFILE", "400 PROFILE_NOT_FOUND"),
    (22, "SSL require 프로필 접속 테스트(비SSL 리스너 → 실패 예상)", "Oracle_SSL_REQUIRE",
     "400 CONNECT_FAILED — SSL 옵션이 URL/프로퍼티에 실제 반영됨을 확인"),
]:
    status, text = call("POST", f"/api/dbprofile/profiles/{urllib.parse.quote(prof)}/connection-test")
    print(f"\n--- [케이스 {no}] {name}")
    print(f"    기대       : {expect}")
    print(f"    요청       : POST /api/dbprofile/profiles/{prof}/connection-test  (본문 없음)")
    print(f"    응답상태   : {status}")
    print(f"    응답본문   : {text}")

# ── 목록 응답 비밀번호 노출 검사 ─────────────────────────────────────────────
print("\n" + "=" * 100)
print("목록 응답 원문 — password 노출 검사")
print("=" * 100)
status, text = call("GET", "/api/dbprofile/profiles")
print(f"GET /api/dbprofile/profiles → {status}")
print(text)
print("\n[검사] 응답 원문에 'password' 키 포함 여부 :", "password" in text)
print("[검사] 응답 원문에 저장된 실제 비밀번호 값 포함 여부 :", (ORA_PW in text) if ORA_PW else "N/A")
print("[검사] hasPassword 필드 존재 여부 :", "hasPassword" in text)

status, text = call("GET", "/api/dbprofile/profiles/Oracle_asis_TDA")
print(f"\nGET /api/dbprofile/profiles/Oracle_asis_TDA → {status}")
print(text)
print("\n[검사] 단건 응답에 'password' 키 포함 여부 :", "password" in text)
print("[검사] 단건 응답에 실제 비밀번호 값 포함 여부 :", (ORA_PW in text) if ORA_PW else "N/A")

# ── 삭제 ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 100)
print("삭제 케이스")
print("=" * 100)
for no, name, prof, expect in [
    (23, "정상 삭제", "Oracle_SSL_REQUIRE", "200 ok=true"),
    (24, "존재하지 않는 프로필 삭제", "NO_SUCH_PROFILE", "404 PROFILE_NOT_FOUND"),
]:
    status, text = call("DELETE", f"/api/dbprofile/profiles/{urllib.parse.quote(prof)}")
    print(f"\n--- [케이스 {no}] {name}")
    print(f"    기대     : {expect}")
    print(f"    응답상태 : {status}")
    print(f"    응답본문 : {text}")

status, text = call("GET", "/api/dbprofile/profiles")
print("\n최종 목록:")
print(text)
