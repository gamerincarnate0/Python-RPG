import unittest
import os
import main
from functions import TextFuncs


class FakeText:
    def __init__(self):
        self.lines = []
        self.tags = set()
        self._state = 'normal'
    def configure(self, **k):
        self._state = k.get('state', self._state)
    def insert(self, where, text):
        # assume text ends in \n
        for ln in text.splitlines():
            self.lines.append(ln)
    def tag_names(self):
        return list(self.tags)
    def tag_configure(self, tag, **k):
        self.tags.add(tag)
    def tag_add(self, tag, a, b):
        pass
    def see(self, x):
        pass
    def delete(self, a, b):
        # support '1.0' to 'end' or range to delete first N lines
        if a == '1.0' and b == 'end':
            self.lines = []
        else:
            # b like '101.0' -> delete first N lines
            try:
                n = int(b.split('.')[0]) - 1
                self.lines = self.lines[n:]
            except Exception:
                pass
    def get(self, a, b):
        return '\n'.join(self.lines)
    def index(self, arg):
        # support 'end-1c' by returning e.g. '5.0'
        return f"{len(self.lines)+1}.0"


class MessagesControlTests(unittest.TestCase):
    def test_clear_and_save(self):
        fake = FakeText()
        main.messages_box = fake

        main.log_message('Hello world')
        main.log_message('Another')

        # verify content present
        self.assertIn('Hello world', fake.get('1.0', 'end'))

        # save to a temp path
        path = 'tmp_messages_test.txt'
        try:
            if os.path.exists(path):
                os.remove(path)
            ok = main.save_messages_to_file(path)
            self.assertTrue(ok)
            with open(path, 'r', encoding='utf-8') as fh:
                data = fh.read()
            self.assertIn('Hello world', data)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

        # clear
        main.clear_messages()
        self.assertEqual(fake.get('1.0', 'end'), '')

    def test_trim_max_lines(self):
        fake = FakeText()
        main.messages_box = fake
        # set a small max
        main.max_messages_lines = 3

        for i in range(6):
            main.log_message(f"Line {i}")

        content = fake.get('1.0', 'end')
        lines = content.split('\n') if content else []
        # last element may be '' due to trailing newline; filter empties
        lines = [l for l in lines if l]
        self.assertLessEqual(len(lines), 3)
        self.assertIn('Line 5', lines)


if __name__ == '__main__':
    unittest.main()
