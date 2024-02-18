def dep_root(doc):
    for t in doc:
        # print(t, "head is", t.head)
        if t == t.head:
            return t


def drop_abbrevs(text):
    clean = []
    for w in text.split(' '):
        if not w.isdigit() and any(c.isdigit() for c in w):  # eg 400VAC
            continue
        if any(not c.isalnum() for c in w):  # eg MCCB-
            continue
        clean.append(w)  # but keep eg "1"
    # clean
    return ' '.join(clean)
