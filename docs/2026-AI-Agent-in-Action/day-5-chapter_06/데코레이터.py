#데코레이터(Decorator): "재시도 및 제한"
#자바의 Spring Retry나 Resilience4j 라이브러리와 같은 역할. 기존 노드를 감싸서 "실패해도 3번은 다시 해봐"라고 명령

import py_trees

# [노드 정의] 가끔 실패하는 불안정한 네트워크 노드
class UnstableNetworkNode(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.attempts = 0

    def update(self):
        self.attempts += 1
        if self.attempts < 3:
            print(f"[Task] 연결 시도 {self.attempts}회: 실패...")
            return py_trees.common.Status.FAILURE
        else:
            print(f"[Task] 연결 시도 {self.attempts}회: 드디어 성공!")
            return py_trees.common.Status.SUCCESS

# [데코레이터 적용] 로직 수정 없이 'Retry' 기능만 덧씌움
network_task = UnstableNetworkNode("Connect to Server")

# 자바의 프록시 패턴처럼 원본 노드를 감쌉니다.
retry_decorator = py_trees.decorators.Retry(
    name="Retry Decorator (Max 5)",
    child=network_task,
    num_attempts=5
)

print("--- 데코레이터(Retry) 테스트 시작 ---")
# 성공할 때까지 계속 Tick (데코레이터가 실패를 가로채서 다시 시도하게 함)
for _ in range(3):
    retry_decorator.tick_once()