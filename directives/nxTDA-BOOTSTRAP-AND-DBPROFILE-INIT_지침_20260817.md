작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT

(수신 지침 사본 — 원문 그대로 보관. 수신일 2026-08-17)

# 배경
nxTDA(Table Data Analysis)는 xDataNexPro 8개 모듈 중 신규 개발 대상(3번 기능).
언어: Java(Spring Boot), DB 직접접속(복제 없음). 이번이 이 프로젝트의 첫 지침이며
X:\Projects\nxTDA는 현재 빈 폴더 상태(git 저장소 아님)이다.

참고 자료(이미 프로젝트에 첨부됨):
- xDataNexPro_제품소개서_v3_3_20250530.pdf (19~23p가 nxTDA 관련)
- nxTDA_요구사항_정리_v3_20260817.docx (전체, 특히 2장 아키텍처 원칙 / 7장 이식대상 / 9-1 DB프로필 / 11장 인프라현황)

이번 지침 범위는 "파트0: 저장소·빌드 골격 초기화"와 "파트1: DB 프로필 관리 모듈"이다.
그 외 기능(문자구성분석, 암호화판정, GROUP BY후보, 스키마변경감지 등)은 이번 범위 아님 — 건드리지 말 것.

---

## 파트0. 프로젝트 저장소·빌드 골격 초기화 (1회성)

1. X:\Projects\nxTDA에 Spring Boot(Java 17, Gradle, Groovy DSL) 프로젝트 골격 생성.
   - groupId/package: com.nextobe.nxtda
   - 모듈 구성(패키지 하위): dbprofile(파트1 대상), (그 외 패키지는 지금 만들지 말 것 — 빈 껍데기 금지)
   - build.gradle에 필요한 최소 의존성만: spring-boot-starter-web, spring-boot-starter-jdbc,
     Oracle/MS-SQL/DB2/Tibero JDBC 드라이버(공개 저장소에 있는 것만, 사내 라이선스 필요한 드라이버는
     주석으로 "라이선스 확보 후 추가" 표시하고 실제 의존성에 넣지 말 것)
   - 프론트: 지금은 정적 리소스 골격만(Tabler CDN 링크 포함한 최소 HTML 1장, "DB 프로필 관리"
     타이틀만 있는 placeholder). 실제 화면 구현은 파트1에 포함.

2. git init, .gitignore(Java/Gradle 표준 + IDE 설정 제외), 최초 커밋
   ("작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT 파트0" 형태의 커밋 메시지)

3. GitHub `nxTDA-src`(Private, 이미 생성됨)에 remote add + `git push -u origin main`

4. `.git\hooks\post-commit`에 자동 push 훅 설치
   (nxDTV에서 이미 검증된 패턴과 동일: `git push origin main`, 실패해도 `exit 0`으로 커밋을 막지 않는 형태)

5. 훅이 실제로 동작하는지 더미 커밋 1개로 검증(push 성공 확인 후 그 더미 커밋은 되돌리지 말고 정상 이력으로 남겨도 됨)

---

## 파트1. DB 프로필 관리 모듈 (nxDTV 설계 이식)

**대상 파일 (신규 생성만, 그 외 파일 건드리지 말 것):**
- `src/main/java/com/nextobe/nxtda/dbprofile/DbProfile.java` (도메인 모델)
- `src/main/java/com/nextobe/nxtda/dbprofile/DbmsType.java` (enum: ORACLE/DB2/TIBERO/MSSQL)
- `src/main/java/com/nextobe/nxtda/dbprofile/ConnectionFactory.java` (어댑터 인터페이스 — DBMS별
  JDBC 연결/SSL 옵션 생성 방식이 다르므로 8번 원칙에 따라 인터페이스+구현체로 분리, 인라인
  if/else로 DBMS 분기 금지)
- `src/main/java/com/nextobe/nxtda/dbprofile/impl/OracleConnectionFactory.java` (1차: Oracle만
  실제 구현. 나머지 DBMS는 같은 인터페이스의 스텁 클래스만 생성하고 TODO 주석 + 미구현 사유 명시.
  스텁을 "구현 완료"로 보고하지 말 것)
- `src/main/java/com/nextobe/nxtda/dbprofile/DbProfileService.java` (저장/조회/비밀번호 처리 —
  nxDTV 설계 스펙 이식: 비밀번호는 서버측에서만 해석, 클라이언트(화면)에는 프로필명만 노출하고
  평문 비밀번호를 응답에 담지 않는 구조)
- `src/main/java/com/nextobe/nxtda/dbprofile/DbProfileController.java` (REST — 화면에서 프로필
  등록/조회/삭제. 비밀번호 값 자체를 응답 JSON에 절대 포함하지 않도록 특히 주의)
- `src/main/resources/templates/dbprofile.html` (Tabler 기반, 프로필 목록+등록 폼)
- 저장소: 파일 기반(H2 또는 SQLite 등 임베디드 DB) — nxTDA 자체 운영 DB 스키마는 아직 없으므로
  프로필 정보 저장용 최소 테이블만 생성. 스키마 파일도 신규 생성만.

**설계 원칙 확인 (구현 전에 반드시 아래를 완료보고서에 명시):**
- nxDTV 코드베이스에서 DB 프로필/SSL 모드/비밀번호 처리 관련 실제 파일을 찾아(경로 모르면 먼저
  탐색해서 정확한 경로 확인 — 탐색 자체는 읽기 전용이라 "다른 파일 수정 금지" 원칙과 무관) 그
  설계(SSL 모드 프로필 기반 처리, 비밀번호 서버측 해석 구조)를 어떻게 이식했는지 대응관계를
  완료보고서에 표로 정리할 것(nxDTV 파일경로 → nxTDA 파일경로 → 이식한 설계 요점).
- nxDTV 코드를 그대로 복사하지 말 것 — Java로 새로 작성.

---

## 검증 요구사항

- 실 서비스 프로세스(JVM) 검증 필요: 작업 시작 전이 아니라 **작업 완료 후** Spring Boot 앱을
  `./gradlew bootRun`으로 기동, 빌드 산출물 타임스탬프가 최종 수정 시각 이후인지 확인 후 검증 진행.
- E2E 검증: 화면(`/dbprofile`)에서 실제로 프로필 등록 버튼을 클릭 → `DbProfileController` →
  `DbProfileService` → 저장소까지 실제로 값이 도달하는지 추적. 저장 후 재조회 시 비밀번호 필드가
  평문으로 응답에 노출되지 않는지 직접 확인(브라우저 개발자도구 Network 탭 캡처 또는 curl 응답
  원문으로 증빙).
- 실제 Oracle DB 접속 테스트가 가능하면: OracleConnectionFactory로 실제 연결 시도 후 성공/실패
  로그 원문 첨부.
- 실제 DB 접속이 이 환경에서 불가능하면(사내 폐쇄망 DB라 접근 불가 등): 15번 원칙에 따라 완료
  보고서에 반드시 고정 줄로 명시 —
  "실검증 상태: 완료 / 대체수단(사유: 실 Oracle DB 접근 불가) / 미검증" 형식.
  이 경우 대체수단으로 로컬 Oracle XE(있으면) 또는 모킹된 JDBC 드라이버 테스트로 대체하고,
  어떤 대체수단을 썼는지까지 명시.
- 입력 형태 사전 나열: 프로필명 중복, 빈 비밀번호, SSL 모드 미선택, 존재하지 않는 DBMS 타입 등
  경계값 케이스를 미리 나열하고 어떤 걸 실제 테스트했는지 표로 제시.
- git diff/커밋해시, 수정 전/후 대조 포함.

## 완료 후

- 검증까지 끝났으면 파트0/파트1 각각 커밋 후 즉시 push(18, 29번). 두 파트가 하나의 지침이지만
  성격이 다르므로(인프라 vs 기능) 별도 커밋으로 나눠도 됨.
- 완료보고 텍스트+증적은 Google Drive `nxTDA-verify\reports\`에 저장, 지침 사본은 이미 위에서
  받은 이 내용을 `nxTDA-verify\directives\`에 저장.
- 완료보고서 전체(작업명 첫줄~마지막줄)를 하나의 마크다운 코드블록으로 작성.
- 완료보고서 본문에 서술형 결론 문단 필수(원자료만 있고 결론 텍스트 없으면 미완료로 간주).

---
권장 모델: Sonnet / 추론 강도: 높음
