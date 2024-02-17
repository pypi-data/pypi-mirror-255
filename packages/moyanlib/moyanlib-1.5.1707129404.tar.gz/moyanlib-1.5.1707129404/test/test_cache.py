import pytest
import time
from moyanlib.cache import Cache

def test_setCache():
    cache = Cache('../.test_cache')
    cache.set('1','fh',1)
    testOut = cache.get('1')
    assert testOut == 'fh'
    cache.delete_all()
    
def test_delCache():
    cache = Cache('../.test_cache')
    cache.set('s','ss')
    cache.delete('s')
    testOut = cache.get('s')
    assert testOut == None
    cache.delete_all()
    
def test_oldCache():
    cache = Cache('../.test_cache')
    cache.set('de','s',1)
    time.sleep(1.001)
    testOut = cache.get('de')
    assert testOut == None
    
    