import matplotlib.pyplot as plt
import itertools
import random
import math
import csv
import numpy
import math
import lmdb
import caffe

def main():
    market = []
    knowndates = []
    datarange = 0
    sentiment = []
    sentimentIterator = 0
    sentimentDisp = []
    backlog = 0
    backlogList = []
    
    with open('s&p500-mar-1-to-apr-17.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == 'Date':
                continue
            market.append(float(row[6]))
            knowndates.append(row[0].split('T')[0])
            datarange = datarange + 1

    returns = []

    for i in range(1, len(market)):
        returns.append(math.log(market[i]/market[i-1]))

    with open('sentiment-2015-4-17.out', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == 'Title':
                continue

            if row[1].split('T')[0] in knowndates:
                if backlog == 0:
                    sentiment.append([numpy.float(i) for i in row[2:]])
                else:   
                    denom = backlog + 1
                    backlogList.append(row)
                    avg = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    while backlog >= 0:
                        for i in range(2, 12):
                            avg[i] = avg[i] + float(backlogList[backlog-1][i])
                        backlog = backlog - 1
                    for i in range(3, 12):
                        avg[i] = avg[i]/denom
                    avg[0] = row[0]
                    avg[1] = row[1]
                    sentiment.append([numpy.float(i) for i in avg[2:]])
                    backlogList = []
                    backlog = 0
            else:
                backlog = backlog + 1
                backlogList.append(row)

    # TODO wipe db before write
    sdEnv = lmdb.open('sentimentData')
    rdEnv = lmdb.open('returnsData')

    with sdEnv.begin(write=True) as sdTxn, rdEnv.begin(write=True) as rdTxn:
        
        i = 0

        for dayReturn, daySentiment in itertools.izip(returns, sentiment):
            
            datum = caffe.proto.caffe_pb2.Datum()
            datum.channels = 10
            datum.height = 1
            datum.width = 1
            datum.data = numpy.ndarray.tobytes(numpy.asarray(daySentiment))
            sdTxn.put('{:08}'.format(i).encode('ascii'), datum.SerializeToString())
            datum = caffe.proto.caffe_pb2.Datum()
            datum.channels = 1
            datum.height = 1
            datum.width = 1
            datum.data = bytes(dayReturn)
            rdTxn.put('{:08}'.format(i).encode('ascii'), datum.SerializeToString())

            i += 1

if __name__ == "__main__":
    import cProfile
    import re
    #cProfile.run('main()')
    main()
