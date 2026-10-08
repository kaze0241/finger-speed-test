import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="손가락 스피드 테스트", layout="wide", initial_sidebar_state="collapsed")

# HTML 파일 읽기
html_file_path = "speed_apm_test.html"

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # HTML을 Streamlit에 임베드
    components.html(html_content, height=1200, scrolling=True)

except FileNotFoundError:
    st.error(f"❌ {html_file_path} 파일을 찾을 수 없습니다. 같은 디렉토리에 있는지 확인하세요.")
