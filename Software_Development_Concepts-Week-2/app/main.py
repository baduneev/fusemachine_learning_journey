# app/main.py
# यो FastAPI application को main entry point file हो


# FastAPI class import gareko
# Yo use garera FastAPI application create garincha
from fastapi import FastAPI
from . import logger

# router.py file bata router import gareko
# Yo router ma customer-related API endpoints define गरिएको छ
from .router import router


# FastAPI application object create gareko
app = FastAPI(

    # API ko title define gareko
    # Swagger UI/docs ma यो title देखिन्छ
    title="Customer API",

    # API ko short description define gareko
    # Documentation ma API ko purpose explain गर्छ
    description="API for managing customers, orders, and payments",

    # API version define gareko
    # Useful when API update/versioning garna parcha
    version="1.0.0"
)


# router.py मा define गरिएका routes main app मा include gareko
# यसपछि /customers related endpoints active हुन्छन्
app.include_router(router)


# Root endpoint define gareko
# URL: /
# Method: GET
# यो API चलिरहेको छ कि छैन check garna simple endpoint हो
@app.get("/")
def home():

    # Client/browser lai simple JSON response return gareko
    return {"message": "Customer API is running"}