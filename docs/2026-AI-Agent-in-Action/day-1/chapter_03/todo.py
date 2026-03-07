from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI(
    title="Daily Task Service",
    description="일일 업무 목록을 조회하는 API",
    version="1.0.0"
)

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    due_date: date

class DailyTaskResponse(BaseModel):
    date: date
    tasks: List[Task]

@app.get("/ping", operation_id="ping")
def ping():
    return {"ok": True}

@app.get(
    "/tasks/daily",
    response_model=DailyTaskResponse,
    tags=["Tasks"],
    summary="일일 업무 목록 조회",
    description="특정 날짜 기준의 업무 목록을 조회합니다. 날짜가 없으면 오늘 날짜 기준으로 반환합니다."
)
def get_daily_tasks(
    date_param: Optional[date] = Query(
        None,
        alias="date",
        description="조회할 날짜 (YYYY-MM-DD)"
    ),
    user_id: Optional[int] = Query(
        None,
        description="사용자 ID"
    )
):
    """
    일일 업무 목록 조회 엔드포인트

    - **date**: 조회할 날짜
    - **user_id**: 특정 사용자의 업무 조회
    """

    query_date = date_param or date.today()

    # 예시 데이터 (실제 서비스에서는 DB 조회)
    tasks = [
        Task(
            id=1,
            title="팀 스탠드업 미팅",
            description="10시 팀 미팅",
            completed=False,
            due_date=query_date
        ),
        Task(
            id=2,
            title="API 문서 작성",
            description="FastAPI OpenAPI 문서 정리",
            completed=True,
            due_date=query_date
        )
    ]

    return DailyTaskResponse(
        date=query_date,
        tasks=tasks
    )

#uvicorn todo:app --reload
#http://127.0.0.1:8000/tasks/daily
#http://localhost:8000/tasks/daily?date=2026-03-06
#http://localhost:8000/tasks/daily?user_id=10
#http://localhost:8000/docs 

#https://smokeproof-ella-implosively.ngrok-free.dev/docs

#curl.exe --ssl-no-revoke -i "https://smokeproof-ella-implosively.ngrok-free.dev/tasks/daily?date=2026-03-07&user_id=1"

"""
오늘 할 일 보여줘

업무 추가해줘

우선순위 정리해줘

일정 계획 만들어줘
"""
