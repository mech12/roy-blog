import py_trees
import time
import random

# ---------------------------------------------------------
# 1. 행동(Action) 및 조건(Condition) 노드 정의
# ---------------------------------------------------------

class CheckTemperature(py_trees.behaviour.Behaviour):
    """현재 온도를 체크하는 노드"""
    #객체 생성시 이름과 한계점을 입력할 수 있다
    def __init__(self, name, threshold=80):
        super(CheckTemperature, self).__init__(name)
        self.threshold = threshold

    def update(self):
        # 실습을 위해 20도 ~ 100도 사이의 랜덤 온도 생성
        current_temp = random.randint(20, 100)
        print(f"\n[Sensor] 현재 온도: {current_temp}도 (기준: {self.threshold}도)")
        
        if current_temp > self.threshold:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class ControlDevice(py_trees.behaviour.Behaviour):
    """장치(팬, 알람 등)를 제어하는 액션 노드"""
    def __init__(self, name, action_text):
        super(ControlDevice, self).__init__(name)
        self.action_text = action_text

    def update(self):
        print(f"⚙️  [Action] {self.action_text}")
        return py_trees.common.Status.SUCCESS

# ---------------------------------------------------------
# 2. 행동 트리(Behavior Tree) 구조 설계
# ---------------------------------------------------------

def create_factory_tree():
    # 루트 노드: Selector (우선순위 결정)
    # 1순위(응급)가 실패해야 2순위(정상)를 확인합니다.
    root = py_trees.composites.Selector(name="Smart Factory Control", memory=False)

    # [1순위] 응급 대응 시퀀스 (온도 > 80일 때)
    emergency_seq = py_trees.composites.Sequence(name="Emergency Response", memory=False)
    emergency_seq.add_children([
        CheckTemperature(name="High Temp Check", threshold=80),
        ControlDevice(name="Sound Alarm", action_text="🚨 사이렌 작동 및 관리자 호출!")
    ])

    # [2순위] 정상 운영 시퀀스 (온도 <= 80이고, 온도 > 30일 때)
    # Selector의 특징상 1순위가 FAILURE(80도 이하)여야 이쪽으로 넘어옵니다.
    normal_seq = py_trees.composites.Sequence(name="Normal Operation", memory=False)
    normal_seq.add_children([
        CheckTemperature(name="Low Temp Check", threshold=30),
        ControlDevice(name="Turn Off Fan", action_text="❄️ 온도가 낮습니다. 냉각 팬 가동 중지.")
    ])

    # 트리 조립
    root.add_children([emergency_seq, normal_seq])
    return root

# ---------------------------------------------------------
# 3. 메인 실행 루프 (Tick)
# ---------------------------------------------------------

if __name__ == "__main__":
    factory_tree = create_factory_tree()
    
    print("--- 스마트 팩토리 행동 트리 시뮬레이션을 시작합니다 (5회 실행) ---")
    
    for i in range(5):
        print(f"\n# Tick {i+1}")
        factory_tree.tick_once()
        
        # 트리의 상태를 시각적으로 출력
        print("\n[Tree Status]")
        print(py_trees.display.unicode_tree(factory_tree, show_status=True))
        
        time.sleep(2) # 다음 판단까지 2초 대기