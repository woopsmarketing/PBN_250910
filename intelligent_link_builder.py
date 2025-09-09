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
            "internal_link_probability": 0.7,  # 내부링크 70% 확률
            "max_internal_links": 5,  # 최대 내부링크 수
            "max_external_links": 3,  # 최대 외부링크 수 (클라이언트 제외)
            "min_similarity_score": 0.3,  # 최소 유사도 점수
            "link_density_limit": 0.03,  # 링크 밀도 제한 (3%)
        }

        print("🔗 지능형 링크 빌더 초기화 완료")

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

        # 콘텐츠에 실제로 존재하는 키워드만 필터링
        existing_keywords = []
        for keyword in all_keywords:
            if keyword.lower() in content.lower():
                existing_keywords.append(keyword)

        print(
            f"📝 콘텐츠에서 {len(existing_keywords)}개 키워드 발견: {existing_keywords}"
        )
        return existing_keywords

    def find_client_link_position(
        self, content: str, keyword: str
    ) -> Optional[Tuple[int, int, str]]:
        """
        클라이언트 링크를 삽입할 최적의 위치를 찾습니다.

        Args:
            content: 검색할 콘텐츠
            keyword: 앵커텍스트로 사용할 키워드

        Returns:
            (시작위치, 끝위치, 매칭된텍스트) 또는 None
        """
        # 1순위: 정확한 키워드 매칭
        pattern = r"\b" + re.escape(keyword) + r"\b"
        match = re.search(pattern, content, re.IGNORECASE)

        if match:
            return (match.start(), match.end(), match.group())

        # 2순위: 키워드가 포함된 구문 찾기
        keyword_parts = keyword.split()
        if len(keyword_parts) > 1:
            for part in keyword_parts:
                if len(part) > 2:  # 너무 짧은 단어 제외
                    pattern = r"\b" + re.escape(part) + r"\b"
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        return (match.start(), match.end(), match.group())

        return None

    def insert_client_link(
        self, content: str, keyword: str, client_url: str
    ) -> Tuple[str, bool]:
        """
        클라이언트 링크를 콘텐츠에 삽입 (100% 확률)

        Args:
            content: 원본 콘텐츠
            keyword: 앵커텍스트 키워드
            client_url: 클라이언트 사이트 URL

        Returns:
            (수정된 콘텐츠, 성공여부)
        """
        print(f"🎯 클라이언트 링크 삽입 시도: '{keyword}' -> {client_url}")

        # 링크 삽입 위치 찾기
        position = self.find_client_link_position(content, keyword)

        if position:
            start, end, matched_text = position

            # 이미 링크가 있는지 확인
            before_text = content[max(0, start - 10) : start]
            after_text = content[end : end + 10]

            if "<a " in before_text or "</a>" in after_text:
                print("   ⚠️ 이미 링크가 있는 위치입니다. 다른 위치를 찾습니다.")
                # 다음 매칭 위치 찾기
                remaining_content = content[end:]
                next_position = self.find_client_link_position(
                    remaining_content, keyword
                )
                if next_position:
                    start, end, matched_text = next_position
                    start += len(content[:end])  # 오프셋 조정
                    end += len(content[:end])
                else:
                    # 강제 삽입: 콘텐츠 시작 부분에 추가
                    print("   🔧 강제 삽입: 콘텐츠 시작 부분에 링크 추가")
                    link_html = f'<a href="{client_url}" target="_blank" rel="noopener">{keyword}</a>'
                    modified_content = link_html + " " + content
                    return modified_content, True

            # 링크 HTML 생성
            link_html = f'<a href="{client_url}" target="_blank" rel="noopener">{matched_text}</a>'

            # 콘텐츠에 링크 삽입
            modified_content = content[:start] + link_html + content[end:]

            print(f"   ✅ 클라이언트 링크 삽입 성공: '{matched_text}'")
            return modified_content, True

        else:
            # 키워드를 찾을 수 없는 경우 강제 삽입
            print(f"   🔧 키워드를 찾을 수 없어 강제 삽입: 콘텐츠 시작 부분")
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

        # PBN에서 유사한 포스트 찾기 (AI 기반 FAISS 시스템 사용)
        similar_posts = self.similarity_system.find_similar_posts_fast(
            keywords,
            limit=self.config["max_internal_links"] * 2,  # 여유있게 가져오기
            min_similarity=self.config["min_similarity_score"],
            random_selection=True,  # 🎲 랜덤 선택으로 중복 링크 방지
        )

        if not similar_posts:
            print("   ❌ 유사한 PBN 포스트를 찾을 수 없습니다.")
            return []

        print(f"   📄 {len(similar_posts)}개의 유사한 PBN 포스트 발견")

        # 링크 후보 생성
        link_candidates = []

        for post in similar_posts:
            # 콘텐츠에서 이 포스트와 관련된 키워드 찾기
            post_title = post["title"]
            post_url = post["url"]
            similarity_score = post.get("similarity_score", 0.5)

            # 포스트 제목에서 키워드 추출 (간단한 방법)
            title_words = re.findall(r"\w+", post_title)
            potential_anchors = []

            # 제목의 주요 단어들을 앵커텍스트 후보로 사용
            for word in title_words:
                if len(word) > 2 and word.lower() in content.lower():
                    potential_anchors.append(word)

            # 원본 키워드도 앵커텍스트 후보에 포함
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    potential_anchors.append(keyword)

            # 가장 적절한 앵커텍스트 선택
            if potential_anchors:
                # 길이와 관련성을 고려해서 선택
                best_anchor = max(potential_anchors, key=lambda x: len(x))

                # 콘텐츠에서 위치 찾기
                pattern = r"\b" + re.escape(best_anchor) + r"\b"
                match = re.search(pattern, content, re.IGNORECASE)

                if match:
                    link_candidates.append(
                        {
                            "anchor_text": best_anchor,
                            "url": post_url,
                            "position": match.start(),
                            "confidence": similarity_score,
                            "post_title": post_title,
                            "site_url": post["site_url"],
                        }
                    )

        # 신뢰도 순으로 정렬
        link_candidates.sort(key=lambda x: x["confidence"], reverse=True)

        print(f"   🔗 {len(link_candidates)}개의 내부링크 후보 생성")
        return link_candidates

    def insert_internal_links(
        self, content: str, link_candidates: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        내부링크들을 콘텐츠에 삽입

        Args:
            content: 원본 콘텐츠
            link_candidates: 링크 후보 리스트

        Returns:
            (수정된 콘텐츠, 삽입된 링크 정보)
        """
        if not link_candidates:
            return content, []

        print(f"🔗 내부링크 삽입 시작: {len(link_candidates)}개 후보")

        modified_content = content
        inserted_links = []
        offset = 0  # 삽입으로 인한 위치 오프셋

        # 위치 순으로 정렬 (앞에서부터 삽입)
        candidates_by_position = sorted(link_candidates, key=lambda x: x["position"])

        for i, candidate in enumerate(candidates_by_position):
            if len(inserted_links) >= self.config["max_internal_links"]:
                break

            # 확률적으로 링크 삽입 결정
            if random.random() > self.config["internal_link_probability"]:
                continue

            anchor_text = candidate["anchor_text"]
            url = candidate["url"]
            position = candidate["position"] + offset

            # 이미 링크가 있는 위치인지 확인
            surrounding_text = modified_content[
                max(0, position - 20) : position + len(anchor_text) + 20
            ]
            if "<a " in surrounding_text and "</a>" in surrounding_text:
                print(f"   ⚠️ 이미 링크가 있는 위치 건너뜀: '{anchor_text}'")
                continue

            # 정확한 위치에서 텍스트 찾기
            pattern = r"\b" + re.escape(anchor_text) + r"\b"
            match = re.search(
                pattern, modified_content[position : position + 50], re.IGNORECASE
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
                        "site_url": candidate["site_url"],
                        "confidence": candidate["confidence"],
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
                link_candidates = self.find_internal_link_opportunities(
                    modified_content, all_keywords
                )

                if link_candidates:
                    modified_content, internal_links = self.insert_internal_links(
                        modified_content, link_candidates
                    )
                    link_report["internal_links"] = internal_links
                else:
                    print("   ❌ 내부링크 후보를 찾을 수 없습니다.")

            # 4. 추가 외부링크 삽입
            print("\n🌐 4단계: 추가 외부링크 삽입")
            modified_content, external_links = self.add_additional_external_links(
                modified_content, all_keywords
            )
            link_report["external_links"] = external_links

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
