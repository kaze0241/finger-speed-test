import streamlit as st
import json
import os
from datetime import datetime
import random
import time

st.set_page_config(page_title="손가락 스피드 테스트", layout="centered", initial_sidebar_state="collapsed")

SCORES_FILE = 'scores.json'

def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_scores(scores):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

def get_rankings():
    scores = load_scores()
    ranked = sorted(scores, key=lambda x: x['apm'], reverse=True)
    return ranked

st.title("⚡ 손가락 스피드 테스트")
st.markdown("### 1부터 50까지 빠르게 순서대로 클릭하세요!")

if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'numbers': [],
        'current': 1,
        'clicked': set(),
        'start_time': None,
        'elapsed': 0
    }

# 게임 시작 버튼
if not st.session_state.game_started:
    st.markdown("""
    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
    <strong>🎮 게임 규칙</strong><br>
    ✓ 1번부터 50번까지 차례대로 클릭하세요<br>
    ✓ 숫자들은 각 테스트마다 다른 위치에 배치됩니다<br>
    ✓ 시간을 기준으로 APM(손가락 속도)을 계산합니다<br>
    ✓ 결과는 익명으로 저장되며 랭킹에 올라갑니다
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 게임 시작", use_container_width=True):
            st.session_state.game_started = True
            st.session_state.game_state['numbers'] = list(range(1, 51))
            random.shuffle(st.session_state.game_state['numbers'])
            st.session_state.game_state['start_time'] = time.time()
            st.rerun()

else:
    # 게임 진행 중
    col1, col2 = st.columns(2)

    with col1:
        elapsed = time.time() - st.session_state.game_state['start_time']
        st.session_state.game_state['elapsed'] = elapsed
        st.metric("⏱️ 시간", f"{elapsed:.1f}초")

    with col2:
        st.metric("🎯 진행", f"{len(st.session_state.game_state['clicked'])}/50")

    st.markdown(f"### 다음: **{st.session_state.game_state['current']}**")

    # 숫자 그리드
    cols_per_row = 10
    game_numbers = st.session_state.game_state['numbers']
    clicked = st.session_state.game_state['clicked']

    for row in range(5):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            idx = row * cols_per_row + col_idx
            num = game_numbers[idx]

            with cols[col_idx]:
                if num in clicked:
                    st.button(f"✓ {num}", disabled=True, key=f"btn_{num}")
                elif num == st.session_state.game_state['current']:
                    if st.button(f"🎯 {num}", key=f"btn_{num}", use_container_width=True):
                        clicked.add(num)
                        st.session_state.game_state['current'] += 1
                        if st.session_state.game_state['current'] > 50:
                            st.session_state.game_ended = True
                            st.rerun()
                        st.rerun()
                else:
                    st.button(f"{num}", disabled=True, key=f"btn_{num}")

# 게임 종료 처리
if 'game_ended' in st.session_state and st.session_state.game_ended:
    time_taken = st.session_state.game_state['elapsed']
    apm = (50 / time_taken) * 60

    # 점수 저장
    scores = load_scores()
    score_entry = {
        'apm': round(apm, 2),
        'time': round(time_taken, 2),
        'timestamp': datetime.now().isoformat()
    }
    scores.append(score_entry)
    save_scores(scores)

    ranked = get_rankings()
    current_rank = next((i+1 for i, s in enumerate(ranked) if s == score_entry), 1)

    st.session_state.game_started = False
    st.session_state.game_ended = False

    st.success("✨ 게임 완료!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚀 APM", f"{round(apm)}")
    with col2:
        st.metric("⏱️ 시간", f"{time_taken:.2f}초")
    with col3:
        st.metric("🏆 순위", f"#{current_rank}/{len(scores)}")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("다시 하기", use_container_width=True):
            st.rerun()

# 랭킹 표시
st.markdown("---")
st.markdown("### 🏆 TOP 10 랭킹")

rankings = get_rankings()
if rankings:
    for idx, item in enumerate(rankings[:10]):
        medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx+1}"
        timestamp = datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        st.write(f"{medal} **{item['apm']:.0f} APM** | {item['time']:.2f}초 | {timestamp}")
else:
    st.info("아직 기록이 없습니다. 첫 도전자가 되세요! 🎮")
