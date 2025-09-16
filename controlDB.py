# sqllite.py
import sqlite3
from sqlite3 import Connection
import os
import pandas as pd
from tabulate import tabulate
import random
import pandas as pd
import re
import xlsxwriter

DB_PATH = "controlDB.db"


def get_connection() -> Connection:
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # PBN 사이트 정보 테이블
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS pbn_sites (
        site_id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_url TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        app_password TEXT NOT NULL
    )
    """
    )

    # 진행 중인 클라이언트 테이블
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    site_url TEXT NOT NULL,
    total_backlinks INTEGER NOT NULL,
    remaining_days INTEGER NOT NULL,
    daily_backlinks INTEGER NOT NULL,
    paused INTEGER NOT NULL DEFAULT 0
    )
    """
    )

    # 키워드를 개별관리하기 위한 새로운 테이블
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS client_keywords (
        keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        keyword TEXT NOT NULL,
        FOREIGN KEY(client_id) REFERENCES clients(client_id)
    )
    """
    )
    # 완료된 클라이언트 테이블

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS completed_clients (
        client_id INTEGER PRIMARY KEY,
        client_name TEXT NOT NULL,
        site_url TEXT NOT NULL,
        total_backlinks INTEGER NOT NULL,
        daily_backlinks INTEGER NOT NULL
    )
    """
    )

    # 구축된 백링크 테이블
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS posts (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        client_name TEXT NOT NULL,
        client_site_url TEXT NOT NULL,
        keyword TEXT NOT NULL,
        pbn_url TEXT NOT NULL,
        FOREIGN KEY(client_id) REFERENCES clients(client_id)
    )
    """
    )

    # PBN 포스트 테이블 (크롤링된 포스트들)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS pbn_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id INTEGER NOT NULL,
        site_url TEXT NOT NULL,
        post_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        excerpt TEXT,
        date_published TEXT,
        word_count INTEGER,
        categories TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
    conn.close()


# 콘솔에 표 형태로 데이터를 출력하는 함수
def print_table(title, data, headers):
    """
    데이터를 표 형태로 출력합니다.
    :param title: 출력할 표의 제목
    :param data: 출력할 데이터 리스트
    :param headers: 표의 헤더(열 이름)
    """
    print(f"\n{title}")
    print(tabulate(data, headers=headers, tablefmt="grid"))


# -----------------------
# PBN SITES FUNCTIONS
# -----------------------
def add_pbn_site(site_url, username, password, app_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO pbn_sites (site_url, username, password, app_password)
    VALUES (?, ?, ?, ?)
    """,
        (site_url, username, password, app_password),
    )
    conn.commit()
    conn.close()


def view_pbn_sites():
    """
    PBN 사이트 정보를 반환하고 표 형태로 출력합니다.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pbn_sites")
    rows = cursor.fetchall()
    conn.close()

    headers = ["Site ID", "Site URL", "Username", "Password", "App Password"]
    print_table("PBN 사이트 정보", rows, headers)
    return rows


# 모든 PBN 사이트 정보 반환
def get_all_pbn_sites():
    """
    pbn_sites 테이블에서 모든 PBN 사이트 정보를 반환
    반환: [(site_id, site_url, username, password, app_password), ...]
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT site_id, site_url, username, password, app_password FROM pbn_sites"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# pbn_sites 중 하나를 랜덤으로 반환
def get_random_pbn_site():
    """
    pbn_sites에서 랜덤으로 하나의 PBN 사이트를 반환
    """
    pbn_sites = get_all_pbn_sites()
    if pbn_sites:
        return random.choice(pbn_sites)
    return None


def get_pbn_site_by_url(domain):
    """
    도메인(예: margiesmassage.com)으로 pbn_sites 정보를 반환
    반환: (site_id, site_url, username, password, app_password) 또는 None
    """
    conn = get_connection()
    cursor = conn.cursor()
    # site_url이 'https://도메인/' 형태이므로 LIKE 검색 사용
    like_pattern = f"%{domain}%"
    cursor.execute(
        "SELECT site_id, site_url, username, password, app_password FROM pbn_sites WHERE site_url LIKE ?",
        (like_pattern,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


# -----------------------
# CLIENT FUNCTIONS
# -----------------------
def add_client(
    client_name, site_url, total_backlinks, remaining_days, daily_min, daily_max
):
    """
    client_name, site_url, total_backlinks, remaining_days, daily_min, daily_max를 입력받아
    clients 테이블에 새로운 클라이언트를 추가 후 client_id를 반환합니다.
    """

    # 기존 로직: 일일평균 (daily_backlinks) 계산
    daily_backlinks = (
        total_backlinks // remaining_days if remaining_days > 0 else total_backlinks
    )

    # DB 연결
    conn = get_connection()
    cursor = conn.cursor()

    # clients 테이블에 daily_min, daily_max 컬럼이 있다고 가정
    cursor.execute(
        """
    INSERT INTO clients 
        (client_name, site_url, total_backlinks, remaining_days, 
         daily_backlinks, daily_min, daily_max, paused)
    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """,
        (
            client_name,
            site_url,
            total_backlinks,
            remaining_days,
            daily_backlinks,
            daily_min,
            daily_max,
        ),
    )

    client_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return client_id


# 조건: paused = 0, remaining_days > 0, daily_backlinks > 0 인 클라이언트 목록 반환
def get_active_clients():
    """
    paused=0, remaining_days>0, daily_backlinks>0 인 클라이언트 목록 반환
    + daily_min, daily_max까지 함께 반환
    반환 형태: [
      (client_id, client_name, site_url, total_backlinks,
       remaining_days, daily_backlinks, paused, daily_min, daily_max),
      ...
    ]
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            client_id, 
            client_name, 
            site_url, 
            total_backlinks, 
            remaining_days, 
            daily_backlinks, 
            paused,
            daily_min,
            daily_max
        FROM clients
        WHERE paused = 0 
          AND remaining_days > 0 
          AND daily_backlinks > 0
          AND status='active'
    """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# 엑셀에서 클라이언트 추가하는 함수
def load_clients_from_excel(excel_file: str):
    # 1) 엑셀 읽기
    df = pd.read_excel(excel_file)

    # 2) 각 행을 순회
    for idx, row in df.iterrows():
        client_name = str(row["client_name"]).strip()
        site_url = str(row["site_url"]).strip()
        total_bl = int(row["total_backlinks"])
        remain_days = int(row["remaining_days"])
        daily_min = int(row["daily_min"])
        daily_max = int(row["daily_max"])
        keywords_cell = str(row["keywords"]).strip()  # "키워드1,키워드2..."

        # controlDB의 add_client 등을 통해 DB에 insert
        # 여기서 add_client를 수정하거나,
        # daily_min/daily_max를 추가로 update_client_info 하는 방식
        # 또는 add_client() 자체를 확장해도 됨.
        client_id = add_client(
            client_name, site_url, total_bl, remain_days, daily_min, daily_max
        )

        # 3) 키워드 분리 후 insert
        if keywords_cell:
            splitted_keywords = [
                kw.strip() for kw in keywords_cell.split(",") if kw.strip()
            ]
            for kw in splitted_keywords:
                add_client_keyword(client_id, kw)

    print("엑셀로부터 클라이언트/키워드 정보를 성공적으로 DB에 입력했습니다.")


# 클라이언트 키워드 추가
def add_client_keyword(client_id, keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO client_keywords (client_id, keyword)
    VALUES (?, ?)
    """,
        (client_id, keyword),
    )
    conn.commit()
    conn.close()


# 클라이언트 키워드 가져오기
def get_client_keywords(client_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT keyword FROM client_keywords WHERE client_id = ?", (client_id,)
    )
    keywords = [row[0] for row in cursor.fetchall()]
    conn.close()
    return keywords


# 클라이언트의 키워드 랜덤 가져오기
def get_random_keyword_for_client(client_id):
    keywords = get_client_keywords(client_id)
    return random.choice(keywords) if keywords else None


# 모든 클라이언트의 키워드보기
def view_all_client_keywords():
    """
    client_keywords 테이블을 JOIN하여
    [keyword_id, client_id, client_name, keyword] 형태로 출력.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # client_keywords와 clients를 JOIN해서 클라이언트 이름도 함께 가져오기
    cursor.execute(
        """
    SELECT 
        ck.keyword_id,
        ck.client_id,
        c.client_name,
        ck.keyword
    FROM client_keywords ck
    JOIN clients c ON ck.client_id = c.client_id
    ORDER BY ck.client_id, ck.keyword_id
    """
    )
    rows = cursor.fetchall()
    conn.close()

    # 표 형태로 출력
    headers = ["Keyword ID", "Client ID", "Client Name", "Keyword"]
    print_table("전체 클라이언트 키워드 목록", rows, headers)
    return rows


def view_clients():
    conn = get_connection()
    cursor = conn.cursor()

    # status 컬럼까지 함께 조회
    cursor.execute(
        """
        SELECT client_id, 
               client_name, 
               site_url, 
               total_backlinks, 
               remaining_days, 
               daily_backlinks, 
               daily_min, 
               daily_max, 
               paused,
               status
        FROM clients
    """
    )
    rows = cursor.fetchall()
    conn.close()

    # 출력용 헤더에 "Status" 추가
    headers = [
        "Client ID",
        "Name",
        "Site URL",
        "Total Backlinks",
        "Remaining Days",
        "Daily Backlinks",
        "daily_min",
        "daily_max",
        "Paused",
        "Status",
    ]
    print_table("현재 진행 중인 클라이언트 정보", rows, headers)
    return rows


def view_completed_clients():
    """
    status='completed'인 클라이언트 목록 + posts 테이블의 built_count
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT client_id, client_name, site_url, total_backlinks, daily_backlinks
          FROM clients
         WHERE status='completed'
    """
    )
    completed = cursor.fetchall()

    data_for_print = []
    for c_id, c_name, c_url, t_bl, d_bl in completed:
        built_count = cursor.execute(
            "SELECT COUNT(*) FROM posts WHERE client_id=?", (c_id,)
        ).fetchone()[0]
        data_for_print.append((c_id, c_name, c_url, built_count, t_bl, d_bl))

    conn.close()
    headers = ["Client ID", "Name", "Site URL", "Built Count", "Total BL", "Daily BL"]
    print_table("완료된 클라이언트(status='completed')", data_for_print, headers)
    return data_for_print

    # 3) 표로 출력
    headers = ["Client ID", "Name", "Site URL", "Built Count", "Total BL", "Daily BL"]
    print_table("완료된 클라이언트 정보 (개선)", data_for_print, headers)
    return data_for_print


def view_posts():
    """
    구축된 백링크 정보를 반환하고 출력합니다.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()
    conn.close()

    headers = ["Post ID", "Client ID", "Client Name", "Site URL", "Keyword", "PBN URL"]
    print_table("구축된 백링크 정보", rows, headers)
    return rows


def update_client_info(client_id, **kwargs):
    """
    kwargs를 통해 column=value 형태로 업데이트 가능.
    예: update_client_info(client_id=1, remaining_days=5, total_backlinks=200)
    daily_backlinks도 total_backlinks나 remaining_days 변경 시 재계산 가능.
    """
    if not kwargs:
        return
    conn = get_connection()
    cursor = conn.cursor()

    # 변경 전 클라이언트 정보 가져오기
    current = cursor.execute(
        "SELECT total_backlinks, remaining_days FROM clients WHERE client_id=?",
        (client_id,),
    ).fetchone()
    if not current:
        conn.close()
        return
    old_total, old_days = current

    set_clauses = []
    values = []
    for column, value in kwargs.items():
        set_clauses.append(f"{column} = ?")
        values.append(value)

    # 업데이트 쿼리 실행
    query = f"UPDATE clients SET {', '.join(set_clauses)} WHERE client_id = ?"
    values.append(client_id)
    cursor.execute(query, values)

    # total_backlinks나 remaining_days가 변경되었다면 daily_backlinks 재계산
    # 우선 변경 후 데이터 가져오기
    cursor.execute(
        "SELECT total_backlinks, remaining_days FROM clients WHERE client_id=?",
        (client_id,),
    )
    new_total, new_days = cursor.fetchone()

    if ("total_backlinks" in kwargs) or ("remaining_days" in kwargs):
        if new_days > 0:
            new_daily = new_total // new_days
        else:
            new_daily = new_total
        cursor.execute(
            "UPDATE clients SET daily_backlinks = ? WHERE client_id = ?",
            (new_daily, client_id),
        )

    conn.commit()
    conn.close()


def pause_client(client_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET paused = 1 WHERE client_id = ?", (client_id,))
    conn.commit()
    conn.close()


def resume_client(client_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET paused = 0 WHERE client_id = ?", (client_id,))
    conn.commit()
    conn.close()


def pause_all_clients():
    conn = get_connection()
    conn.execute("UPDATE clients SET paused = 1")
    conn.commit()
    conn.close()


def resume_all_clients():
    conn = get_connection()
    conn.execute("UPDATE clients SET paused = 0")
    conn.commit()
    conn.close()


def move_client_to_completed(client_id):
    """
    작업 완료된 클라이언트를 status='completed'로 변경하고, paused=1 (일시정지) 처리.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE clients
           SET status='completed',
               paused=1  -- ✅ 완료된 클라이언트는 정지 상태로 변경
         WHERE client_id=?
    """,
        (client_id,),
    )
    conn.commit()
    conn.close()
    print(
        f"✅ 클라이언트 {client_id}가 status='completed', paused=1 로 변경되었습니다."
    )


def add_post(client_id, client_name, client_site_url, keyword, pbn_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO posts (client_id, client_name, client_site_url, keyword, pbn_url)
    VALUES (?, ?, ?, ?, ?)
    """,
        (client_id, client_name, client_site_url, keyword, pbn_url),
    )
    conn.commit()
    conn.close()


def add_pbn_post(
    site_id,
    site_url,
    post_id,
    title,
    url,
    excerpt,
    date_published,
    word_count,
    categories=None,
    tags=None,
):
    """
    새로 생성된 포스트를 pbn_posts 테이블에 추가

    Args:
        site_id: PBN 사이트 ID
        site_url: PBN 사이트 URL
        post_id: WordPress 포스트 ID
        title: 포스트 제목
        url: 포스트 URL
        excerpt: 포스트 요약
        date_published: 발행일 (ISO 형식)
        word_count: 단어 수
        categories: 카테고리 리스트 (선택사항)
        tags: 태그 리스트 (선택사항)
    """
    import json
    from datetime import datetime

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO pbn_posts 
            (site_id, site_url, post_id, title, url, excerpt, date_published, word_count, categories, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                site_id,
                site_url,
                post_id,
                title,
                url,
                excerpt,
                date_published,
                word_count,
                json.dumps(categories or [], ensure_ascii=False),
                json.dumps(tags or [], ensure_ascii=False),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        print(f"   💾 pbn_posts 테이블에 포스트 추가 완료: {title}")
        return True
    except Exception as e:
        print(f"   ❌ pbn_posts 테이블 추가 실패: {e}")
        return False
    finally:
        conn.close()


def view_client_status(client_id):
    """
    클라이언트의 현재 상태 및 구축 상황 조회
    예:
    id| 이름    | 구축수량| 남은수량 | 남은날짜
    해당 클라이언트의 posts 테이블에서 구축된 수량 = count(*)
    남은수량 = total_backlinks - 구축된 수량
    남은날짜 = remaining_days
    """
    conn = get_connection()
    cursor = conn.cursor()
    c = cursor.execute(
        "SELECT client_name, total_backlinks, remaining_days FROM clients WHERE client_id=?",
        (client_id,),
    ).fetchone()
    if not c:
        conn.close()
        return None
    client_name, total_bl, remain_days = c
    built_count = cursor.execute(
        "SELECT COUNT(*) FROM posts WHERE client_id=?", (client_id,)
    ).fetchone()[0]
    remaining_count = total_bl - built_count
    conn.close()

    # print_table 함수로 출력
    headers = [
        "Client ID",
        "Client Name",
        "Built Count",
        "Remaining Count",
        "Remaining Days",
    ]
    data = [(client_id, client_name, built_count, remaining_count, remain_days)]
    print_table("클라이언트 상태", data, headers)

    return {
        "client_id": client_id,
        "client_name": client_name,
        "built_count": built_count,
        "remaining_count": remaining_count,
        "remaining_days": remain_days,
    }


def show_all_tables():
    conn = get_connection()
    cursor = conn.cursor()
    tables = ["pbn_sites", "clients", "completed_clients", "posts"]

    result = {}
    for t in tables:
        rows = cursor.execute(f"SELECT * FROM {t}").fetchall()
        result[t] = rows
    conn.close()
    return result


def fetch_all_posts():
    """
    DB에서 모든 백링크 정보를 가져옴
    → 이제 status='completed'여도 clients 테이블에 존재하므로
       JOIN이 정상적으로 걸려서 모두 표시됨
    """
    conn = get_connection()
    query = """
    SELECT 
        p.post_id, 
        p.client_id, 
        c.client_name, 
        c.site_url AS client_site, 
        p.keyword, 
        p.pbn_url AS post_url
    FROM posts p
    JOIN clients c ON p.client_id = c.client_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# https:// 시트이름 에러
def clean_sheet_name(name):
    return re.sub(r"[\[\]\:\*\?\/\\]", "", name).strip()[:31]


def save_all_backlinks_to_excel(output_file="backlink_report.xlsx"):
    """
    모든 클라이언트와 백링크 정보를 엑셀 파일로 저장합니다.
    첫 번째 탭에 전체 데이터를 넣고, 클라이언트별로 탭을 생성합니다.
    """
    # 모든 데이터를 가져옵니다.
    posts_df = fetch_all_posts()

    if posts_df.empty:
        print("백링크 데이터가 없습니다. 엑셀 파일이 생성되지 않았습니다.")
        return

    # ExcelWriter를 사용해 파일 저장 시작
    writer = pd.ExcelWriter(output_file, engine="xlsxwriter")

    # 첫 번째 탭: 전체 백링크 데이터
    posts_df.to_excel(writer, sheet_name="All_Backlinks", index=False)

    # 클라이언트별 탭 생성
    clients = posts_df["client_id"].unique()
    for client_id in clients:
        client_posts = posts_df[posts_df["client_id"] == client_id]
        raw_name = client_posts["client_name"].iloc[0]
        safe_name = clean_sheet_name(f"{raw_name[:10]}_{client_id}")
        # 클라이언트별 탭에 데이터 저장
        client_posts.to_excel(writer, sheet_name=safe_name, index=False)

    # 엑셀 파일 저장 완료
    writer.close()
    print(f"모든 백링크 보고서가 성공적으로 저장되었습니다: {output_file}")


# 테이블의 모든 데이터를 삭제하는 함수
def reset_table_and_id_forcefully(table_name, create_table_sql):
    """
    테이블을 강제로 삭제하고 다시 생성해 ID를 1부터 시작하도록 리셋하는 함수
    :param table_name: 테이블 이름
    :param create_table_sql: 테이블 생성 SQL문
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 테이블 삭제
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"{table_name} 테이블이 삭제되었습니다.")

        # 테이블 다시 생성
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"{table_name} 테이블이 새로 생성되었습니다. ID가 1부터 시작됩니다.")

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()


# 특정 테이블의 특정 데이터를 삭제하는 함수
def delete_record_by_id(table_name, record_id, id_column_name="id"):
    """
    특정 테이블에서 ID 컬럼 값을 기준으로 데이터를 삭제하는 함수
    :param table_name: 삭제할 테이블의 이름
    :param record_id: 삭제할 레코드의 ID
    :param id_column_name: 기본 키나 식별 컬럼 이름 (기본값: id)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # SQL 인젝션 방지를 위해 파라미터화된 쿼리 사용
        query = f"DELETE FROM {table_name} WHERE {id_column_name} = ?"
        cursor.execute(query, (record_id,))
        conn.commit()
        print(
            f"{table_name} 테이블에서 {id_column_name} = {record_id}인 데이터가 삭제되었습니다."
        )
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()

    # 예시: PBN 사이트에서 site_id가 1인 데이터 삭제
    # delete_record_by_id("pbn_sites", 1, "site_id")
    # 예시: 클라이언트 테이블에서 client_id가 2인 데이터 삭제
    # delete_record_by_id("clients", 2, "client_id")


def migrate_remove_keywords_from_clients():
    """
    clients 테이블에서 keywords 컬럼을 제거하기 위한 마이그레이션 함수.
    1. clients_new 테이블 생성 (keywords 없는 스키마)
    2. 기존 clients 데이터 keywords 제외하고 clients_new로 복사
    3. clients 테이블 삭제
    4. clients_new를 clients로 rename
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. 새로운 테이블 생성
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS clients_new (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            site_url TEXT NOT NULL,
            total_backlinks INTEGER NOT NULL,
            remaining_days INTEGER NOT NULL,
            daily_backlinks INTEGER NOT NULL,
            paused INTEGER NOT NULL DEFAULT 0
        )
        """
        )

        # 2. 기존 clients 데이터 중 keywords 제외하고 복사
        #    기존 clients 구조: client_id, client_name, site_url, keywords, total_backlinks, remaining_days, daily_backlinks, paused
        #    새로운 구조:      client_id, client_name, site_url, total_backlinks, remaining_days, daily_backlinks, paused
        #    keywords 컬럼을 제외하고 나머지만 SELECT
        cursor.execute(
            """
        INSERT INTO clients_new (client_id, client_name, site_url, total_backlinks, remaining_days, daily_backlinks, paused)
        SELECT client_id, client_name, site_url, total_backlinks, remaining_days, daily_backlinks, paused
        FROM clients
        """
        )

        conn.commit()

        # 3. 기존 clients 테이블 삭제
        cursor.execute("DROP TABLE clients")

        # 4. 새 테이블 이름 변경
        cursor.execute("ALTER TABLE clients_new RENAME TO clients")
        conn.commit()
        print("clients 테이블에서 keywords 컬럼 제거 마이그레이션 완료.")
    except Exception as e:
        print("마이그레이션 중 오류 발생:", e)
    finally:
        conn.close()


def migrate_add_daily_min_max():
    import sqlite3
    from controlDB import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "ALTER TABLE clients ADD COLUMN daily_min INTEGER NOT NULL DEFAULT 1;"
        )
    except Exception as e:
        print("daily_min 추가 중 오류 (이미 존재할 수 있음)", e)
    try:
        c.execute(
            "ALTER TABLE clients ADD COLUMN daily_max INTEGER NOT NULL DEFAULT 5;"
        )
    except Exception as e:
        print("daily_max 추가 중 오류 (이미 존재할 수 있음)", e)
    conn.commit()
    conn.close()
    print("migrate_add_daily_min_max 완료")


def migrate_add_status_column():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # status 컬럼 추가 (이미 존재하면 예외 발생할 수 있음)
        cursor.execute(
            "ALTER TABLE clients ADD COLUMN status TEXT NOT NULL DEFAULT 'active';"
        )
        conn.commit()
        print("clients 테이블에 status 컬럼 추가 완료.")
    except Exception as e:
        print("status 컬럼 추가 중 오류 (이미 존재할 수 있음):", e)
    finally:
        conn.close()


def migrate_completed_clients_to_status():
    conn = get_connection()
    cursor = conn.cursor()

    # 1) completed_clients 테이블의 모든 행을 가져온 뒤
    rows = cursor.execute("SELECT * FROM completed_clients").fetchall()
    if not rows:
        print("completed_clients 테이블이 비어있거나 없습니다.")
    else:
        # completed_clients 테이블 구조:
        # (client_id, client_name, site_url, total_backlinks, daily_backlinks)
        for row in rows:
            (c_id, c_name, c_url, t_bl, d_bl) = row
            # clients에 해당 c_id가 이미 존재하는지 확인
            # (이미 삭제된 뒤 move 되었다면 존재 X)
            client_in_main = cursor.execute(
                "SELECT client_id FROM clients WHERE client_id=?", (c_id,)
            ).fetchone()
            if not client_in_main:
                # 없다면, 새로 INSERT
                cursor.execute(
                    """
                INSERT INTO clients (
                    client_id, client_name, site_url, 
                    total_backlinks, remaining_days, daily_backlinks,
                    paused, status
                ) VALUES (?, ?, ?, ?, 0, ?, 0, 'completed')
                """,
                    (c_id, c_name, c_url, t_bl, d_bl),
                )
            else:
                # 이미 있으면(이상 케이스) status만 'completed'로 변경
                cursor.execute(
                    """
                UPDATE clients
                   SET status='completed'
                 WHERE client_id=?
                """,
                    (c_id,),
                )
        conn.commit()
        print("completed_clients → clients 마이그레이션 완료 (status='completed')")

    # 2) completed_clients 테이블 DROP (원치 않으면 주석 처리)
    try:
        cursor.execute("DROP TABLE completed_clients")
        conn.commit()
        print("completed_clients 테이블 삭제 완료.")
    except Exception as e:
        print("completed_clients 테이블 삭제 중 오류:", e)
    finally:
        conn.close()


def remove_duplicate_clients():
    """
    (client_name, site_url)이 동일한 클라이언트를 '중복'으로 보고,
    가장 작은 client_id 하나만 남기고 나머지는 모두 삭제한다.
    단, posts/keywords는 원본 client_id로 업데이트하여 데이터 손실을 최소화.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 모든 클라이언트 정보를 client_id 오름차순으로 가져오기
    rows = cursor.execute(
        """
        SELECT client_id, client_name, site_url
        FROM clients
        ORDER BY client_id
    """
    ).fetchall()

    # (client_name, site_url)를 키로 하는 dict
    # → 처음 등장하는 client_id를 '원본'으로
    unique_map = {}  # key: (name, url), value: main_client_id
    duplicates_list = []  # [(dup_id, main_id), ...]

    for cid, cname, curl in rows:
        key = (cname.strip(), curl.strip())  # 공백제거 등
        if key not in unique_map:
            # 첫등장이면 원본으로 등록
            unique_map[key] = cid
        else:
            # 이미 있으면 중복 발생
            main_id = unique_map[key]
            # 중복 기록
            duplicates_list.append((cid, main_id))

    # 실제 DB 업데이트
    merged_count = 0
    for dup_id, main_id in duplicates_list:
        # posts 테이블: 중복 client_id → main_id로 변경
        cursor.execute(
            """
            UPDATE posts
               SET client_id=?
             WHERE client_id=?
        """,
            (main_id, dup_id),
        )

        # client_keywords: 동일하게
        cursor.execute(
            """
            UPDATE client_keywords
               SET client_id=?
             WHERE client_id=?
        """,
            (main_id, dup_id),
        )

        # 이제 clients에서 중복 row 삭제
        cursor.execute(
            """
            DELETE FROM clients
             WHERE client_id=?
        """,
            (dup_id,),
        )
        merged_count += 1

    conn.commit()
    conn.close()

    print(
        f"중복 제거가 완료되었습니다. 총 {merged_count}개 중복 클라이언트가 삭제되었습니다."
    )


class ControlDB:
    """데이터베이스 관리 클래스"""

    def __init__(self):
        """데이터베이스 연결 초기화"""
        self.db_path = DB_PATH

    def get_pbn_sites(self):
        """PBN 사이트 목록 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pbn_sites")
        rows = cursor.fetchall()
        conn.close()

        sites = []
        for row in rows:
            sites.append(
                {
                    "id": row[0],
                    "url": row[1],
                    "username": row[2],
                    "password": row[3],
                    "app_password": row[4],
                }
            )
        return sites

    def get_clients(self):
        """클라이언트 목록 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT client_id, client_name, site_url, total_backlinks, 
                   remaining_days, daily_backlinks, paused, status
            FROM clients
        """
        )
        rows = cursor.fetchall()
        conn.close()

        clients = []
        for row in rows:
            clients.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "target_url": row[2],
                    "total_backlinks": row[3],
                    "remaining_days": row[4],
                    "daily_backlinks": row[5],
                    "paused": row[6],
                    "status": row[7] if len(row) > 7 else "active",
                }
            )
        return clients

    def get_client_keywords(self, client_id):
        """클라이언트의 키워드 목록 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT keyword FROM client_keywords WHERE client_id = ?", (client_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        keywords = []
        for row in rows:
            keywords.append({"keyword": row[0]})
        return keywords

    def add_pbn_site(self, site_url, username, password, app_password):
        """PBN 사이트 추가"""
        return add_pbn_site(site_url, username, password, app_password)

    def add_client(
        self, client_name, site_url, total_backlinks, remaining_days, daily_backlinks
    ):
        """클라이언트 추가"""
        return add_client(
            client_name, site_url, total_backlinks, remaining_days, daily_backlinks
        )

    def add_client_keyword(self, client_id, keyword):
        """클라이언트 키워드 추가"""
        return add_client_keyword(client_id, keyword)

    def update_client_status(self, client_id, status):
        """클라이언트 상태 업데이트"""
        return update_client_status(client_id, status)

    def get_posts(self):
        """포스트 목록 조회"""
        return fetch_all_posts()

    def save_post(self, post_data):
        """포스트 저장"""
        # TODO: 포스트 저장 기능 구현
        pass


# 초기 실행 시 테이블 생성
if __name__ == "__main__":
    # create_tables()
    # migrate_remove_keywords_from_clients()
    print("DB 및 테이블이 준비되었습니다.")
    load_clients_from_excel("client_info.xlsx")

    username = "admin"
    password = "Bamalba123!@#"  # 예시

    # (2) 추가할 사이트 목록 (site_url, app_password) 형태
    new_sites = [
        ("https://ididlabel.com/", "FsOp Mtmk AiVD hrL6 YyZH dNGg"),
        ("https://jxneel.com/", "JCY8 b6bH BIhJ N0ZY ngQs GePx"),
        ("https://kerala-music.com/", "kwDg WHwt EsxD DkNn rm9k C3HZ"),
        ("https://prospectionrecords.com/", "hJ27 2xPV uSDz i1bH gCG9 dDW5"),
        ("https://royaltroyalt.com/", "04cZ iV2C DuZV gIEx R4C2 3u8L"),
        ("https://ukf10.com/", "vEhv QdNE 2QTT xEO9 q9Fy h5v1"),
        ("https://bombaada.com/", "Dypz CheV aWl1 ZGcq HSqS PhIf"),
        ("https://rudeawakening-records.com/", "Oi2Y NZmk wFHC YGtV gMdv oOr3"),
        ("https://brockaflower.net/", "moUy kjCD o6W5 tXYR DRSQ breM"),
        ("https://needloverecords.com/", "9gqD dkLr XBoR ArOQ OEMS ttML"),
        ("https://ladyworkhub.com/", "jojN 0Vwr ArZi gyNy HdfP C5dd"),
        ("https://jobforgirl.com/", "G0kS 4uYB qp7j jCpX xcm7 Wn8e"),
        ("https://albaprincess.com/", "Uihu wMho OAue S8Pg VB9s xL9c"),
        ("https://jobangelgirl.com/", "X6Ce 4OEG DGVM JOJX 7bCx h3Ei"),
        ("https://work4babe.com/", "b7mE gGKH 8OHJ aKIL Kt15 7wBh"),
        ("https://bamladyjob.com/", "oiD4 Jno3 MKwx 8OiL jMIg nRo1"),
        ("https://prettyjobhub.com/", "GrW6 s6uL Klpo acew ajOs rDdT"),
        ("https://ladylancer.com/", "yldm Z3oV Shj9 dlSv wXDY BrYL"),
        ("https://ladyalbamarket.com/", "SKkb izH3 MVbm vvzx wkuz 4IxS"),
        ("https://jobcutie.com/", "eszn 5x5s Toj0 wSwW LXRI Hq98"),
        # 추가로 언급된 10개 (add_pbn_site 예시)
        ("https://reneteo.com/", "Y0L8 Pknu bbEG 0zZd kucU jx9b"),
        ("https://zalzip.com/", "2g0u xM77 2AQ7 a6f7 DWEc xgNM"),
        ("https://hikecove.com/", "JkXa VbjQ 1cTE zUtV W3yW kYVF"),
        ("https://rocketdon.com/", "9OlI GhE2 1kgm bEqG 8kl5 jnom"),
        ("https://suggestott.com/", "GpoQ zoJe f4fC c1mo mb28 ZW6M"),
        ("https://albambang.com/", "ghLZ c9qw EA7Q GcNa ZDIt m4n1"),
        ("https://bamlovealba.com/", "K2mw ehfw H1np ejpZ 1Ow9 TMcC"),
        ("https://foralba.com/", "khp0 2UFY P37Z 2jFt CfYK 6DRN"),
        ("https://lovelygirljob.com/", "Nqw2 nbUi SufJ Lyxu PuBe UtU1"),
        ("https://myladyjob.com/", "LZw7 hM1K tMuR wtSg qrcB cwSo"),
    ]

    # (3) 반복문으로 DB에 insert
    for site_url, app_pass in new_sites:
        add_pbn_site(site_url, username, password, app_pass)

    print("새로운 30개 사이트를 모두 pbn_sites 테이블에 추가했습니다.")
    # username = "admin"
    # password1 = "Lqp1o2k3!"
    # password2 = "Bamalba123!@#"
    # add_pbn_site("https://yururira-blog.com/", username, password1, "PHvR ANPR P9cI LqR3 md5D 5zEK")
    # add_pbn_site("https://gamecubedlx.com/", username, password1, "XHsN 7uce KhO8 jQGB 7VAD 14HC")
    # add_pbn_site("https://realfooddiets.com/", username, password1, "34Vz l4yL 7GZ4 MX2E RAIA oT7u")
    # add_pbn_site("https://volantsports.com/", username, password1, "8CkX OoRX qJlF bQKd 5Nbz E0o5")
    # add_pbn_site("https://secondmassage.com/", username, password1, "JrK1 Smms lCkS sZdY bJnI 89Rt")
    # add_pbn_site("https://croadriainvest.com/", username, password1, "aZoM qPIw a5K6 Flhk Uvl4 K1Zt")
    # add_pbn_site("https://maihiendidongnghean.com/", username, password1, "RO80 5pXd V6RO Y17j w4iW kab0")
    # add_pbn_site("https://margiesmassage.com/", username, password1, "S5gO LWVf rkk5 cb0J ajdV 6lXQ")
    # add_pbn_site("https://donofan.org/", username, password1, "ADsB Kdah bq7d 8yKK Kb4E 2Vdt")
    # add_pbn_site("https://cheryhardcore.com/", username, password1, "ysbq Z4tO E2CJ yuxj aShF oblu")
    # add_pbn_site("https://spam-news.com/", username, password1, "9vH6 Lt2u KWJj xzYg iqf6 QV6M")
    # add_pbn_site("https://easyridersdanang.com/", username, password1, "WCiI LJq4 w0LM Anp0 TyDI 9uCe")
    # add_pbn_site("https://dailydoseofsales.com/", username, password1, "WCiI LJq4 w0LM Anp0 TyDI 9uCe")
    # add_pbn_site("https://uniqecasino.com/", username, password1, "OzFB 6eeA Pn2U Zx6z 68A5 PuHz")
    # add_pbn_site("https://totoagc.com/", username, password1, "cmTW gkIp Eqq1 cx8V qzYX gG6Y")
    # add_pbn_site("https://andybakerlive.com/", username, password1, "t9PE GtLa Qi2L oxn9 YReS bGd2")
    # add_pbn_site("https://hvslive.com/", username, password1, "ylM0 u4oI S70U m2On IY8U YlZ7")
    # add_pbn_site("https://justlygamble.com/", username, password1, "fb8o Fejb Bzfe giSJ 1r7f 4thg")
    # add_pbn_site("https://futuresportsedition.com/", username, password1, "7O28 ZE2D 4Dji UIz4 PbIP A4dF")
    # add_pbn_site("https://cheshireparlour.com/", username, password2, "oiIC xyDM SB0Q 10bR Fr3f nrIp")
    # add_pbn_site("https://osucr.com/", username, password2, "pLNi feo0 M4gU fI2K MAVb lrFM")
    # add_pbn_site("https://hvpwc.com/", username, password2, "qZY0 sjbl ZWkX ny1z jBv0 edZg")
    # add_pbn_site("https://ppjwc.com/", username, password2, "ZXQh 2wJw Y3AV l3qp yRTW NBm2")
    # add_pbn_site("https://tapsule.me/", username, password2, "roTX 6icl n6PM 2XkT 3A7H muim")
    fetch_all_posts()
    migrate_add_status_column()
    migrate_completed_clients_to_status()
    # view_pbn_sites()
    view_clients()

    # view_all_client_keywords()
    # view_completed_clients()
