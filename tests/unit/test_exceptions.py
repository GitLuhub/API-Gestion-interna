import pytest
from app.core.exceptions import AppException, NotFoundException, BadRequestException, UnauthorizedException, ForbiddenException

def test_exceptions():
    e1 = AppException(status_code=500, detail="Error")
    assert e1.status_code == 500
    
    e2 = NotFoundException("NF")
    assert e2.status_code == 404
    
    e3 = BadRequestException("BR")
    assert e3.status_code == 400
    
    e4 = UnauthorizedException("UA")
    assert e4.status_code == 401
    
    e5 = ForbiddenException("FB")
    assert e5.status_code == 403
