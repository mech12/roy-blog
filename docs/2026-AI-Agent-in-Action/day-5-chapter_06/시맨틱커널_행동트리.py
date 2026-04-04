import py_trees
import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# 1. 환경변수 설정 (실제 키가 없어도 로직 테스트는 가능하도록 함)
api_key = os.getenv("OPENAI_API_KEY", "dummy_key")

async def create_agent_kernel():
    kernel = Kernel()
    # 실제 API 호출이 일어나지 않더라도 구조상 필요함
    kernel.add_service(OpenAIChatCompletion(
        service_id="agent_brain", 
        ai_model_id="gpt-4o", 
        api_key=api_key
    ))
    return kernel

# 2. 분석 노드: 'is_urgent'에 대한 쓰기 권한 확보
class AnalyzeEmailNode(py_trees.behaviour.Behaviour):
    def __init__(self, name, kernel):
        super().__init__(name)
        self.kernel = kernel
        # [핵심 수정] 클라이언트를 만들 때 쓸(write) 키를 리스트로 명시합니다.
        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="is_urgent", access=py_trees.common.Access.WRITE)

    def update(self):
        print(f"\n[BT] '{self.name}' 실행: 데이터 분석 시작")
        
        # 분석 결과 시뮬레이션
        result = "URGENT"
        
        if result == "URGENT":
            # 이제 등록된 키에 안전하게 접근 가능합니다.
            self.blackboard.is_urgent = True
            print(f"[Blackboard] 'is_urgent'를 {self.blackboard.is_urgent}(으)로 기록함.")
            return py_trees.common.Status.SUCCESS
        else:
            self.blackboard.is_urgent = False
            return py_trees.common.Status.FAILURE

# 3. 실행 노드: 'is_urgent'에 대한 읽기 권한 확보
class DraftReplyNode(py_trees.behaviour.Behaviour):
    def __init__(self, name, kernel):
        super().__init__(name)
        self.kernel = kernel
        # [핵심 수정] 클라이언트를 만들 때 읽을(read) 키를 리스트로 명시합니다.
        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="is_urgent", access=py_trees.common.Access.READ)

    def update(self):
        print(f"[BT] '{self.name}' 실행: 게시판 확인 중...")
        
        # 블랙보드 데이터 확인 (반드시 존재 여부를 체크하는 게 에이전트 설계의 정석입니다)
        try:
            if self.blackboard.is_urgent:
                print("[Action] 긴급 대응 초안 작성을 완료했습니다.")
                return py_trees.common.Status.SUCCESS
        except AttributeError:
            print("[Error] 블랙보드에 'is_urgent' 데이터가 없습니다.")
            return py_trees.common.Status.FAILURE
            
        return py_trees.common.Status.FAILURE

# --- 실행부 ---
async def run_agent():
    sk_kernel = await create_agent_kernel()
    
    # 트리 구성
    root = py_trees.composites.Sequence(name="Email Support Agent", memory=True)
    analyze = AnalyzeEmailNode("Analyze Email", sk_kernel)
    draft = DraftReplyNode("Draft Reply", sk_kernel)
    root.add_children([analyze, draft])
    
    print("\n--- 블랙보드 기반 에이전트 가동 ---")
    
    # 1회 작동 테스트
    root.tick_once()
    print("\n" + py_trees.display.unicode_tree(root, show_status=True))

if __name__ == "__main__":
    asyncio.run(run_agent())