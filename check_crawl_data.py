#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크롤링 데이터 확인 스크립트
"""

import sqlite3
import os


def check_crawl_data():
    """크롤링된 데이터 확인"""

    db_files = ["pbn_content_database.db", "controlDB.db"]

    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n📊 {db_file} 데이터 확인:")
            print("=" * 40)

            try:
                with sqlite3.connect(db_file) as conn:
                    cursor = conn.cursor()

                    # 테이블 목록 확인
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    print(f"📋 테이블: {tables}")

                    # pbn_posts 테이블이 있으면 상세 정보
                    if "pbn_posts" in tables:
                        cursor.execute("SELECT COUNT(*) FROM pbn_posts")
                        total_posts = cursor.fetchone()[0]
                        print(f"📄 총 포스트 수: {total_posts:,}개")

                        cursor.execute("SELECT COUNT(DISTINCT site_url) FROM pbn_posts")
                        unique_sites = cursor.fetchone()[0]
                        print(f"🌐 크롤링된 사이트 수: {unique_sites}개")

                        # 사이트별 포스트 수 (상위 5개)
                        cursor.execute(
                            """
                            SELECT site_url, COUNT(*) as post_count 
                            FROM pbn_posts 
                            GROUP BY site_url 
                            ORDER BY post_count DESC 
                            LIMIT 5
                        """
                        )
                        top_sites = cursor.fetchall()

                        print("\n🏆 포스트 수 상위 5개 사이트:")
                        for site_url, count in top_sites:
                            print(f"   • {site_url}: {count:,}개")

                        # 최근 크롤링된 포스트 샘플
                        cursor.execute(
                            """
                            SELECT title, site_url, date_published 
                            FROM pbn_posts 
                            ORDER BY created_at DESC 
                            LIMIT 3
                        """
                        )
                        recent_posts = cursor.fetchall()

                        print("\n📝 최근 크롤링된 포스트 샘플:")
                        for title, site_url, date_pub in recent_posts:
                            print(f"   • {title[:50]}... ({site_url})")

                    # crawl_logs 테이블이 있으면 로그 정보
                    if "crawl_logs" in tables:
                        cursor.execute("SELECT COUNT(*) FROM crawl_logs")
                        log_count = cursor.fetchone()[0]
                        print(f"📊 크롤링 로그 수: {log_count}개")

                        cursor.execute(
                            """
                            SELECT status, COUNT(*) 
                            FROM crawl_logs 
                            GROUP BY status
                        """
                        )
                        status_counts = cursor.fetchall()

                        print("📈 크롤링 상태별 통계:")
                        for status, count in status_counts:
                            print(f"   • {status}: {count}개")

            except Exception as e:
                print(f"❌ 데이터베이스 확인 중 오류: {e}")
        else:
            print(f"❌ {db_file} 파일이 존재하지 않습니다.")


def check_api_errors():
    """API 오류 분석"""

    print("\n🔍 API 오류 분석:")
    print("=" * 30)

    error_codes = {
        400: "잘못된 요청 (Bad Request)",
        401: "인증 실패 (Unauthorized)",
        403: "접근 금지 (Forbidden)",
        404: "페이지 없음 (Not Found)",
        500: "서버 오류 (Internal Server Error)",
        502: "게이트웨이 오류 (Bad Gateway)",
        503: "서비스 사용 불가 (Service Unavailable)",
    }

    print("📋 HTTP 상태 코드 의미:")
    print("• 400 (Bad Request): WordPress REST API 요청이 잘못되었거나")
    print("  해당 페이지에 더 이상 포스트가 없을 때 발생")
    print("• SSL 인증서 오류: 사이트의 SSL 인증서가 만료되었거나 자체 서명된 경우")
    print("• 500 오류: 서버 과부하나 내부 오류")

    print("\n✅ 크롤링 성공 기준:")
    print("• 각 사이트별로 수집된 포스트 수가 표시됨")
    print("• '✅ 크롤링 완료' 메시지와 함께 저장된 포스트 수 표시")
    print("• API 오류가 발생해도 그 전까지 수집된 데이터는 정상 저장됨")


if __name__ == "__main__":
    check_crawl_data()
    check_api_errors()
