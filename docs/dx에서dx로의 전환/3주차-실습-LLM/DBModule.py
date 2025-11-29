# pip install SQLAlchemy pymysql

from sqlalchemy import create_engine, text
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine import Connection

class Database:
    """
    SQLAlchemy Core를 사용하여 직접 SQL 쿼리를 실행하고
    pymysql의 DictCursor처럼 딕셔너리 형태의 결과를 반환하는 클래스입니다.
    """
    def __init__(self):
        # ⭐️ DB URL 설정 (user:password@host:port/db_name)
        # pymysql 드라이버를 사용: mysql+pymysql://user01:1234@localhost:3306/mydb
        DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/sakila"
        
        # Engine 생성: DB 연결 및 설정을 관리하는 객체 (클래스 생성 시 한 번만 초기화)
        self.engine = create_engine(DATABASE_URL)
        
    def __enter__(self):
        """with 문 사용 시 Connection 객체 생성 및 반환"""
        # Connection을 열고, DictCursor처럼 결과를 딕셔너리 형태로 반환하도록 설정
        self.connection: Connection = self.engine.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 문 종료 시 커밋 또는 롤백 및 연결 해제"""
        if exc_type:
            # 오류 발생 시 롤백
            self.connection.rollback()
        else:
            # 오류가 없으면 커밋
            self.connection.commit()
        # 연결 해제
        self.connection.close()

    # --- insert, update, delete (Commit 필요) ---
    def execute(self, query: str, args: dict = None) -> CursorResult:
        """INSERT, UPDATE, DELETE 문을 실행하고 트랜잭션을 관리합니다."""
        # text()를 사용하여 SQL 문자열을 SQLAlchemy에서 인식하도록 변환
        result = self.connection.execute(text(query), args)
        # commit은 __exit__에서 자동 처리됩니다.
        return result

    # --- 데이터 딱 한 개만 가져오기 (Select One) ---
    def executeOne(self, query: str, args: dict = None) -> dict | None:
        """SELECT 문을 실행하고 첫 번째 레코드 하나를 딕셔너리 형태로 반환합니다."""
        result = self.connection.execute(text(query), args)
        # fetchone()으로 첫 번째 레코드를 가져오고, ._mapping()으로 딕셔너리 형태로 반환
        row = result.fetchone()
        return row._mapping if row else None
        
    # --- 데이터 여러 개 가져오기 (Select All) ---
    def executeAll(self, query: str, args: dict = None) -> list[dict]:
        """SELECT 문을 실행하고 모든 레코드를 딕셔너리 리스트 형태로 반환합니다."""
        result = self.connection.execute(text(query), args)
        # fetchall()로 모든 레코드를 가져오고, 각 레코드를 딕셔너리 형태로 변환하여 리스트로 반환
        return [row._mapping for row in result.fetchall()]


# 이 클래스는 반드시 with 구문 안에서 사용해야 합니다.

# 예시 테이블: users (id INT, name VARCHAR, email VARCHAR)가 있다고 가정

if __name__ == "__main__":
    try:
        with Database() as db:
            sql = """
            SELECT a.actor_id, first_name, last_name, title, description   
            FROM actor as a 
            left outer join film_actor as b on a.actor_id=b.actor_id
            left outer join film as c on b.film_id=b.film_id
            where first_name like :first_name
            """
            # # 1. INSERT/UPDATE/DELETE 실행 예시
            # db.execute("INSERT INTO users (name, email) VALUES (:name, :email)", 
            #            {"name": "김철수", "email": "kim@example.com"})
            
            # 2. SELECT * (여러 개 가져오기) 예시
            actors = db.executeAll(sql, {"first_name": "NICK"})
            print("--- executeAll 결과 ---")
            for actor in actors:
                print(f"ID: {actor['first_name']}, 이름: {actor['last_name']}, 영화: {actor['title']}")

            
    except Exception as e:
        print(f"\n데이터베이스 작업 중 오류 발생: {e}")