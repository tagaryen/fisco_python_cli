
def writeFile(path, data):
    with open(path, mode='w', encoding='utf-8') as f:
        f.write(data)