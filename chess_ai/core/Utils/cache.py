import pickle


def load(fp):
    with open(fp, 'rb') as f:
        return pickle.load(f)


def save(obj, fp):
    with open(fp, 'wb') as f:
        pickle.dump(obj, f)
