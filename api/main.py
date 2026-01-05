"""Main entry point for the FastAPI application."""

from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse

from api.core import database, models
from api.routers import auth, file, search, user

app = FastAPI()


app.include_router(auth.router)
app.include_router(file.router)
app.include_router(search.router)
app.include_router(user.router)


@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    Creates tables in the database.
    """
    database.create_tables()


@app.get(
    "/healthcheck",
    tags=["healthcheck"],
    response_model=models.HealthCheck,
    status_code=status.HTTP_200_OK,
)
def health_check():
    """
    Endpoint for performing health check.

    Returns
    -------
    models.HealthCheck
        The health check response.
    """
    return models.HealthCheck(status="OK")


@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def root():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slideshow Background with Centered Title</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            height: 100vh; /* Set full height of viewport */
            overflow: hidden; /* Hide overflow content */
            position: relative; /* Position the slideshow images */
            display: flex;
            justify-content: center; /* Center horizontally */
            align-items: center; /* Center vertically */
            animation: slideshow 30s linear infinite; /* Start slideshow animation */
        }

        @keyframes slideshow {
            0%, 100% { background-image: url('https://images.unsplash.com/photo-1714244322811-f1387dc93909?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); } /* Initial and final image */
            20% { background-image: url('https://plus.unsplash.com/premium_photo-1713840471972-c0e7f2813383?q=80&w=2069&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); } /* Switch to second image */
            40% { background-image: url('https://images.unsplash.com/photo-1714227667702-54ac7d02eb9e?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); } /* Switch to third image */
            60% { background-image: url('https://images.unsplash.com/photo-1527161153332-99adcc6f2966?q=80&w=2069&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); } /* Switch to fourth image */
            80% { background-image: url('https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=2072&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); } /* Switch to fifth image */
        }

        .title {
            color: white;
            font-size: 65px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* Add a subtle text shadow */
            position: absolute; /* Position the title on top of the slideshow */
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <div class="title">
        MicroServices
    </div>
</body>
</html>

    """  # noqa: E501
    return HTMLResponse(content=html, status_code=200)
