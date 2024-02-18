import unittest
import json
import os
import shutil
from pycaptions import Captions, save_extensions, style_options


IGNORE_JSON_FIELDS = ["filename"]
JSON_FIELDS = ["identifier", "json_version", "default_language", "time_length", "filename", "file_extensions", "options", "block_list"]
TEST_FILES_PATH = "test/captions/"
TEST_FILES = ["test.en.srt", "test.en.sub", "test.en.vtt", "test.ttml"]
TEST_MULTILINGUAL = ["test.ttml", "test.en.es.sub", "test.en.es.srt"]
EXTENSIONS = save_extensions.getvars().values()
STYLE = [None, "full"]

if os.path.exists("tmp/"): 
    shutil.rmtree("tmp/")

os.makedirs("tmp/")


class TestCaptions(unittest.TestCase):

    def check_file_size(self, file_path):
        return os.path.getsize(file_path) == 0

    def check_json_fields(self, file_path):
        with open(file_path) as f:
            data = json.load(f)
        
        for i in JSON_FIELDS:
            self.assertIn(i, data)

        self.assertGreater(len(data["block_list"]), 0)

    def compare_json_ignore_field(self, file1_path, file2_path, ignored_fields):
        with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
            data1 = json.load(file1)
            data2 = json.load(file2)

        # Remove the specified field from both dictionaries
        for field in ignored_fields:
            data1.pop(field)
            data2.pop(field)

        self.assertEqual(data1, data2)

    def test_all(self):
        for filename in TEST_FILES:
            with Captions(TEST_FILES_PATH+filename, encoding="auto") as c:
                for ext in EXTENSIONS:
                    _out = f"tmp/from_{filename.split('.')[-1]}"
                    c.save(_out, output_format=ext)
                    self.assertFalse(self.check_file_size(c.makeFilename(_out,ext)), ext)

    def test_json(self):
        for filename in TEST_FILES:
            with Captions(TEST_FILES_PATH+filename, encoding="auto") as c:
                c.toJson(f"tmp/from_{filename.split('.')[-1]}")
                self.check_json_fields(f"tmp/from_{filename.split('.')[-1]}.json")

    def test_style(self):
        for s in STYLE:
            style_options.style = s
            with Captions(TEST_FILES_PATH+TEST_FILES[0], encoding="auto") as c:
                for ext in EXTENSIONS:
                    _out = f"tmp/style_{str(s)}"
                    c.save(_out, output_format=ext)
                    self.assertFalse(self.check_file_size(c.makeFilename(_out,ext)), ext)
    
    def test_auto_lines(self):
        for s in STYLE:
            with Captions(TEST_FILES_PATH+TEST_FILES[0], encoding="auto") as c:
                for ext in EXTENSIONS:
                    _out = f"tmp/line_auto_{str(s)}"
                    c.save(_out, output_format=ext, style=s, lines=0)
                    self.assertFalse(self.check_file_size(c.makeFilename(_out,ext)), ext)

    def test_one_line(self):
        for s in STYLE:
            with Captions(TEST_FILES_PATH+TEST_FILES[0], encoding="auto") as c:
                for ext in EXTENSIONS:
                    _out = f"tmp/line_one_{str(s)}"
                    c.save(_out, output_format=ext, style=s, lines=1)
                    self.assertFalse(self.check_file_size(c.makeFilename(_out,ext)), ext)


    def test_json_to_json(self):
        for filename in TEST_FILES:
            _in = f"tmp/from_{filename.split('.')[-1]}.json"
            with Captions(TEST_FILES_PATH+filename, encoding="auto") as c:
                c.toJson(_in)
            _out = f"tmp/from_{filename.split('.')[-1]}_json.json"
            with Captions(_in) as c:
                c.toJson(_out)
            self.compare_json_ignore_field(_in, _out, IGNORE_JSON_FIELDS)

    def test_multilingual(self):
        for filename in TEST_MULTILINGUAL:
            with Captions(TEST_FILES_PATH+filename, encoding="auto") as c:
                for ext in EXTENSIONS:
                    _out = f"tmp/multilingual_from_{filename.split('.')[-1]}"
                    c.save(_out, ["en", "es"], output_format=ext, lines=1)
                    self.assertFalse(self.check_file_size(c.makeFilename(_out,ext, ["en","es"])), ext)

if __name__ == '__main__':
    unittest.main()