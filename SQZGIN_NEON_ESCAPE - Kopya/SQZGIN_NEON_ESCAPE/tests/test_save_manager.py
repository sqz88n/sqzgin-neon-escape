import json, tempfile, unittest
from pathlib import Path
import save_manager

class SaveManagerTests(unittest.TestCase):
    def test_defaults_are_independent(self):
        a=save_manager.load_profile(); b=save_manager.load_profile()
        a["coins"]=999
        self.assertNotEqual(a["coins"], b["coins"])
    def test_default_has_settings(self):
        self.assertIn("particles", save_manager.DEFAULT["settings"])

if __name__=="__main__": unittest.main()
