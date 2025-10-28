#!/usr/bin/env python3
"""
Gmail API를 사용한 이메일 분류 및 통계 프로그램

사용법:
    python gmail_main.py
    python gmail_main.py --max 200
    python gmail_main.py --query "is:unread"
"""

import argparse
import sys
import os
from dotenv import load_dotenv

from gmail_classifier import GmailClassifier
from email_statistics import EmailStatisticsAnalyzer


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description='Gmail API를 사용한 이메일 분류 및 통계 프로그램',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python gmail_main.py
  python gmail_main.py --max 200
  python gmail_main.py --query "is:unread"
  python gmail_main.py --query "from:example@gmail.com" --output results

Gmail 검색 쿼리 예제:
  is:unread           - 읽지 않은 이메일
  is:starred          - 별표 표시된 이메일
  from:user@gmail.com - 특정 발신자
  subject:회의         - 제목에 '회의' 포함
  after:2024/01/01    - 특정 날짜 이후
  has:attachment      - 첨부파일 있는 이메일
        """
    )

    parser.add_argument(
        '--max',
        '-m',
        type=int,
        default=100,
        help='분석할 최대 이메일 개수 (기본값: 100)'
    )

    parser.add_argument(
        '--query',
        '-q',
        default='',
        help='Gmail 검색 쿼리 (예: "is:unread", "from:example@gmail.com")'
    )

    parser.add_argument(
        '--output',
        '-o',
        default='output',
        help='결과 출력 디렉토리 (기본값: output)'
    )

    parser.add_argument(
        '--no-visualize',
        action='store_true',
        help='시각화 차트 생성하지 않음'
    )

    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='CSV 파일 저장하지 않음'
    )

    parser.add_argument(
        '--credentials',
        '-c',
        default='credentials.json',
        help='OAuth 2.0 클라이언트 ID 파일 경로 (기본값: credentials.json)'
    )

    parser.add_argument(
        '--list-labels',
        action='store_true',
        help='Gmail 라벨 목록만 출력하고 종료'
    )

    args = parser.parse_args()

    # 환경 변수 로드
    load_dotenv()

    # 환경 변수에서 설정 읽기 (CLI 인자가 우선)
    if not args.credentials:
        args.credentials = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')

    if not args.max:
        args.max = int(os.getenv('MAX_EMAILS', 100))

    try:
        # Gmail API 클라이언트 초기화
        print("Gmail API 연결 중...")
        classifier = GmailClassifier(credentials_file=args.credentials)

        # 라벨 목록만 출력하는 경우
        if args.list_labels:
            labels = classifier.get_labels()
            print("\n" + "=" * 80)
            print("Gmail 라벨 목록")
            print("=" * 80)
            print(f"\n총 {len(labels)}개의 라벨:")
            for label in labels:
                label_type = label['type']
                print(f"  - {label['name']} ({label_type})")
            return

        # 이메일 가져오기
        print(f"\nGmail에서 최대 {args.max}개의 이메일을 가져오는 중...")
        if args.query:
            print(f"검색 쿼리: {args.query}")

        emails = classifier.get_emails(max_results=args.max, query=args.query)

        if not emails:
            print("\n가져온 이메일이 없습니다.")
            return

        # 이메일 분류
        print("\n이메일 분류 중...")
        classified_emails = classifier.classify_emails(emails)

        print(f"\n분류 완료! {len(classified_emails)}개의 이메일을 분석했습니다.")

        # 통계 분석
        print("\n통계 분석 중...")
        analyzer = EmailStatisticsAnalyzer(classified_emails)

        # 통계 요약 출력
        analyzer.print_summary()

        # CSV 저장
        if not args.no_csv:
            analyzer.save_to_csv(args.output)

        # 시각화
        if not args.no_visualize:
            print("\n시각화 생성 중...")
            analyzer.plot_visualizations(args.output)

        print("\n" + "=" * 80)
        print("완료!")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"\n오류: {e}", file=sys.stderr)
        print("\n설정 방법:", file=sys.stderr)
        print("1. Google Cloud Console에서 프로젝트 생성", file=sys.stderr)
        print("2. Gmail API 활성화", file=sys.stderr)
        print("3. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)", file=sys.stderr)
        print("4. credentials.json 파일 다운로드", file=sys.stderr)
        print("5. 이 파일을 프로젝트 디렉토리에 저장", file=sys.stderr)
        print("\n자세한 내용: https://developers.google.com/gmail/api/quickstart/python")
        sys.exit(1)
    except Exception as e:
        print(f"\n예기치 않은 오류: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
