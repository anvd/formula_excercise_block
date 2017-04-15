import unittest

import db_service

class DbServiceTest(unittest.TestCase):
    
    def test_delete_xblock(self):
        xblock_id = '654c3231d8a7408496f38a09569d25ee'
        
        print('test_delete_xblock: ' + xblock_id)
        db_service.delete_xblock(xblock_id)
        

    def test_is_xblock_submitted(self):
        item_id = 'block-v1:Home+CS102+2017_T1+type@codeplayground+block@29c6de98b19148b1b60f09a3ef0ce410'
        
        self.assertTrue(db_service.is_xblock_submitted(item_id))
        self.assertFalse(db_service.is_xblock_submitted(item_id + '1'))
        
        item_id1 = 'block-v1:Home+CS107+2017_T1+type@formula_exercise_block+block@748b6a77191f458ab4377ca7a93cc814'
        self.assertFalse(db_service.is_xblock_submitted(item_id1))
        
    

if __name__ == '__main__':
    unittest.main()
