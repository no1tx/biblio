from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import uvicorn

from database import Book, Client, Rent

web_app = FastAPI(title='Biblio')

templates = Jinja2Templates(directory='content/')

web_app.mount("/static", StaticFiles(directory='./static'), name='static')


def render(name, context=None):
    return templates.TemplateResponse(name, context=context)


@web_app.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

@web_app.get("/clients", response_class=HTMLResponse)
def clients(request: Request):
    clients = Client.get_all()
    return templates.TemplateResponse('clients.html', context={'request': request, 'data': clients})
if __name__ == '__main__':
    uvicorn.run(web_app, port=9003)
