import py_trees

#전기가 있으면 -> 온도를 체크해서 -> 에어컨을 켠다
import py_trees
import random

# 1. 상태 체크 노드 (Condition)
class IsPowerOn(py_trees.behaviour.Behaviour):
    def update(self):
        # 전력이 공급되는지 확인 (여기선 무조건 True)
        print("  [체크] 전원 공급 상태 확인 중...")
        return py_trees.common.Status.SUCCESS

class IsTooHot(py_trees.behaviour.Behaviour):
    def update(self):
        # 25도 이상이면 더운 것으로 간주 (랜덤값으로 시뮬레이션)
        temp = random.randint(20, 30)
        print(f"  [체크] 현재 온도: {temp}도")
        return py_trees.common.Status.SUCCESS if temp >= 25 else py_trees.common.Status.FAILURE

# 2. 동작 노드 (Action)
class TurnOnAircon(py_trees.behaviour.Behaviour):
    def update(self):
        print("  [동작] 에어컨을 가동합니다!")
        return py_trees.common.Status.SUCCESS

class OpenWindow(py_trees.behaviour.Behaviour):
    def update(self):
        print("  [동작] 창문을 열어 환기합니다.")
        return py_trees.common.Status.SUCCESS

# --- 트리 구성 ---

# 시나리오 1: 에어컨 가동 (전기 있고 + 더우면 -> 켠다)
cool_down = py_trees.composites.Sequence(name="에어컨 모드", memory=True)
cool_down.add_children([IsPowerOn(name="전원 확인"), IsTooHot(name="온도 확인"), TurnOnAircon(name="가동")])

# 시나리오 2: 환기 (에어컨 못 켜면 차선책)
ventilation = py_trees.composites.Sequence(name="환기 모드", memory=True)
ventilation.add_children([OpenWindow(name="창문 개방")])

# 루트 설정 (Selector)
root = py_trees.composites.Selector(name="스마트홈 비서", memory=True)
root.add_children([cool_down, ventilation])

# 실행부
behavior_tree = py_trees.trees.BehaviourTree(root)
for i in range(1, 4):
    print(f"\n--- 에이전트 판단 {i}회차 ---")
    behavior_tree.tick()