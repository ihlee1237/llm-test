"""
이메일 분류 결과에 대한 통계 계산 및 시각화 모듈
"""
from typing import List, Dict, Any
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os

# 한글 폰트 설정 (한글 깨짐 방지)
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False


class EmailStatisticsAnalyzer:
    """이메일 분류 통계 분석기"""

    def __init__(self, classified_emails: List[Dict[str, Any]]):
        """
        Args:
            classified_emails: gmail_classifier.py의 classify_emails 결과
        """
        self.emails = classified_emails
        self.df = self._create_dataframe()

    def _create_dataframe(self) -> pd.DataFrame:
        """이메일 데이터를 DataFrame으로 변환"""
        data = []

        for email in self.emails:
            # 사용자 라벨이 있으면 각 라벨별로 행 생성, 없으면 하나의 행
            if email['user_labels']:
                for label in email['user_labels']:
                    data.append({
                        'id': email['id'],
                        'subject': email['subject'][:50] + '...' if len(email['subject']) > 50 else email['subject'],
                        'from': email['from'],
                        'date': email['date'],
                        'label': label,
                        'label_type': 'user',
                        'is_inbox': email['is_inbox'],
                        'is_unread': email['is_unread'],
                        'is_important': email['is_important'],
                        'is_starred': email['is_starred']
                    })
            else:
                # 사용자 라벨이 없으면 시스템 라벨 사용
                primary_label = 'INBOX' if email['is_inbox'] else 'OTHER'
                data.append({
                    'id': email['id'],
                    'subject': email['subject'][:50] + '...' if len(email['subject']) > 50 else email['subject'],
                    'from': email['from'],
                    'date': email['date'],
                    'label': primary_label,
                    'label_type': 'system',
                    'is_inbox': email['is_inbox'],
                    'is_unread': email['is_unread'],
                    'is_important': email['is_important'],
                    'is_starred': email['is_starred']
                })

        return pd.DataFrame(data)

    def get_label_statistics(self) -> pd.DataFrame:
        """라벨별 통계"""
        if self.df.empty:
            return pd.DataFrame()

        stats = self.df.groupby('label').agg({
            'id': 'count',
            'is_unread': 'sum',
            'is_important': 'sum',
            'is_starred': 'sum'
        })

        stats.columns = ['총_이메일수', '읽지않음', '중요', '별표']
        stats['읽음_비율(%)'] = ((stats['총_이메일수'] - stats['읽지않음']) / stats['총_이메일수'] * 100).round(2)

        return stats.sort_values('총_이메일수', ascending=False)

    def get_domain_statistics(self) -> pd.DataFrame:
        """발신자 도메인별 통계"""
        if self.df.empty:
            return pd.DataFrame()

        # 이메일 주소에서 도메인 추출
        import re
        domains = []
        for from_email in self.df['from']:
            match = re.search(r'@([\w.-]+)', from_email)
            if match:
                domains.append(match.group(1))
            else:
                domains.append('Unknown')

        self.df['domain'] = domains

        domain_stats = self.df.groupby('domain').agg({
            'id': 'count',
            'is_unread': 'sum'
        })

        domain_stats.columns = ['이메일수', '읽지않음']
        domain_stats = domain_stats.sort_values('이메일수', ascending=False)

        return domain_stats.head(20)  # 상위 20개 도메인

    def get_status_statistics(self) -> Dict[str, Any]:
        """이메일 상태 통계"""
        if self.df.empty:
            return {}

        total = len(self.emails)  # 중복 제거를 위해 원본 이메일 리스트 사용

        return {
            '총_이메일수': total,
            '받은편지함': sum(1 for e in self.emails if e['is_inbox']),
            '읽지않음': sum(1 for e in self.emails if e['is_unread']),
            '중요': sum(1 for e in self.emails if e['is_important']),
            '별표': sum(1 for e in self.emails if e['is_starred']),
            '읽지않음_비율(%)': round(sum(1 for e in self.emails if e['is_unread']) / total * 100, 2) if total > 0 else 0,
            '사용자_라벨_있음': sum(1 for e in self.emails if e['user_labels']),
        }

    def get_top_labels(self, n: int = 10) -> pd.DataFrame:
        """상위 N개 라벨"""
        if self.df.empty:
            return pd.DataFrame()

        label_counts = self.df['label'].value_counts().head(n)
        return pd.DataFrame({
            '라벨': label_counts.index,
            '이메일수': label_counts.values
        })

    def print_summary(self):
        """통계 요약 출력"""
        print("\n" + "=" * 80)
        print("Gmail 이메일 분류 통계")
        print("=" * 80)

        # 상태 통계
        status_stats = self.get_status_statistics()
        print("\n" + "-" * 80)
        print("이메일 상태 요약:")
        print("-" * 80)
        for key, value in status_stats.items():
            print(f"{key}: {value}")

        # 라벨별 통계
        print("\n" + "-" * 80)
        print("라벨별 통계:")
        print("-" * 80)
        label_stats = self.get_label_statistics()
        if not label_stats.empty:
            print(label_stats.to_string())
        else:
            print("라벨 정보 없음")

        # 상위 라벨
        print("\n" + "-" * 80)
        print("상위 10개 라벨:")
        print("-" * 80)
        top_labels = self.get_top_labels()
        if not top_labels.empty:
            print(top_labels.to_string(index=False))
        else:
            print("라벨 정보 없음")

        # 도메인별 통계
        print("\n" + "-" * 80)
        print("상위 20개 발신자 도메인:")
        print("-" * 80)
        domain_stats = self.get_domain_statistics()
        if not domain_stats.empty:
            print(domain_stats.to_string())
        else:
            print("도메인 정보 없음")

    def save_to_csv(self, output_dir: str = "output"):
        """결과를 CSV 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)

        # 전체 이메일 리스트
        self.df.to_csv(f"{output_dir}/emails_list.csv", index=False, encoding='utf-8-sig')

        # 라벨 통계
        label_stats = self.get_label_statistics()
        if not label_stats.empty:
            label_stats.to_csv(f"{output_dir}/label_statistics.csv", encoding='utf-8-sig')

        # 도메인 통계
        domain_stats = self.get_domain_statistics()
        if not domain_stats.empty:
            domain_stats.to_csv(f"{output_dir}/domain_statistics.csv", encoding='utf-8-sig')

        print(f"\nCSV 파일이 '{output_dir}' 폴더에 저장되었습니다:")
        print(f"  - emails_list.csv")
        print(f"  - label_statistics.csv")
        print(f"  - domain_statistics.csv")

    def plot_visualizations(self, output_dir: str = "output"):
        """시각화 차트 생성"""
        os.makedirs(output_dir, exist_ok=True)

        # 1. 라벨별 이메일 수 (상위 10개)
        if not self.df.empty:
            plt.figure(figsize=(12, 6))
            top_labels = self.get_top_labels(15)
            plt.bar(range(len(top_labels)), top_labels['이메일수'])
            plt.xlabel('Label')
            plt.ylabel('Email Count')
            plt.title('Top 15 Labels by Email Count')
            plt.xticks(range(len(top_labels)), top_labels['라벨'], rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/label_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 2. 읽음/읽지않음 비율
        status_stats = self.get_status_statistics()
        if status_stats:
            plt.figure(figsize=(8, 8))
            read = status_stats['총_이메일수'] - status_stats['읽지않음']
            unread = status_stats['읽지않음']
            plt.pie([read, unread], labels=['Read', 'Unread'], autopct='%1.1f%%', startangle=90)
            plt.title('Read vs Unread Emails')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/read_status.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 3. 도메인별 이메일 수 (상위 15개)
        domain_stats = self.get_domain_statistics()
        if not domain_stats.empty:
            plt.figure(figsize=(12, 6))
            top_domains = domain_stats.head(15)
            plt.barh(range(len(top_domains)), top_domains['이메일수'])
            plt.ylabel('Domain')
            plt.xlabel('Email Count')
            plt.title('Top 15 Sender Domains')
            plt.yticks(range(len(top_domains)), top_domains.index)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/domain_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 4. 이메일 상태 요약 (중요, 별표 등)
        if status_stats:
            plt.figure(figsize=(10, 6))
            categories = ['Inbox', 'Unread', 'Important', 'Starred']
            values = [
                status_stats['받은편지함'],
                status_stats['읽지않음'],
                status_stats['중요'],
                status_stats['별표']
            ]
            colors = ['#4285f4', '#ea4335', '#fbbc04', '#34a853']
            plt.bar(categories, values, color=colors)
            plt.ylabel('Count')
            plt.title('Email Status Summary')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/status_summary.png", dpi=300, bbox_inches='tight')
            plt.close()

        print(f"\n시각화 차트가 '{output_dir}' 폴더에 저장되었습니다:")
        print(f"  - label_distribution.png")
        print(f"  - read_status.png")
        print(f"  - domain_distribution.png")
        print(f"  - status_summary.png")
