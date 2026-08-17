# -*- coding: utf-8 -*-
"""nxTDA DB 프로필 화면 E2E — 실제 브라우저로 폼을 채우고 '프로필 등록' 버튼을 클릭한다.

증빙 목적:
  1) 화면 버튼 클릭 → DbProfileController → DbProfileService → H2 저장소까지 값이 실제로 도달
  2) 저장 후 재조회 응답(Network 탭 원문)에 평문 비밀번호가 없음
  3) 접속 테스트 요청에 비밀번호가 실려 나가지 않음(요청 본문 자체가 없음)
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8098"
SHOT_DIR = r"C:\Users\NEXTOB~1\AppData\Local\Temp\claude\X--Projects-nxTDA\e88f43f6-8fa9-4de4-8fae-8a89175cbf9f\scratchpad"

ORA = json.load(open(r"X:\Projects\nxDTV\db_presets_src.json", encoding="utf-8"))
ORA = next(p for p in ORA if p.get("name") == "Oracle_asis")
ORA_PW = ORA.get("password") or ""
ADV = ORA.get("advanced_options") or {}

PROFILE_NAME = "Oracle_asis_BROWSER"

captured = []


def mask(text):
    """출력용 마스킹 — 실제 비밀번호 문자열만 가린다. 다른 부분은 원문 그대로 남긴다."""
    if not text:
        return text
    return text.replace(ORA_PW, "<<MASKED-PASSWORD len=%d>>" % len(ORA_PW)) if ORA_PW else text


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()

    def on_request(req):
        if "/api/dbprofile/" in req.url:
            body = None
            try:
                body = req.post_data
            except Exception:
                body = None
            captured.append(("REQUEST", req.method, req.url, body))

    def on_response(res):
        if "/api/dbprofile/" in res.url:
            try:
                body = res.text()
            except Exception:
                body = "<본문 없음>"
            captured.append(("RESPONSE", str(res.status), res.url, body))

    page.on("request", on_request)
    page.on("response", on_response)

    print("=" * 100)
    print("STEP 1 — /dbprofile 화면 진입")
    print("=" * 100)
    page.goto(BASE + "/dbprofile", wait_until="networkidle")
    print("페이지 타이틀:", page.title())
    print("h2.page-title :", page.inner_text("h2.page-title"))
    page.screenshot(path=SHOT_DIR + r"\e2e_01_초기화면.png", full_page=True)

    print()
    print("=" * 100)
    print("STEP 2 — 폼 입력 후 [프로필 등록] 버튼 실제 클릭")
    print("=" * 100)
    page.fill("#profileName", PROFILE_NAME)
    page.select_option("#dbmsType", "ORACLE")
    page.fill("#host", str(ORA["host"]))
    page.fill("#port", str(ORA["port"]))
    page.fill("#databaseName", str(ORA["dbname"]))
    page.fill("#username", str(ORA["user"]))
    page.fill("#password", ORA_PW)
    page.select_option("#sslMode", "")            # SSL 모드 미선택
    page.select_option("#connectType", "service_name")
    page.fill("#serviceName", str(ORA["dbname"]))
    page.fill("#schemaName", str(ADV.get("schema", "")))
    print("입력 완료 — 비밀번호 입력칸 길이:", len(page.input_value("#password")))

    page.click("#btn-save")
    page.wait_for_selector("#alert-msg", timeout=15000)
    page.wait_for_timeout(500)
    print("화면 알림:", page.inner_text("#alert-msg"))
    print("저장 직후 비밀번호 입력칸 길이(화면에 비밀번호를 남기지 않는지):",
          len(page.input_value("#password")))
    page.screenshot(path=SHOT_DIR + r"\e2e_02_등록후.png", full_page=True)

    print()
    print("목록 테이블 렌더 결과:")
    for row in page.query_selector_all("#profile-tbody tr[data-profile-name]"):
        print("   ", " | ".join(c.inner_text().strip().replace("\n", " ")
                                for c in row.query_selector_all("td")))

    print()
    print("=" * 100)
    print("STEP 3 — 저장된 프로필로 [접속테스트] 버튼 실제 클릭 (실 Oracle)")
    print("=" * 100)
    row = page.query_selector(f'#profile-tbody tr[data-profile-name="{PROFILE_NAME}"]')
    row.query_selector("button.btn-test").click()
    page.wait_for_function(
        "() => document.querySelector('#alert-msg') && "
        "document.querySelector('#alert-msg').innerText.includes('%s')" % PROFILE_NAME,
        timeout=60000)
    page.wait_for_timeout(500)
    print("화면 알림:", page.inner_text("#alert-msg"))
    page.screenshot(path=SHOT_DIR + r"\e2e_03_접속테스트.png", full_page=True)

    print()
    print("=" * 100)
    print("STEP 4 — 브라우저가 실제로 주고받은 통신 원문 (개발자도구 Network 탭 상당)")
    print("=" * 100)
    for kind, meta, url, body in captured:
        print(f"\n[{kind}] {meta} {url}")
        if kind == "REQUEST":
            print("  요청본문:", mask(body) if body else "(본문 없음)")
        else:
            print("  응답본문:", mask(body))

    print()
    print("=" * 100)
    print("STEP 5 — 응답 원문 비밀번호 노출 검사 (마스킹 전 원문 기준)")
    print("=" * 100)
    leak = False
    for kind, meta, url, body in captured:
        if kind != "RESPONSE" or not body:
            continue
        has_key = '"password"' in body
        has_val = bool(ORA_PW) and (ORA_PW in body)
        if has_key or has_val:
            leak = True
        print(f"  {meta} {url}")
        print(f"     password 키 포함 = {has_key} / 실제 비밀번호 값 포함 = {has_val}")
    print()
    print("판정:", "❌ 비밀번호 노출 발견" if leak else "✅ 모든 응답에서 password 키/값 모두 미노출")

    browser.close()

sys.exit(0)
