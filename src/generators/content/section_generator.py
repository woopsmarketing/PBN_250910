# v1.0 - 고도화된 섹션 콘텐츠 생성기 (PBN 시스템용)
# SEO 최적화된 섹션별 콘텐츠 생성

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import random

class ContentTone(Enum):
    """콘텐츠 톤 정의"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"

class ContentStructure(Enum):
    """콘텐츠 구조 정의"""
    PROBLEM_SOLUTION = "problem_solution"
    STEP_BY_STEP = "step_by_step"
    COMPARISON = "comparison"
    LIST = "list"
    STORY = "story"

@dataclass
class SectionConfig:
    """섹션 생성 설정"""
    min_words: int = 200
    max_words: int = 500
    include_subheadings: bool = True
    include_bullet_points: bool = True
    include_examples: bool = True
    include_statistics: bool = True
    tone: ContentTone = ContentTone.PROFESSIONAL
    structure: ContentStructure = ContentStructure.PROBLEM_SOLUTION

class AdvancedSectionGenerator:
    """고도화된 섹션 콘텐츠 생성기"""
    
    def __init__(self, config: SectionConfig = None):
        self.config = config or SectionConfig()
        self.transition_phrases = [
            "또한", "더불어", "그뿐만 아니라", "특히", "구체적으로",
            "예를 들어", "실제로", "결과적으로", "따라서", "그러므로"
        ]
        self.power_words = [
            "핵심", "중요한", "필수적인", "효과적인", "성공적인",
            "전문적인", "혁신적인", "검증된", "실용적인", "최적화된"
        ]
        self.statistics_templates = [
            "연구에 따르면 {percentage}%의 경우에서 효과가 입증되었습니다.",
            "최근 조사 결과 {percentage}%의 사용자가 만족도를 표시했습니다.",
            "통계적으로 {percentage}%의 성공률을 보여줍니다.",
            "데이터 분석 결과 {percentage}%의 개선 효과가 나타났습니다."
        ]
    
    def generate_section_content(self, 
                                section_title: str,
                                topic: str,
                                target_keyword: str,
                                lsi_keywords: List[str] = None,
                                section_type: str = "main_content") -> Dict[str, any]:
        """
        섹션별 고품질 콘텐츠를 생성합니다.
        
        Args:
            section_title: 섹션 제목
            topic: 주제
            target_keyword: 타겟 키워드
            lsi_keywords: LSI 키워드 목록
            section_type: 섹션 유형
            
        Returns:
            섹션 콘텐츠 정보 딕셔너리
        """
        # 콘텐츠 구조 결정
        structure = self._determine_content_structure(section_type, topic)
        
        # 메인 콘텐츠 생성
        main_content = self._generate_main_content(
            section_title, topic, target_keyword, lsi_keywords, structure
        )
        
        # 서브헤딩 생성
        subheadings = self._generate_subheadings(
            section_title, topic, target_keyword, lsi_keywords
        )
        
        # 불릿 포인트 생성
        bullet_points = self._generate_bullet_points(
            section_title, topic, target_keyword, lsi_keywords
        )
        
        # 예시 생성
        examples = self._generate_examples(
            section_title, topic, target_keyword, lsi_keywords
        )
        
        # 통계 생성
        statistics = self._generate_statistics(
            section_title, topic, target_keyword, lsi_keywords
        )
        
        # 전체 콘텐츠 조합
        full_content = self._combine_content(
            main_content, subheadings, bullet_points, examples, statistics
        )
        
        # SEO 점수 계산
        seo_score = self._calculate_seo_score(
            full_content, target_keyword, lsi_keywords
        )
        
        return {
            "content": full_content,
            "main_content": main_content,
            "subheadings": subheadings,
            "bullet_points": bullet_points,
            "examples": examples,
            "statistics": statistics,
            "word_count": len(full_content.split()),
            "seo_score": seo_score,
            "structure": structure.value
        }
    
    def _determine_content_structure(self, section_type: str, topic: str) -> ContentStructure:
        """콘텐츠 구조를 결정합니다."""
        if section_type == "introduction":
            return ContentStructure.STORY
        elif section_type == "main_content":
            return ContentStructure.PROBLEM_SOLUTION
        elif section_type == "tips":
            return ContentStructure.LIST
        elif section_type == "examples":
            return ContentStructure.STORY
        elif section_type == "conclusion":
            return ContentStructure.PROBLEM_SOLUTION
        else:
            return ContentStructure.PROBLEM_SOLUTION
    
    def _generate_main_content(self, 
                              section_title: str,
                              topic: str,
                              target_keyword: str,
                              lsi_keywords: List[str],
                              structure: ContentStructure) -> str:
        """메인 콘텐츠를 생성합니다."""
        
        if structure == ContentStructure.PROBLEM_SOLUTION:
            return self._generate_problem_solution_content(
                section_title, topic, target_keyword, lsi_keywords
            )
        elif structure == ContentStructure.STEP_BY_STEP:
            return self._generate_step_by_step_content(
                section_title, topic, target_keyword, lsi_keywords
            )
        elif structure == ContentStructure.LIST:
            return self._generate_list_content(
                section_title, topic, target_keyword, lsi_keywords
            )
        elif structure == ContentStructure.STORY:
            return self._generate_story_content(
                section_title, topic, target_keyword, lsi_keywords
            )
        else:
            return self._generate_default_content(
                section_title, topic, target_keyword, lsi_keywords
            )
    
    def _generate_problem_solution_content(self, 
                                          section_title: str,
                                          topic: str,
                                          target_keyword: str,
                                          lsi_keywords: List[str]) -> str:
        """문제-해결 구조 콘텐츠를 생성합니다."""
        content = f"{section_title}에서 가장 중요한 것은 {target_keyword}의 효과적인 활용입니다. "
        
        # 문제 제시
        content += f"많은 사람들이 {topic}에 대해 어려움을 겪고 있으며, 이는 {target_keyword}에 대한 올바른 이해가 부족하기 때문입니다. "
        
        # 해결책 제시
        content += f"하지만 {target_keyword}를 올바르게 이해하고 활용한다면, {topic}에서 놀라운 성과를 얻을 수 있습니다. "
        
        # 구체적 방법 제시
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            content += f"특히 {lsi} {target_keyword}는 {topic}의 성공을 위한 핵심 요소입니다. "
        
        # 추가 설명
        content += f"이를 통해 {topic}에서 지속적인 성장과 발전을 이룰 수 있으며, "
        content += f"{target_keyword}의 진정한 가치를 경험할 수 있습니다."
        
        return content
    
    def _generate_step_by_step_content(self, 
                                      section_title: str,
                                      topic: str,
                                      target_keyword: str,
                                      lsi_keywords: List[str]) -> str:
        """단계별 구조 콘텐츠를 생성합니다."""
        content = f"{section_title}를 성공적으로 수행하기 위해서는 체계적인 접근이 필요합니다. "
        
        # 첫 번째 단계
        content += f"먼저 {target_keyword}에 대한 기본적인 이해를 갖춰야 합니다. "
        
        # 두 번째 단계
        content += f"다음으로 {topic}에 맞는 구체적인 계획을 수립해야 합니다. "
        
        # 세 번째 단계
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            content += f"그리고 {lsi} {target_keyword}를 활용한 실행 계획을 세워야 합니다. "
        
        # 마지막 단계
        content += f"마지막으로 지속적인 모니터링과 개선을 통해 {topic}에서 최적의 결과를 얻을 수 있습니다."
        
        return content
    
    def _generate_list_content(self, 
                              section_title: str,
                              topic: str,
                              target_keyword: str,
                              lsi_keywords: List[str]) -> str:
        """리스트 구조 콘텐츠를 생성합니다."""
        content = f"{section_title}에서 성공하기 위한 핵심 요소들은 다음과 같습니다. "
        
        # 첫 번째 요소
        content += f"첫째, {target_keyword}에 대한 깊이 있는 이해가 필요합니다. "
        
        # 두 번째 요소
        content += f"둘째, {topic}에 맞는 구체적인 전략을 수립해야 합니다. "
        
        # 세 번째 요소
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            content += f"셋째, {lsi} {target_keyword}를 효과적으로 활용해야 합니다. "
        
        # 네 번째 요소
        content += f"넷째, 지속적인 학습과 개선을 통해 {topic}에서 성과를 높여야 합니다."
        
        return content
    
    def _generate_story_content(self, 
                               section_title: str,
                               topic: str,
                               target_keyword: str,
                               lsi_keywords: List[str]) -> str:
        """스토리 구조 콘텐츠를 생성합니다."""
        content = f"{section_title}에서 {target_keyword}의 중요성을 보여주는 실제 사례가 있습니다. "
        
        # 스토리 시작
        content += f"한 전문가가 {topic}에 도전했을 때, {target_keyword}에 대한 올바른 이해가 없어 어려움을 겪었습니다. "
        
        # 전환점
        content += f"하지만 {target_keyword}의 핵심 원리를 깨닫고 나서는 놀라운 변화가 일어났습니다. "
        
        # 결과
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            content += f"특히 {lsi} {target_keyword}를 활용한 접근 방식이 {topic}에서 큰 성과를 가져왔습니다. "
        
        # 교훈
        content += f"이 사례는 {target_keyword}의 올바른 이해와 활용이 {topic}의 성공을 위한 핵심임을 보여줍니다."
        
        return content
    
    def _generate_default_content(self, 
                                 section_title: str,
                                 topic: str,
                                 target_keyword: str,
                                 lsi_keywords: List[str]) -> str:
        """기본 콘텐츠를 생성합니다."""
        content = f"{section_title}는 {topic}에서 매우 중요한 역할을 합니다. "
        content += f"{target_keyword}를 통해 {topic}의 성공을 이룰 수 있으며, "
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            content += f"특히 {lsi} {target_keyword}는 {topic}에 필수적인 요소입니다. "
        
        content += f"따라서 {target_keyword}에 대한 올바른 이해와 활용이 {topic}의 성공을 위한 핵심입니다."
        
        return content
    
    def _generate_subheadings(self, 
                             section_title: str,
                             topic: str,
                             target_keyword: str,
                             lsi_keywords: List[str]) -> List[str]:
        """서브헤딩들을 생성합니다."""
        if not self.config.include_subheadings:
            return []
        
        subheadings = [
            f"{target_keyword}의 핵심 원리",
            f"{topic}에서의 {target_keyword} 활용",
            f"{target_keyword} 성공을 위한 전략"
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            subheadings.append(f"{lsi} {target_keyword}의 장점")
        
        return subheadings[:3]  # 최대 3개
    
    def _generate_bullet_points(self, 
                               section_title: str,
                               topic: str,
                               target_keyword: str,
                               lsi_keywords: List[str]) -> List[str]:
        """불릿 포인트들을 생성합니다."""
        if not self.config.include_bullet_points:
            return []
        
        bullet_points = [
            f"{target_keyword}는 {topic}의 성공을 위한 핵심 요소입니다.",
            f"{target_keyword}를 올바르게 이해하면 {topic}에서 큰 성과를 얻을 수 있습니다.",
            f"{target_keyword}의 효과적인 활용이 {topic}의 성공을 좌우합니다."
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            bullet_points.append(f"{lsi} {target_keyword}는 {topic}에 특별한 효과를 가져옵니다.")
        
        return bullet_points[:4]  # 최대 4개
    
    def _generate_examples(self, 
                          section_title: str,
                          topic: str,
                          target_keyword: str,
                          lsi_keywords: List[str]) -> List[str]:
        """예시들을 생성합니다."""
        if not self.config.include_examples:
            return []
        
        examples = [
            f"예를 들어, {target_keyword}를 활용한 {topic} 사례에서 놀라운 성과를 보였습니다.",
            f"구체적으로는 {target_keyword}가 {topic}의 성공에 결정적인 역할을 했습니다.",
            f"실제로 {target_keyword}를 통해 {topic}에서 지속적인 성장을 이룬 사례가 있습니다."
        ]
        
        if lsi_keywords:
            lsi = lsi_keywords[0] if lsi_keywords else ""
            examples.append(f"특히 {lsi} {target_keyword}는 {topic}에서 특별한 효과를 보여줍니다.")
        
        return examples[:3]  # 최대 3개
    
    def _generate_statistics(self, 
                            section_title: str,
                            topic: str,
                            target_keyword: str,
                            lsi_keywords: List[str]) -> List[str]:
        """통계 정보들을 생성합니다."""
        if not self.config.include_statistics:
            return []
        
        # 랜덤 통계 생성
        percentages = [85, 92, 78, 88, 95, 82, 90, 87]
        percentage = random.choice(percentages)
        
        statistics = [
            f"연구에 따르면 {percentage}%의 경우에서 {target_keyword}가 {topic}에 효과적임이 입증되었습니다.",
            f"최근 조사 결과 {percentage}%의 사용자가 {target_keyword}를 통한 {topic} 성과에 만족하고 있습니다.",
            f"통계적으로 {percentage}%의 성공률을 보이는 {target_keyword}는 {topic}에 필수적입니다."
        ]
        
        return statistics[:2]  # 최대 2개
    
    def _combine_content(self, 
                        main_content: str,
                        subheadings: List[str],
                        bullet_points: List[str],
                        examples: List[str],
                        statistics: List[str]) -> str:
        """전체 콘텐츠를 조합합니다."""
        content = main_content + "\n\n"
        
        # 서브헤딩 추가
        if subheadings:
            content += "## 주요 포인트\n\n"
            for subheading in subheadings:
                content += f"### {subheading}\n\n"
        
        # 불릿 포인트 추가
        if bullet_points:
            content += "## 핵심 요소\n\n"
            for bullet in bullet_points:
                content += f"• {bullet}\n"
            content += "\n"
        
        # 예시 추가
        if examples:
            content += "## 실제 사례\n\n"
            for example in examples:
                content += f"{example}\n\n"
        
        # 통계 추가
        if statistics:
            content += "## 통계 자료\n\n"
            for stat in statistics:
                content += f"{stat}\n\n"
        
        return content.strip()
    
    def _calculate_seo_score(self, 
                           content: str, 
                           target_keyword: str, 
                           lsi_keywords: List[str]) -> int:
        """SEO 점수를 계산합니다."""
        score = 0
        
        # 타겟 키워드 밀도
        word_count = len(content.split())
        keyword_count = content.lower().count(target_keyword.lower())
        keyword_density = keyword_count / word_count if word_count > 0 else 0
        
        if 0.01 <= keyword_density <= 0.03:  # 1-3% 밀도
            score += 30
        elif 0.005 <= keyword_density <= 0.05:  # 0.5-5% 밀도
            score += 20
        
        # LSI 키워드 포함 여부
        if lsi_keywords:
            lsi_count = sum(1 for lsi in lsi_keywords 
                          if lsi.lower() in content.lower())
            score += lsi_count * 10
        
        # 단어 수 점수
        if 200 <= word_count <= 500:
            score += 20
        elif 150 <= word_count <= 600:
            score += 10
        
        # 파워 워드 포함 여부
        power_word_count = sum(1 for word in self.power_words 
                             if word in content)
        score += power_word_count * 5
        
        return score

# 사용 예시
if __name__ == "__main__":
    # 섹션 생성기 설정
    config = SectionConfig(
        min_words=200,
        max_words=500,
        include_subheadings=True,
        include_bullet_points=True,
        include_examples=True,
        include_statistics=True,
        tone=ContentTone.PROFESSIONAL
    )
    
    # 섹션 생성기 인스턴스 생성
    generator = AdvancedSectionGenerator(config)
    
    # 섹션 콘텐츠 생성
    result = generator.generate_section_content(
        section_title="마케팅의 핵심 원리",
        topic="성공하는 방법",
        target_keyword="마케팅",
        lsi_keywords=["디지털", "온라인", "전략"],
        section_type="main_content"
    )
    
    # 결과 출력
    print("=== 생성된 섹션 콘텐츠 ===")
    print(f"단어 수: {result['word_count']}")
    print(f"SEO 점수: {result['seo_score']}")
    print(f"구조: {result['structure']}")
    print()
    print("=== 메인 콘텐츠 ===")
    print(result['main_content'])
    print()
    print("=== 전체 콘텐츠 ===")
    print(result['content'])