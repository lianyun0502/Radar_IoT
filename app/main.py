from fastapi import FastAPI
from Router import auth, user

app = FastAPI(
    version="1.0.0",
    debug=True
    )


app.include_router(auth.router)
app.include_router(user.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=5000, reload=True)