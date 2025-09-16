#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최신 글 우선 정렬 테스트
"""

import sqlite3
from datetime import datetime

def test_recent_posts():
    """최신 글 우선 정렬 테스트"""
    
    print("=== 최신 글 우선 정렬 테스트 ===")
    
    # pbn_posts 테이블에서 최근 포스트들 확인
    conn = sqlite3.connect('controlDB.db')
    cursor = conn.cursor()
    
    # 최근 10개 포스트 가져오기
    cursor.execute("""
        SELECT id, title, date_published 
        FROM pbn_posts 
        ORDER BY id DESC 
        LIMIT 10
    """)
    recent_posts = cursor.fetchall()
    
    print(f"pbn_posts 테이블 최근 10개 포스트:")
    for i, post in enumerate(recent_posts, 1):
        print(f"  {i}. ID: {post[0]} | {post[1][:50]}... | {post[2]}")
    
    # 날짜별 정렬 테스트
    print(f"\n날짜별 정렬 테스트:")
    
    def safe_date_sort(post):
        """안전한 날짜 정렬을 위한 함수"""
        try:
            date_str = post[2]  # date_published
            if date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.min
        except (ValueError, TypeError):
            return datetime.min
    
    # 날짜 기준으로 정렬
    sorted_posts = sorted(recent_posts, key=safe_date_sort, reverse=True)
    
    print("최신 글 우선 정렬 결과:")
    for i, post in enumerate(sorted_posts, 1):
        date_obj = safe_date_sort(post)
        print(f"  {i}. {date_obj.strftime('%Y-%m-%d %H:%M')} | {post[1][:50]}...")
    
    conn.close()

if __name__ == "__main__":
    test_recent_posts()