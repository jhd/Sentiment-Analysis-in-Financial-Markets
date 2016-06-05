db = lmdb.open('/home/jhd/Documents/projects/sentimentNN/sentimentData')
txn = db.begin()
cur = txn.cursor()
for (key, value) in cur:
    print key, value

