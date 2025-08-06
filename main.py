
from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

from api.v1.routes import router
from auth import verify_token

app = FastAPI(
    title="LLM Query System",
    version="1.0.0"
)

# ✅ Secure all endpoints under the prefix
app.include_router(router, prefix="/api/v1/hackrx", dependencies=[Depends(verify_token)])

# ✅ Add Swagger Auth Support (Authorize Button)
security = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="LLM Query System",
        version="1.0.0",
        description="HackRx LLM Query System with Token Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
@app.get("/")
def root():
    return {"message": "LLM Query System is running 🚀"}