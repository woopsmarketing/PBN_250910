#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAISS 인덱스 상태 확인
"""

import sqlite3
import json
from pathlib import Path

def check_faiss_status():
    """FAISS 인덱스와 데이터베이스 상태 확인"""
    
    print("=== FAISS 인덱스 상태 확인 ===")
    
    # 1. pbn_posts 테이블 확인
    conn = sqlite3.connect('controlDB.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pbn_posts")
    pbn_posts_count = cursor.fetchone()[0]
    print(f"pbn_posts 테이블: {pbn_posts_count:,}개 포스트")
    
    # 최근 포스트 3개 확인
    cursor.execute("""
        SELECT id, title, date_published 
        FROM pbn_posts 
        ORDER BY id DESC 
        LIMIT 3
    """)
    recent_posts = cursor.fetchall()
    
    print("\n최근 포스트 3개:")
    for post in recent_posts:
        print(f"  ID: {post[0]} | {post[1]} | {post[2]}")
    
    conn.close()
    
    # 2. FAISS 인덱스 파일 확인
    faiss_file = Path("embedding_cache/faiss_index.bin")
    metadata_file = Path("embedding_cache/post_metadata.json")
    
    print(f"\nFAISS 인덱스 파일:")
    print(f"  faiss_index.bin: {'존재' if faiss_file.exists() else '없음'}")
    print(f"  post_metadata.json: {'존재' if metadata_file.exists() else '없음'}")
    
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"  메타데이터 포스트 수: {len(metadata):,}개")
        
        if metadata:
            print(f"\nFAISS 메타데이터 최근 3개:")
            for i, post in enumerate(metadata[-3:], 1):
                print(f"  {i}. {post.get('title', 'No Title')} | {post.get('date_published', 'No Date')}")
    
    # 3. 비교
    print(f"\n비교 결과:")
    print(f"  pbn_posts 테이블: {pbn_posts_count:,}개")
    if metadata_file.exists():
        print(f"  FAISS 메타데이터: {len(metadata):,}개")
        if pbn_posts_count > len(metadata):
            print(f"  차이: {pbn_posts_count - len(metadata):,}개 (FAISS가 뒤처짐)")
        elif pbn_posts_count < len(metadata):
            print(f"  차이: {len(metadata) - pbn_posts_count:,}개 (데이터 불일치)")
        else:
            print(f"  동기화 완료")
    else:
        print(f"  FAISS 메타데이터 파일이 없습니다")

if __name__ == "__main__":
    check_faiss_status()