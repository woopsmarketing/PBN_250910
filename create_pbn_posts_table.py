#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pbn_posts 테이블 생성
"""

from controlDB import create_tables

def main():
    print("=== pbn_posts 테이블 생성 ===")
    create_tables()
    print("테이블 생성 완료")

if __name__ == "__main__":
    main()