from openai import OpenAI
import numpy as np
from sklearn.decomposition import PCA
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")

client = OpenAI(api_key=api_key)

def get_embedding(text, model="text-embedding-3-small"):
    # 최신 모델 사용 권장
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# 샘플 문서 (의미적 군집화를 확인하기 위한 한글 문장들)
documents = [
    "하늘은 푸르고 아름답습니다.",
    "이 푸르고 아름다운 하늘을 사랑해요!",
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
    "왕의 아침 식사에는 소시지, 햄, 베이컨, 계란, 토스트, 콩이 나옵니다.",
    "나는 녹색 계란과 햄, 소시지, 베이컨을 좋아해요!",
    "갈색 여우는 빠르고 파란 개는 게으릅니다!",
    "오늘 하늘은 매우 푸르고 정말 아름답네요.",
    "개는 게으르지만 갈색 여우는 정말 빠릅니다!"
]

# 각 문서에 대한 임베딩 생성
embeddings = [get_embedding(doc) for doc in documents]

# PCA 적용을 위해 넘파이 배열로 변환
embeddings_array = np.array(embeddings)

# 임베딩의 원래 차원 출력 (예: 1536차원)
print(f"원래 임베딩 형태: {embeddings_array.shape}")

# PCA를 사용하여 차원을 3차원으로 축소
pca = PCA(n_components=3)
reduced_embeddings = pca.fit_transform(embeddings_array)

# Plotly를 이용한 3D 산점도 생성
fig = go.Figure(data=[go.Scatter3d(
    x=reduced_embeddings[:, 0],
    y=reduced_embeddings[:, 1],
    z=reduced_embeddings[:, 2],
    mode='markers+text',
    text=documents,      # 마우스 호버 시 보여줄 텍스트
    hoverinfo='text',
    marker=dict(
        size=10,
        color=list(range(len(documents))), # 문서별 고유 색상 부여
        colorscale='Viridis',
        opacity=0.8
    )
)])

# 그래프 제목 및 축 라벨 설정
fig.update_layout(
    title="문서 임베딩의 3차원 시각화 (PCA 적용)",
    scene=dict(
        xaxis_title='주성분 1 (PCA 1)',
        yaxis_title='주성분 2 (PCA 2)',
        zaxis_title='주성분 3 (PCA 3)'
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

fig.show()