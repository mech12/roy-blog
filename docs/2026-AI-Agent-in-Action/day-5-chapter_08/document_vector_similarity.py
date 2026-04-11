import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 샘플 문서 데이터 (한국어)
documents = [
    "하늘은 푸르고 아름답습니다.",
    "이 푸르고 아름다운 하늘이 좋아요!",
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "왕의 아침 식사에는 소시지, 햄, 베이컨, 계란, 토스트, 콩이 나옵니다.",
    "나는 녹색 계란과 햄, 소시지, 베이컨을 좋아해요!",
    "갈색 여우는 빠르고 파란 개는 게으릅니다!",
    "오늘 하늘은 매우 푸르고 정말 아름답네요.",
    "개는 게으르지만 갈색 여우는 정말 빠릅니다!"
]

# TF-IDF를 이용한 벡터화
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

# 코사인 유사도 계산
cosine_similarities = cosine_similarity(X)

while True:
    # 사용자로부터 비교할 문서 번호 입력 받기
    prompt = f"비교할 문서 번호(0-{len(documents)-1})를 입력하거나 종료하려면 'exit'를 입력하세요: "
    selected_document_index = input(prompt).strip()
    
    if selected_document_index.lower() == 'exit':
        print("프로그램을 종료합니다.")
        break

    if not selected_document_index.isdigit() or not 0 <= int(selected_document_index) < len(documents):
        print("잘못된 입력입니다. 올바른 문서 번호를 입력해주세요.")
        continue

    selected_document_index = int(selected_document_index)

    # 선택된 문서의 유사도 점수 추출
    selected_document_similarities = cosine_similarities[selected_document_index]

    # 시각화를 위해 긴 문장은 앞부분만 잘라서 라벨링 (50자 제한)
    x_axis_labels = [doc[:50] + "..." if len(doc) > 50 else doc for doc in documents]

    # Plotly를 이용한 막대 그래프 시각화
    fig = go.Figure([go.Bar(x=x_axis_labels, 
                            y=selected_document_similarities)])

    selected_text = documents[selected_document_index][:50]
    fig.update_layout(
        title=f"'{selected_text}...' 문서와 다른 문서들 간의 코사인 유사도",
        xaxis_title="비교 대상 문서",
        yaxis_title="코사인 유사도 점수",
        xaxis={'tickangle': 45}  # 라벨 가독성을 위해 45도 회전
    )

    fig.show()

    