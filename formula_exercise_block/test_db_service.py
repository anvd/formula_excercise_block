import unittest

import db_service

class DbServiceTest(unittest.TestCase):
    
    def test_delete_xblock(self):
        xblock_id = '654c3231d8a7408496f38a09569d25ee'
        
        print('test_delete_xblock: ' + xblock_id)
        db_service.delete_xblock(xblock_id)
        


if __name__ == '__main__':
    unittest.main()
