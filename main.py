# main.py

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

# fastapi 객체 생성
app = FastAPI()

# jinja2 템플릿 객체 생성
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "fortuneToday":"동쪽으로 가면 귀인을 만나요"
        }
    )

# get 방식 /post 요청 처리
@app.get("/post", response_class=HTMLResponse)
def fetPosts(request: Request, db:Session = Depends(get_db)):
    # DB 에서 글 목록을 가져오기 위한 sql 준비
    query = text("""
                SELECT num, writer, title, content, created_at
                FROM post
                ORDER BY num DESC
            """)
    
    result = db.execute(query)
    posts = result.fetchall()
    
    return templates.TemplateResponse(
        request=request,
        name="post/list.html",
        context = {
            "posts":posts
        }
    )

# 1. 작성 폼 화면 요청
@app.get("/post/new", response_class=HTMLResponse)
def new_post_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="post/new-form.html", # 파일 경로 확인
        context={}
    )

# 2. 폼 데이터 저장 처리
@app.post("/post/new")
async def create_post(
    writer: str = Form(...), 
    title: str = Form(...), 
    content: str = Form(...), 
    db: Session = Depends(get_db)
):
    # SQL을 사용하여 데이터 삽입
    query = text("""
        INSERT INTO post (writer, title, content)
        VALUES (:writer, :title, :content)
    """)
    
    db.execute(query, {"writer": writer, "title": title, "content": content})
    db.commit() # DB에 반영
    
    # 저장 후 글 목록 페이지로 리다이렉트
    return RedirectResponse(url="/post", status_code=302)

@app.get("/post/{num}", response_class=HTMLResponse)
def post_detail(request: Request, num: int, db: Session = Depends(get_db)):
    # 특정 번호의 게시글을 가져오기 위한 SQL
    query = text("""
                SELECT num, writer, title, content, created_at
                FROM post
                WHERE num = :num
            """)
    
    # 파라미터 바인딩을 통해 안전하게 쿼리 실행
    result = db.execute(query, {"num": num})
    post = result.fetchone()
    
    if post is None:
        # 글이 없을 경우 처리 (간단하게 홈으로 리다이렉트하거나 에러 페이지 출력)
        return HTMLResponse(content="존재하지 않는 게시글입니다.", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="post/detail.html", # 상세 페이지 템플릿 파일명
        context={
            "post": post
        }
    )

# 삭제 처리 요청
@app.get("/post/delete/{num}")
def delete_post(num: int, db: Session = Depends(get_db)):
    query = text("DELETE FROM post WHERE num = :num")
    db.execute(query, {"num": num})
    db.commit()
    
    return RedirectResponse(url="/post", status_code=302)