from fastapi import Request

USERNAME = "admin"
PASSWORD = "admin"

def validate_user(username: str, password: str) -> bool:
    return username == USERNAME and password == PASSWORD


def is_logged_in(request: Request) -> bool:
    return request.session.get("user") is not None