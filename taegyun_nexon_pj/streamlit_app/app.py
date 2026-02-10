"""
Maple-Agent Streamlit App
Groq API 기반 하이브리드 RAG 데모
"""
import streamlit as st
import sys
from pathlib import Path

# langchain_app 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "langchain_app"))

from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from services.maple_rag_service import MapleRAGService


def main():
    """메인 앱"""
    # 페이지 설정
    st.set_page_config(
        page_title="Nexon Maple-Agent Demo",
        page_icon="🏹",
        layout="wide"
    )
    
    # 사이드바 (API Key 입력)
    groq_api_key = render_sidebar()
    
    # 메인 타이틀
    st.title("🍁 Maple-Agent: 하이브리드 RAG 지식베이스")
    st.markdown("""
    이 데모는 **PostgreSQL, Milvus, Neo4j**를 결합하여 메이플스토리 지식을 답변하는 AI 에이전트입니다.
    
    - **PostgreSQL**: 정확한 키워드 매칭
    - **Milvus**: 의미 기반 벡터 검색
    - **Neo4j**: 그래프 관계 추론
    - **RRF**: Reciprocal Rank Fusion으로 최적 결과 융합
    """)
    
    # RAG 서비스 초기화
    if groq_api_key:
        if "rag_service" not in st.session_state:
            with st.spinner("🔄 RAG 엔진 초기화 중..."):
                try:
                    st.session_state.rag_service = MapleRAGService(
                        groq_api_key=groq_api_key
                    )
                    st.success("✅ RAG 엔진 준비 완료!")
                except Exception as e:
                    st.error(f"❌ 초기화 실패: {e}")
                    st.stop()
        
        # 채팅 인터페이스
        render_chat_interface(st.session_state.rag_service)
    else:
        st.info("👈 사이드바에서 Groq API Key를 입력해주세요.")
        st.markdown("""
        ### 시작하기
        1. [Groq Console](https://console.groq.com/)에서 API Key 발급
        2. 왼쪽 사이드바에 API Key 입력
        3. 질문 입력 (예: "도적 전직 어디서?")
        """)


if __name__ == "__main__":
    main()
