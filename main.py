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
def postNew(request: Request, writer: str = Form(...), title: str = Form(...), content: str = Form(...),
            db: Session = Depends(get_db)):
    # DB 에 저장할 sql 문  준비
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
    """)
    # query 문을 실행하면서 같이 전달한 dict 의 키값과  :writer , :title, :content 동일한 위치에 값이 바인딩되어서 실행된다.
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()

    # 특정 경로로 요청을 다시 하도록 리다일렉트 응답을 준다. 
    return templates.TemplateResponse(
        request=request, 
        name="post/alert.html",
        context={
            "msg":"글 정보를 추가 했습니다!",
            "url":"/post"
        }
    )

# 삭제 처리 요청
@app.get("/post/delete/{num}")
def delete_post(num: int, db: Session = Depends(get_db)):
    query = text("DELETE FROM post WHERE num = :num")
    db.execute(query, {"num": num})
    db.commit()
    
    return RedirectResponse(url="/post", status_code=302)