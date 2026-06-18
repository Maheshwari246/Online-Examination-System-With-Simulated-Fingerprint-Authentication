import time
import random
import threading
import sqlite3
from colorama import Fore, Style, init

init(autoreset=True)

# ==========================
# DATABASE SETUP
# ==========================
conn = sqlite3.connect(
    "/data/user/0/ru.iiec.pydroid3/files/exam.db",
    check_same_thread=False
)
cursor = conn.cursor()

# ==========================
# TABLES
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    fingerprint_id TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    score REAL
)
""")

conn.commit()

# ==========================
# RESET USERS (IMPORTANT FIX OPTION)
# ==========================
# 👉 If fingerprint issue still comes, uncomment below ONCE
# cursor.execute("DELETE FROM users")
# conn.commit()

# ==========================
# INSERT DEFAULT STUDENTS
# ==========================
existing = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]

if existing == 0:
    for i in range(1, 11):
        cursor.execute("""
        INSERT INTO users (username, password, fingerprint_id)
        VALUES (?, ?, ?)
        """, (f"student{i}", f"pass{i}", f"fp{i}"))
    conn.commit()

# ==========================
# LOGIN SYSTEM
# ==========================
def login_system():
    print(Fore.CYAN + Style.BRIGHT + "===== LOGIN SYSTEM =====")

    username = input(Fore.YELLOW + "Enter Username: ").strip()
    password = input(Fore.YELLOW + "Enter Password: ").strip()

    cursor.execute(
        "SELECT password, fingerprint_id FROM users WHERE username=?",
        (username,)
    )
    data = cursor.fetchone()

    if not data:
        print(Fore.RED + "User Not Found!")
        return None

    db_password, db_fingerprint = data

    if password != db_password:
        print(Fore.RED + "Wrong Password!")
        return None

    print(Fore.GREEN + "Password Correct!")

    fid = input(Fore.MAGENTA + "Enter Fingerprint ID (fp1-fp10): ").strip()

    # ✅ SAFE COMPARISON FIX
    if fid.strip().lower() == db_fingerprint.strip().lower():
        print(Fore.GREEN + "Fingerprint Verified!")
        print(Fore.GREEN + "Login Successful!\n")
        return username
    else:
        print(Fore.RED + f"Fingerprint Wrong! Expected: {db_fingerprint}")
        return None


# ==========================
# EXAM CONFIG
# ==========================
exam_time_seconds = 600
exam_time_up = False

question_bank = [
    {"q":"CPU stands for?","options":["Central Processing Unit","Control Unit","Computer Process","None"],"ans":"Central Processing Unit"},
    {"q":"Python is used for?","options":["All","AI","Web","Game"],"ans":"All"},
    {"q":"Which is Database?","options":["MySQL","Google","HTML","Chrome"],"ans":"MySQL"},
    {"q":"HTML stands for?","options":["Hyper Text Markup Language","High Text Markup Language","Hyper Tabular Markup Language","None"],"ans":"Hyper Text Markup Language"},
    {"q":"Which language is used for AI?","options":["Python","C","Java","All"],"ans":"Python"},
    {"q":"Which is search engine?","options":["Chrome","Google","Python","MySQL"],"ans":"Google"},
    {"q":"Which is programming language?","options":["HTML","CSS","Python","SQL"],"ans":"Python"},
    {"q":"Which is frontend framework?","options":["React","MySQL","Python","C"],"ans":"React"},
    {"q":"Which is DBMS?","options":["MySQL","Python","HTML","CSS"],"ans":"MySQL"},
    {"q":"Which is server-side language?","options":["Python","HTML","CSS","JavaScript"],"ans":"Python"},
]

# ==========================
# TIMER
# ==========================
def exam_timer():
    global exam_time_up
    remaining = exam_time_seconds

    while remaining > 0:
        mins, secs = divmod(remaining, 60)
        print(Fore.MAGENTA + f"\r[Exam Timer: {mins:02d}:{secs:02d}]", end="")
        time.sleep(1)
        remaining -= 1

    exam_time_up = True
    print(Fore.RED + "\n\nExam Time Over!")


# ==========================
# EXAM START
# ==========================
def start_exam(username):
    global exam_time_up
    score = 0
    negative_mark = -0.25

    questions = question_bank.copy()
    random.shuffle(questions)

    threading.Thread(target=exam_timer, daemon=True).start()

    for q in questions:
        if exam_time_up:
            break

        print("\n" + "-" * 40)

        options = q["options"].copy()
        random.shuffle(options)

        letters = ["A", "B", "C", "D"]
        option_map = dict(zip(letters, options))

        correct_letter = [
            k for k, v in option_map.items() if v == q["ans"]
        ][0]

        print(Fore.YELLOW + q["q"])
        for l in letters:
            print(f"{l}. {option_map[l]}")

        ans = input("Your Answer: ").strip().upper()

        if ans == correct_letter:
            print(Fore.GREEN + "Correct!")
            score += 1
        elif ans in letters:
            print(Fore.RED + f"Wrong! Correct: {correct_letter}")
            score += negative_mark
        else:
            print(Fore.RED + f"Invalid! Correct: {correct_letter}")
            score += negative_mark

    print("\n" + "=" * 40)
    print(Fore.CYAN + f"Final Score: {score}/{len(questions)}")
    print("=" * 40)

    cursor.execute(
        "INSERT INTO results (username, score) VALUES (?, ?)",
        (username, score)
    )
    conn.commit()

    print(Fore.GREEN + "Result saved ✅")


# ==========================
# RESULTS FEATURES
# ==========================
def show_all_results():
    print("\n📊 All Results:")
    cursor.execute("SELECT username, score FROM results")
    for row in cursor.fetchall():
        print(f"{row[0]} → {row[1]}")


def show_topper():
    print("\n🏆 Top 5 Toppers:")
    cursor.execute("""
        SELECT username, score
        FROM results
        ORDER BY score DESC
        LIMIT 5
    """)
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {row[0]} → {row[1]}")


def student_history():
    name = input("Enter username: ").strip()
    cursor.execute(
        "SELECT score FROM results WHERE username=?",
        (name,)
    )
    data = cursor.fetchall()

    print(f"\n📁 {name} History:")

    if not data:
        print("No history found")
        return

    for i, row in enumerate(data, 1):
        print(f"Attempt {i}: {row[0]}")


# ==========================
# MAIN PROGRAM
# ==========================
if __name__ == "__main__":

    user = login_system()

    if user:
        start_exam(user)

        while True:
            print("\n===== MENU =====")
            print("1. All Results")
            print("2. Top 5 Toppers")
            print("3. Student History")
            print("4. Exit")

            ch = input("Enter choice: ").strip()

            if ch == "1":
                show_all_results()
            elif ch == "2":
                show_topper()
            elif ch == "3":
                student_history()
            elif ch == "4":
                break
            else:
                print("Invalid choice")

    conn.close()