import java.sql.*;

/**
 * H2 저장소 직접 조회 — 화면 클릭으로 들어온 값이 실제 테이블 행까지 도달했는지 확인한다.
 * 비밀번호는 값이 아니라 길이/일치여부만 출력한다.
 */
public class StoreCheck {
    public static void main(String[] args) throws Exception {
        String url = "jdbc:h2:file:X:/Projects/nxTDA/data/nxtda_admin;AUTO_SERVER=TRUE";
        String expectedPw = args.length > 0 ? args[0] : "";
        try (Connection c = DriverManager.getConnection(url, "nxtda", "")) {
            System.out.println("H2 접속 성공: " + url);
            System.out.println();
            System.out.println("=== nxtda_db_profile 테이블 컬럼 구성 ===");
            try (ResultSet rs = c.getMetaData().getColumns(null, null, "NXTDA_DB_PROFILE", null)) {
                while (rs.next()) {
                    System.out.printf("  %-14s %-12s nullable=%s%n",
                            rs.getString("COLUMN_NAME"), rs.getString("TYPE_NAME"),
                            rs.getInt("NULLABLE") == 1);
                }
            }
            System.out.println();
            System.out.println("=== 저장된 행 (password 는 값 대신 길이/일치여부만) ===");
            String sql = "SELECT profile_id, profile_nm, dbms_type, host, port, database_name, "
                    + "username, ssl_mode, connect_type, service_name, sid, schema_name, "
                    + "LENGTH(password) AS pw_len, created_at, updated_at, last_used_at, password "
                    + "FROM nxtda_db_profile ORDER BY profile_id";
            try (Statement st = c.createStatement(); ResultSet rs = st.executeQuery(sql)) {
                while (rs.next()) {
                    String stored = rs.getString("password");
                    System.out.println("  profile_id    = " + rs.getLong("profile_id"));
                    System.out.println("  profile_nm    = " + rs.getString("profile_nm"));
                    System.out.println("  dbms_type     = " + rs.getString("dbms_type"));
                    System.out.println("  host:port     = " + rs.getString("host") + ":" + rs.getInt("port"));
                    System.out.println("  database_name = " + rs.getString("database_name"));
                    System.out.println("  username      = " + rs.getString("username"));
                    System.out.println("  ssl_mode      = " + rs.getString("ssl_mode") + "  (NULL = 미선택 저장)");
                    System.out.println("  connect_type  = " + rs.getString("connect_type"));
                    System.out.println("  service_name  = " + rs.getString("service_name"));
                    System.out.println("  sid           = " + rs.getString("sid"));
                    System.out.println("  schema_name   = " + rs.getString("schema_name"));
                    System.out.println("  password      = <값 미출력> length=" + rs.getObject("pw_len")
                            + " / 화면에서 입력한 값과 일치=" + (!expectedPw.isEmpty() && expectedPw.equals(stored)));
                    System.out.println("  created_at    = " + rs.getTimestamp("created_at"));
                    System.out.println("  updated_at    = " + rs.getTimestamp("updated_at"));
                    System.out.println("  last_used_at  = " + rs.getTimestamp("last_used_at"));
                    System.out.println("  ----");
                }
            }
            try (Statement st = c.createStatement();
                 ResultSet rs = st.executeQuery("SELECT COUNT(*) FROM nxtda_db_profile")) {
                rs.next();
                System.out.println("총 행 수 = " + rs.getInt(1));
            }
        }
    }
}
