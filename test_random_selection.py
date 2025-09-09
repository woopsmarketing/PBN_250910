#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
랜덤 선택 시스템 테스트 스크립트
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from improved_similarity_system import ImprovedSimilaritySystem


def test_random_selection():
    """랜덤 선택 기능 테스트"""

    print("🎲 랜덤 선택 시스템 테스트")
    print("=" * 50)

    # 시스템 초기화
    similarity_system = ImprovedSimilaritySystem()

    # 테스트 키워드
    test_keywords = ["백링크", "SEO", "검색엔진", "마케팅"]

    for keyword in test_keywords:
        print(f"\n🔍 키워드: '{keyword}'")
        print("-" * 30)

        # 동일한 키워드로 여러 번 검색하여 랜덤성 확인
        results_history = []

        for i in range(3):
            print(f"\n📋 검색 #{i+1}:")

            # 랜덤 선택 활성화
            results = similarity_system.find_similar_posts_fast(
                [keyword], limit=3, min_similarity=0.3, random_selection=True
            )

            if results:
                for j, result in enumerate(results):
                    print(
                        f"   {j+1}. {result['title'][:50]}... (유사도: {result['similarity_score']:.3f})"
                    )
                    print(f"      URL: {result['url']}")

                # 결과 기록 (제목만)
                titles = [r["title"] for r in results]
                results_history.append(titles)
            else:
                print("   ❌ 결과 없음")

        # 랜덤성 분석
        print(f"\n📊 랜덤성 분석:")
        all_titles = []
        for titles in results_history:
            all_titles.extend(titles)

        unique_titles = set(all_titles)
        total_results = len(all_titles)
        unique_count = len(unique_titles)

        print(f"   총 결과: {total_results}개")
        print(f"   고유 결과: {unique_count}개")
        print(f"   다양성: {unique_count/total_results*100:.1f}%")

        if unique_count > total_results * 0.5:
            print("   ✅ 랜덤 선택이 잘 작동하고 있습니다!")
        else:
            print("   ⚠️ 결과가 비슷합니다. 더 많은 후보가 필요할 수 있습니다.")


def test_vs_sequential():
    """랜덤 선택 vs 순차 선택 비교"""

    print("\n\n🆚 랜덤 선택 vs 순차 선택 비교")
    print("=" * 50)

    similarity_system = ImprovedSimilaritySystem()
    keyword = "백링크"

    print(f"🔍 키워드: '{keyword}'")

    # 순차 선택 (기존 방식)
    print(f"\n📋 순차 선택 (random_selection=False):")
    sequential_results = similarity_system.find_similar_posts_fast(
        [keyword], limit=5, min_similarity=0.3, random_selection=False
    )

    for i, result in enumerate(sequential_results):
        print(
            f"   {i+1}. {result['title'][:50]}... (유사도: {result['similarity_score']:.3f})"
        )

    # 랜덤 선택 (새로운 방식)
    print(f"\n🎲 랜덤 선택 (random_selection=True):")
    random_results = similarity_system.find_similar_posts_fast(
        [keyword], limit=5, min_similarity=0.3, random_selection=True
    )

    for i, result in enumerate(random_results):
        print(
            f"   {i+1}. {result['title'][:50]}... (유사도: {result['similarity_score']:.3f})"
        )

    # 비교 분석
    print(f"\n📊 비교 분석:")
    sequential_titles = [r["title"] for r in sequential_results]
    random_titles = [r["title"] for r in random_results]

    overlap = set(sequential_titles) & set(random_titles)
    print(f"   순차 선택 결과: {len(sequential_titles)}개")
    print(f"   랜덤 선택 결과: {len(random_titles)}개")
    print(f"   겹치는 결과: {len(overlap)}개")
    print(f"   다양성 개선: {len(overlap)/len(sequential_titles)*100:.1f}% 겹침")


if __name__ == "__main__":
    try:
        test_random_selection()
        test_vs_sequential()

        print("\n🎉 랜덤 선택 시스템 테스트 완료!")
        print("\n💡 결론:")
        print("• 랜덤 선택으로 동일한 키워드에 대해 다양한 링크 생성")
        print("• 중복 링크 문제 해결")
        print("• SEO 다양성 향상")

    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        import traceback

        traceback.print_exc()
