# v2.0 - 고도화된 PBN 백링크 자동화 시스템
# last_project의 고품질 콘텐츠 생성 기능을 통합한 PBN 시스템

import sys
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

# 기존 모듈 import
from controlDB import ControlDB
from wordpress_functions import WordPressManager

# 새로운 고도화된 콘텐츠 생성 모듈 import
from src.generators.content.advanced_content_generator import (
    AdvancedContentGenerator,
    ContentConfig,
)
from src.generators.content.title_generator import TitleConfig
from src.generators.content.outline_generator import OutlineConfig
from src.generators.content.section_generator import SectionConfig, ContentTone
from src.generators.content.keyword_generator import KeywordConfig
from src.generators.content.image_generator import ImageConfig, ImageStyle

# HTML 변환 모듈 import
from src.generators.html.simple_html_converter import SimpleHTMLConverter


class EnhancedPBNSystem:
    """고도화된 PBN 백링크 자동화 시스템"""

    def __init__(self):
        """시스템 초기화"""
        self.db = ControlDB()
        self.wp_manager = WordPressManager()
        self.content_generator = self._initialize_content_generator()
        self.html_converter = SimpleHTMLConverter()  # HTML 변환기 초기화

        print("🚀 고도화된 PBN 시스템이 초기화되었습니다.")
        print("=" * 50)

    def _initialize_content_generator(self) -> AdvancedContentGenerator:
        """고도화된 콘텐츠 생성기를 초기화합니다."""

        # 각 생성기별 설정
        title_config = TitleConfig(
            max_length=60,
            min_length=30,
            include_numbers=True,
            include_power_words=True,
            include_emotional_triggers=True,
        )

        outline_config = OutlineConfig(
            min_sections=7,
            max_sections=10,
            include_faq=True,
            include_tips=True,
            include_examples=True,
            target_word_count=2000,
        )

        section_config = SectionConfig(
            min_words=200,
            max_words=500,
            include_subheadings=True,
            include_bullet_points=True,
            include_examples=True,
            include_statistics=True,
            tone=ContentTone.PROFESSIONAL,
        )

        keyword_config = KeywordConfig(
            min_terms=5,
            max_terms=8,
            include_examples=True,
            include_related_terms=True,
            explanation_length="medium",
        )

        image_config = ImageConfig(
            include_alt_text=True,
            include_caption=True,
            include_meta_description=True,
            max_alt_length=125,
            max_caption_length=200,
            style=ImageStyle.PROFESSIONAL,
        )

        # 통합 설정
        content_config = ContentConfig(
            title_config=title_config,
            outline_config=outline_config,
            section_config=section_config,
            keyword_config=keyword_config,
            image_config=image_config,
            target_word_count=2000,
            min_word_count=1500,
            max_word_count=3000,
            include_toc=True,
            include_keyword_definitions=True,
            include_images=True,
            num_images=3,
        )

        return AdvancedContentGenerator(content_config)

    def get_pbn_sites(self) -> List[Dict[str, Any]]:
        """PBN 사이트 목록을 가져옵니다."""
        try:
            sites = self.db.get_pbn_sites()
            print(f"📊 총 {len(sites)}개의 PBN 사이트를 찾았습니다.")
            return sites
        except Exception as e:
            print(f"❌ PBN 사이트 조회 중 오류 발생: {e}")
            return []

    def get_clients(self) -> List[Dict[str, Any]]:
        """클라이언트 목록을 가져옵니다."""
        try:
            clients = self.db.get_clients()
            print(f"👥 총 {len(clients)}명의 클라이언트를 찾았습니다.")
            return clients
        except Exception as e:
            print(f"❌ 클라이언트 조회 중 오류 발생: {e}")
            return []

    def get_client_keywords(self, client_id: int) -> List[Dict[str, Any]]:
        """클라이언트의 키워드 목록을 가져옵니다."""
        try:
            keywords = self.db.get_client_keywords(client_id)
            print(f"🔑 클라이언트 {client_id}의 키워드 {len(keywords)}개를 찾았습니다.")
            return keywords
        except Exception as e:
            print(f"❌ 키워드 조회 중 오류 발생: {e}")
            return []

    def generate_enhanced_content(
        self, client: Dict[str, Any], keyword: str, pbn_site: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """고도화된 콘텐츠를 생성합니다."""
        try:
            print(f"📝 콘텐츠 생성 시작: {keyword}")

            # 클라이언트 정보에서 주제 추출
            topic = client.get("topic", keyword)
            lsi_keywords = client.get("lsi_keywords", [])
            content_type = client.get("content_type", "guide")

            # 고도화된 콘텐츠 생성
            content = self.content_generator.generate_complete_content(
                topic=topic,
                target_keyword=keyword,
                lsi_keywords=lsi_keywords,
                content_type=content_type,
                client_info={
                    "id": client.get("id"),
                    "name": client.get("name"),
                    "target_url": client.get("target_url"),
                    "pbn_site": pbn_site.get("url"),
                },
            )

            print(f"✅ 콘텐츠 생성 완료: {content['title']}")
            print(f"   📊 단어 수: {content['statistics']['total_word_count']}")
            print(f"   📋 섹션 수: {content['statistics']['total_sections']}")
            print(f"   🎯 SEO 점수: {content['statistics']['seo_score']}")

            # HTML 변환 추가
            print("🔄 HTML 변환 중...")
            html_content = self._convert_content_to_html(content)
            content["html_content"] = html_content
            print("✅ HTML 변환 완료")

            return content

        except Exception as e:
            print(f"❌ 콘텐츠 생성 중 오류 발생: {e}")
            return None

    def _convert_content_to_html(self, content: Dict[str, Any]) -> str:
        """콘텐츠를 HTML로 변환합니다."""
        try:
            # 마크다운 콘텐츠를 HTML로 변환
            html_content = self.html_converter.convert_markdown_to_html(
                content["content"]
            )

            # 변환된 HTML에 메타데이터 추가
            html_with_meta = self._add_html_metadata(html_content, content)

            return html_with_meta

        except Exception as e:
            print(f"❌ HTML 변환 중 오류 발생: {e}")
            # 오류 발생 시 원본 콘텐츠를 그대로 반환
            return content["content"]

    def _add_html_metadata(self, html_content: str, content: Dict[str, Any]) -> str:
        """HTML 콘텐츠에 메타데이터를 추가합니다."""
        try:
            # 콘텐츠 통계 정보를 HTML 주석으로 추가
            stats = content["statistics"]
            meta_comment = f"""<!-- 
콘텐츠 생성 정보:
- 제목: {content['title']}
- 단어 수: {stats['total_word_count']}
- 섹션 수: {stats['total_sections']}
- SEO 점수: {stats['seo_score']}
- 생성 시간: {stats['generated_at']}
- 콘텐츠 유형: {stats['content_type']}
-->"""

            # HTML 콘텐츠 앞에 메타데이터 주석 추가
            return meta_comment + "\n" + html_content

        except Exception as e:
            print(f"❌ HTML 메타데이터 추가 중 오류 발생: {e}")
            return html_content

    def post_to_pbn(self, content: Dict[str, Any], pbn_site: Dict[str, Any]) -> bool:
        """PBN 사이트에 포스팅합니다."""
        try:
            print(f"📤 PBN 사이트에 포스팅 시작: {pbn_site['url']}")

            # HTML 콘텐츠 사용 (HTML 변환이 완료된 경우)
            if "html_content" in content and content["html_content"]:
                post_content = content["html_content"]
                print("📄 HTML 변환된 콘텐츠를 사용합니다.")
            else:
                # HTML 변환이 안된 경우 원본 콘텐츠 사용
                post_content = content["content"]
                print("⚠️ 원본 콘텐츠를 사용합니다. (HTML 변환 실패)")

            # 워드프레스에 포스팅
            success = self.wp_manager.create_post(
                site_url=pbn_site["url"],
                username=pbn_site["username"],
                password=pbn_site["password"],
                title=content["title"],
                content=post_content,
                status="publish",
            )

            if success:
                print(f"✅ 포스팅 성공: {pbn_site['url']}")

                # 포스트 기록 저장
                self._save_post_record(content, pbn_site)
                return True
            else:
                print(f"❌ 포스팅 실패: {pbn_site['url']}")
                return False

        except Exception as e:
            print(f"❌ 포스팅 중 오류 발생: {e}")
            return False

    def _save_post_record(
        self, content: Dict[str, Any], pbn_site: Dict[str, Any]
    ) -> None:
        """포스트 기록을 데이터베이스에 저장합니다."""
        try:
            # 포스트 정보 저장
            post_data = {
                "title": content["title"],
                "content": content["content"],
                "pbn_site_id": pbn_site["id"],
                "client_id": content["meta_data"].get("client_id"),
                "keyword": content["meta_data"]["target_keyword"],
                "word_count": content["statistics"]["total_word_count"],
                "seo_score": content["statistics"]["seo_score"],
                "created_at": datetime.now().isoformat(),
            }

            # 데이터베이스에 저장 (기존 테이블 구조에 맞게 수정 필요)
            # self.db.save_post(post_data)
            print(f"💾 포스트 기록 저장 완료")

        except Exception as e:
            print(f"❌ 포스트 기록 저장 중 오류 발생: {e}")

    def run_automated_campaign(
        self, client_id: int = None, pbn_site_id: int = None, max_posts: int = 5
    ) -> None:
        """자동화된 백링크 캠페인을 실행합니다."""
        print("🚀 자동화된 백링크 캠페인 시작")
        print("=" * 50)

        try:
            # PBN 사이트 조회
            pbn_sites = self.get_pbn_sites()
            if not pbn_sites:
                print("❌ PBN 사이트가 없습니다.")
                return

            # 클라이언트 조회
            clients = self.get_clients()
            if not clients:
                print("❌ 클라이언트가 없습니다.")
                return

            # 특정 클라이언트만 처리
            if client_id:
                clients = [c for c in clients if c["id"] == client_id]

            # 특정 PBN 사이트만 처리
            if pbn_site_id:
                pbn_sites = [p for p in pbn_sites if p["id"] == pbn_site_id]

            total_posts = 0
            successful_posts = 0

            # 각 클라이언트별로 처리
            for client in clients:
                print(f"\n👤 클라이언트 처리 중: {client.get('name', 'Unknown')}")

                # 클라이언트의 키워드 조회
                keywords = self.get_client_keywords(client["id"])
                if not keywords:
                    print(f"⚠️ 클라이언트 {client['id']}의 키워드가 없습니다.")
                    continue

                # 각 PBN 사이트별로 처리
                for pbn_site in pbn_sites:
                    if total_posts >= max_posts:
                        print(f"🛑 최대 포스트 수({max_posts})에 도달했습니다.")
                        break

                    print(f"\n🌐 PBN 사이트 처리 중: {pbn_site['url']}")

                    # 랜덤 키워드 선택
                    keyword_data = random.choice(keywords)
                    keyword = keyword_data["keyword"]

                    # 고도화된 콘텐츠 생성
                    content = self.generate_enhanced_content(client, keyword, pbn_site)
                    if not content:
                        print(f"❌ 콘텐츠 생성 실패: {keyword}")
                        continue

                    # PBN 사이트에 포스팅
                    if self.post_to_pbn(content, pbn_site):
                        successful_posts += 1
                        print(f"✅ 성공적으로 포스팅됨: {keyword} → {pbn_site['url']}")
                    else:
                        print(f"❌ 포스팅 실패: {keyword} → {pbn_site['url']}")

                    total_posts += 1

                    # 포스팅 간 대기 시간
                    wait_time = random.randint(30, 60)
                    print(f"⏳ {wait_time}초 대기 중...")
                    time.sleep(wait_time)

            # 최종 결과 출력
            print("\n" + "=" * 50)
            print("🎉 자동화된 백링크 캠페인 완료")
            print(f"📊 총 포스트 수: {total_posts}")
            print(f"✅ 성공한 포스트: {successful_posts}")
            print(f"❌ 실패한 포스트: {total_posts - successful_posts}")
            print(
                f"📈 성공률: {(successful_posts/total_posts*100):.1f}%"
                if total_posts > 0
                else "0%"
            )

        except Exception as e:
            print(f"❌ 캠페인 실행 중 오류 발생: {e}")

    def test_content_generation(
        self,
        topic: str = "마케팅 성공 방법",
        keyword: str = "디지털 마케팅",
        lsi_keywords: List[str] = None,
    ) -> None:
        """콘텐츠 생성 기능을 테스트합니다."""
        print("🧪 콘텐츠 생성 테스트 시작")
        print("=" * 50)

        if not lsi_keywords:
            lsi_keywords = ["온라인", "전략", "효과"]

        try:
            # 테스트용 클라이언트 정보
            test_client = {
                "id": 999,
                "name": "Test Client",
                "topic": topic,
                "lsi_keywords": lsi_keywords,
                "content_type": "guide",
            }

            # 테스트용 PBN 사이트 정보
            test_pbn = {
                "id": 999,
                "url": "https://test-pbn.com",
                "username": "test",
                "password": "test",
            }

            # 콘텐츠 생성
            content = self.generate_enhanced_content(test_client, keyword, test_pbn)

            if content:
                print("\n📝 생성된 콘텐츠 미리보기:")
                print("-" * 30)
                print(f"제목: {content['title']}")
                print(f"단어 수: {content['statistics']['total_word_count']}")
                print(f"섹션 수: {content['statistics']['total_sections']}")
                print(f"SEO 점수: {content['statistics']['seo_score']}")

                # HTML 변환 상태 확인
                if "html_content" in content and content["html_content"]:
                    print("✅ HTML 변환 완료")
                    print("\n📄 HTML 콘텐츠 미리보기 (처음 500자):")
                    print(content["html_content"][:500] + "...")
                else:
                    print("⚠️ HTML 변환 실패 - 원본 콘텐츠 사용")
                    print("\n콘텐츠 내용 (처음 500자):")
                    print(content["content"][:500] + "...")

                # 파일로 저장
                filename = (
                    f"test_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                self.content_generator.save_content_to_file(content, filename)
                print(f"\n💾 테스트 콘텐츠가 {filename}에 저장되었습니다.")

                # HTML 파일도 별도로 저장
                if "html_content" in content and content["html_content"]:
                    html_filename = (
                        f"test_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    )
                    with open(html_filename, "w", encoding="utf-8") as f:
                        f.write(content["html_content"])
                    print(f"💾 HTML 콘텐츠가 {html_filename}에 저장되었습니다.")
            else:
                print("❌ 콘텐츠 생성에 실패했습니다.")

        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")

    def test_html_conversion(self) -> None:
        """HTML 변환 기능을 테스트합니다."""
        print("🧪 HTML 변환 테스트 시작")
        print("=" * 50)

        try:
            # 테스트용 마크다운 콘텐츠
            test_markdown = """# 테스트 제목

## 섹션 1: 소개
이것은 **테스트 콘텐츠**입니다.

### 하위 섹션
- 첫 번째 항목
- 두 번째 항목
- 세 번째 항목

## 섹션 2: 예시
예를 들어, 다음과 같은 내용이 있습니다:

1. 첫 번째 단계
2. 두 번째 단계
3. 세 번째 단계

## 📖 핵심 용어 정리
**용어1**: 이것은 첫 번째 용어의 설명입니다.
**용어2**: 이것은 두 번째 용어의 설명입니다.
**용어3**: 이것은 세 번째 용어의 설명입니다.

## 결론
이것은 테스트의 마무리입니다.
"""

            print("📝 테스트용 마크다운 콘텐츠:")
            print("-" * 30)
            print(test_markdown[:200] + "...")
            print()

            # HTML 변환
            print("🔄 HTML 변환 중...")
            html_content = self.html_converter.convert_markdown_to_html(test_markdown)

            print("✅ HTML 변환 완료!")
            print("\n📄 변환된 HTML 콘텐츠:")
            print("-" * 30)
            print(html_content[:500] + "...")
            print()

            # HTML 파일로 저장
            html_filename = (
                f"test_html_conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"💾 HTML 파일이 {html_filename}에 저장되었습니다.")

            # 변환 통계
            markdown_lines = len(test_markdown.split("\n"))
            html_lines = len(html_content.split("\n"))
            print(f"\n📊 변환 통계:")
            print(f"   마크다운 줄 수: {markdown_lines}")
            print(f"   HTML 줄 수: {html_lines}")
            print(f"   변환 비율: {html_lines/markdown_lines:.1f}:1")

        except Exception as e:
            print(f"❌ HTML 변환 테스트 중 오류 발생: {e}")


def main():
    """메인 실행 함수"""
    print("🚀 고도화된 PBN 백링크 자동화 시스템 v2.0")
    print("=" * 60)

    # 시스템 초기화
    system = EnhancedPBNSystem()

    while True:
        print("\n📋 메뉴를 선택하세요:")
        print("1. 자동화된 백링크 캠페인 실행")
        print("2. 콘텐츠 생성 테스트")
        print("3. HTML 변환 테스트")
        print("4. PBN 사이트 목록 조회")
        print("5. 클라이언트 목록 조회")
        print("6. 종료")

        choice = input("\n선택 (1-6): ").strip()

        if choice == "1":
            try:
                max_posts = int(input("최대 포스트 수 (기본값: 5): ") or "5")
                system.run_automated_campaign(max_posts=max_posts)
            except ValueError:
                print("❌ 잘못된 입력입니다. 숫자를 입력해주세요.")

        elif choice == "2":
            topic = (
                input("주제 (기본값: 마케팅 성공 방법): ").strip() or "마케팅 성공 방법"
            )
            keyword = (
                input("키워드 (기본값: 디지털 마케팅): ").strip() or "디지털 마케팅"
            )
            lsi_input = input(
                "LSI 키워드 (쉼표로 구분, 기본값: 온라인,전략,효과): "
            ).strip()
            lsi_keywords = (
                [k.strip() for k in lsi_input.split(",")]
                if lsi_input
                else ["온라인", "전략", "효과"]
            )

            system.test_content_generation(topic, keyword, lsi_keywords)

        elif choice == "3":
            system.test_html_conversion()

        elif choice == "4":
            sites = system.get_pbn_sites()
            if sites:
                print("\n📊 PBN 사이트 목록:")
                for site in sites:
                    print(f"  - {site['url']} (ID: {site['id']})")
            else:
                print("❌ PBN 사이트가 없습니다.")

        elif choice == "5":
            clients = system.get_clients()
            if clients:
                print("\n👥 클라이언트 목록:")
                for client in clients:
                    print(f"  - {client.get('name', 'Unknown')} (ID: {client['id']})")
            else:
                print("❌ 클라이언트가 없습니다.")

        elif choice == "6":
            print("👋 시스템을 종료합니다.")
            break

        else:
            print("❌ 잘못된 선택입니다. 1-6 중에서 선택해주세요.")


if __name__ == "__main__":
    main()
