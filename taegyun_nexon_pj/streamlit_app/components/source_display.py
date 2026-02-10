"""
Source Display Component
검색 출처 및 근거 표시
"""
import streamlit as st


def display_sources(sources: list, search_results: list):
    """
    검색 출처 및 결과 표시
    
    Args:
        sources: 사용된 데이터 소스 리스트 (["PostgreSQL", "Milvus", "Neo4j"])
        search_results: 검색 결과 상세
    """
    with st.expander("🔍 답변 근거 (Retrieval Sources)", expanded=False):
        # 데이터 소스 표시
        st.markdown("#### 📊 사용된 데이터 소스")
        cols = st.columns(len(sources) if sources else 1)
        
        for idx, source in enumerate(sources):
            with cols[idx]:
                if source == "PostgreSQL":
                    st.success(f"✅ {source}")
                elif source == "Milvus":
                    st.info(f"🔵 {source}")
                elif source == "Neo4j":
                    st.warning(f"🟡 {source}")
                else:
                    st.write(f"📁 {source}")
        
        st.divider()
        
        # 검색 결과 상세
        if search_results:
            st.markdown("#### 📝 검색된 항목")
            
            for idx, result in enumerate(search_results[:5], 1):
                data = result.get("data", {})
                score = result.get("score", 0)
                match_type = result.get("match_type", "unknown")
                
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{idx}. {data.get('canonical_name', 'Unknown')}** ({data.get('category', 'N/A')})")
                        
                        # 설명 (최대 100자)
                        description = data.get('description', '')
                        if len(description) > 100:
                            description = description[:100] + "..."
                        st.caption(description)
                    
                    with col2:
                        st.metric("점수", f"{score:.1f}", help=f"Match Type: {match_type}")
                
                if idx < len(search_results[:5]):
                    st.divider()
