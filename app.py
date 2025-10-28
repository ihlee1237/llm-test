#!/usr/bin/env python3
"""
Gmail 이메일 분류 및 통계 웹 애플리케이션
"""
import os
import json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

from web_gmail_classifier import WebGmailClassifier
from email_statistics import EmailStatisticsAnalyzer

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # 개발 환경에서는 False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# OAuth 설정
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/gmail.readonly'
    }
)


@app.route('/')
def index():
    """홈페이지"""
    user = session.get('user')
    return render_template('index.html', user=user)


@app.route('/login')
def login():
    """Google OAuth 로그인 시작"""
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    """Google OAuth 콜백"""
    try:
        token = google.authorize_access_token()

        # 사용자 정보 저장
        user_info = token.get('userinfo')
        if user_info:
            session['user'] = {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }

        # OAuth 토큰 저장
        session['oauth_token'] = {
            'token': token.get('access_token'),
            'refresh_token': token.get('refresh_token'),
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'scopes': token.get('scope', '').split()
        }

        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"인증 오류: {e}")
        return f"인증 오류가 발생했습니다: {str(e)}", 400


@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session.get('user')
    return render_template('dashboard.html', user=user)


@app.route('/api/analyze')
def analyze():
    """이메일 분석 API"""
    if 'oauth_token' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        # OAuth 토큰에서 Credentials 생성
        token_info = session['oauth_token']
        credentials = Credentials(
            token=token_info['token'],
            refresh_token=token_info.get('refresh_token'),
            token_uri=token_info['token_uri'],
            client_id=token_info['client_id'],
            client_secret=token_info['client_secret'],
            scopes=token_info['scopes']
        )

        # 파라미터 가져오기
        max_emails = request.args.get('max', default=100, type=int)
        query = request.args.get('query', default='', type=str)

        # Gmail 이메일 가져오기
        classifier = WebGmailClassifier(credentials)
        emails = classifier.get_emails(max_results=max_emails, query=query)

        if not emails:
            return jsonify({
                'error': '이메일을 가져올 수 없습니다.',
                'total_emails': 0
            })

        # 이메일 분류
        classified_emails = classifier.classify_emails(emails)

        # 통계 분석
        analyzer = EmailStatisticsAnalyzer(classified_emails)

        # 통계 데이터 생성
        status_stats = analyzer.get_status_statistics()
        label_stats = analyzer.get_label_statistics()
        domain_stats = analyzer.get_domain_statistics()
        top_labels = analyzer.get_top_labels(10)

        # 라벨 통계를 딕셔너리로 변환
        label_stats_dict = label_stats.to_dict('index') if not label_stats.empty else {}
        domain_stats_dict = domain_stats.to_dict('index') if not domain_stats.empty else {}
        top_labels_dict = top_labels.to_dict('records') if not top_labels.empty else []

        return jsonify({
            'success': True,
            'total_emails': len(emails),
            'status_stats': status_stats,
            'label_stats': label_stats_dict,
            'domain_stats': domain_stats_dict,
            'top_labels': top_labels_dict,
            'classified_emails_count': len(classified_emails)
        })

    except Exception as e:
        print(f"분석 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'분석 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/labels')
def get_labels():
    """사용자의 Gmail 라벨 목록 API"""
    if 'oauth_token' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        # OAuth 토큰에서 Credentials 생성
        token_info = session['oauth_token']
        credentials = Credentials(
            token=token_info['token'],
            refresh_token=token_info.get('refresh_token'),
            token_uri=token_info['token_uri'],
            client_id=token_info['client_id'],
            client_secret=token_info['client_secret'],
            scopes=token_info['scopes']
        )

        classifier = WebGmailClassifier(credentials)
        labels = classifier.get_labels()

        return jsonify({
            'success': True,
            'labels': labels
        })

    except Exception as e:
        print(f"라벨 가져오기 오류: {e}")
        return jsonify({'error': f'라벨을 가져올 수 없습니다: {str(e)}'}), 500


if __name__ == '__main__':
    # 템플릿 폴더 확인
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # 정적 파일 폴더 확인
    if not os.path.exists('static'):
        os.makedirs('static')

    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("\n" + "=" * 80)
    print("Gmail 이메일 분류 및 통계 웹 애플리케이션")
    print("=" * 80)
    print(f"\n서버 시작: http://localhost:{port}")
    print("\n주의: Google OAuth 설정이 필요합니다.")
    print("1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성 (웹 애플리케이션)")
    print(f"2. 승인된 리디렉션 URI에 http://localhost:{port}/authorize 추가")
    print("3. .env 파일에 GOOGLE_CLIENT_ID와 GOOGLE_CLIENT_SECRET 설정")
    print("=" * 80 + "\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
