MyKey = "YOUR_GEMINI_API_KEY"
#conda install google-cloud-storage

from google.cloud import storage

def list_gcs_images_in_prefix(bucket_name, prefix):
    """
    주어진 GCS 버킷 및 프리픽스(경로) 내의 모든 파일 목록을 가져옵니다.
    """
    print(f"--- GCS 버킷 '{bucket_name}' 검색 시작 ---")

    # Storage 클라이언트 초기화
    # (일반적으로 환경 변수 GOOGLE_APPLICATION_CREDENTIALS 또는 
    #  GCP 환경 설정을 통해 자동으로 인증됩니다.)
    client = storage.Client(api_key=MyKey)
    
    # 버킷 객체 가져오기
    bucket = client.bucket(bucket_name)

    # 지정된 경로(prefix)로 시작하는 모든 Blob(파일) 목록을 가져옵니다.
    blobs = bucket.list_blobs(prefix=prefix)

    image_list = []
    
    for blob in blobs:
        # 경로 자체가 아닌 실제 파일 이름만 필터링하거나 출력
        # blob.name은 'generative-ai/image/scones.jpg'와 같은 전체 경로입니다.
        if not blob.name.endswith('/'): # 폴더 이름이 아닌 실제 파일만 필터링
            image_list.append(blob.name)

    return image_list

# 검색할 버킷 이름과 경로(프리픽스) 설정
BUCKET_NAME = "cloud-samples-data"
PREFIX = "generative-ai/image/" # 반드시 '/'로 끝나야 해당 경로 하위 파일들을 검색합니다.

try:
    image_files = list_gcs_images_in_prefix(BUCKET_NAME, PREFIX)

    print(f"\n✅ '{PREFIX}' 경로에서 발견된 이미지 목록 ({len(image_files)}개):")
    for file_path in image_files:
        print(f" - {file_path.split('/')[-1]} (전체 경로: {file_path})")
    
    # 원래 URL 형식으로 이미지 URL 재생성 (예시)
    if image_files:
        sample_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{image_files[0]}"
        print(f"\n👉 첫 번째 이미지의 URL 예시: {sample_url}")

except Exception as e:
    print(f"\n❌ 오류가 발생했습니다. Google Cloud 인증 또는 API 권한을 확인하세요.")
    print(f"오류 내용: {e}")