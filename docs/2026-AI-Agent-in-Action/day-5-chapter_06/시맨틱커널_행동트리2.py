import py_trees
import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# 1. 시맨틱 커널 설정 (지능 담당)
async def get_kernel():
    kernel = Kernel()
    api_key = os.getenv("OPENAI_API_KEY", "your_key")
    kernel.add_service(OpenAIChatCompletion(service_id="boss", ai_model_id="gpt-4o", api_key=api_key))
    return kernel

# 2. 감정 분석 노드 (SK 사용)
class SentimentAnalysisNode(py_trees.behaviour.Behaviour):
    def __init__(self, name, kernel):
        super().__init__(name)
        self.kernel = kernel
        self.blackboard = py_trees.blackboard.Client(name=name)
        # 권한: 원문 읽기(READ), 감정 결과 쓰기(WRITE)
        self.blackboard.register_key(key="email_body", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="sentiment", access=py_trees.common.Access.WRITE)

    def update(self):
        print(f" [SK] '{self.name}' 가동: 감정 분석 중...")
        email = self.blackboard.email_body
        
        # SK 프롬프트 실행 (실제로는 비동기 처리가 필요하지만 테스트용으로 결과 고정)
        # "이 메일의 감정은? [ANGRY, HAPPY, NEUTRAL]"
        result = "ANGRY" 
        
        self.blackboard.sentiment = result
        print(f"📌 [Blackboard] 분석 완료: {result}")
        return py_trees.common.Status.SUCCESS

# 3. 대응 노드 (결과 확인용)
class ReplyNode(py_trees.behaviour.Behaviour):
    def __init__(self, name, target_sentiment):
        super().__init__(name)
        self.target = target_sentiment
        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="sentiment", access=py_trees.common.Access.READ)

    def update(self):
        # 블랙보드의 감정이 내가 담당하는 감정과 맞는지 확인
        if self.blackboard.sentiment == self.target:
            print(f" [Action] {self.name}: 담당 구역입니다. 답장을 작성합니다.")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

# --- 실행부 ---
async def main():
    kernel = await get_kernel()
    
    # 블랙보드 초기값 주입 (누가 보낸 이메일)
    setup = py_trees.blackboard.Client(name="Setup")
    setup.register_key(key="email_body", access=py_trees.common.Access.WRITE)
    setup.email_body = "배송이 왜 이따위야! 당장 환불해줘!"

    # 트리 구성 (Sequence 안에 Selector 넣기)
    root = py_trees.composites.Sequence(name="Main", memory=True)
    analyzer = SentimentAnalysisNode("Analyzer", kernel)
    
    # 감정에 따라 길을 나누는 Selector
    responder = py_trees.composites.Selector(name="Responder", memory=True)
    angry_handler = ReplyNode("Angry_Handler", "ANGRY")
    happy_handler = ReplyNode("Happy_Handler", "HAPPY")
    
    responder.add_children([angry_handler, happy_handler])
    root.add_children([analyzer, responder])

    print("\n---  통합 에이전트 실행 ---")
    root.tick_once()
    print("\n" + py_trees.display.unicode_tree(root, show_status=True))

if __name__ == "__main__":
    asyncio.run(main())