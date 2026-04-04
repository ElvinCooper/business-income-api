from app.schemas.error import ErrorResponse


def test_error_response_creation():
    response = ErrorResponse(message="Test error")
    assert response.message == "Test error"


def test_error_response_model_dump():
    response = ErrorResponse(message="Test error")
    data = response.model_dump()
    assert data == {"message": "Test error"}


def test_error_response_validation():
    response = ErrorResponse(message="")
    assert response.message == ""
