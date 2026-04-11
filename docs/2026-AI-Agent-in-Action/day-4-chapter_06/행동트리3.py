#블랙보드란 에이전트들 간의 공유게시판이다.
#직접 소통 대신 '게시판'을 통한 간접 소통  에이전트 A가 게시판에 쓰고  B가 읽는다 
#칸(Key)마다 설정된 '출입 권한'
#각 에이전트(노드)는 자기가 접근할 칸(Key)과 권한(Read/Write)을 미리 허가받아야 합니다.
#단기 기억(Working Memory)의 역할
#에이전트가 "지금 무엇을 하고 있는지", "방금 분석한 결과가 무엇인지"를 보관하는 단기 메모리입니다. 
#작업이 끝나면 초기화하거나 다음 작업으로 넘겨주는 흐름 제어의 기준이 됩니다.

import py_trees
import time

# 1. 조건 확인 노드 (READ 권한)
class CheckHungryNode(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Client(name=name)
        # 'is_hungry' 칸을 읽겠다고 확실히 등록 - 키를 등록한다 
        self.blackboard.register_key(key="is_hungry", access=py_trees.common.Access.READ)

    def update(self):
        # 등록한 키 이름과 사용하는 변수명이 반드시 일치해야 합니다.
        if self.blackboard.is_hungry: 
            print(f"[BT] '{self.name}': 게시판 확인 결과, 배가 고픕니다!")
            return py_trees.common.Status.SUCCESS
        else:
            print(f"[BT] '{self.name}': 배가 안 고프네요. 통과!")
            return py_trees.common.Status.FAILURE

# 2. 행동 실행 노드 (WRITE 권한)
class EatFoodNode(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Client(name=name)
        # 'is_hungry' 칸을 쓰겠다고 확실히 등록
        self.blackboard.register_key(key="is_hungry", access=py_trees.common.Access.WRITE)

    def update(self):
        print(f"[BT] '{self.name}': 냠냠... 밥을 맛있게 먹었습니다.")
        # 행동 완료 후 상태 변경
        self.blackboard.is_hungry = False
        print("[Blackboard] 'is_hungry' 상태를 False로 변경했습니다.")
        return py_trees.common.Status.SUCCESS

# --- 실행부 ---
def run_simple_agent():
    # [1] 블랙보드 초기 세팅
    setup = py_trees.blackboard.Client(name="Setup")
    setup.register_key(key="is_hungry", access=py_trees.common.Access.WRITE)
    setup.is_hungry = True 

    # [2] 트리 구성
    #memory=True는 앞서 성공한 단계(Node)를 건너뛰고, 멈췄던 지점부터 작업을 이어가는 진행 위치 기억 장치임
    #memoy=False의 경우 무조건 처음부터 진행한다. 
    #memory가 false일 경우 무한루프가능성

    root = py_trees.composites.Sequence(name="Eat Routine", memory=True)
    check = CheckHungryNode("Check Hunger")
    eat = EatFoodNode("Eat Food")
    root.add_children([check, eat])

    # [3] 에이전트 가동
    print("에이전트 루틴 시작!")
    root.tick_once()
    
    print("\n" + py_trees.display.unicode_tree(root, show_status=True))

if __name__ == "__main__":
    run_simple_agent()