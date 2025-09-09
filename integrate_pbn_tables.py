#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PBN 테이블 통합 스크립트
기존 controlDB.db에 pbn_posts 테이블을 추가하여 하나의 DB로 통합
"""

import sqlite3
import os
from pathlib import Path


def integrate_pbn_tables():
    """기존 controlDB.db에 PBN 포스트 테이블 추가"""

    print("🔧 PBN 테이블 통합 시작...")

    # 기존 controlDB.db에 연결
    control_db_path = "controlDB.db"

    if not os.path.exists(control_db_path):
        print("❌ controlDB.db 파일을 찾을 수 없습니다.")
        return False

    try:
        with sqlite3.connect(control_db_path) as conn:
            cursor = conn.cursor()

            print("📋 기존 테이블 확인 중...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"   기존 테이블: {existing_tables}")

            # PBN 포스트 테이블 생성 (이미 있으면 무시)
            print("🆕 pbn_posts 테이블 생성 중...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pbn_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    site_url TEXT NOT NULL,
                    post_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    excerpt TEXT,
                    date_published TEXT,
                    word_count INTEGER DEFAULT 0,
                    categories TEXT,  -- JSON 형태로 저장
                    tags TEXT,        -- JSON 형태로 저장
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (site_id) REFERENCES pbn_sites (site_id)
                )
            """
            )

            # 크롤링 로그 테이블 생성
            print("📊 crawl_logs 테이블 생성 중...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crawl_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    site_url TEXT NOT NULL,
                    total_posts INTEGER DEFAULT 0,
                    successful_posts INTEGER DEFAULT 0,
                    failed_posts INTEGER DEFAULT 0,
                    crawl_duration REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (site_id) REFERENCES pbn_sites (site_id)
                )
            """
            )

            # 인덱스 생성 (검색 성능 향상)
            print("🔍 인덱스 생성 중...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_pbn_posts_site_id ON pbn_posts(site_id)",
                "CREATE INDEX IF NOT EXISTS idx_pbn_posts_title ON pbn_posts(title)",
                "CREATE INDEX IF NOT EXISTS idx_pbn_posts_url ON pbn_posts(url)",
                "CREATE INDEX IF NOT EXISTS idx_pbn_posts_date ON pbn_posts(date_published)",
                "CREATE INDEX IF NOT EXISTS idx_crawl_logs_site_id ON crawl_logs(site_id)",
                "CREATE INDEX IF NOT EXISTS idx_crawl_logs_status ON crawl_logs(status)",
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            conn.commit()

            # 테이블 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            updated_tables = [row[0] for row in cursor.fetchall()]

            print("✅ 테이블 통합 완료!")
            print(f"📋 현재 테이블: {updated_tables}")

            # 각 테이블의 레코드 수 확인
            print("\n📊 테이블별 레코드 수:")
            for table in ["pbn_sites", "clients", "pbn_posts", "crawl_logs"]:
                if table in updated_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   {table}: {count:,}개")

            return True

    except Exception as e:
        print(f"❌ 테이블 통합 중 오류: {e}")
        return False


def migrate_existing_data():
    """기존 pbn_content_database.db 데이터를 controlDB.db로 이전"""

    old_db_path = "pbn_content_database.db"
    control_db_path = "controlDB.db"

    if not os.path.exists(old_db_path):
        print("ℹ️ 기존 pbn_content_database.db가 없습니다. 새로 시작합니다.")
        return True

    print("🔄 기존 데이터 마이그레이션 시작...")

    try:
        # 기존 데이터 읽기
        with sqlite3.connect(old_db_path) as old_conn:
            old_cursor = old_conn.cursor()

            # pbn_posts 데이터 가져오기
            old_cursor.execute(
                """
                SELECT site_id, site_url, post_id, title, url, excerpt, 
                       date_published, word_count, categories, tags
                FROM pbn_posts
            """
            )
            posts_data = old_cursor.fetchall()

            # crawl_logs 데이터 가져오기
            old_cursor.execute(
                """
                SELECT site_id, site_url, total_posts, successful_posts, 
                       failed_posts, crawl_duration, status, error_message
                FROM crawl_logs
            """
            )
            logs_data = old_cursor.fetchall()

        # 새 데이터베이스에 삽입
        with sqlite3.connect(control_db_path) as new_conn:
            new_cursor = new_conn.cursor()

            # 포스트 데이터 삽입
            if posts_data:
                print(f"📄 {len(posts_data)}개 포스트 데이터 이전 중...")
                new_cursor.executemany(
                    """
                    INSERT OR IGNORE INTO pbn_posts 
                    (site_id, site_url, post_id, title, url, excerpt, 
                     date_published, word_count, categories, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    posts_data,
                )

            # 로그 데이터 삽입
            if logs_data:
                print(f"📊 {len(logs_data)}개 로그 데이터 이전 중...")
                new_cursor.executemany(
                    """
                    INSERT OR IGNORE INTO crawl_logs 
                    (site_id, site_url, total_posts, successful_posts, 
                     failed_posts, crawl_duration, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    logs_data,
                )

            new_conn.commit()

        print("✅ 데이터 마이그레이션 완료!")

        # 기존 파일 백업 후 삭제 여부 확인
        backup_path = f"{old_db_path}.backup"
        os.rename(old_db_path, backup_path)
        print(f"📦 기존 DB를 {backup_path}로 백업했습니다.")

        return True

    except Exception as e:
        print(f"❌ 데이터 마이그레이션 중 오류: {e}")
        return False


def update_crawler_to_use_control_db():
    """크롤러가 controlDB.db를 사용하도록 수정"""

    print("🔧 크롤러 설정 업데이트 중...")

    # pbn_content_crawler.py 파일 수정
    crawler_file = "pbn_content_crawler.py"

    if not os.path.exists(crawler_file):
        print("❌ pbn_content_crawler.py 파일을 찾을 수 없습니다.")
        return False

    try:
        # 파일 읽기
        with open(crawler_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 기본 데이터베이스 경로 변경
        updated_content = content.replace(
            'db_path: str = "pbn_content_database.db"', 'db_path: str = "controlDB.db"'
        )

        # 파일 쓰기
        with open(crawler_file, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print("✅ 크롤러 설정 업데이트 완료!")
        return True

    except Exception as e:
        print(f"❌ 크롤러 설정 업데이트 중 오류: {e}")
        return False


def main():
    """메인 통합 프로세스"""

    print("🚀 PBN 시스템 데이터베이스 통합 시작")
    print("=" * 50)

    steps = [
        ("테이블 구조 통합", integrate_pbn_tables),
        ("기존 데이터 마이그레이션", migrate_existing_data),
        ("크롤러 설정 업데이트", update_crawler_to_use_control_db),
    ]

    success_count = 0

    for step_name, step_func in steps:
        print(f"\n🔄 {step_name} 실행 중...")

        if step_func():
            print(f"✅ {step_name} 완료")
            success_count += 1
        else:
            print(f"❌ {step_name} 실패")
            break

    print("\n" + "=" * 50)
    if success_count == len(steps):
        print("🎉 모든 통합 과정이 완료되었습니다!")
        print("\n📋 다음 단계:")
        print("1. python enhanced_main_v2.py 실행")
        print("2. 메뉴에서 '21. PBN 콘텐츠 크롤링' 선택")
        print("3. 크롤링 완료 후 링크 빌딩 시스템 사용")
    else:
        print(f"⚠️ {success_count}/{len(steps)} 단계만 완료되었습니다.")
        print("문제를 해결한 후 다시 시도해주세요.")


if __name__ == "__main__":
    main()
