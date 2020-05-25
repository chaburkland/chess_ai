import os

def get(filename):
    base = os.path.dirname(__file__)
    return os.path.join(base, 'input', filename)
