"""
웹 애플리케이션용 Gmail API 클래스
"""
import base64
import re
from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class WebGmailClassifier:
    """웹 애플리케이션용 Gmail API 클래스 (credentials를 외부에서 받음)"""

    def __init__(self, credentials: Credentials):
        """
        Gmail API 클라이언트 초기화

        Args:
            credentials: Google OAuth2 Credentials 객체
        """
        self.credentials = credentials
        self.service = build('gmail', 'v1', credentials=credentials)

    def get_user_email(self) -> str:
        """현재 사용자의 이메일 주소 가져오기"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress', 'Unknown')
        except Exception as e:
            print(f"사용자 이메일 가져오기 오류: {e}")
            return 'Unknown'

    def get_labels(self) -> List[Dict[str, str]]:
        """
        사용자의 Gmail 라벨 목록 가져오기

        Returns:
            라벨 정보 리스트
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            return [
                {
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type', 'user')
                }
                for label in labels
            ]
        except Exception as e:
            print(f"라벨 목록 가져오기 오류: {e}")
            return []

    def _decode_message(self, message_data: Dict) -> str:
        """메시지 본문 디코딩"""
        if 'data' in message_data:
            return base64.urlsafe_b64decode(message_data['data']).decode('utf-8', errors='ignore')

        if 'parts' in message_data:
            parts_text = []
            for part in message_data['parts']:
                if part['mimeType'] == 'text/plain':
                    parts_text.append(self._decode_message(part['body']))
            return '\n'.join(parts_text)

        return ""

    def get_emails(self, max_results: int = 100, query: str = '') -> List[Dict[str, Any]]:
        """
        Gmail에서 이메일 가져오기

        Args:
            max_results: 가져올 최대 이메일 개수
            query: Gmail 검색 쿼리

        Returns:
            이메일 정보 리스트
        """
        try:
            # 메시지 목록 가져오기
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg_id = message['id']

                # 메시지 세부 정보 가져오기
                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                # 헤더에서 정보 추출
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                # 라벨 정보
                label_ids = msg.get('labelIds', [])

                # 메시지 본문
                body = self._decode_message(msg['payload'])

                # 스니펫 (간단한 미리보기)
                snippet = msg.get('snippet', '')

                emails.append({
                    'id': msg_id,
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'labels': label_ids,
                    'body': body[:1000],  # 처음 1000자만
                    'snippet': snippet
                })

            return emails

        except Exception as e:
            print(f"이메일 가져오기 오류: {e}")
            import traceback
            traceback.print_exc()
            return []

    def classify_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        이메일을 라벨 기반으로 분류

        Args:
            emails: 이메일 리스트

        Returns:
            분류된 이메일 정보 리스트
        """
        # 라벨 정보 가져오기
        labels = self.get_labels()
        label_map = {label['id']: label['name'] for label in labels}

        classified_emails = []

        for email in emails:
            # 라벨 ID를 이름으로 변환
            label_names = [label_map.get(label_id, label_id) for label_id in email['labels']]

            # 시스템 라벨과 사용자 라벨 구분
            system_labels = [
                label for label in label_names
                if label in ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH', 'UNREAD', 'STARRED', 'IMPORTANT']
            ]
            user_labels = [
                label for label in label_names
                if label not in system_labels
            ]

            classified_emails.append({
                'id': email['id'],
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date'],
                'snippet': email['snippet'],
                'body': email['body'],
                'all_labels': label_names,
                'system_labels': system_labels,
                'user_labels': user_labels,
                'is_inbox': 'INBOX' in label_names,
                'is_unread': 'UNREAD' in label_names,
                'is_important': 'IMPORTANT' in label_names,
                'is_starred': 'STARRED' in label_names
            })

        return classified_emails
