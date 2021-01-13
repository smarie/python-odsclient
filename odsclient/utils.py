import sys

from io import BytesIO   # to handle byte strings
from io import StringIO  # to handle unicode strings

if sys.version_info >= (3, 0):
    def create_reading_buffer(value, is_literal):
        return StringIO(value)
else:
    def create_reading_buffer(value, is_literal):
        if is_literal:
            return BytesIO(value)
        else:
            return StringIO(value)
