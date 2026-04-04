import py_trees

# ==========================================
#  [공통 모듈] 이메일 수집 서브트리 (잘 만든 레고 블록)
# ==========================================
def create_email_fetch_subtree():
    # 자바의 공통 메서드나 클래스처럼 독립적으로 구성합니다.
    fetch_sequence = py_trees.composites.Sequence(name="Fetch Email Subtree", memory=True)
    
    check_net = py_trees.behaviours.Success("Check Network") # 가짜 노드
    fetch_mail = py_trees.behaviours.Success("Fetch from Gmail API") # 가짜 노드
    
    fetch_sequence.add_children([check_net, fetch_mail])
    return fetch_sequence


# ==========================================
#  [에이전트 A] 개인 비서 (공통 모듈 사용)
# ==========================================
print("---  비서 에이전트 트리 구성 ---")
secretary_root = py_trees.composites.Sequence(name="Secretary Agent Root", memory=True)

# 공통 모듈 플러그인!
email_fetcher = create_email_fetch_subtree() 

summarize = py_trees.behaviours.Success("Summarize Emails")

secretary_root.add_children([email_fetcher, summarize])

# 트리 구조 출력 (서브트리가 쏙 들어간 모습 확인)
print(py_trees.display.unicode_tree(secretary_root))


# ==========================================
#  [에이전트 B] 보안 감시자 (똑같은 모듈 사용)
# ==========================================
print("\n---  보안 에이전트 트리 구성 ---")
security_root = py_trees.composites.Selector(name="Security Agent Root", memory=False)

# 똑같은 공통 모듈을 또 플러그인!
email_fetcher_2 = create_email_fetch_subtree() 

scan_virus = py_trees.behaviours.Success("Scan for Viruses")

security_root.add_children([email_fetcher_2, scan_virus])

# 트리 구조 출력
print(py_trees.display.unicode_tree(security_root))