# -*- coding: utf-8 -*-
# manager.py
import sys
from controlDB import (
    add_pbn_site,
    view_pbn_sites,
    delete_record_by_id,
    add_client,
    view_clients,
    view_completed_clients,
    move_client_to_completed,
    update_client_info,
    pause_client,
    resume_client,
    pause_all_clients,
    resume_all_clients,
    view_client_status,
    fetch_all_posts,
    save_all_backlinks_to_excel,
    show_all_tables,
    add_client_keyword,
    get_client_keywords,
    remove_duplicate_clients,
)


def display_menu():
    print("\n========== Manager Menu ==========")
    print("1. PBN 사이트 추가")
    print("2. PBN 사이트 조회")
    print("3. PBN 사이트 삭제")
    print("4. 클라이언트 추가")
    print("5. 클라이언트 조회")
    print("6. 클라이언트 정보 수정")
    print("7. 클라이언트 남은 기간 단축/연장")
    print("8. 클라이언트 작업 완료 처리")
    print("9. 완료된 클라이언트 조회")
    print("10. 모든 테이블 상태 확인")
    print("11. 특정 클라이언트 상태 조회")
    print("12. 특정 클라이언트 일시정지/재개")
    print("13. 모든 클라이언트 일시정지")
    print("14. 모든 클라이언트 재개")
    print("15. 백링크 보고서 엑셀로 저장")
    print("16. (추가) 특정 클라이언트 키워드 조회")
    print("17. 중복 클라이언트 제거")
    print("q. 종료")
    print("==================================")


def add_pbn_site_prompt():
    site_url = input("PBN 사이트 URL 입력: ")
    username = input("PBN 사이트 관리자 아이디 입력: ")
    password = input("PBN 사이트 관리자 비밀번호 입력: ")
    app_password = input("PBN 사이트 응용프로그램 비밀번호 입력: ")
    add_pbn_site(site_url, username, password, app_password)
    print("PBN 사이트 추가 완료")


# 여러 개의 PBN 사이트를 한 번에 추가하는 함수 (사이트가 추가될때마다 수정)
def bulk_add_pbn_sites():
    """
    여러 개의 PBN 사이트를 한 번에 추가하는 함수
    """
    sites = [
        (
            "https://jungbomoum.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "pFMJ A3pn Ea4e Y7hv LcfO G0Nb",
        ),
        (
            "https://krhobby.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "JnOx eVsN 39o2 RrB3 stHU UoSO",
        ),
        (
            "https://joenfeel.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "5CnL vndl 6X6Y Egew g1eJ uSCQ",
        ),
        (
            "https://hugekrblog.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "NIq2 ToaV 7o89 heZ2 mnVe 2vBd",
        ),
        (
            "https://myjungbo.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "l6S0 7qlC pUHI pjd6 mOrV 2s7w",
        ),
        (
            "https://koreaallinfo.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "TLQ6 gvCT EMNq MnTn F86i crBT",
        ),
        (
            "https://clearmind.ai.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "s4GP qqNQ i7qG Tz1W vYGz ylR4",
        ),
        (
            "https://cleanspirit.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "W272 rpTb MOXB QE3n hVLK oLJB",
        ),
        (
            "https://uptolife.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "c3p5 sGcA zD9v mD4A rIEo kwsw",
        ),
        (
            "https://owngoodinfo.co.kr/",
            "admin",
            "Lqp1o2k3!@#",
            "atu1 3EH5 DVaS AN5x JRG2 7OUV",
        ),
    ]

    for site_url, username, password, app_password in sites:
        add_pbn_site(site_url, username, password, app_password)
        print(f"추가 완료: {site_url}")
    print("\n모든 PBN 사이트가 추가되었습니다.")


def delete_pbn_site_prompt():
    view_pbn_sites()  # 현재 PBN 사이트 목록 조회
    site_id = int(input("삭제할 PBN site_id 입력: "))
    delete_record_by_id("pbn_sites", site_id, "site_id")


def add_client_prompt():
    client_name = input("클라이언트 이름: ").strip()
    site_url = input("클라이언트 사이트 주소: ").strip()
    total_backlinks = int(
        input_with_validation(
            "총 백링크 수: ", is_positive_int, "양의 정수를 입력하세요."
        )
    )
    remaining_days = int(
        input_with_validation(
            "업로드 기간(일): ", is_positive_int, "양의 정수를 입력하세요."
        )
    )
    # 새로 추가될 부분
    daily_min = int(
        input_with_validation(
            "일일 최소 백링크 수(daily_min): ",
            is_positive_int,
            "양의 정수를 입력하세요.",
        )
    )
    daily_max = int(
        input_with_validation(
            "일일 최대 백링크 수(daily_max): ",
            is_positive_int,
            "양의 정수를 입력하세요.",
        )
    )
    if daily_min > daily_max:
        print("일일 최소수량이 최대수량보다 클 수 없습니다. 다시 입력하세요.")
        return

    # clients 테이블에 min/max까지 넣어야 하므로 인자 수정
    client_id = add_client(
        client_name, site_url, total_backlinks, remaining_days, daily_min, daily_max
    )
    print(f"클라이언트 '{client_name}' 추가 완료. (ID: {client_id})")

    # 키워드 입력 부분
    keyword_str = input("추가할 키워드들(쉼표로 구분): ").strip()
    if keyword_str:
        for kw in keyword_str.split(","):
            add_client_keyword(client_id, kw.strip())
    print("키워드 추가 완료.")


def update_client_prompt():
    view_clients()
    client_id = int(input("수정할 클라이언트 ID: "))
    print("\n수정할 내용을 선택하세요:")
    print("1. 클라이언트 이름")
    print("2. 사이트 주소")
    print("3. (추가) 키워드 입력")
    print("4. 백링크 수량(total_backlinks)")
    print("5. 남은 기간(단축/연장)")
    print("6. 일일 최소/최대 백링크 값(daily_min, daily_max) 수정")
    choice = input("선택: ").strip()

    if choice == "1":
        new_value = input("새 클라이언트 이름: ").strip()
        update_client_info(client_id, client_name=new_value)
    elif choice == "2":
        new_value = input("새 사이트 주소: ").strip()
        update_client_info(client_id, site_url=new_value)
    elif choice == "3":
        new_keywords = input("추가할 키워드(쉼표 구분): ").strip()
        if new_keywords:
            for kw in new_keywords.split(","):
                add_client_keyword(client_id, kw.strip())
        print("키워드 추가 완료.")
    elif choice == "4":
        new_total = int(
            input_with_validation("새 백링크 수(양의 정수): ", is_positive_int)
        )
        update_client_info(client_id, total_backlinks=new_total)
    elif choice == "5":
        new_days = int(input_with_validation("새 남은 기간(일): ", is_positive_int))
        update_client_info(client_id, remaining_days=new_days)
    elif choice == "6":
        new_min = int(
            input_with_validation("새 일일 최소 백링크 수: ", is_positive_int)
        )
        new_max = int(
            input_with_validation("새 일일 최대 백링크 수: ", is_positive_int)
        )
        if new_min > new_max:
            print("최소수량이 최대수량보다 클 수 없습니다. 취소합니다.")
            return
        # daily_min, daily_max가 clients 테이블에 있다고 가정
        update_client_info(client_id, daily_min=new_min, daily_max=new_max)
        print("daily_min, daily_max 수정 완료.")
    else:
        print("잘못된 선택입니다.")

    print("클라이언트 정보 수정 완료")


def extend_or_reduce_days_prompt():
    view_clients()
    client_id = int(input("기간 변경할 클라이언트 ID: "))
    change_days = int(input("변경할 일수(+는 연장, -는 단축): "))
    # update_client_info 이용
    # remaining_days에 change_days를 더해준다
    # 예: 기존 10일인데 5를 단축하려면 -5
    # 기존 remaining_days 가져오는 과정은 생략 (이미 lovealbaDB에서 가능)
    # 여기서는 단순하게 처리
    # 일일평균 구축량 자동 재계산은 update_client_info 에서 처리
    # remaining_days = 기존_remaining_days + change_days
    # 간단히 update_client_info(client_id, remaining_days=(기존+change_days))
    # 여기서 기존값 가져오는 로직 없이 바로 하려면
    # 기존 API 구조 상 update_client_info가 기존 값 접근 가능
    # 다만 기존 remaining_days를 알기 위해 view_client_status를 이용
    status = view_client_status(client_id)
    if not status:
        print("존재하지 않는 클라이언트입니다.")
        return
    new_days = status["remaining_days"] + change_days
    if new_days < 1:
        print("남은 기간은 1일 이상이어야 합니다.")
        return
    update_client_info(client_id, remaining_days=new_days)
    print(f"클라이언트 {client_id}의 남은 기간 변경 완료: {new_days}일")


def complete_client_prompt():
    view_clients()
    client_id = int(input("작업 완료 처리할 클라이언트 ID: "))
    move_client_to_completed(client_id)
    print("클라이언트 작업 완료 처리 완료")


def view_client_status_prompt():
    view_clients()
    client_id = int(input("상태 조회할 클라이언트 ID: "))
    status = view_client_status(client_id)
    if status:
        print(f"\n클라이언트 ID: {status['client_id']}")
        print(f"이름: {status['client_name']}")
        print(f"구축된 백링크 수: {status['built_count']}")
        print(f"남은 백링크 수: {status['remaining_count']}")
        print(f"남은 기간: {status['remaining_days']} 일")
    else:
        print("해당 클라이언트를 찾을 수 없습니다.")


def pause_resume_client_prompt():
    view_clients()
    client_id = int(input("일시 정지/재개할 클라이언트 ID: "))
    action = input("일시정지(pause) / 재개(resume): ").strip().lower()
    if action == "pause":
        pause_client(client_id)
        print(f"{client_id} 클라이언트 일시정지 완료")
    elif action == "resume":
        resume_client(client_id)
        print(f"{client_id} 클라이언트 재개 완료")
    else:
        print("잘못된 명령입니다.")


def view_client_keywords_prompt():
    """
    특정 클라이언트의 키워드를 확인하는 간단한 메뉴
    """
    view_clients()
    cid = input_with_validation(
        "키워드를 조회할 클라이언트 ID: ", lambda x: x.isdigit()
    )
    cid = int(cid)
    keywords = get_client_keywords(cid)
    if keywords:
        print(f"클라이언트 {cid}의 키워드 목록:")
        for kw in keywords:
            print(" -", kw)
    else:
        print("등록된 키워드가 없습니다.")


def input_with_validation(
    prompt,
    validation_func=lambda x: True,
    error_message="잘못된 입력입니다. 다시 시도하세요.",
):
    """
    입력 값을 검증하고 유효한 값만 반환하는 함수.
    :param prompt: 사용자 입력 메시지
    :param validation_func: 입력 값을 검증하는 함수(불리언 반환)
    :param error_message: 검증 실패 시 표시할 메시지
    """
    while True:
        value = input(prompt).strip()
        if validation_func(value):
            return value
        else:
            print(error_message)


def is_positive_int(x):
    return x.isdigit() and int(x) > 0


def main():
    while True:
        display_menu()
        choice = input("작업 선택(q 종료): ").lower()

        if choice == "1":
            add_pbn_site_prompt()
        elif choice == "2":
            view_pbn_sites()
        elif choice == "3":
            delete_pbn_site_prompt()
        elif choice == "4":
            add_client_prompt()
        elif choice == "5":
            view_clients()
        elif choice == "6":
            update_client_prompt()
        elif choice == "7":
            extend_or_reduce_days_prompt()
        elif choice == "8":
            complete_client_prompt()
        elif choice == "9":
            view_completed_clients()
        elif choice == "10":
            show_all_tables()
        elif choice == "11":
            view_client_status_prompt()
        elif choice == "12":
            pause_resume_client_prompt()
        elif choice == "13":
            pause_all_clients()
            print("모든 클라이언트 일시정지 완료")
        elif choice == "14":
            resume_all_clients()
            print("모든 클라이언트 재개 완료")
        elif choice == "15":
            output_file = input("엑셀 파일명(기본: backlink_report.xlsx): ").strip()
            if not output_file:
                output_file = "backlink_report.xlsx"
            save_all_backlinks_to_excel(output_file)
        elif choice == "16":
            view_client_keywords_prompt()  # 새 함수 호출
        elif choice == "17":
            remove_duplicate_clients()
        elif choice == "18":
            bulk_add_pbn_sites()
        elif choice == "q":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("잘못된 선택입니다. 다시 시도하세요.")


if __name__ == "__main__":
    main()
