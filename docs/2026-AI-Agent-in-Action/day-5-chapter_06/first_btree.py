import py_trees


# 컨디션 노드  py_trees.behaviour.Behaviour 를 상속받아야 한다 
# 추상 클래스를 상속받아 직접 정의하는 실행 단위
#현재 상태를 체크하여 SUCCESS 또는 FAILURE를 반환합니다.
class HasApple(py_trees.behaviour.Behaviour):
    def __init__(self, name): #생성자
        super(HasApple, self).__init__(name)

    def update(self):
        # 1. 실제 로직 수행 (API 호출, 조건 체크 등)
        #success_condition = self.do_something()
        # Condition check (placeholder for actual logic)
        if True:  # Replace with actual condition  #무조건 TRUE만 반환 몇번을 반복해도 사과만 먹고 끝난다
            return py_trees.common.Status.SUCCESS  #FAILURE 를 반환하면 배만 먹는다 
        else:
            return py_trees.common.Status.FAILURE

#행동노드
class EatApple(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(EatApple, self).__init__(name)

    def update(self):
        # Action (placeholder for actual action)
        print("Eating apple")
        return py_trees.common.Status.SUCCESS


class HasPear(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(HasPear, self).__init__(name)

    def update(self):
        # Condition check (placeholder for actual logic)
        if True:  # Replace with actual condition
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class EatPear(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(EatPear, self).__init__(name)

    def update(self):
        # Action (placeholder for actual action)
        print("Eating pear")
        return py_trees.common.Status.SUCCESS


# 노드들을 생성한다 
has_apple = HasApple(name="Has apple")
eat_apple = EatApple(name="Eat apple")
sequence_1 = py_trees.composites.Sequence(name="Sequence 1", memory=True)
sequence_1.add_children([has_apple, eat_apple]) #사과가 있으면 사과를 먹어라 

has_pear = HasPear(name="Has pear")
eat_pear = EatPear(name="Eat pear")
sequence_2 = py_trees.composites.Sequence(name="Sequence 2", memory=True)
sequence_2.add_children([has_pear, eat_pear]) # 배가 있으면 배를 먹어라 

root = py_trees.composites.Selector(name="Selector", memory=True)
root.add_children([sequence_1, sequence_2])

# 행동트리를 만든다. 두개의 Sequence 노드를 갖는다 
behavior_tree = py_trees.trees.BehaviourTree(root)

# Execute the behavior tree
py_trees.logging.level = py_trees.logging.Level.DEBUG
for i in range(1, 4):
    print("\n------------------ Tick {0} ------------------".format(i))
    behavior_tree.tick()

#Tick 1: Selector가 Sequence 1을 찌릅니다. 사과가 있다면 Eat apple이 실행되고 SUCCESS를 반환합니다. 루트인 Selector는 첫 자식이 성공했으므로 기분 좋게 종료합니다.
#Tick 2 & 3: 만약 조건(HasApple)이 FAILURE로 바뀐다면, Selector는 즉시 Sequence 2로 넘어가서 배가 있는지 확인하고 먹는 자율성을 보여줍니다.

#https://github.com/cxbxmxcx/GPTAssistantsPlayGround