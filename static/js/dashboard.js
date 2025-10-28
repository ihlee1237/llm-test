// 차트 인스턴스 저장
let topLabelsChart = null;
let readStatusChart = null;

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 분석 버튼 클릭 이벤트
    document.getElementById('analyzeBtn').addEventListener('click', analyzeEmails);

    // 라벨 목록 버튼 클릭 이벤트
    document.getElementById('viewLabelsBtn').addEventListener('click', showLabels);

    // 모달 닫기 버튼
    document.querySelector('.close-modal').addEventListener('click', closeModal);

    // 모달 외부 클릭 시 닫기
    document.getElementById('labelsModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
});

// 이메일 분석 함수
async function analyzeEmails() {
    const maxEmails = document.getElementById('maxEmails').value;
    const query = document.getElementById('emailQuery').value;

    // UI 업데이트
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('results').style.display = 'none';

    // API 호출
    try {
        const url = `/api/analyze?max=${maxEmails}&query=${encodeURIComponent(query)}`;
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '분석 중 오류가 발생했습니다.');
        }

        // 로딩 숨기기
        document.getElementById('loading').style.display = 'none';

        // 결과 표시
        displayResults(data);

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').textContent = error.message;
        document.getElementById('error').style.display = 'block';
        console.error('분석 오류:', error);
    }
}

// 결과 표시 함수
function displayResults(data) {
    // 상태 통계 업데이트
    const stats = data.status_stats;
    document.getElementById('totalEmails').textContent = stats['총_이메일수'];
    document.getElementById('inboxEmails').textContent = stats['받은편지함'];
    document.getElementById('unreadEmails').textContent = stats['읽지않음'];
    document.getElementById('importantEmails').textContent = stats['중요'];
    document.getElementById('starredEmails').textContent = stats['별표'];

    // 라벨 통계 테이블
    displayLabelStats(data.label_stats);

    // 상위 라벨 차트
    displayTopLabelsChart(data.top_labels);

    // 도메인 통계 테이블
    displayDomainStats(data.domain_stats);

    // 읽음 상태 차트
    displayReadStatusChart(stats);

    // 결과 섹션 표시
    document.getElementById('results').style.display = 'block';
}

// 라벨 통계 테이블 표시
function displayLabelStats(labelStats) {
    const tbody = document.getElementById('labelStatsBody');
    tbody.innerHTML = '';

    if (!labelStats || Object.keys(labelStats).length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">라벨 데이터가 없습니다.</td></tr>';
        return;
    }

    // 객체를 배열로 변환하고 정렬
    const sortedLabels = Object.entries(labelStats).sort((a, b) => {
        return b[1]['총_이메일수'] - a[1]['총_이메일수'];
    });

    sortedLabels.forEach(([label, stats]) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${label}</strong></td>
            <td>${stats['총_이메일수']}</td>
            <td>${stats['읽지않음']}</td>
            <td>${stats['중요']}</td>
            <td>${stats['별표']}</td>
            <td>${stats['읽음_비율(%)'].toFixed(2)}%</td>
        `;
        tbody.appendChild(row);
    });
}

// 도메인 통계 테이블 표시
function displayDomainStats(domainStats) {
    const tbody = document.getElementById('domainStatsBody');
    tbody.innerHTML = '';

    if (!domainStats || Object.keys(domainStats).length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">도메인 데이터가 없습니다.</td></tr>';
        return;
    }

    // 객체를 배열로 변환하고 정렬
    const sortedDomains = Object.entries(domainStats).sort((a, b) => {
        return b[1]['이메일수'] - a[1]['이메일수'];
    });

    sortedDomains.slice(0, 20).forEach(([domain, stats]) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${domain}</strong></td>
            <td>${stats['이메일수']}</td>
            <td>${stats['읽지않음']}</td>
        `;
        tbody.appendChild(row);
    });
}

// 상위 라벨 차트 표시
function displayTopLabelsChart(topLabels) {
    const ctx = document.getElementById('topLabelsChart');

    // 기존 차트 제거
    if (topLabelsChart) {
        topLabelsChart.destroy();
    }

    if (!topLabels || topLabels.length === 0) {
        ctx.parentElement.innerHTML = '<p style="text-align: center;">라벨 데이터가 없습니다.</p>';
        return;
    }

    const labels = topLabels.map(item => item['라벨']);
    const data = topLabels.map(item => item['이메일수']);

    topLabelsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '이메일 수',
                data: data,
                backgroundColor: [
                    '#4285f4',
                    '#ea4335',
                    '#fbbc04',
                    '#34a853',
                    '#ff6d00',
                    '#46bdc6',
                    '#7baaf7',
                    '#f07b72',
                    '#fdd663',
                    '#81c995'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// 읽음 상태 차트 표시
function displayReadStatusChart(stats) {
    const ctx = document.getElementById('readStatusChart');

    // 기존 차트 제거
    if (readStatusChart) {
        readStatusChart.destroy();
    }

    const read = stats['총_이메일수'] - stats['읽지않음'];
    const unread = stats['읽지않음'];

    readStatusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['읽음', '읽지않음'],
            datasets: [{
                data: [read, unread],
                backgroundColor: [
                    '#34a853',
                    '#ea4335'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 라벨 목록 표시
async function showLabels() {
    try {
        const response = await fetch('/api/labels');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '라벨을 가져올 수 없습니다.');
        }

        const labelsList = document.getElementById('labelsList');
        labelsList.innerHTML = '';

        if (!data.labels || data.labels.length === 0) {
            labelsList.innerHTML = '<p>라벨이 없습니다.</p>';
        } else {
            // 시스템 라벨과 사용자 라벨 분리
            const systemLabels = data.labels.filter(l => l.type === 'system');
            const userLabels = data.labels.filter(l => l.type === 'user');

            if (systemLabels.length > 0) {
                labelsList.innerHTML += '<h3 style="margin-bottom: 1rem;">시스템 라벨</h3>';
                systemLabels.forEach(label => {
                    labelsList.innerHTML += `
                        <div class="label-item">
                            <span class="label-name">${label.name}</span>
                            <span class="label-type">시스템</span>
                        </div>
                    `;
                });
            }

            if (userLabels.length > 0) {
                labelsList.innerHTML += '<h3 style="margin: 2rem 0 1rem;">사용자 라벨</h3>';
                userLabels.forEach(label => {
                    labelsList.innerHTML += `
                        <div class="label-item">
                            <span class="label-name">${label.name}</span>
                            <span class="label-type">사용자</span>
                        </div>
                    `;
                });
            }
        }

        // 모달 표시
        document.getElementById('labelsModal').style.display = 'flex';

    } catch (error) {
        alert('라벨을 가져오는 중 오류가 발생했습니다: ' + error.message);
        console.error('라벨 가져오기 오류:', error);
    }
}

// 모달 닫기
function closeModal() {
    document.getElementById('labelsModal').style.display = 'none';
}
