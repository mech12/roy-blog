import py_trees
import time
import random


# 1. 행동(Action) 정의
class CheckTemperature(py_trees.behaviour.Behaviour):
    def update(self):
        # 실제로는 센서 데이터를 읽어오지만, 여기선 랜덤/고정값 사용
        # 이부분에서 실제 작업을 진행해야 한다. 
        # 온도를 설정해서 80도 이상이면 SUCCESS  아니면 FALSE를 전달한다 
        temp = random.randint(70,90)
        print(temp)
        if temp > 80 :
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

#경고음 발생 Action 
class PlayAlarm(py_trees.behaviour.Behaviour):
    def update(self):
        print("[Action] 경고음 발생! (노래 재생 API 호출)")
        return py_trees.common.Status.SUCCESS

# 2. 트리 구성
# 1. Selector (선택 노드, 기호: ?)
# 자식들 중 하나라도 'SUCCESS'를 반환하면 즉시 멈추고 성공을 보고합니다.
# "우선순위"를 정할 때 사용합니다. (긴급 대응이 일반 가동보다 우선!)
root = py_trees.composites.Selector(name="스마트팩토리", memory=False)

# 2. Sequence (순차 노드, 기호: ->)
# 자식들이 모두 'SUCCESS'여야만 최종 성공합니다. 하나라도 실패하면 중단합니다.
# "단계별 실행"에 사용합니다. (온도 체크 성공 -> 알람 울리기 성공)
emergency_seq = py_trees.composites.Sequence(name="비상상황", memory=False)


# 응급 시나리오: [온도 체크] 하고 나서 [알람 울리기]
emergency_seq.add_children([
    CheckTemperature(name="Is Temp > 80?"), 
    PlayAlarm(name="Sound Alarm")
])

# 전체 트리: [응급 시나리오]를 먼저 시도하고, 안 되면 다른 걸 해라!
root.add_child(emergency_seq)


# 3. 실행 (Tick)
for i in range(5):
    print(f"\n--- Tick {i} ---")
    root.tick_once()  #트리에 tick(행동하라) 는 신호를 보낸다. 
    #행동 트리의 tick_once()는 루트 노드가 최종 결과(Success/Failure)를 낼 때까지만 실행
    
    # 현재 트리의 상태를 기호로 출력 (시각화)
    #print(py_trees.display.unicode_tree(root))
    time.sleep(1)