"""
Sidebar Component
API Key 입력 및 설정
"""
import streamlit as st


def render_sidebar() -> str:
    """
    사이드바 렌더링
    
    Returns:
        Groq API Key (입력된 경우)
    """
    st.sidebar.title("🔐 Security Settings")
    
    # API Key 입력
    groq_api_key = st.sidebar.text_input(
        "Groq API Key",
        type="password",
        help="키는 서버에 저장되지 않고 세션 동안만 유지됩니다.",
        placeholder="gsk_..."
    )
    
    if groq_api_key:
        st.sidebar.success("✅ API Key 입력됨")
    
    # 구분선
    st.sidebar.divider()
    
    # 고급 설정 (옵션)
    with st.sidebar.expander("⚙️ 고급 설정"):
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="낮을수록 정확하고 일관적, 높을수록 창의적"
        )
        
        st.session_state.max_results = st.slider(
            "최대 검색 결과",
            min_value=3,
            max_value=10,
            value=5,
            help="검색할 최대 항목 수"
        )
    
    # 정보
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### 📚 사용 가능한 데이터
    - 맵 (MAP): 14개
    - NPC: 9개
    - 몬스터 (MONSTER): 8개
    - 아이템 (ITEM): 3개
    
    ### 💡 예시 질문
    - "도적 전직 어디서?"
    - "스포아 어디서 잡아?"
    - "아이스진 어디서 구해?"
    """)
    
    return groq_api_key
