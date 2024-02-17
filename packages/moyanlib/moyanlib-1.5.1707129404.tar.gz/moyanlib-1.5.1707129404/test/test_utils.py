#pylint:disable=E1101
import moyanlib
import pytest

def test_DeviceID():
    testID = moyanlib.getDeviceID()
    assert type(testID)==str
    assert len(testID)==40
    
def test_GenVerifyCode():
    testCode = moyanlib.genVerifiCode(16)
    assert type(testCode)==str
    assert len(testCode)==16
    assert ' ' not in testCode
    
