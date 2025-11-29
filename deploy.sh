#!/bin/bash

# Roy's Tech Blog 배포 스크립트
# 사용법: ./deploy.sh "커밋 메시지"

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 커밋 메시지 확인
if [ -z "$1" ]; then
    COMMIT_MSG="Update blog content - $(date '+%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

echo -e "${YELLOW}📝 변경사항 확인...${NC}"
git status --short

# 변경사항이 있는지 확인
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ 변경사항이 없습니다.${NC}"
    exit 0
fi

echo -e "${YELLOW}📦 변경사항 스테이징...${NC}"
git add .

echo -e "${YELLOW}💾 커밋 생성: ${COMMIT_MSG}${NC}"
git commit -m "$COMMIT_MSG"

echo -e "${YELLOW}🚀 GitHub에 푸시...${NC}"
git push origin main

echo -e "${GREEN}✅ 배포 완료!${NC}"
echo -e "${GREEN}🔗 블로그 주소: https://mech12.github.io/roy-blog/${NC}"
echo ""
echo -e "${YELLOW}📊 GitHub Actions 빌드 상태 확인:${NC}"
echo "   https://github.com/mech12/roy-blog/actions"
