import os
import sys
import pymysql
from datetime import datetime

# ==========================================
# SECTION 1: CONFIGURATION & CONSTANTS
# ==========================================
TIP_BLUE  = "#003087"
TIP_GOLD  = "#FDB913"
TIP_DARK  = "#1A1A2E"
TIP_LIGHT = "#F4F6FA"
TIP_WHITE = "#FFFFFF"
TIP_BORD  = "#D0D7E3"
TIP_MUTED = "#6C7A99"
TIP_GREEN = "#1A7C4F"
TIP_RED   = "#C0392B"

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tip_logo.png")

DB_CONFIG = dict(
    host     = "localhost",
    port     = 3306,
    db       = "scds_db",      
    user     = "root",
    password = "",             
)

# ==========================================
# SECTION 2: DATABASE CONNECTION ENGINE
# ==========================================
class SQLDBConnector:
    def __init__(self, db="", username="", password="", host="", port=3306):
        self.db       = db
        self.username = username
        self.password = password
        self.host     = host
        self.port     = port

    def _connect(self):
        return pymysql.connect(
            host=self.host, port=self.port,
            db=self.db, user=self.username, password=self.password,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )

    def executequery(self, sql="", parameters=()):
        try:
            conn   = self._connect()
            cursor = conn.cursor()
            cursor.execute(sql, parameters)
            result = cursor.fetchall()
            conn.close()
            return result
        except pymysql.MySQLError as e:
            print(f"Query Error: {e}"); return []

    def executecommit(self, sql="", parameters=()):
        try:
            conn   = self._connect()
            cursor = conn.cursor()
            cursor.execute(sql, parameters)
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        except pymysql.MySQLError as e:
            print(f"Commit Error: {e}"); return None

def _db():
    return SQLDBConnector(
        db=DB_CONFIG["db"], username=DB_CONFIG["user"], 
        password=DB_CONFIG["password"], host=DB_CONFIG["host"], 
        port=DB_CONFIG["port"]
    )

# ==========================================
# SECTION 3: SCHEMA INITIALIZATION
# ==========================================
def init_db():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"], port=DB_CONFIG["port"],
            user=DB_CONFIG["user"], password=DB_CONFIG["password"],
            autocommit=True
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['db']}` CHARACTER SET utf8mb4")
        conn.select_db(DB_CONFIG["db"])

        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role ENUM('Admin','Staff','Nurse') NOT NULL,
            full_name VARCHAR(100)) ENGINE=InnoDB""")

        cur.execute("""CREATE TABLE IF NOT EXISTS students (
            student_id VARCHAR(10) PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            course VARCHAR(20), year_level VARCHAR(20),
            date_of_birth VARCHAR(10), contact_no VARCHAR(20),
            address VARCHAR(200), emergency_contact VARCHAR(100),
            blood_type VARCHAR(5), known_allergies VARCHAR(200)) ENGINE=InnoDB""")

        cur.execute("""CREATE TABLE IF NOT EXISTS consultations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(10) NOT NULL,
            date_of_visit VARCHAR(10) NOT NULL,
            chief_complaint VARCHAR(200), diagnosis VARCHAR(200),
            treatment VARCHAR(300), prescribed_meds VARCHAR(300),
            nurse_notes TEXT, nurse_on_duty VARCHAR(100),
            follow_up_date VARCHAR(10),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE) ENGINE=InnoDB""")

        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            cur.executemany("INSERT INTO users (username,password,role,full_name) VALUES (%s,%s,%s,%s)",
                           [("admin","admin123","Admin","System Administrator")])
        conn.close()
    except Exception as e: print(f"Init Error: {e}")

# ==========================================
# SECTION 4: USER & STUDENT OPERATIONS
# ==========================================
def db_auth(u, p):
    rows = _db().executequery("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
    return rows[0] if rows else None

def db_students(): 
    return _db().executequery("SELECT * FROM students ORDER BY full_name")

def db_save_student(s):
    _db().executecommit("""INSERT INTO students VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE full_name=%s, course=%s, year_level=%s, date_of_birth=%s,
        contact_no=%s, address=%s, emergency_contact=%s, blood_type=%s, known_allergies=%s""",
        (s["student_id"], s["full_name"], s.get("course",""), s.get("year_level",""),
         s.get("date_of_birth",""), s.get("contact_no",""), s.get("address",""),
         s.get("emergency_contact",""), s.get("blood_type",""), s.get("known_allergies",""),
         s["full_name"], s.get("course",""), s.get("year_level",""), s.get("date_of_birth",""),
         s.get("contact_no",""), s.get("address",""), s.get("emergency_contact",""),
         s.get("blood_type",""), s.get("known_allergies","")))

# ==========================================
# SECTION 5: CONSULTATION & REPORT LOGIC
# ==========================================
def db_consultations(sid):
    return _db().executequery("SELECT * FROM consultations WHERE student_id=%s ORDER BY date_of_visit DESC", (sid,))

def db_report():
    db = _db()
    return dict(
        ts = db.executequery("SELECT COUNT(*) AS cnt FROM students")[0]["cnt"],
        tc = db.executequery("SELECT COUNT(*) AS cnt FROM consultations")[0]["cnt"],
        blood = db.executequery("SELECT blood_type, COUNT(*) cnt FROM students GROUP BY blood_type ORDER BY cnt DESC"),
        complaints = db.executequery("SELECT chief_complaint, COUNT(*) cnt FROM consultations WHERE chief_complaint != '' GROUP BY chief_complaint ORDER BY cnt DESC LIMIT 10"),
        allergies = db.executequery("SELECT known_allergies, COUNT(*) cnt FROM students WHERE known_allergies != '' AND LOWER(known_allergies) != 'none' GROUP BY known_allergies ORDER BY cnt DESC"),
        courses = db.executequery("SELECT course, COUNT(*) cnt FROM students GROUP BY course ORDER BY cnt DESC"),
        recent = db.executequery("SELECT s.full_name, s.student_id, c.date_of_visit, c.chief_complaint FROM consultations c JOIN students s ON s.student_id = c.student_id ORDER BY c.date_of_visit DESC LIMIT 20")
    )