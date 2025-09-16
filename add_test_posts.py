#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트용 포스트 데이터 추가
"""

import sqlite3
from datetime import datetime, timedelta
import json

def add_test_posts():
    """테스트용 포스트 데이터 추가"""
    
    print("=== 테스트용 포스트 데이터 추가 ===")
    
    conn = sqlite3.connect('controlDB.db')
    cursor = conn.cursor()
    
    # 테스트 포스트 데이터 (다양한 날짜로)
    test_posts = [
        {
            "site_id": 1,
            "site_url": "https://test1.com",
            "post_id": 1001,
            "title": "구글 SEO 최적화 방법 - 2024년 최신 가이드",
            "url": "https://test1.com/seo-guide-2024",
            "excerpt": "구글 SEO를 위한 최신 최적화 방법들을 소개합니다.",
            "date_published": (datetime.now() - timedelta(days=1)).isoformat(),
            "word_count": 1200,
            "categories": json.dumps(["SEO", "마케팅"]),
            "tags": json.dumps(["구글", "SEO", "최적화"])
        },
        {
            "site_id": 1,
            "site_url": "https://test1.com",
            "post_id": 1002,
            "title": "백링크 구축 전략 - 효과적인 링크 빌딩",
            "url": "https://test1.com/backlink-strategy",
            "excerpt": "백링크 구축을 위한 효과적인 전략과 방법을 알려드립니다.",
            "date_published": (datetime.now() - timedelta(days=3)).isoformat(),
            "word_count": 1500,
            "categories": json.dumps(["백링크", "SEO"]),
            "tags": json.dumps(["백링크", "링크빌딩", "SEO"])
        },
        {
            "site_id": 2,
            "site_url": "https://test2.com",
            "post_id": 2001,
            "title": "PBN 백링크의 장단점 분석",
            "url": "https://test2.com/pbn-analysis",
            "excerpt": "PBN 백링크의 장점과 단점을 자세히 분석해보겠습니다.",
            "date_published": (datetime.now() - timedelta(days=7)).isoformat(),
            "word_count": 1800,
            "categories": json.dumps(["PBN", "백링크"]),
            "tags": json.dumps(["PBN", "백링크", "분석"])
        },
        {
            "site_id": 1,
            "site_url": "https://test1.com",
            "post_id": 1003,
            "title": "구글 상위노출을 위한 콘텐츠 마케팅",
            "url": "https://test1.com/content-marketing",
            "excerpt": "구글 상위노출을 위한 콘텐츠 마케팅 전략을 소개합니다.",
            "date_published": (datetime.now() - timedelta(hours=6)).isoformat(),
            "word_count": 2000,
            "categories": json.dumps(["콘텐츠", "마케팅"]),
            "tags": json.dumps(["콘텐츠", "마케팅", "구글"])
        },
        {
            "site_id": 2,
            "site_url": "https://test2.com",
            "post_id": 2002,
            "title": "SEO 키워드 연구 방법론",
            "url": "https://test2.com/keyword-research",
            "excerpt": "효과적인 SEO 키워드 연구 방법을 단계별로 설명합니다.",
            "date_published": (datetime.now() - timedelta(days=14)).isoformat(),
            "word_count": 1600,
            "categories": json.dumps(["키워드", "SEO"]),
            "tags": json.dumps(["키워드", "연구", "SEO"])
        }
    ]
    
    # 포스트 삽입
    for post in test_posts:
        cursor.execute("""
            INSERT INTO pbn_posts 
            (site_id, site_url, post_id, title, url, excerpt, date_published, word_count, categories, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post["site_id"],
            post["site_url"],
            post["post_id"],
            post["title"],
            post["url"],
            post["excerpt"],
            post["date_published"],
            post["word_count"],
            post["categories"],
            post["tags"],
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"테스트 포스트 {len(test_posts)}개 추가 완료")

if __name__ == "__main__":
    add_test_posts()