import py_trees
import time

# 1. 가끔 실패하는 불안정한 작업 노드
class FlakyTaskNode(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.count = 0

    def update(self):
        self.count += 1
        if self.count < 3:
            print(f"   [Task] 작업 중... ({self.count}/3)")
            return py_trees.common.Status.RUNNING # 진행 중
        elif self.count == 3:
            print("   [Task] 작업 성공!")
            return py_trees.common.Status.SUCCESS # 성공
        else:
            return py_trees.common.Status.FAILURE # 실패

# 2. 트리 구성
root = py_trees.composites.Sequence(name="Visual Demo Root", memory=True)
task = FlakyTaskNode("Flaky Task")
root.add_child(task)

# 3. 실시간 시각화 루프
print("--- 🎨 시각화 데모 시작 (매 초마다 상태 확인) ---")
for tick in range(1, 5):
    print(f"\n[Tick {tick}]")
    root.tick_once()
    
    # [핵심] 현재 트리의 상태를 시각적으로 출력 (색깔이 나오면 더 이쁩니다)
    print(py_trees.display.unicode_tree(root, show_status=True))
    time.sleep(1)