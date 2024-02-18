import unittest
from theoduchamps_picsou import picsou

class MyTestCase(unittest.TestCase):
    def test_something(self):
        account = picsou.delete_money_from_bank_account(100, 200)
        self.assertEqual(9600, account)
        
        account = picsou.delete_money_from_bank_account(100, 0)
        self.assertEqual(9500, account)
    
if __name__ == "__main__":
    unittest.main()