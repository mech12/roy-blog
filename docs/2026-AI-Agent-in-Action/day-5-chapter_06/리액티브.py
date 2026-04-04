#리액티브(Reactive): "우선순위 가로채기"
#자바의 Interrupt 혹은 Event Priority 개념입니다. 
# 평소엔 일을 하다가 상단 노드에 긴급 신호가 오면 하던 일을 즉시 멈추고 갈아탑니다.

import py_trees

# 1. 긴급 모니터링 노드 (리액티브 체크)
class EmergencyMonitor(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="fire_alarm", access=py_trees.common.Access.READ)

    def update(self):
        if getattr(self.blackboard, "fire_alarm", False):
            print("🚨 [Reactive] 화재 감지! 모든 업무를 중단하고 대피합니다!")
            return py_trees.common.Status.SUCCESS # 우선순위가 높으므로 여기서 트리 종료
        return py_trees.common.Status.FAILURE # 화재 없으면 다음 우선순위로 양보

# [트리 구성] Selector의 memory=False 설정이 리액티브의 핵심!
root = py_trees.composites.Selector(name="Reactive Root", memory=False)

monitor = EmergencyMonitor("Fire Sensor")
work = py_trees.behaviours.Running("Working Hard...") # 평상시 업무

root.add_children([monitor, work])

# 테스트 세팅
bb = py_trees.blackboard.Client(name="Admin")
bb.register_key(key="fire_alarm", access=py_trees.common.Access.WRITE)

print("--- 리액티브 테스트 (평상시) ---")
root.tick_once()

print("\n--- 리액티브 테스트 (긴급 상황 발생) ---")
bb.fire_alarm = True # 블랙보드 상태 변경
root.tick_once()