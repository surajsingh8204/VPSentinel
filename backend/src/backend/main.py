from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def message():
    return{"message":"Hello from server"}


#if __name__=="__main__":
    #import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=4000, reload=True)
