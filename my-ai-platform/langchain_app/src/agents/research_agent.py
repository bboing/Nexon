"""LangGraph 연구 에이전트 - 멀티 스텝 워크플로우"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.models.llm import llm_model
from src.models.langfuse_callback import get_langfuse_handler
from src.retrievers.milvus_retriever import MilvusRetriever
import time
import logging

logger = logging.getLogger(__name__)


# 에이전트 상태 정의
class ResearchState(TypedDict):
    """연구 에이전트 상태"""
    task: str
    research_results: Annotated[list, "연구 결과"]
    analysis: Annotated[str, "분석 내용"]
    final_report: Annotated[str, "최종 리포트"]
    steps: Annotated[list, "실행 단계"]
    status: str


class ResearchAgent:
    """LangGraph 기반 연구 에이전트
    
    워크플로우:
    1. 정보 수집 (RAG 검색)
    2. 분석 (LLM)
    3. 리포트 작성 (LLM)
    4. 검토 (조건부 재작성)
    """
    
    def __init__(self):
        self.llm = llm_model.llm
        self.retriever = MilvusRetriever()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """LangGraph 워크플로우 구축"""
        workflow = StateGraph(ResearchState)
        
        # 노드 추가
        workflow.add_node("research", self._research_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("write_report", self._write_report_node)
        workflow.add_node("review", self._review_node)
        
        # 엣지 정의
        workflow.set_entry_point("research")
        workflow.add_edge("research", "analyze")
        workflow.add_edge("analyze", "write_report")
        workflow.add_edge("write_report", "review")
        
        # 조건부 엣지 (리포트 품질에 따라 재작성)
        workflow.add_conditional_edges(
            "review",
            self._should_rewrite,
            {
                "rewrite": "write_report",  # 재작성
                "finish": END  # 완료
            }
        )
        
        return workflow.compile()
    
    async def _research_node(self, state: ResearchState) -> ResearchState:
        """1단계: 정보 수집"""
        logger.info(f"[Research] 정보 수집 시작: {state['task']}")
        
        # RAG 검색
        results = await self.retriever.search(state["task"], top_k=3)
        
        state["research_results"] = results
        state["steps"].append({
            "step": "research",
            "description": "정보 수집 완료",
            "results_count": len(results)
        })
        
        return state
    
    async def _analyze_node(self, state: ResearchState) -> ResearchState:
        """2단계: 분석"""
        logger.info("[Analyze] 분석 시작")
        
        # 수집된 정보를 LLM으로 분석
        context = "\n".join([r["content"] for r in state["research_results"]])
        
        prompt = f"""다음 정보를 바탕으로 '{state['task']}'에 대한 핵심 인사이트를 분석하세요:

{context}

분석 결과:"""
        
        # Langfuse 추적
        callbacks = []
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
        
        analysis = self.llm.predict(prompt, callbacks=callbacks)
        
        state["analysis"] = analysis
        state["steps"].append({
            "step": "analyze",
            "description": "분석 완료"
        })
        
        return state
    
    async def _write_report_node(self, state: ResearchState) -> ResearchState:
        """3단계: 리포트 작성"""
        logger.info("[Write] 리포트 작성")
        
        prompt = f"""다음 분석을 바탕으로 '{state['task']}'에 대한 간결한 리포트를 작성하세요:

분석 내용:
{state['analysis']}

리포트 (300자 이내):"""
        
        # Langfuse 추적
        callbacks = []
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
        
        report = self.llm.predict(prompt, callbacks=callbacks)
        
        state["final_report"] = report
        state["steps"].append({
            "step": "write_report",
            "description": "리포트 작성 완료"
        })
        
        return state
    
    async def _review_node(self, state: ResearchState) -> ResearchState:
        """4단계: 검토"""
        logger.info("[Review] 리포트 검토")
        
        # 간단한 품질 체크 (실제로는 더 정교한 로직 필요)
        report_length = len(state["final_report"])
        
        if report_length < 50:
            state["status"] = "needs_rewrite"
            state["steps"].append({
                "step": "review",
                "description": "재작성 필요 (너무 짧음)"
            })
        else:
            state["status"] = "approved"
            state["steps"].append({
                "step": "review",
                "description": "리포트 승인"
            })
        
        return state
    
    def _should_rewrite(self, state: ResearchState) -> str:
        """재작성 여부 결정"""
        # 최대 1회 재작성만 허용 (무한 루프 방지)
        rewrite_count = sum(1 for s in state["steps"] if s["step"] == "write_report")
        
        if state["status"] == "needs_rewrite" and rewrite_count < 2:
            return "rewrite"
        return "finish"
    
    async def execute(self, task: str, session_id: str = None) -> dict:
        """에이전트 실행"""
        start_time = time.time()
        
        # 초기 상태
        initial_state: ResearchState = {
            "task": task,
            "research_results": [],
            "analysis": "",
            "final_report": "",
            "steps": [],
            "status": "running"
        }
        
        # 그래프 실행
        final_state = await self.graph.ainvoke(initial_state)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return {
            "result": final_state["final_report"],
            "steps": final_state["steps"],
            "execution_time_ms": execution_time,
            "status": "completed"
        }
