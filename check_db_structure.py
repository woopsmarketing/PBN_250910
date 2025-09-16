#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 구조 및 데이터 확인
"""

import sqlite3

def check_database():
    """데이터베이스 구조와 데이터 확인"""
    
    conn = sqlite3.connect('controlDB.db')
    cursor = conn.cursor()
    
    print("=== 데이터베이스 테이블 목록 ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "="*60)
    
    # 각 테이블의 스키마와 데이터 수 확인
    for table in tables:
        table_name = table[0]
        print(f"\n=== {table_name} 테이블 ===")
        
        # 스키마 확인
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("컬럼 구조:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # 데이터 수 확인
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"총 레코드 수: {count:,}개")
        
        # 샘플 데이터 확인 (처음 3개)
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            samples = cursor.fetchall()
            print("샘플 데이터:")
            for i, sample in enumerate(samples, 1):
                print(f"  {i}. {sample}")
    
    conn.close()

if __name__ == "__main__":
    check_database()