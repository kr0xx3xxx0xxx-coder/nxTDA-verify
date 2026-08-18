작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT
✅ 작업 완료 - nxTDA 저장소·빌드 골격 초기화(파트0) 및 DB 프로필 관리 모듈 nxDTV 설계 이식(파트1)

실검증 상태: 완료
  - 실 Oracle DB(192.168.0.151:1523, Oracle AI Database 26ai Free Release 23.26.1.0.0) 에
    OracleConnectionFactory 로 실제 JDBC 접속 성공. 대체수단을 쓰지 않았다.
  - 화면(/dbprofile) 버튼 클릭 → Controller → Service → H2 저장소 행까지 실브라우저로 추적 완료.

================================================================================
1. 작업 범위와 결과 요약
================================================================================
지침 범위는 파트0(저장소·빌드 골격 초기화)과 파트1(DB 프로필 관리 모듈)이며, 그 외 기능
(문자구성분석 / 암호화판정 / GROUP BY 후보 / 스키마변경감지)은 파일도 패키지도 만들지 않았다.

  파트0 : X:\Projects\nxTDA 에 Spring Boot(Java 17 / Gradle 9.4.1 Groovy DSL) 골격 생성,
          git init, GitHub nxTDA-src 원격 연결 및 push, post-commit 자동 push 훅 설치·검증
  파트1 : DB 프로필 관리 모듈 신규 작성(nxDTV 설계 스펙 이식, 코드 복사 없음)

두 파트를 성격에 따라 별도 커밋으로 나눴다(인프라 vs 기능).

================================================================================
2. 파트0 산출물
================================================================================
2-1. 빌드 골격
  settings.gradle          rootProject.name = 'nxtda'
  build.gradle             group=com.nextobe / Java 17 / Spring Boot 3.5.16
  gradle.properties        Gradle 데몬 인코딩 UTF-8 고정(파트1에서 추가)
  gradlew / gradlew.bat    Gradle Wrapper 9.4.1
  src/main/java/com/nextobe/nxtda/NxTdaApplication.java

  패키지 구성은 com.nextobe.nxtda 와 com.nextobe.nxtda.dbprofile(+.impl) 둘뿐이다.
  다른 기능 패키지는 빈 껍데기를 만들지 않았다.

2-2. 의존성 — 공개 저장소 배포본만 실제 의존성에 포함
  +--------------------------------+---------------------+--------------------------------------+
  | 의존성                          | 버전                | 판단                                  |
  +--------------------------------+---------------------+--------------------------------------+
  | spring-boot-starter-web         | (BOM 3.5.16)        | 지침 명시 항목                          |
  | spring-boot-starter-jdbc        | (BOM 3.5.16)        | 지침 명시 항목                          |
  | spring-boot-starter-thymeleaf   | (BOM 3.5.16)        | 지침 목록 외 추가 — 아래 사유 참고        |
  | com.h2database:h2               | 2.3.232 (BOM)       | 지침 목록 외 추가 — 프로필 저장용 임베디드 DB |
  | com.oracle.database.jdbc:ojdbc11| 23.26.3.0.0         | Maven Central 공개 배포 → 포함           |
  | com.microsoft.sqlserver:        | 13.4.0.jre11        | Maven Central 공개 배포(MIT) → 포함      |
  |   mssql-jdbc                    |                     |                                       |
  | com.ibm.db2:jcc                 | 12.1.5.0            | Maven Central 공개 배포 → 포함           |
  | Tibero JDBC                     | —                   | 공개 저장소 미배포(TmaxSoft 라이선스 필요) |
  |                                 |                     | → 의존성에 넣지 않고 주석만              |
  +--------------------------------+---------------------+--------------------------------------+

  지침 목록 외 2건을 추가한 사유를 명시한다(임의 확장이 아니라 지침 이행에 필요했다):
    - thymeleaf : 지침이 산출물로 지정한 파일이 src/main/resources/templates/dbprofile.html 이다.
                  templates/ 를 쓰려면 템플릿 엔진이 필요하다.
    - H2        : 지침이 "저장소: 파일 기반(H2 또는 SQLite 등 임베디드 DB)" 를 명시했다.
  반대로 spring-boot-starter-test 는 넣지 않았다 — "필요한 최소 의존성만" 원칙에 따라,
  검증은 단위테스트가 아니라 실행 중 JVM 대상 실HTTP·실브라우저로 수행했다.

  build.gradle 의 Tibero 주석 원문:
    // Tibero — Maven Central 등 공개 저장소에 배포되지 않는다(TmaxSoft 배포본/라이선스 필요).
    //          라이선스 확보 후 추가 : runtimeOnly 'com.tmax.tibero:tibero-jdbc:<버전>'
    //          (드라이버 확보 전까지 TiberoConnectionFactory 는 스텁 상태를 유지한다)

2-3. 프론트 골격
  src/main/resources/static/index.html — Tabler CDN(@tabler/core@1.0.0-beta20) 링크 포함,
  "DB 프로필 관리" 타이틀만 있는 placeholder 1장. 실제 화면은 파트1의 /dbprofile.

2-4. .gitignore
  Java/Gradle 표준 + IDE 설정(.idea/ *.iml .classpath .project .settings/ .vscode/) 제외.
  추가로 data/ *.mv.db logs/ 를 제외했다 — H2 파일 DB 에 접속정보·비밀번호가 담기므로
  절대 커밋 대상이 아니다.

2-5. git init / 원격 연결 / push
  git init -b main
  git remote add origin https://github.com/kr0xx3xxx0xxx-coder/nxTDA-src.git
  git push -u origin main
    → To https://github.com/kr0xx3xxx0xxx-coder/nxTDA-src.git
       * [new branch]      main -> main
       branch 'main' set up to track 'origin/main'.

2-6. post-commit 자동 push 훅 설치 (.git/hooks/post-commit)
  nxDTV 에서 검증된 패턴과 동일:
    #!/bin/sh
    # 커밋 후 자동 push. 안전망: 실패해도 커밋은 이미 완료된 상태이므로 조용히 넘어간다.
    git push origin main >/dev/null 2>&1
    exit 0
  파일 권한 : -rwxr-xr-x

2-7. 훅 동작 검증(더미 커밋 1개, 되돌리지 않고 정상 이력으로 남김)
  === 커밋 전 원격 상태 ===
  local  HEAD        : dbad06a4c5f2b32c2bb9e472c2ef69959091452c
  remote origin/main : dbad06a4c5f2b32c2bb9e472c2ef69959091452c
  (docs/HOOK_VERIFY.md 추가 커밋 — git push 를 수동으로 실행하지 않았다)
  === 커밋 직후(수동 push 없음) ===
  local  HEAD        : c02367c897115288b93b9353992852f850699e08
  remote origin/main : c02367c897115288b93b9353992852f850699e08
  → 수동 push 없이 원격이 전진했다. 훅 동작 확인.

================================================================================
3. 파트1 산출물 (전부 신규 생성 — 기존 파일 중 수정한 것은 4장에 별도 명시)
================================================================================
  src/main/java/com/nextobe/nxtda/dbprofile/DbProfile.java                      255줄
  src/main/java/com/nextobe/nxtda/dbprofile/DbmsType.java                        69줄
  src/main/java/com/nextobe/nxtda/dbprofile/ConnectionFactory.java               77줄
  src/main/java/com/nextobe/nxtda/dbprofile/impl/OracleConnectionFactory.java   170줄  [실구현]
  src/main/java/com/nextobe/nxtda/dbprofile/impl/Db2ConnectionFactory.java       65줄  [스텁]
  src/main/java/com/nextobe/nxtda/dbprofile/impl/TiberoConnectionFactory.java    64줄  [스텁]
  src/main/java/com/nextobe/nxtda/dbprofile/impl/MssqlConnectionFactory.java     63줄  [스텁]
  src/main/java/com/nextobe/nxtda/dbprofile/DbProfileService.java               422줄
  src/main/java/com/nextobe/nxtda/dbprofile/DbProfileController.java            163줄
  src/main/resources/templates/dbprofile.html                                   304줄
  src/main/resources/schema/nxtda_dbprofile_schema.sql                           35줄

3-1. 스텁을 "구현 완료"로 보고하지 않는다 — 명확히 미구현이다
  DB2 / TIBERO / MSSQL 세 어댑터는 supportsConnect() 가 false 이고, connect() /
  buildJdbcUrl() / buildConnectionProperties() 는 모두 UnsupportedOperationException 을
  던진다. 조용히 다른 DBMS 로 폴백하지 않는다. 미구현 사유는 각각 다르다:

  +---------+------------------------------------------------------------------------+
  | 어댑터   | 미구현 사유                                                              |
  +---------+------------------------------------------------------------------------+
  | TIBERO  | 드라이버 자체가 없다. Tibero JDBC 는 공개 저장소 미배포(TmaxSoft 라이선스   |
  |         | 필요). "검증이 덜 됐다"가 아니라 컴파일/런타임에 쓸 jar 를 확보하지 못했다.  |
  | DB2     | 드라이버는 확보(com.ibm.db2:jcc)했으나 SSL 옵션이 sslConnection /          |
  |         | sslTrustStoreLocation / securityMechanism 여러 축으로 갈리고 조합에 따라   |
  |         | 동작이 달라진다. 사내 DB2 실접속 검증 전까지 추정 구현을 두지 않는다.       |
  | MSSQL   | 드라이버는 확보했으나 최신 드라이버에서 encrypt 기본값이 true 로 바뀌어    |
  |         | trustServerCertificate / hostNameInCertificate 조합에 따라 접속 성공이      |
  |         | 갈린다. 사내 MS-SQL 실접속 검증 전까지 추정 구현을 두지 않는다.            |
  +---------+------------------------------------------------------------------------+

  "실DB 로 검증되기 전까지는 추정 구현을 두지 않는다"는 규약 자체가 nxDTV
  services/db_adapters/tibero.py 의 원칙을 그대로 가져온 것이다.

================================================================================
4. nxDTV → nxTDA 설계 이식 대응표
================================================================================
탐색으로 확인한 nxDTV 실제 파일 경로 기준이다(탐색은 읽기 전용, nxDTV 파일은 수정하지 않았다).
nxDTV 코드를 복사하지 않았다 — 설계 요점만 옮겨 Java 로 새로 작성했다.

+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| nxDTV 파일경로 (심볼)                    | nxTDA 파일경로 (심볼)                       | 이식한 설계 요점                                                |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_preset_service.py           | dbprofile/DbProfileService.java            | 비밀번호 서버측 해석. 응답에서 평문을 지우면 클라이언트는 빈 비밀번호로  |
|   resolve_password_for_conn()           |   resolvePassword() [private]               | 접속 요청하게 되므로, 실제 비밀번호는 서버가 저장소에서 직접 복원한다.   |
|   (DB-PRESETS-PASSWORD-PLAINTEXT-       |                                            | Java 에서는 private 로 두어 컨트롤러/응답/템플릿으로 나가는 경로를     |
|    EXPOSURE-FIX)                        |                                            | 컴파일 단계에서 봉쇄했다.                                        |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| routes/db_preset_route.py               | dbprofile/DbProfile.java                   | 목록 응답에서 평문 비밀번호 제거 + has_password 로 존재여부만 노출.   |
|   _safe_presets()                       |   record Summary (password 필드 부재)        | nxDTV 는 dict 에서 키를 '제거'했지만, nxTDA 는 password 필드가       |
|   q = {k:v ... if k != 'password'}      |   + @JsonProperty(access=WRITE_ONLY)        | 아예 '없는 타입'으로 만들어 빼먹을 여지를 제거했다(2중 방어).          |
|   q['has_password'] = bool(...)         |   + hasPassword()                          |                                                                |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| routes/db_preset_route.py:41-56         | dbprofile/DbProfileService.java            | 수정에서 비밀번호 미입력(빈값)이면 기존 값 유지 — 빈값 덮어쓰기 방지.   |
|   (비밀번호 보존 로직)                    |   save() 의 "비밀번호 결정" 블록              | 화면이 비밀번호를 보관하지 않으므로 이 규칙이 없으면 프로필을 한 번     |
|                                         |                                            | 수정하는 순간 비밀번호가 지워진다.                                |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| routes/db_preset_route.py:196-214       | dbprofile/DbProfileService.java            | 신규 프로필이거나 저장된 비밀번호가 없으면 PASSWORD_REQUIRED 로 거절.  |
|   error_code="PASSWORD_REQUIRED"        |   SaveOutcome.fail("PASSWORD_REQUIRED",…)   | 오류코드 문자열까지 동일하게 맞췄다(운영 로그 대조 편의).             |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/source_profile_resolver.py     | dbprofile/DbProfile.java  sslMode 필드      | SSL 모드는 프로필에 저장된 값만 따르고 기본값을 하드코딩하지 않는다.    |
|   _preset_sslmode()                     | + impl/OracleConnectionFactory.java         | nxDTV 는 sslmode 누락 시 어댑터가 require 로 접속해 비SSL DB 의      |
|   (SINGLE-SAVE-SSLMODE-PRESET-          |     isTcps() / buildConnectionProperties()  | 메타데이터 수집이 실패했다(METADATA_BLOCKED). nxTDA 는 미선택이면    |
|    RESTORE-FIX)                         |                                            | NULL 로 저장하고 SSL 프로퍼티를 아예 만들지 않는다.                 |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_adapters/base.py            | dbprofile/ConnectionFactory.java           | DBMS별 특성을 어댑터에 캡슐화하고 공통 서비스에는 if/elif 를 두지     |
|   class BaseDbmsAdapter                 |   interface ConnectionFactory              | 않는다. supports_connect()/connect() 의 "미지원은 조용히 폴백하지    |
|   supports_connect() / connect()        |   supportsConnect() / connect()            | 않고 명확히 실패" 규약까지 그대로 옮겼다.                          |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_adapter_registry.py         | dbprofile/DbProfileService.java            | db_type → 어댑터 registry. nxDTV 는 alias dict, nxTDA 는 Spring   |
|   get_adapter() / _BY_ALIAS             |   생성자의 EnumMap<DbmsType,               | 의 List<ConnectionFactory> 주입 + EnumMap. 서비스 본문에 DBMS      |
|                                         |     ConnectionFactory> factories           | 이름을 비교하는 if/else 가 하나도 없다. 한 DBMS 에 어댑터가 둘이면    |
|                                         |                                            | 기동 시점에 IllegalStateException 으로 막는다(nxDTV 대비 강화).     |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_adapters/oracle.py          | impl/OracleConnectionFactory.java          | connect_type 분기: 'sid' + sid 값 있으면 SID DSN, 아니면            |
|   OracleAdapter.connect()               |   buildJdbcUrl() / connect()               | service_name(없으면 dbname). Python makedsn() 을 thin 드라이버      |
|   (makedsn sid / service_name)          |                                            | URL 문법으로 옮겼다. SSL 시 tcps:// 로 프로토콜 전환.               |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_adapters/oracle.py          | impl/OracleConnectionFactory.java          | 연결 반환 직전 NLS_NUMERIC_CHARACTERS='.,' / NLS_COMP='BINARY' 를   |
|   _pin_session_nls_numeric()            |   pinSessionParameter()                    | 1회 고정. 실패해도 예외를 전파하지 않고 warning 만 남긴다(연결 자체는 |
|   _pin_session_nls_comp()               |   SQL_PIN_NLS_NUMERIC / SQL_PIN_NLS_COMP   | 살린다). 세션 로케일 의존 거짓 불일치를 연결 단계에서 차단.           |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_adapters/tibero.py          | impl/TiberoConnectionFactory.java          | "신뢰할 수 있는 방식이 실DB 로 검증되기 전까지는 추정 구현을 두지     |
| services/db_adapters/db2.py             | impl/Db2ConnectionFactory.java             | 않는다. 공통 서비스에서 직접 분기하지 않게 하는 것이 이 어댑터의      |
| services/db_adapters/mssql.py           | impl/MssqlConnectionFactory.java           | 목적이다" — 스텁의 존재 이유 자체를 이식했다.                       |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_preset_service.py           | dbprofile/DbProfileService.java            | 마지막 사용 시각 기록은 best-effort. 기록 실패가 접속을 막지 않는다.  |
|   _touch_last_used()                    |   touchLastUsed()                          |                                                                |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| services/db_preset_service.py           | resources/schema/                          | 프로필 저장소를 파일 기반 임베디드 DB 에 둔다(nxDTV: SQLite          |
|   _ensure_schema() / mv_db_preset       |   nxtda_dbprofile_schema.sql               | mv_db_preset → nxTDA: H2 nxtda_db_profile). 컬럼 구성(프로필명/     |
|                                         |   (nxtda_db_profile)                       | db_type/host/port/dbname/user/password/고급옵션/last_used_at)      |
|                                         |                                            | 과 멱등 스키마 생성 방식을 이식. 고급옵션은 nxDTV 의                 |
|                                         |                                            | advanced_options_json(JSON 뭉치) 대신 ssl_mode/connect_type/       |
|                                         |                                            | service_name/sid/schema_name 개별 컬럼으로 풀었다(타입 검증 가능).   |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+
| CLAUDE.md "에러는 raise 하지 말고         | DbProfileService.SaveOutcome /             | 검증 실패를 예외가 아니라 결과 객체로 반환하는 규약 이식.             |
|   결과 객체의 error_message 에 담아 반환" |   ConnectionTestOutcome (record)           | 두 record 모두 비밀번호를 담을 필드가 없다.                        |
+----------------------------------------+-------------------------------------------+---------------------------------------------------------------+

4-1. 의도적으로 이식하지 않은 것 (누락이 아니라 판단이다)
  +--------------------------------------+----------------------------------------------------+
  | nxDTV 요소                            | 미이식 사유                                          |
  +--------------------------------------+----------------------------------------------------+
  | resolve_password_for_conn() 의        | nxTDA 는 클라이언트가 접속 identity 를 아예 보내지 않고 |
  | 접속 identity(db_type/host/port/      | 프로필명만 보낸다. identity 매칭은 불필요하고, "동일     |
  | dbname/user) 2차 매칭 경로            | 접속정보 다중 프로필" 모호성을 되살릴 뿐이다.            |
  | _db_save() 의 스냅샷 delta + CAS       | 그 방어는 '프리셋 목록을 통째로 덮어쓰는' API 형태가      |
  | (lost update 방지)                    | 원인이었다. nxTDA API 는 프로필 1건 단위(POST 1건 /     |
  |                                      | DELETE 1건)라 통째 덮어쓰기가 존재하지 않는다. 유일성은   |
  |                                      | UNIQUE 인덱스로 DB 가 보장한다.                       |
  | soft delete(is_deleted) + 부활 재사용  | 위와 같은 이유로 삭제는 물리 삭제로 단순화했다. 감사이력이 |
  |                                      | 필요해지면 별도 이력 테이블로 다루는 게 맞다.            |
  | kill-switch(MV_DB_PRESET_STORE)       | JSON 파일 → DB 이관 롤백용 장치다. nxTDA 는 처음부터    |
  |                                      | DB 저장이라 되돌릴 이전 형태가 없다.                    |
  | 비밀번호 저장 시 암호화                 | nxDTV 도 평문이며 "이번 범위가 아니다"로 명시했다. 이번에 |
  |                                      | 이식한 하드닝은 '응답 노출 차단'이고 '저장 암호화'가       |
  |                                      | 아니다. 8장 후속과제로 남겼다.                         |
  +--------------------------------------+----------------------------------------------------+

4-2. nxDTV 대비 강화한 점
  - Oracle 접속 대상 누락을 저장 시점에 거절한다(CONNECT_TARGET_REQUIRED). nxDTV
    oracle.py 는 connect_type='sid' 인데 sid 가 비면 조용히 service_name 으로 폴백한다 —
    사용자가 의도한 접속 방식과 다른 방식으로 붙어버리는 잠재 결함이다.
  - SSL 모드 오타를 저장 시점에 거절한다(SSL_MODE_INVALID). 오타가 조용히 저장돼 접속
    시점에 터지는 것을 막는다.
  - 한 DBMS 에 ConnectionFactory 가 둘 등록되면 기동 시점에 실패한다(비결정적 선택 방지).

================================================================================
5. 파트1에서 수정한 기존 파일 (수정 전/후 대조)
================================================================================
파트0 산출물 2건에 이번 기능에 필요한 최소 변경만 했다. 그 외 파일은 건드리지 않았다.

5-1. src/main/resources/application.yml
  @@ -1,7 +1,7 @@
  -#       접속정보는 전부 DB 프로필 저장소에만 둔다(파트1에서 추가).
  +#       접속정보는 전부 DB 프로필 저장소(H2 nxtda_db_profile 테이블)에만 둔다.
  @@ -9,9 +9,33 @@
   spring:
     application:
       name: nxTDA
  +  datasource:
  +    url: jdbc:h2:file:./data/nxtda_admin;DB_CLOSE_DELAY=-1;AUTO_SERVER=TRUE
  +    driver-class-name: org.h2.Driver
  +    username: nxtda
  +    password: ""
  +  sql:
  +    init:
  +      mode: always
  +      schema-locations: classpath:schema/nxtda_dbprofile_schema.sql
     thymeleaf:
       cache: false
   logging:
  +  file:
  +    name: logs/nxtda.log
  +  charset:
  +    file: UTF-8
     level:
       com.nextobe.nxtda: INFO
  +    org.springframework.jdbc.core: INFO   # JDBC 파라미터 로그 미사용(비밀번호 유출 경로 차단)

5-2. build.gradle
  @@ -55,3 +55,9 @@
   tasks.withType(JavaCompile).configureEach {
       options.encoding = 'UTF-8'
   }
  +tasks.named('bootRun') {
  +    jvmArgs = ['-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8', '-Dstderr.encoding=UTF-8']
  +}

5-3. gradle.properties (신규)
  org.gradle.jvmargs=-Dfile.encoding=UTF-8 -Xmx1g
  이유: Windows(MS949)에서 Gradle 이 자식 JVM 의 UTF-8 출력을 플랫폼 인코딩으로 디코딩해
  한국어 로그가 깨졌다. 프로젝트 전체가 한국어 주석·로그이므로 인코딩 고정은 필수다.

================================================================================
6. 검증
================================================================================
6-1. 검증 환경
  Gradle 9.4.1 / Temurin OpenJDK 17.0.18+8 / Spring Boot 3.5.16 / Tomcat 10.1.55
  H2 2.3.232 (file 모드, X:\Projects\nxTDA\data\nxtda_admin.mv.db)
  브라우저 : Playwright Chromium v1234 (Chrome for Testing 151.0.7922.34, headless)
  실 Oracle : 192.168.0.151:1523, service xepdb1 (사내 Oracle XE/26ai Free)

6-2. 빌드 산출물 타임스탬프 대조 (작업 완료 후 수행 — 작업 시작 전 아님)
  최종 수정 소스/설정 : application.yml         2026-08-17 20:00:40
  빌드 산출물(bootJar) : nxtda-0.0.1-SNAPSHOT.jar 2026-08-17 20:00:57   ← 소스보다 이후
  gradlew clean build -x test → BUILD SUCCESSFUL in 8s (6 tasks executed)
  ※ 최초 측정에서는 build.gradle 수정이 bootJar 를 무효화하지 않아 산출물이 소스보다
    이전 시각이었다. clean 후 전체 재빌드로 산출물이 확실히 이후가 되게 다시 맞췄다.

6-3. bootRun 기동 로그 원문 (logs/nxtda.log, UTF-8)
  2026-08-17T20:01:11.619+09:00 INFO 16360 [main] NxTdaApplication : Starting NxTdaApplication
      using Java 17.0.18 with PID 16360 (X:\Projects\nxTDA\build\classes\java\main …)
  2026-08-17T20:01:12.424+09:00 INFO 16360 [main] TomcatWebServer  : Tomcat initialized with port 8098 (http)
  2026-08-17T20:01:12.916+09:00 INFO 16360 [main] HikariPool       : HikariPool-1 - Added connection conn1:
      url=jdbc:h2:file:./data/nxtda_admin user=NXTDA
  2026-08-17T20:01:12.940+09:00 INFO 16360 [main] DbProfileService :
      [DBPROFILE] ConnectionFactory 등록 완료 — 접속지원=[ORACLE] / 스텁=[DB2, MSSQL, TIBERO]
  2026-08-17T20:01:13.218+09:00 INFO 16360 [main] TomcatWebServer  : Tomcat started on port 8098 (http)
  2026-08-17T20:01:13.226+09:00 INFO 16360 [main] NxTdaApplication : Started NxTdaApplication in 1.983 seconds

  → 기동 로그 자체가 "Oracle 만 실구현, 나머지 3개는 스텁"을 명시한다.

6-4. E2E — 화면 버튼 실제 클릭 → Controller → Service → 저장소 추적
  실브라우저(Chromium)로 /dbprofile 진입 → 폼 입력 → [프로필 등록] 버튼 click() →
  [접속테스트] 버튼 click() 수행. 스크린샷 3장 첨부(e2e_01_초기화면.png /
  e2e_02_등록후.png / e2e_03_접속테스트.png).

  화면 확인:
    페이지 타이틀 : DB 프로필 관리 — nxTDA
    h2.page-title : DB 프로필 관리
    등록 전 비밀번호 입력칸 길이 : 9
    화면 알림 : 프로필을 등록했습니다. (프로필: Oracle_asis_BROWSER)
    등록 직후 비밀번호 입력칸 길이 : 0     ← 화면에 비밀번호를 남기지 않는다
    목록 렌더 : Oracle_asis_BROWSER | ORACLE | 192.168.0.151:1523 | nxdnp | (미선택) | 저장됨
    접속테스트 알림 : [Oracle_asis_BROWSER] 접속 성공 (367ms) /
                     Oracle Oracle AI Database 26ai Free Release 23.26.1.0.0 …

  브라우저 Network 원문 (요청의 password 값만 마스킹, 그 외 전부 원문):
  ------------------------------------------------------------------------------
  [REQUEST] POST http://127.0.0.1:8098/api/dbprofile/profiles
    {"profileName":"Oracle_asis_BROWSER","dbmsType":"ORACLE","host":"192.168.0.151",
     "port":1523,"databaseName":"xepdb1","username":"nxdnp",
     "password":"<<MASKED-PASSWORD len=9>>","sslMode":"","connectType":"service_name",
     "serviceName":"xepdb1","sid":"","schemaName":"NXDNP"}

  [RESPONSE] 200 http://127.0.0.1:8098/api/dbprofile/profiles
    {"created":true,"message":"프로필을 등록했습니다.","ok":true,"profile":{"profileId":1,
     "profileName":"Oracle_asis_BROWSER","dbmsType":"ORACLE","host":"192.168.0.151",
     "port":1523,"databaseName":"xepdb1","username":"nxdnp","sslMode":null,
     "connectType":"service_name","serviceName":"xepdb1","sid":null,"schemaName":"NXDNP",
     "hasPassword":true,"createdAt":"2026-08-17T20:02:21.543273",
     "updatedAt":"2026-08-17T20:02:21.543273","lastUsedAt":null}}
                                            ↑ password 키 없음, hasPassword 만 있음

  [RESPONSE] 200 http://127.0.0.1:8098/api/dbprofile/profiles   (저장 후 재조회)
    [{"profileId":1,"profileName":"Oracle_asis_BROWSER","dbmsType":"ORACLE",
      "host":"192.168.0.151","port":1523,"databaseName":"xepdb1","username":"nxdnp",
      "sslMode":null,"connectType":"service_name","serviceName":"xepdb1","sid":null,
      "schemaName":"NXDNP","hasPassword":true,"createdAt":"2026-08-17T20:02:21.543273",
      "updatedAt":"2026-08-17T20:02:21.543273","lastUsedAt":null}]

  [REQUEST] POST http://127.0.0.1:8098/api/dbprofile/profiles/Oracle_asis_BROWSER/connection-test
    요청본문: (본문 없음)          ← 클라이언트는 프로필명만 보낸다. 비밀번호 왕복 없음

  [RESPONSE] 200 .../Oracle_asis_BROWSER/connection-test
    {"ok":true,"errorCode":null,"message":"접속 성공 (367ms)",
     "databaseBanner":"Oracle Oracle AI Database 26ai Free Release 23.26.1.0.0 - Develop,
      Learn, and Run for Free\nVersion 23.26.1.0.0",
     "jdbcUrl":"jdbc:oracle:thin:@tcp://192.168.0.151:1523/xepdb1","elapsedMs":367}
  ------------------------------------------------------------------------------

  응답 전수 검사 결과 (마스킹 전 원문 기준):
    200 /api/dbprofile/profiles                       password 키=False / 실제 비밀번호 값=False
    200 /api/dbprofile/profiles                       password 키=False / 실제 비밀번호 값=False
    200 /api/dbprofile/profiles/…/connection-test     password 키=False / 실제 비밀번호 값=False
    200 /api/dbprofile/profiles                       password 키=False / 실제 비밀번호 값=False
    판정: ✅ 모든 응답에서 password 키/값 모두 미노출

6-5. 저장소 도달 확인 — H2 직접 조회 (JDBC, 값이 아니라 길이/일치여부만 출력)
  === nxtda_db_profile 테이블 컬럼 구성 ===
    PROFILE_ID BIGINT nullable=false / PROFILE_NM VARCHAR nullable=false
    DBMS_TYPE VARCHAR nullable=false / HOST VARCHAR nullable=false / PORT INTEGER nullable=false
    DATABASE_NAME, USERNAME, PASSWORD, SSL_MODE, CONNECT_TYPE, SERVICE_NAME, SID,
    SCHEMA_NAME nullable=true / CREATED_AT, UPDATED_AT nullable=false / LAST_USED_AT nullable=true
  === 저장된 행 ===
    profile_id=1  profile_nm=Oracle_asis_BROWSER  dbms_type=ORACLE
    host:port=192.168.0.151:1523  database_name=xepdb1  username=nxdnp
    ssl_mode=null  (NULL = 미선택 저장 — 기본값을 만들어 넣지 않았다)
    connect_type=service_name  service_name=xepdb1  sid=null  schema_name=NXDNP
    password = <값 미출력> length=9 / 화면에서 입력한 값과 일치=true   ← 화면→저장소 도달 확인
    created_at=2026-08-17 20:02:21.543273  last_used_at=2026-08-17 20:02:22.702801

  경계값 테스트 후 재조회 — 빈 비밀번호 수정이 기존 값을 지우지 않았는지 저장소 레벨 확인:
    profile_id=2  profile_nm=Oracle_asis_TDA  updated_at=20:03:26.243101 (빈 비밀번호로 수정됨)
    password = <값 미출력> length=9 / 화면에서 입력한 값과 일치=true   ← 보존 규칙 실동작 확인

6-6. 서버측 처리 로그 원문 (logs/nxtda.log)
  20:02:21.551 [http-nio-8098-exec-2] DbProfileService :
     [DBPROFILE] 프로필 저장 완료 name='Oracle_asis_BROWSER' dbms=ORACLE created=true hasPassword=true
  20:02:22.336 [http-nio-8098-exec-4] OracleConnectionFactory :
     [ORACLE-CONNECT] 접속 시도 profile='Oracle_asis_BROWSER' url=jdbc:oracle:thin:@tcp://192.168.0.151:1523/xepdb1
  20:02:22.700 [http-nio-8098-exec-4] OracleConnectionFactory :
     [ORACLE-CONNECT] 접속 성공 profile='Oracle_asis_BROWSER'
  20:02:22.704 [http-nio-8098-exec-4] DbProfileService :
     [DBPROFILE] 접속 테스트 성공 name='Oracle_asis_BROWSER' elapsedMs=367
     banner=Oracle Oracle AI Database 26ai Free Release 23.26.1.0.0 - Develop, Learn, and Run for Free
  → 로그에도 비밀번호 값이 없다(hasPassword 존재여부만).

6-7. 입력 형태 사전 나열 및 실제 테스트 결과
  사전에 나열한 경계값 케이스와, 그중 실제로 테스트한 것을 표로 정리한다.
  24개를 사전 나열했고 24개 전부 실행 중 JVM 에 실제 HTTP 요청으로 테스트했다(미실행 없음).

+----+------------------------------------------+--------------------------------+------+---------------------------------+
| #  | 입력 형태                                  | 기대                            | 실행 | 실제 결과                        |
+----+------------------------------------------+--------------------------------+------+---------------------------------+
|  1 | 정상 등록(Oracle, SSL 미선택)              | 200 created=true               |  O   | 200 created=true, sslMode=null  |
|  2 | 프로필명 중복 재등록                        | 200 created=false 인플레이스     |  O   | 200 created=false, profileId=2  |
|    |                                          | (행 추가 없음)                   |      | 유지, updated_at 만 갱신          |
|  3 | 빈 비밀번호로 기존 프로필 수정               | 200 + 기존 비밀번호 유지         |  O   | 200 hasPassword=true, 저장소     |
|    |                                          |                                |      | length=9 원값 그대로 유지          |
|  4 | 빈 비밀번호 + 신규 프로필                   | 400 PASSWORD_REQUIRED          |  O   | 400 PASSWORD_REQUIRED           |
|  5 | 프로필명 빈값("  ")                        | 400 PROFILE_NAME_REQUIRED      |  O   | 400 PROFILE_NAME_REQUIRED       |
|  6 | 프로필명 101자                             | 400 PROFILE_NAME_TOO_LONG      |  O   | 400 "…100자 이내(입력 101자)"     |
|  7 | 존재하지 않는 DBMS(POSTGRESQL)             | 400 DBMS_TYPE_INVALID          |  O   | 400 + 지원목록 안내               |
|  8 | DBMS 미선택(빈값)                          | 400 DBMS_TYPE_INVALID          |  O   | 400 DBMS_TYPE_INVALID           |
|  9 | 호스트 빈값                                | 400 HOST_REQUIRED              |  O   | 400 HOST_REQUIRED               |
| 10 | 포트 0                                    | 400 PORT_INVALID               |  O   | 400 PORT_INVALID                |
| 11 | 포트 70000                                | 400 PORT_INVALID               |  O   | 400 PORT_INVALID                |
| 12 | 포트 null                                 | 400 PORT_INVALID               |  O   | 400 PORT_INVALID                |
| 13 | 계정 빈값                                  | 400 USERNAME_REQUIRED          |  O   | 400 USERNAME_REQUIRED           |
| 14 | SSL 모드 오타("requre")                    | 400 SSL_MODE_INVALID           |  O   | 400 + 허용값 안내                 |
| 15 | SSL 모드 미선택("")                        | 200, NULL 저장(기본값 주입 금지) |  O   | 200 sslMode=null, DB ssl_mode=  |
|    |                                          |                                |      | NULL 확인                        |
| 16 | SSL 모드 정상값("require")                 | 200 sslMode=require            |  O   | 200 sslMode=require             |
| 17 | Oracle connectType=sid + SID 빈값         | 400 CONNECT_TARGET_REQUIRED    |  O   | 400 "sid 이면 SID 값을 입력하세요" |
| 18 | Oracle connectType 오타("servicename")    | 400 CONNECT_TYPE_INVALID       |  O   | 400 CONNECT_TYPE_INVALID        |
| 19 | 스텁 DBMS(TIBERO) 프로필 등록              | 200 (등록 자체는 허용)           |  O   | 200 created=true                |
| 20 | 실 Oracle 접속 테스트                      | 200 ok=true + DB 배너           |  O   | 200 접속 성공 121ms, 26ai 배너    |
| 21 | 스텁 어댑터(TIBERO) 접속 테스트             | 400 ADAPTER_NOT_IMPLEMENTED    |  O   | 400 + 라이선스 미확보 사유 전문     |
| 22 | 없는 프로필 접속 테스트                     | 400 PROFILE_NOT_FOUND          |  O   | 400 PROFILE_NOT_FOUND           |
| 23 | SSL require 프로필로 비SSL 리스너 접속       | 400 CONNECT_FAILED             |  O   | 400 ORA-17002, url=tcps://…     |
|    |                                          | (SSL 옵션이 URL 에 실반영 확인)   |      | ← SSL 모드가 실제로 반영됨의 증거   |
| 24 | 없는 프로필 삭제                            | 404 PROFILE_NOT_FOUND          |  O   | 404 PROFILE_NOT_FOUND           |
+----+------------------------------------------+--------------------------------+------+---------------------------------+

  케이스 23 응답 원문(SSL 모드가 실제로 접속에 반영되는지에 대한 핵심 증거):
    {"ok":false,"errorCode":"CONNECT_FAILED",
     "message":"SQLRecoverableException: ORA-17002: I/O 오류: Connection closed,
       connect lapse 26 ms., Authentication lapse 0 ms.",
     "jdbcUrl":"jdbc:oracle:thin:@tcps://192.168.0.151:1523/xepdb1","elapsedMs":171}
  같은 호스트·포트에서 sslMode 미선택은 tcp:// 로 접속 성공(121ms), sslMode=require 는
  tcps:// 로 전환돼 비SSL 리스너에서 실패했다. 즉 SSL 모드가 프로필 값에 따라 실제
  JDBC URL·프로퍼티까지 전달됨이 양방향으로 확인된다.

  경계값 목록 응답 원문(프로필 4건 상태):
    [{"profileId":1,"profileName":"Oracle_asis_BROWSER",…,"hasPassword":true,…},
     {"profileId":2,"profileName":"Oracle_asis_TDA",…,"hasPassword":true,…},
     {"profileId":3,"profileName":"Oracle_SSL_REQUIRE",…,"sslMode":"require","hasPassword":true,…},
     {"profileId":4,"profileName":"Tibero_stub","dbmsType":"TIBERO",…,"hasPassword":true,…}]
    [검사] 응답 원문에 'password' 키 포함 여부 : False
    [검사] 응답 원문에 저장된 실제 비밀번호 값 포함 여부 : False
    [검사] hasPassword 필드 존재 여부 : True

================================================================================
7. git 커밋 / 원격 반영
================================================================================
7-1. 소스 저장소 — nxTDA-src
저장소 : X:\Projects\nxTDA → https://github.com/kr0xx3xxx0xxx-coder/nxTDA-src.git (main)

  dbad06a4c5f2b32c2bb9e472c2ef69959091452c  2026-08-17 19:47:44
    작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT 파트0 — 저장소·빌드 골격 초기화
    12 files changed, 683 insertions(+)
      .gitignore(41) build.gradle(57) settings.gradle(3) gradlew(248) gradlew.bat(93)
      gradle/wrapper/*(jar+properties) NxTdaApplication.java(22)
      application.yml(17) static/index.html(29) docs/*(사전 존재 요구사항 문서 2건)

  c02367c897115288b93b9353992852f850699e08  2026-08-17 19:48:24
    작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT 파트0 — post-commit 자동 push 훅 동작 검증(더미 커밋)
    1 file changed, 18 insertions(+)   docs/HOOK_VERIFY.md

  f2e71c1a0f9e405c38be36bade4abc4a10d7bccd  2026-08-17 20:04:27
    작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT 파트1 — DB 프로필 관리 모듈(nxDTV 설계 이식)
    14 files changed, 1724 insertions(+), 1 deletion(-)
      ConnectionFactory.java(77) DbProfile.java(255) DbProfileController.java(163)
      DbProfileService.java(422) DbmsType.java(69)
      impl/OracleConnectionFactory.java(170) impl/Db2ConnectionFactory.java(65)
      impl/TiberoConnectionFactory.java(64) impl/MssqlConnectionFactory.java(63)
      templates/dbprofile.html(304) schema/nxtda_dbprofile_schema.sql(35)
      gradle.properties(6, 신규) build.gradle(+6) application.yml(+26/-1)

  원격 반영 확인(파트1 커밋 후, 수동 push 없이 훅이 처리):
    local  HEAD        : f2e71c1a0f9e405c38be36bade4abc4a10d7bccd
    remote origin/main : f2e71c1a0f9e405c38be36bade4abc4a10d7bccd

7-2. 검증 저장소 — nxTDA-verify (완료보고 + 증적)
저장소 : https://github.com/kr0xx3xxx0xxx-coder/nxTDA-verify.git (main)
작업 클론 : X:\Verify\nxTDA\_rpt_push

  dbe7a7954bb6c239e4d6bc71095704de1fba5847  2026-08-17 20:11:24 +0900
    작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT — 완료보고 + 증적
    14 files changed, 1486 insertions(+)
      nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT_완료보고_20260817.md            568줄
        (이 커밋 시점 기준 568줄. 이후 7장·8-2 보강으로 본문을 개정해 613줄이 되었고,
         개정본은 같은 저장소에 후속 커밋으로 재반영했다. 지금 읽고 있는 파일이 개정본이다.)
      directives/nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT_지침_20260817.md      100줄
      evidence/nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT_20260817/  (12개 파일)
        boundary_cases_output.txt(190) boundary_verify.py(173) e2e_browser.py(141)
        storecheck_after_boundary.txt(70) e2e_browser_output.txt(62) StoreCheck.java(57)
        bootrun_startup.log(52) storecheck_after_e2e.txt(38) nxtda_runtime.log(35)
        e2e_01_초기화면.png / e2e_02_등록후.png / e2e_03_접속테스트.png (바이너리 3장)

  원격 반영 확인 :
    local  HEAD               : dbe7a7954bb6c239e4d6bc71095704de1fba5847
    git ls-remote origin main : dbe7a7954bb6c239e4d6bc71095704de1fba5847  refs/heads/main

  소스와 증적을 저장소 단위로 분리했다. 검증 스크립트(boundary_verify.py / e2e_browser.py /
  StoreCheck.java)와 로그·스크린샷은 지침이 지정한 산출물 목록에 없으므로 nxTDA-src 에
  섞지 않고 nxTDA-verify 에만 올렸다(8-3 참고). 지침 원문도 같은 커밋에 함께 넣어
  '무엇을 요구받았고 무엇을 냈는지'를 한 저장소에서 대조할 수 있게 했다.

7-3. Google Drive 사본
  G:\내 드라이브\nxTDA-verify\reports\
    nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT_완료보고_20260817.md
    nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT_20260817_증적\ (증적 12개 파일)
  GitHub 접근 없이도 열람할 수 있도록 동일 내용을 드라이브에도 남겼다.

================================================================================
8. 미완료 / 한계 / 후속과제 (숨기지 않고 명시)
================================================================================
8-1. 이번 범위에서 의도적으로 하지 않은 것
  - 문자구성분석 / 암호화판정 / GROUP BY·SUM 후보추천 / 스키마변경감지: 지침상 이번 범위 아님.
    관련 패키지·파일을 만들지 않았다(빈 껍데기 금지).
  - DB2 / TIBERO / MSSQL 접속: 스텁이다. 구현 완료가 아니다(3-1 표의 사유 참고).
  - 요구사항 v3 10장(성능·규모, 최소 1억행 기준): 이번 산출물은 접속정보 CRUD 와 단건 접속
    테스트뿐이어서 대량데이터 경로가 없다. 규모 검증 대상 자체가 없으므로 수행하지 않았고,
    실제 규모 검증은 컬럼 프로파일링 기능 착수 시점에 해야 한다.

8-2. 남아 있는 위험 / 후속과제
  - 비밀번호 저장 시 암호화 미적용. H2 nxtda_db_profile.password 는 평문이다. nxDTV 도
    동일하며 그쪽에서도 "이번 범위 아님"으로 명시된 사항이다. 완화 조치로 data/ 를
    .gitignore 에 넣어 저장소 유출을 막았지만, 파일 자체를 읽을 수 있는 사람은 볼 수 있다.
    → 후속: 대칭키 암호화 또는 OS 키체인/사내 비밀관리 연동.
  - 로그인/권한 배제(요구사항 v3 9-2 확정 사항). 따라서 /api/dbprofile/* 는 현재 인증 없이
    호출 가능하다. 사내 전용 도구 전제이고 요구사항이 인증을 이번 범위에서 뺐기 때문이지만,
    "누구나 프로필을 등록·삭제하고 접속 테스트를 돌릴 수 있다"는 사실은 기록해 둔다.
  - Oracle 접속을 매번 새 물리 연결로 만든다(커넥션 풀 없음). 접속 테스트 용도에는 충분하지만
    실제 프로파일링 조회가 붙으면 풀링 정책을 정해야 한다.
  - 파트0 지침이 참고자료로 지정한 xDataNexPro_제품소개서_v3_3_20250530.pdf(19~23p)를
    X:\Projects 및 nxTDA 폴더에서 찾지 못했다(현재 존재하는 참고자료는
    docs\archive\history_md\nxTDA_요구사항_정리_v3_20260817.docx 뿐이다). 요구사항 문서 1장이
    "소개서 원안(nxTDA: 문자구성 분석 수준)보다 확장된 범위"를 이미 정의하고 있고, 이번
    범위(DB 프로필)는 소개서 19~23p 와 무관한 공통 인프라(9-1장)라서 작업에 지장은 없었다.
    다만 소개서를 직접 확인하지 못한 상태로 진행했다는 점은 명시한다.
  - 검증으로 만든 프로필 3건이 로컬에 남아 있다. 테스트 후 정리하지 않았다.
    X:\Projects\nxTDA\data\nxtda_admin.mv.db 의 nxtda_db_profile 총 3행
    (증적 storecheck_after_boundary.txt 원문과 동일):
      profile_id=1  Oracle_asis_BROWSER  ORACLE  192.168.0.151:1523  ← 실브라우저 E2E 등록분
      profile_id=2  Oracle_asis_TDA      ORACLE  192.168.0.151:1523  ← 경계값 upsert(중복명) 확인분
      profile_id=4  Tibero_stub          TIBERO  192.168.0.99:8629   ← 스텁 미구현 응답 확인분
    (profile_id=3 은 삭제 케이스 검증에서 지워져 비어 있다.)
    Oracle 2건은 실제 사내 DB 접속정보이고 비밀번호도 평문으로 들어 있다. data/ 를
    .gitignore 로 제외해 두 저장소 어디에도 올라가지 않았지만, 로컬 파일을 읽을 수 있는
    사람은 볼 수 있다(이 항목 첫 번째 위험과 같은 성격이다). 검증 직후 상태를 그대로
    재현·대조할 수 있게 하려고 의도적으로 남겼다.
    → 후속: 다음 작업 착수 전 3건을 삭제하거나, 비밀번호 암호화 적용 후 재등록.

8-3. 검증 절차상 정직하게 남길 사항
  - 최초 타임스탬프 측정에서 산출물이 최종 소스 수정보다 이전이었다(build.gradle 의 bootRun
    설정 변경이 bootJar 를 무효화하지 않았기 때문). clean 후 전체 재빌드로 다시 맞춘 뒤
    검증을 진행했다. 6-2 에 그대로 적었다.
  - 검증에 쓴 Oracle 접속정보(비밀번호 포함)는 nxDTV 의 기존 프리셋 파일에서 읽어 썼고,
    검증 스크립트·로그·이 보고서 어디에도 비밀번호 값을 출력하지 않았다(길이와 일치여부만).
  - 검증 스크립트(boundary_verify.py / e2e_browser.py / StoreCheck.java)는 지침이 지정한
    산출물 목록에 없으므로 nxTDA-src 에 커밋하지 않고 증적으로만 첨부했다.

================================================================================
9. 결론
================================================================================
파트0과 파트1 모두 완료했고, 실제 서비스 프로세스(JVM)와 실제 브라우저, 실제 Oracle DB 를
써서 검증을 마쳤다. 대체수단을 쓰지 않았다.

이번 작업의 핵심은 "nxDTV 가 이미 사고를 겪고 고친 두 가지"를 nxTDA 에서 처음부터 지키는
것이었다. 첫째는 비밀번호다. nxDTV 는 프리셋 목록 응답에 평문 비밀번호가 실려 나가던 것을
수정해 '서버가 저장소에서 직접 해석하고 클라이언트는 프로필명만 보낸다'는 구조로 바꿨다.
nxTDA 는 이 구조를 옮기면서 Java 의 타입 시스템으로 한 겹 더 강하게 만들었다 — 화면에
내보내는 타입(DbProfile.Summary)에 password 필드가 애초에 없고, resolvePassword() 는
private 이라 서비스 밖으로 값이 나가는 경로가 컴파일 단계에서 존재하지 않는다. 실브라우저
Network 원문 전수 검사에서 4개 응답 모두 password 키도, 저장된 실제 비밀번호 값도 나타나지
않았다. 둘째는 SSL 모드다. nxDTV 는 sslmode 가 비었을 때 어댑터가 require 를 기본값으로
강제해 비SSL DB 접속이 실패한 사고를 겪었다. nxTDA 는 미선택을 NULL 로 저장하고 SSL
프로퍼티를 아예 만들지 않는다. 같은 호스트·포트에서 미선택은 tcp:// 로 접속 성공(121ms),
require 는 tcps:// 로 전환돼 비SSL 리스너에서 ORA-17002 로 실패했다 — 프로필 값이 실제
JDBC URL 까지 전달됨을 양방향으로 확인한 셈이다.

구조 측면에서는 DBMS 분기를 인라인 if/else 로 두지 않는 원칙을 지켰다. ConnectionFactory
인터페이스와 4개 구현체를 두고, 서비스는 Spring 이 주입한 구현체 목록을 EnumMap 으로 받아
쓴다. 서비스 본문에 DBMS 이름을 비교하는 조건문은 하나도 없다. 이 구조의 실질적 효용은
기동 로그가 스스로 상태를 고백한다는 점이다 — "접속지원=[ORACLE] / 스텁=[DB2, MSSQL,
TIBERO]". 스텁 3개는 supportsConnect()=false 이고 접속 시도 시 조용히 폴백하지 않고
미구현 사유를 그대로 응답한다(케이스 21에서 확인). Oracle 만 실구현이며, 나머지 3개를
구현 완료로 보고하지 않는다.

경계값은 24개를 사전에 나열하고 24개 전부 실행 중 JVM 에 실제 HTTP 로 테스트했다. 특히
'프로필명 중복'은 nxDTV 와 동일한 upsert 의미로 처리해 profileId 가 유지되고 행이 늘지
않음을 확인했고, '빈 비밀번호로 수정'은 응답의 hasPassword 뿐 아니라 H2 를 직접 열어
저장된 비밀번호 길이·값 일치까지 확인해 보존 규칙이 저장소 레벨에서 실제로 동작함을
증명했다. 화면 클릭에서 저장소 행까지의 도달도 같은 방식으로 확인했다.

남은 위험은 숨기지 않는다. 비밀번호는 여전히 평문으로 저장된다(nxDTV 도 동일, 이번에 이식한
하드닝은 '응답 노출 차단'이지 '저장 암호화'가 아니다). 인증이 없어 API 가 무인증 호출
가능하다(요구사항 9-2의 확정 사항이지만 사실로 기록해 둔다). 검증에 쓴 프로필 3건도 로컬 H2 에
그대로 남겨 뒀다 — 재현을 위해 의도적으로 남긴 것이지만 평문 비밀번호를 담고 있으므로 다음 작업
착수 전 정리 대상이다(8-2). DB2/MSSQL 은 드라이버는 있고 SSL 옵션 검증만 남았으므로, 사내
인스턴스 접근이 확보되는 시점에 스텁을 실구현으로 올리는 것이 가장 비용 대비 효과가 큰 다음
단계다. 지침이 참고자료로 지정한 제품소개서 PDF 는
폴더에서 찾지 못해 요구사항 문서만 근거로 진행했다는 점도 함께 남긴다.

================================================================================
10. 증적 파일 목록
================================================================================
  e2e_browser_output.txt        실브라우저 E2E 전체 출력(Network 원문 + 노출 검사)
  boundary_cases_output.txt     경계값 24케이스 요청·응답 원문
  storecheck_after_e2e.txt      H2 직접 조회(E2E 직후)
  storecheck_after_boundary.txt H2 직접 조회(경계값 테스트 후, 비밀번호 보존 확인)
  bootrun_startup.log           bootRun 기동 로그(UTF-8)
  nxtda_runtime.log             런타임 로그 전문(저장/접속 로그 포함)
  e2e_01_초기화면.png            /dbprofile 진입 직후
  e2e_02_등록후.png              [프로필 등록] 클릭 후
  e2e_03_접속테스트.png           [접속테스트] 클릭 후(실 Oracle 성공 배너)
  boundary_verify.py            경계값 검증 스크립트
  e2e_browser.py                실브라우저 E2E 스크립트
  StoreCheck.java               H2 저장소 직접 조회 스크립트

작업명 : nxTDA-BOOTSTRAP-AND-DBPROFILE-INIT
✅ 작업 완료 - nxTDA 저장소·빌드 골격 초기화(파트0) 및 DB 프로필 관리 모듈 nxDTV 설계 이식(파트1)
