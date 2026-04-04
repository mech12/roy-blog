import py_trees
#실행 전 유효성 검증"
#자바의 if (apiKey != null) 같은 Pre-condition 체크입니다. 
#블랙보드에 필요한 데이터가 없으면 아예 다음 단계로 가지 못하게 막습니다.

# [노드 정의] API 키가 있는지 체크하는 가드 노드
class ApiKeyGuard(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Client(name=name)
        self.blackboard.register_key(key="api_key", access=py_trees.common.Access.READ)

    def update(self):
        # 자바의 if (apiKey == null) throw Exception; 과 같은 논리
        if hasattr(self.blackboard, "api_key") and self.blackboard.api_key:
            print("[Guard] API 키 발견! 다음 단계로 진행합니다.")
            return py_trees.common.Status.SUCCESS
        else:
            print("[Guard] API 키가 없습니다. 동작을 차단합니다.")
            return py_trees.common.Status.FAILURE

# [트리 구성] 가드가 통과해야만 실제 업무(Task)가 실행됨
guard = ApiKeyGuard("Check API Key")
task = py_trees.behaviours.Success("Actual API Call Task") # 성공을 가정하는 가짜 노드

root = py_trees.composites.Sequence(name="Guard Demo", memory=True)
root.add_children([guard, task])

# 테스트: 키가 없을 때의 결과 확인
print("--- 가드 테스트 시작 ---")
root.tick_once()