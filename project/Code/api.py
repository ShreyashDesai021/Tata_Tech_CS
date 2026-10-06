import os
from functools import lru_cache
from typing import Literal
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from engine import Engine
app=FastAPI(title='CS1 HLD Evidence API',version='1.0.0')
@lru_cache
def engine(): return Engine(os.getenv('HLD_MODE','baseline'))
class Question(BaseModel):
 question:str=Field(min_length=1,max_length=2000)
 project:Literal['powertrain','body','thermal']='powertrain'
 version:str|None=None
@app.get('/health')
def health(): return {'status':'ok','mode':os.getenv('HLD_MODE','baseline'),'data':'synthetic','authentication':'single-user-local-demo'}
@app.post('/ask')
def ask(q:Question):
 try:return engine().ask(q.question,q.project,q.version)
 except ValueError as e:raise HTTPException(400,str(e))
 except Exception as e:raise HTTPException(503,str(e))
@app.get('/inventory/{project}')
def inventory(project:Literal['powertrain','body','thermal']): return engine().inventory(project)
@app.get('/findings/{project}')
def findings(project:Literal['powertrain','body','thermal']): return engine().findings(project)
@app.get('/compare')
def compare(): return engine().compare()
