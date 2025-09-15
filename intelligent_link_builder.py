# 지능형 링크 빌더 시스템
# 콘텐츠 내에 내부링크와 외부링크를 자동으로 삽입

import re
import random
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pbn_content_crawler import PBNContentCrawler
from improved_similarity_system import ImprovedSimilaritySystem


@dataclass
class LinkCandidate:
    """링크 후보 데이터 클래스"""

    text: str  # 앵커 텍스트
    url: str  # 링크 URL
    link_type: str  # 'internal' 또는 'external'
    position: int  # 콘텐츠 내 위치
    confidence: float  # 신뢰도 점수 (0-1)
    source: str  # 링크 소스 ('client', 'pbn', 'external')


class IntelligentLinkBuilder:
    """지능형 링크 빌더 클래스"""

    def __init__(self, crawler: PBNContentCrawler = None):
        """
        링크 빌더 초기화

        Args:
            crawler: PBN 콘텐츠 크롤러 인스턴스
        """
        self.crawler = crawler or PBNContentCrawler()
        self.similarity_system = ImprovedSimilaritySystem()  # 🧠 AI 기반 유사도 시스템

        # 링크 삽입 설정
        self.config = {
            "external_link_probability": 1.0,  # 외부링크(클라이언트) 100% 확률
            "internal_link_probability": 1.0,  # 내부링크 100% 확률 (2~5개 랜덤)
            "min_internal_links": 2,  # 최소 내부링크 수 (1→2로 증가)
            "max_internal_links": 5,  # 최대 내부링크 수 (3→5로 증가)
            "max_external_links": 0,  # 외부링크 비활성화 (주석처리)
            "min_similarity_score": 0.2,  # 최소 유사도 점수 (0.3→0.2로 낮춤)
            "link_density_limit": 0.05,  # 링크 밀도 제한 (3%→5%로 증가)
        }

        print("🔗 지능형 링크 빌더 초기화 완료")

    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """두 단어 간의 유사도를 계산합니다 (간단한 Jaccard 유사도)"""
        if not word1 or not word2:
            return 0.0

        # 2-gram 기반 Jaccard 유사도
        def get_ngrams(text, n=2):
            return set(text[i : i + n] for i in range(len(text) - n + 1))

        ngrams1 = get_ngrams(word1)
        ngrams2 = get_ngrams(word2)

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))

        return intersection / union if union > 0 else 0.0

    def _extract_additional_keywords(self, content: str) -> List[str]:
        """콘텐츠에서 추가 키워드를 추출합니다"""
        import re

        # HTML 태그 제거
        clean_content = re.sub(r"<[^>]+>", " ", content)

        # 특수문자 제거하고 단어 추출
        words = re.findall(r"\b[가-힣]{2,}\b", clean_content)

        # 제외할 일반적인 단어들 (불용어)
        stop_words = {
            "관리",
            "간단한",
            "공고를",
            "검색",
            "지원",
            "찾는",
            "주말",
            "방법",
            "기법",
            "도구",
            "원리",
            "전략",
            "운영",
            "성장",
            "수익성",
            "구현",
            "개발",
            "최적화",
            "통합",
            "자동화",
            "학습",
            "훈련",
            "역량",
            "운동",
            "영양",
            "웰빙",
            "예방",
            "방법",
            "기법",
            "도구",
            "원리",
            "이것",
            "저것",
            "그것",
            "여기",
            "저기",
            "그기",
            "때문",
            "위해",
            "통해",
            "대해",
            "관련",
            "비해",
            "따라",
            "의해",
            "로서",
            "으로",
            "에서",
            "에게",
            "한테",
            "처럼",
            "같이",
            "보다",
            "많이",
            "적게",
            "잘못",
            "바르게",
            "올바르게",
            "정확히",
            "명확히",
            "확실히",
            "분명히",
            "자세히",
            "간단히",
            "쉽게",
            "어렵게",
            "빠르게",
            "천천히",
            "조금씩",
            "점점",
            "점차",
            "차츰",
            "서서히",
            "급격히",
            "급속히",
            "느리게",
            "빨리",
        }

        # 빈도수 계산 (불용어 제외)
        word_freq = {}
        for word in words:
            if (
                len(word) >= 2 and word not in stop_words
            ):  # 2글자 이상이고 불용어가 아닌 경우만
                word_freq[word] = word_freq.get(word, 0) + 1

        # 빈도수 3 이상인 단어들을 키워드로 선택 (최대 5개로 제한)
        additional_keywords = [
            word
            for word, freq in sorted(
                word_freq.items(), key=lambda x: x[1], reverse=True
            )
            if freq >= 3  # 빈도수 기준을 3으로 높임
        ][
            :5
        ]  # 최대 5개로 제한

        return additional_keywords

    def is_excluded_section(self, content: str, position: int) -> bool:
        """
        해당 위치가 링크 삽입 제외 영역인지 확인
        제목, 목차, 용어정리 섹션만 제외하고 일반 본문은 허용

        Args:
            content: 전체 콘텐츠
            position: 확인할 위치

        Returns:
            제외 영역이면 True, 아니면 False
        """
        # 위치 앞뒤로 100자씩 확인 (범위 축소)
        start = max(0, position - 100)
        end = min(len(content), position + 100)
        context = content[start:end]

        # 1. 제목 태그 내부 확인 (h1~h6 태그 안의 텍스트) - 더 관대하게
        title_pattern = r"<h[1-6][^>]*>.*?</h[1-6]>"
        title_matches = list(
            re.finditer(title_pattern, context, re.IGNORECASE | re.DOTALL)
        )
        for match in title_matches:
            if match.start() <= position - start <= match.end():
                # H2 태그는 허용 (섹션 제목이므로)
                if "<h2" in match.group().lower():
                    print(f"      ✅ H2 태그 허용: {match.group()[:50]}...")
                    continue
                print(f"      🔍 제목 태그 내부 감지: {match.group()[:50]}...")
                return True

        # 2. 목차 관련 태그 확인 (ol, ul, li 태그)
        list_patterns = [
            r"<ol[^>]*>.*?</ol>",  # 순서있는 목록
            r"<ul[^>]*>.*?</ul>",  # 순서없는 목록
            r"<li[^>]*>.*?</li>",  # 목록 항목
        ]
        for pattern in list_patterns:
            matches = list(re.finditer(pattern, context, re.IGNORECASE | re.DOTALL))
            for match in matches:
                if match.start() <= position - start <= match.end():
                    print(f"      🔍 목록 태그 내부 감지: {match.group()[:50]}...")
                    return True

        # 3. 용어정리 관련 태그 확인 (dl, dt, dd)
        definition_patterns = [
            r"<dl[^>]*>.*?</dl>",  # 정의 목록
            r"<dt[^>]*>.*?</dt>",  # 정의 용어
            r"<dd[^>]*>.*?</dd>",  # 정의 설명
        ]
        for pattern in definition_patterns:
            matches = list(re.finditer(pattern, context, re.IGNORECASE | re.DOTALL))
            for match in matches:
                if match.start() <= position - start <= match.end():
                    print(f"      🔍 정의 태그 내부 감지: {match.group()[:50]}...")
                    return True

        # 4. 특별한 ID나 클래스 확인
        special_patterns = [
            r'id="[^"]*toc[^"]*"',  # 목차 관련 ID
            r'id="[^"]*terms[^"]*"',  # 용어정리 관련 ID
            r'class="[^"]*toc[^"]*"',  # 목차 관련 클래스
            r'class="[^"]*terms[^"]*"',  # 용어정리 관련 클래스
        ]
        for pattern in special_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                print(f"      🔍 특별 ID/클래스 감지: {pattern}")
                return True

        # 5. 네비게이션 태그 확인
        if re.search(r"<nav[^>]*>", context, re.IGNORECASE):
            print(f"      🔍 네비게이션 태그 감지")
            return True

        # 6. <p> 태그 내부는 허용 (일반 본문)
        if re.search(r"<p[^>]*>", context, re.IGNORECASE):
            print(f"      ✅ <p> 태그 내부 본문 영역 (허용)")
            return False

        # 7. 기타 일반 본문 영역도 허용
        print(f"      ✅ 일반 본문 영역으로 판단 (허용)")
        return False

    def _is_inside_title_tag(self, content: str, position: int) -> bool:
        """제목 태그 내부인지 확인"""
        start = max(0, position - 100)
        end = min(len(content), position + 100)
        context = content[start:end]

        title_pattern = r"<h[1-6][^>]*>.*?</h[1-6]>"
        matches = list(re.finditer(title_pattern, context, re.IGNORECASE | re.DOTALL))
        for match in matches:
            if match.start() <= position - start <= match.end():
                return True
        return False

    def _is_inside_list_tag(self, content: str, position: int) -> bool:
        """목록 태그 내부인지 확인"""
        start = max(0, position - 100)
        end = min(len(content), position + 100)
        context = content[start:end]

        list_patterns = [
            r"<ol[^>]*>.*?</ol>",
            r"<ul[^>]*>.*?</ul>",
            r"<li[^>]*>.*?</li>",
        ]
        for pattern in list_patterns:
            matches = list(re.finditer(pattern, context, re.IGNORECASE | re.DOTALL))
            for match in matches:
                if match.start() <= position - start <= match.end():
                    return True
        return False

    def _is_inside_paragraph_tag(self, content: str, position: int) -> bool:
        """<p> 태그 내부인지 확인"""
        start = max(0, position - 100)
        end = min(len(content), position + 100)
        context = content[start:end]

        p_pattern = r"<p[^>]*>.*?</p>"
        matches = list(re.finditer(p_pattern, context, re.IGNORECASE | re.DOTALL))
        for match in matches:
            if match.start() <= position - start <= match.end():
                return True
        return False

    def _has_existing_link(self, content: str, position: int, length: int) -> bool:
        """해당 위치에 이미 링크가 있는지 확인"""
        # 위치 앞뒤로 50자씩 확인
        start = max(0, position - 50)
        end = min(len(content), position + length + 50)
        context = content[start:end]

        # <a> 태그가 있는지 확인
        if re.search(r"<a\s+[^>]*>", context, re.IGNORECASE):
            return True
        return False

    def extract_keywords_from_content(
        self,
        content: str,
        main_keyword: str,
        lsi_keywords: List[str] = None,
        longtail_keywords: List[str] = None,
    ) -> List[str]:
        """
        콘텐츠에서 링크 가능한 키워드들을 추출

        Args:
            content: 분석할 콘텐츠
            main_keyword: 메인 키워드
            lsi_keywords: LSI 키워드 리스트
            longtail_keywords: 롱테일 키워드 리스트

        Returns:
            추출된 키워드 리스트
        """
        all_keywords = [main_keyword]

        if lsi_keywords:
            all_keywords.extend(lsi_keywords)

        if longtail_keywords:
            all_keywords.extend(longtail_keywords)

        # 콘텐츠에 실제로 존재하는 키워드만 필터링 (부분 매칭 포함)
        existing_keywords = []
        for keyword in all_keywords:
            # 정확한 매칭
            if keyword.lower() in content.lower():
                existing_keywords.append(keyword)
            # 부분 매칭 (키워드의 70% 이상 일치)
            elif len(keyword) >= 4:  # 4글자 이상인 키워드만
                for word in content.lower().split():
                    if (
                        len(word) >= 4
                        and self._calculate_similarity(keyword.lower(), word) >= 0.7
                    ):
                        existing_keywords.append(keyword)
                        break  # 하나만 찾으면 충분

        # 추가 키워드 추출 (콘텐츠에서 직접 추출)
        additional_keywords = self._extract_additional_keywords(content)
        existing_keywords.extend(additional_keywords)

        # 중복 제거
        existing_keywords = list(set(existing_keywords))

        print(
            f"📝 콘텐츠에서 {len(existing_keywords)}개 키워드 발견: {existing_keywords}"
        )
        return existing_keywords

    def find_client_link_position(
        self, content: str, keyword: str
    ) -> Optional[Tuple[int, int, str]]:
        """
        클라이언트 링크를 삽입할 최적의 위치를 찾습니다.
        제외 영역과 HTML 태그 내부는 피합니다.

        Args:
            content: 검색할 콘텐츠
            keyword: 앵커텍스트로 사용할 키워드

        Returns:
            (시작위치, 끝위치, 매칭된텍스트) 또는 None
        """
        # 1순위: 정확한 키워드 매칭 (HTML 태그 외부에서만)
        pattern = r"\b" + re.escape(keyword) + r"\b"
        matches = list(re.finditer(pattern, content, re.IGNORECASE))

        for match in matches:
            start, end = match.start(), match.end()
            matched_text = match.group()

            # 제외 영역 확인
            if self.is_excluded_section(content, start):
                print(f"      ⚠️ 제외 영역에서 발견: '{matched_text}' (건너뜀)")
                continue

            # HTML 태그 내부인지 확인
            before_text = content[max(0, start - 50) : start]
            after_text = content[end : end + 50]

            # 태그 내부에 있는지 확인
            if self._is_inside_html_tag(before_text, after_text):
                print(f"      ⚠️ HTML 태그 내부에서 발견: '{matched_text}' (건너뜀)")
                continue

            print(f"      ✅ 적절한 위치 발견: '{matched_text}' (위치: {start})")
            return (start, end, matched_text)

        # 2순위: 키워드가 포함된 구문 찾기
        keyword_parts = keyword.split()
        if len(keyword_parts) > 1:
            for part in keyword_parts:
                if len(part) > 2:  # 너무 짧은 단어 제외
                    pattern = r"\b" + re.escape(part) + r"\b"
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))

                    for match in matches:
                        start, end = match.start(), match.end()
                        matched_text = match.group()

                        # 제외 영역 확인
                        if self.is_excluded_section(content, start):
                            continue

                        # HTML 태그 내부인지 확인
                        before_text = content[max(0, start - 50) : start]
                        after_text = content[end : end + 50]

                        if self._is_inside_html_tag(before_text, after_text):
                            continue

                        print(
                            f"      ✅ 부분 키워드 위치 발견: '{matched_text}' (위치: {start})"
                        )
                        return (start, end, matched_text)

        return None

    def _is_inside_html_tag(self, before_text: str, after_text: str) -> bool:
        """
        해당 위치가 HTML 태그 내부인지 확인

        Args:
            before_text: 위치 이전 텍스트
            after_text: 위치 이후 텍스트

        Returns:
            HTML 태그 내부이면 True
        """
        # 태그 시작과 끝을 찾기
        last_open_tag = before_text.rfind("<")
        last_close_tag = before_text.rfind(">")

        # 태그가 열려있고 닫히지 않았으면 태그 내부
        if last_open_tag > last_close_tag:
            return True

        # 다음 태그가 닫는 태그인지 확인
        next_close_tag = after_text.find(">")
        next_open_tag = after_text.find("<")

        if next_close_tag != -1 and (
            next_open_tag == -1 or next_close_tag < next_open_tag
        ):
            return True

        return False

    def insert_client_link(
        self, content: str, keyword: str, client_url: str
    ) -> Tuple[str, bool]:
        """
        클라이언트 링크를 콘텐츠에 삽입 (100% 확률) - 간단하고 확실한 방식

        Args:
            content: 원본 콘텐츠
            keyword: 앵커텍스트 키워드
            client_url: 클라이언트 사이트 URL

        Returns:
            (수정된 콘텐츠, 성공여부)
        """
        print(f"🎯 클라이언트 링크 삽입 시도: '{keyword}' -> {client_url}")

        # 1. 키워드가 본문에 있는지 확인
        if keyword.lower() not in content.lower():
            print(f"   🔧 키워드를 찾을 수 없어 강제 삽입: 콘텐츠 시작 부분")
            link_html = (
                f'<a href="{client_url}" target="_blank" rel="noopener">{keyword}</a>'
            )
            modified_content = link_html + " " + content
            return modified_content, True

        # 2. 모든 키워드 위치 찾기
        pattern = re.escape(keyword)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))

        # 3. 가장 적합한 위치 찾기 (우선순위: <p> 태그 > 일반 본문)
        best_position = None
        best_priority = 0  # 0: 제외, 1: 일반 본문, 2: <p> 태그

        for match in matches:
            position = match.start()

            # 제외 조건 확인
            if self._is_inside_title_tag(content, position):
                print(
                    f"      🔍 제목 태그 내부 감지: {content[position-20:position+20]}..."
                )
                continue
            if self._is_inside_list_tag(content, position):
                print(
                    f"      🔍 목록 태그 내부 감지: {content[position-20:position+20]}..."
                )
                continue
            if self._has_existing_link(content, position, len(keyword)):
                print(f"      ⚠️ 이미 링크가 있는 위치: '{keyword}'")
                continue

            # 우선순위 결정
            priority = 1  # 기본: 일반 본문
            if self._is_inside_paragraph_tag(content, position):
                priority = 2  # <p> 태그 내부가 더 우선

            if priority > best_priority:
                best_position = position
                best_priority = priority

        # 4. 가장 적합한 위치에 링크 삽입
        if best_position is not None:
            # 링크 HTML 생성
            link_html = (
                f'<a href="{client_url}" target="_blank" rel="noopener">{keyword}</a>'
            )

            # 콘텐츠에 링크 삽입
            modified_content = (
                content[:best_position]
                + link_html
                + content[best_position + len(keyword) :]
            )

            if best_priority == 2:
                print(f"      ✅ <p> 태그 내부 본문: '{keyword}'")
            else:
                print(f"      ✅ 일반 본문 영역: '{keyword}'")

            print(f"   ✅ 클라이언트 링크 삽입 성공: '{keyword}'")
            return modified_content, True
        else:
            # 적합한 위치를 찾을 수 없는 경우 강제 삽입
            print(f"   🔧 적합한 위치를 찾을 수 없어 강제 삽입: 콘텐츠 시작 부분")
            link_html = (
                f'<a href="{client_url}" target="_blank" rel="noopener">{keyword}</a>'
            )
            modified_content = link_html + " " + content
            return modified_content, True

    def find_internal_link_opportunities(
        self, content: str, keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        내부링크 삽입 기회를 찾습니다.

        Args:
            content: 분석할 콘텐츠
            keywords: 검색할 키워드 리스트

        Returns:
            내부링크 후보 리스트
        """
        print(f"🔍 내부링크 기회 탐색 중... (키워드: {len(keywords)}개)")

        # PBN에서 유사한 포스트 찾기 (간단한 방식)
        similar_posts = self.similarity_system.find_similar_posts_fast(
            keywords,
            limit=9,  # 충분한 후보 확보
            min_similarity=0.3,  # 낮은 임계값으로 더 많은 후보 확보
            random_selection=True,
        )

        if not similar_posts:
            print("   ❌ 유사한 PBN 포스트를 찾을 수 없습니다.")
            return []

        print(f"   📄 {len(similar_posts)}개의 유사한 PBN 포스트 발견")

        # 링크 후보 생성
        link_candidates = []

        for i, post in enumerate(similar_posts):
            # 콘텐츠에서 이 포스트와 관련된 키워드 찾기
            post_title = post["title"]
            post_url = post["url"]
            similarity_score = post.get("similarity_score", 0.5)

            print(f"   🔍 포스트 {i+1} 분석: {post_title[:50]}...")

            # 원본 키워드를 우선적으로 앵커텍스트 후보로 사용
            potential_anchors = []

            # 1순위: 콘텐츠에서 발견된 원본 키워드들
            original_keywords_found = []
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    potential_anchors.append(keyword)
                    original_keywords_found.append(keyword)

            print(f"      🎯 원본 키워드 발견: {original_keywords_found}")

            # 2순위: PBN 포스트 제목에서 추출한 단어들 (원본 키워드가 부족할 때만)
            if len(potential_anchors) < 3:  # 원본 키워드가 3개 미만일 때만
                title_words = re.findall(r"\w+", post_title)
                additional_words = []
                for word in title_words:
                    if (
                        len(word) > 2
                        and word.lower() in content.lower()
                        and word not in potential_anchors
                    ):  # 중복 방지
                        potential_anchors.append(word)
                        additional_words.append(word)
                print(f"      📝 제목에서 추가 발견: {additional_words}")

            print(f"      📝 최종 앵커텍스트 후보: {potential_anchors}")

            # 가장 적절한 앵커텍스트 선택 (다양성 고려)
            if potential_anchors:
                # 중복을 피하기 위해 이미 사용된 앵커텍스트 제외
                available_anchors = [
                    anchor
                    for anchor in potential_anchors
                    if not any(
                        candidate.get("anchor_text") == anchor
                        for candidate in link_candidates
                    )
                ]

                if not available_anchors:
                    # 모든 후보가 이미 사용됨 - 랜덤 선택
                    available_anchors = potential_anchors

                # 길이와 관련성을 고려해서 선택 (다양성 우선)
                if len(available_anchors) > 1:
                    # 2개 이상이면 랜덤 선택으로 다양성 확보
                    best_anchor = random.choice(available_anchors)
                else:
                    best_anchor = available_anchors[0]

                print(
                    f"      🎯 선택된 앵커텍스트: '{best_anchor}' (후보: {len(available_anchors)}개)"
                )

                # 콘텐츠에서 위치 찾기
                pattern = r"\b" + re.escape(best_anchor) + r"\b"
                match = re.search(pattern, content, re.IGNORECASE)

                if match:
                    position = match.start()
                    print(f"      📍 위치 발견: {position}")

                    # 제외 영역 확인
                    if self.is_excluded_section(content, position):
                        print(f"      ⚠️ 제외 영역이므로 건너뜀: '{best_anchor}'")
                        continue

                    # 이미 링크가 있는지 확인
                    surrounding_text = content[
                        max(0, position - 20) : position + len(best_anchor) + 20
                    ]
                    if "<a " in surrounding_text and "</a>" in surrounding_text:
                        print(f"      ⚠️ 이미 링크가 있는 위치: '{best_anchor}'")
                        continue

                    link_candidates.append(
                        {
                            "anchor_text": best_anchor,
                            "url": post_url,
                            "position": position,
                            "confidence": similarity_score,
                            "post_title": post_title,
                            "site_url": post["site_url"],
                        }
                    )
                    print(f"      ✅ 링크 후보 추가: '{best_anchor}' -> {post_url}")
                else:
                    print(f"      ❌ 콘텐츠에서 위치를 찾을 수 없음: '{best_anchor}'")
            else:
                print(f"      ❌ 앵커텍스트 후보 없음")

        # 신뢰도 순으로 정렬
        link_candidates.sort(key=lambda x: x["confidence"], reverse=True)

        print(f"   🔗 {len(link_candidates)}개의 내부링크 후보 생성")
        return link_candidates

    def find_internal_link_opportunities_simple(
        self, content: str, keywords: List[str], client_keyword: str = None
    ) -> List[Dict[str, Any]]:
        """
        내부링크 삽입 기회를 찾습니다. (요구사항에 맞는 로직)

        Args:
            content: 분석할 콘텐츠
            keywords: 검색할 키워드 리스트
            client_keyword: 클라이언트 링크에 사용된 키워드 (제외용)

        Returns:
            내부링크 후보 리스트
        """
        print(f"🔍 내부링크 기회 탐색 중... (키워드: {len(keywords)}개)")

        # 1. PBN에서 유사한 포스트 찾기 (더 많은 후보, 낮은 임계값)
        similar_posts = self.similarity_system.find_similar_posts_fast(
            keywords,
            limit=50,  # 후보 확보 (20→50으로 증가)
            min_similarity=0.15,  # 임계값 낮춤 (0.3→0.15)
            random_selection=True,
        )

        if not similar_posts:
            print("   ❌ 유사한 PBN 포스트를 찾을 수 없습니다.")
            return []

        print(f"   📄 {len(similar_posts)}개의 유사한 PBN 포스트 발견")

        # 2. 내부링크 개수 랜덤 선택 (2~5개)
        target_count = random.randint(2, 5)
        print(f"   🎲 내부링크 목표 개수: {target_count}개")

        # 3. PBN 포스트에서 랜덤으로 선택
        selected_posts = random.sample(
            similar_posts, min(target_count, len(similar_posts))
        )
        print(f"   🎲 선택된 PBN 포스트: {len(selected_posts)}개")

        # 4. 클라이언트 링크에 사용된 키워드 제외
        available_keywords = (
            [kw for kw in keywords if kw.lower() != client_keyword.lower()]
            if client_keyword
            else keywords
        )
        print(f"   🎯 사용 가능한 키워드: {available_keywords}")

        if not available_keywords:
            print("   ❌ 사용 가능한 키워드가 없습니다.")
            return []

        # 5. 각 키워드에 대해 링크 후보 생성
        link_candidates = []

        for i, post in enumerate(selected_posts):
            post_title = post.get("title", "")
            post_url = post.get("url", "")

            print(f"   🔍 포스트 {i+1} 분석: {post_title[:50]}...")

            # 사용 가능한 키워드 중에서 본문에 있는 것들 찾기 (부분 매칭 포함)
            valid_keywords = []
            for keyword in available_keywords:
                # 정확한 매칭
                if keyword.lower() in content.lower():
                    valid_keywords.append((keyword, 1.0))  # (키워드, 우선순위)
                # 부분 매칭 (키워드의 70% 이상 일치)
                elif len(keyword) >= 4:  # 4글자 이상인 키워드만
                    for word in content.lower().split():
                        if (
                            len(word) >= 4
                            and self._calculate_similarity(keyword.lower(), word) >= 0.7
                        ):
                            valid_keywords.append(
                                (keyword, 0.8)
                            )  # 부분 매칭은 낮은 우선순위

            if not valid_keywords:
                print(f"      ❌ 포스트 {i+1}에 사용 가능한 키워드가 없습니다.")
                continue

            # 우선순위 순으로 정렬하여 가장 적합한 키워드 선택
            valid_keywords.sort(key=lambda x: x[1], reverse=True)
            selected_keyword = valid_keywords[0][0]
            print(f"      🎯 선택된 키워드: '{selected_keyword}'")

            # 키워드 위치 찾기
            pattern = re.escape(selected_keyword)
            matches = list(re.finditer(pattern, content, re.IGNORECASE))

            # 가장 적합한 위치 찾기
            best_position = None
            best_priority = 0

            for match in matches:
                position = match.start()

                # 제외 조건 확인
                if self._is_inside_title_tag(content, position):
                    continue
                if self._is_inside_list_tag(content, position):
                    continue
                if self._has_existing_link(content, position, len(selected_keyword)):
                    continue

                # 우선순위 결정
                priority = 1  # 기본: 일반 본문
                if self._is_inside_paragraph_tag(content, position):
                    priority = 2  # <p> 태그 내부가 더 우선

                if priority > best_priority:
                    best_position = position
                    best_priority = priority

            # 링크 후보 생성
            if best_position is not None:
                candidate = {
                    "anchor_text": selected_keyword,
                    "url": post_url,
                    "position": best_position,
                    "post_title": post_title,
                    "similarity_score": post.get("similarity_score", 0.5),
                }

                link_candidates.append(candidate)

                if best_priority == 2:
                    print(f"      ✅ <p> 태그 내부 본문: '{selected_keyword}'")
                else:
                    print(f"      ✅ 일반 본문 영역: '{selected_keyword}'")

                print(
                    f"      🎯 내부링크 후보 생성: '{selected_keyword}' -> {post_url[:50]}..."
                )

        print(f"   🔗 {len(link_candidates)}개의 내부링크 후보 생성")
        return link_candidates

    def insert_internal_links(
        self, content: str, link_candidates: List[Dict[str, Any]], target_count: int = 3
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        내부링크들을 콘텐츠에 삽입

        Args:
            content: 원본 콘텐츠
            link_candidates: 링크 후보 리스트
            target_count: 목표 링크 수

        Returns:
            (수정된 콘텐츠, 삽입된 링크 정보)
        """
        if not link_candidates:
            return content, []

        print(
            f"🔗 내부링크 삽입 시작: {len(link_candidates)}개 후보 (목표: {target_count}개)"
        )

        modified_content = content
        inserted_links = []
        offset = 0  # 삽입으로 인한 위치 오프셋

        # 위치 순으로 정렬 (앞에서부터 삽입)
        candidates_by_position = sorted(link_candidates, key=lambda x: x["position"])

        for i, candidate in enumerate(candidates_by_position):
            if len(inserted_links) >= target_count:
                break

            anchor_text = candidate["anchor_text"]
            url = candidate["url"]
            position = candidate["position"] + offset

            # 제외 영역 확인 (더 관대하게)
            if self.is_excluded_section(modified_content, position):
                print(f"   ⚠️ 제외 영역입니다 (제목/목차/용어정리): '{anchor_text}'")
                continue

            # 이미 링크가 있는 위치인지 확인
            surrounding_text = modified_content[
                max(0, position - 20) : position + len(anchor_text) + 20
            ]
            if "<a " in surrounding_text and "</a>" in surrounding_text:
                print(f"   ⚠️ 이미 링크가 있는 위치 건너뜀: '{anchor_text}'")
                continue

            # 정확한 위치에서 텍스트 찾기 (더 넓은 범위)
            pattern = re.escape(anchor_text)
            match = re.search(
                pattern, modified_content[position : position + 100], re.IGNORECASE
            )

            if match:
                actual_start = position + match.start()
                actual_end = position + match.end()
                actual_text = modified_content[actual_start:actual_end]

                # 링크 HTML 생성
                link_html = (
                    f'<a href="{url}" target="_blank" rel="noopener">{actual_text}</a>'
                )

                # 콘텐츠에 링크 삽입
                modified_content = (
                    modified_content[:actual_start]
                    + link_html
                    + modified_content[actual_end:]
                )

                # 오프셋 업데이트
                offset += len(link_html) - len(actual_text)

                # 삽입된 링크 정보 기록
                inserted_links.append(
                    {
                        "anchor_text": actual_text,
                        "url": url,
                        "post_title": candidate["post_title"],
                        "site_url": candidate.get(
                            "site_url", url
                        ),  # site_url이 없으면 url 사용
                        "confidence": candidate.get(
                            "similarity_score", 0.5
                        ),  # confidence 대신 similarity_score 사용
                    }
                )

                print(f"   ✅ 내부링크 삽입: '{actual_text}' -> {url}")

        print(f"🎉 내부링크 삽입 완료: {len(inserted_links)}개 삽입")
        return modified_content, inserted_links

    def add_additional_external_links(
        self, content: str, keywords: List[str]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        추가 외부링크 삽입 (권위있는 사이트들)

        Args:
            content: 원본 콘텐츠
            keywords: 키워드 리스트

        Returns:
            (수정된 콘텐츠, 삽입된 링크 정보)
        """
        # 권위있는 사이트들 (예시)
        authoritative_sites = [
            {"domain": "wikipedia.org", "name": "위키피디아"},
            {"domain": "naver.com", "name": "네이버"},
            {"domain": "google.com", "name": "구글"},
            {"domain": "tistory.com", "name": "티스토리"},
            {"domain": "brunch.co.kr", "name": "브런치"},
        ]

        # 실제 구현에서는 더 정교한 로직 필요
        # 여기서는 간단한 예시로 구현

        modified_content = content
        inserted_links = []

        # 확률적으로 1-2개의 외부링크 추가
        if random.random() < 0.5 and keywords:  # 50% 확률
            selected_keyword = random.choice(keywords)
            selected_site = random.choice(authoritative_sites)

            # 가상의 URL 생성 (실제로는 검색 API 등을 사용해야 함)
            external_url = (
                f"https://{selected_site['domain']}/search?q={selected_keyword}"
            )

            # 키워드 위치 찾기
            pattern = r"\b" + re.escape(selected_keyword) + r"\b"
            matches = list(re.finditer(pattern, modified_content, re.IGNORECASE))

            if matches:
                # 마지막 매칭 위치에 링크 삽입 (이미 클라이언트 링크가 있을 가능성이 낮음)
                match = matches[-1]
                start, end = match.start(), match.end()
                matched_text = match.group()

                # 이미 링크가 있는지 확인
                surrounding = modified_content[max(0, start - 10) : end + 10]
                if "<a " not in surrounding:
                    link_html = f'<a href="{external_url}" target="_blank" rel="noopener">{matched_text}</a>'
                    modified_content = (
                        modified_content[:start] + link_html + modified_content[end:]
                    )

                    inserted_links.append(
                        {
                            "anchor_text": matched_text,
                            "url": external_url,
                            "site_name": selected_site["name"],
                            "type": "external",
                        }
                    )

                    print(
                        f"   🌐 외부링크 추가: '{matched_text}' -> {selected_site['name']}"
                    )

        return modified_content, inserted_links

    def build_comprehensive_links(
        self,
        content: str,
        keyword: str,
        client_url: str,
        lsi_keywords: List[str] = None,
        longtail_keywords: List[str] = None,
    ) -> Dict[str, Any]:
        """
        종합적인 링크 빌딩 수행

        Args:
            content: 원본 콘텐츠
            keyword: 메인 키워드
            client_url: 클라이언트 사이트 URL
            lsi_keywords: LSI 키워드 리스트
            longtail_keywords: 롱테일 키워드 리스트

        Returns:
            링크 빌딩 결과 딕셔너리
        """
        print("🚀 종합적인 링크 빌딩 시작")
        print("=" * 50)

        modified_content = content
        link_report = {
            "client_link": None,
            "internal_links": [],
            "external_links": [],
            "total_links": 0,
            "success": False,
        }

        try:
            # 1. 클라이언트 링크 삽입 (100% 확률)
            print("🎯 1단계: 클라이언트 링크 삽입")
            modified_content, client_success = self.insert_client_link(
                modified_content, keyword, client_url
            )

            if client_success:
                link_report["client_link"] = {
                    "keyword": keyword,
                    "url": client_url,
                    "type": "client",
                }
                print("   ✅ 클라이언트 링크 삽입 성공")
            else:
                print("   ❌ 클라이언트 링크 삽입 실패")

            # 2. 키워드 추출
            print("\n🔍 2단계: 링크 가능한 키워드 추출")
            all_keywords = self.extract_keywords_from_content(
                modified_content, keyword, lsi_keywords, longtail_keywords
            )

            # 3. 내부링크 삽입
            print("\n🔗 3단계: 내부링크 삽입")
            if all_keywords:
                # 2~5개 랜덤 선택
                target_count = random.randint(
                    self.config["min_internal_links"], self.config["max_internal_links"]
                )
                print(f"🎲 내부링크 목표 개수: {target_count}개 (2~5개 중 랜덤 선택)")

                link_candidates = self.find_internal_link_opportunities_simple(
                    modified_content, all_keywords, keyword  # 클라이언트 키워드 전달
                )

                if link_candidates:
                    modified_content, internal_links = self.insert_internal_links(
                        modified_content, link_candidates, target_count
                    )
                    link_report["internal_links"] = internal_links
                else:
                    print("   ❌ 내부링크 후보를 찾을 수 없습니다.")

            # 4. 추가 외부링크 삽입 (비활성화)
            # print("\n🌐 4단계: 추가 외부링크 삽입")
            # modified_content, external_links = self.add_additional_external_links(
            #     modified_content, all_keywords
            # )
            # link_report["external_links"] = external_links
            link_report["external_links"] = []  # 외부링크 비활성화

            # 5. 최종 결과 계산
            link_report["total_links"] = (
                (1 if link_report["client_link"] else 0)
                + len(link_report["internal_links"])
                + len(link_report["external_links"])
            )
            link_report["success"] = link_report["total_links"] > 0

            # 최종 보고서 출력
            print("\n" + "=" * 50)
            print("🎉 링크 빌딩 완료!")
            print(f"📊 총 삽입된 링크: {link_report['total_links']}개")
            print(f"   🎯 클라이언트 링크: {1 if link_report['client_link'] else 0}개")
            print(f"   🔗 내부링크: {len(link_report['internal_links'])}개")
            print(f"   🌐 외부링크: {len(link_report['external_links'])}개")

            if link_report["internal_links"]:
                print("\n📋 삽입된 내부링크:")
                for link in link_report["internal_links"]:
                    print(f"   • '{link['anchor_text']}' -> {link['post_title']}")

            return {"content": modified_content, "report": link_report}

        except Exception as e:
            print(f"❌ 링크 빌딩 중 오류 발생: {e}")
            import traceback

            traceback.print_exc()

            link_report["success"] = False
            link_report["error"] = str(e)

            return {"content": content, "report": link_report}  # 원본 콘텐츠 반환


# 테스트 함수
def test_link_builder():
    """링크 빌더 테스트"""
    print("🧪 링크 빌더 테스트 시작")

    # 테스트 데이터
    test_content = """
    <h1>백링크 테스트의 중요성</h1>
    <p>백링크는 SEO에서 매우 중요한 요소입니다. 검색엔진최적화를 위해서는 고품질의 백링크가 필요합니다.</p>
    <p>백링크 테스트를 통해 웹사이트의 성능을 향상시킬 수 있습니다.</p>
    <h2>SEO 전략</h2>
    <p>효과적인 SEO 전략에는 백링크 구축이 포함됩니다.</p>
    """

    test_keyword = "백링크 테스트"
    test_client_url = "https://example-client.com"
    test_lsi_keywords = ["SEO", "검색엔진최적화", "링크빌딩"]
    test_longtail_keywords = ["백링크 테스트 방법", "SEO 백링크 전략"]

    # 크롤러 초기화 (실제 데이터가 있다고 가정)
    crawler = PBNContentCrawler()
    link_builder = IntelligentLinkBuilder(crawler)

    # 링크 빌딩 실행
    result = link_builder.build_comprehensive_links(
        test_content,
        test_keyword,
        test_client_url,
        test_lsi_keywords,
        test_longtail_keywords,
    )

    print("\n📄 결과 콘텐츠:")
    print(result["content"])

    print("\n📊 링크 빌딩 보고서:")
    print(json.dumps(result["report"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import json

    test_link_builder()
