import matplotlib.pyplot as plt
import random
import math
import csv
import numpy
import math

def fitness(model, expectedOutput, sentiment):
    fitness = 0
    predictedOutput = [expectedOutput[0]]

    for i in range(1, len(expectedOutput)):

        modelMod = 0

        for sen in sentiment:
            
            for k in range(0, 10):

                modelMod = modelMod + model[k] * float(sen[k+3])

        predictedOutput.append(predictedOutput[i-1] + modelMod)       

    for i in range(0, len(predictedOutput)):
        fitness = fitness + pow((predictedOutput[i] - expectedOutput[i]), 2)
    if abs(fitness) < 1:
        #fitness = 1/abs(fitness)
        pass
    return fitness

def getFitest(population, market, sentiment):
    fitest = float("inf")
    bestFit = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for pop in population:
        popFitness = fitness(pop, market, sentiment)
        if abs(popFitness) < 1:
            #popFitness = 1/abs(popFitness)
            pass
        if abs(popFitness) <  abs(fitest):
            fitest = popFitness
            bestFit = pop
    return (fitest, bestFit)

def initPopulation(popSize):
    pop = []

    for i in range(0, popSize):
        individual = []
        for k in range(0, 10):
            individual.append(numpy.random.normal(0, 1)/100)
        pop.append(individual)

    return pop

def nextGen(population, market, sentiment):
    sortedPop = sorted(population, key=lambda pop: fitness(pop, market,sentiment))
    newPop = []
    for i in range(0, len(population)/10):
        for k in range(0, 10):
            tmp = population[i]
            while numpy.random.uniform(0, 1) < 0.5:
                tmp[numpy.random.randint(0, 10)] = numpy.random.normal(0, 1)/100
            while numpy.random.uniform(0, 1) < 0.5:
                target = numpy.random.randint(0, 10)
                tmp[target] = sortedPop[numpy.random.randint(0, len(sortedPop))][target]

            newPop.append(tmp)
#    for i in range(0, len(population)):
#        while numpy.random.uniform(0, 1) < 0.5:
#            target = numpy.random.randint(0, 10)
#            tmp = newPop[numpy.random.randint(0, 11)][target]
#            newPop[numpy.random.randint(0, 11)][target] = newPop[i][target]
#            newPop[i][target] = tmp
#        while numpy.random.uniform(0, 1) < 0.5:
#            target = numpy.random.randint(0, 10)
#            newPop[i][target] = newPop[i][target] + numpy.random.normal(0, 1)*10
 
    return newPop

def main():
    market = []
    knowndates = []
    datarange = 0
    sentiment = []
    sentimentIterator = 0
    sentimentDisp = []
    backlog = 0
    backlogList = []
    
    with open('../s&p500-mar-1-to-apr-17.csv', 'rb') as csvfile:
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
    print returns
    with open('../sentiment-2015-4-17.out', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == 'Title':
                continue

            if row[1].split('T')[0] in knowndates:
                if backlog == 0:
                    sentiment.append(row)
                else:   
                    denom = backlog + 1
                    backlogList.append(row)
                    avg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    while backlog >= 0:
                        for i in range(2, 12):
                            avg[i] = avg[i] + float(backlogList[backlog-1][i])
                        backlog = backlog - 1
                    for i in range(3, 12):
                        avg[i] = avg[i]/denom
                    avg[0] = row[0]
                    avg[1] = row[1]
                    sentiment.append(avg)
                    backlogList = []
                    backlog = 0
            else:
                backlog = backlog + 1
                backlogList.append(row)
    
    population = initPopulation(1000)
    generations = 0
    bestFit = float("inf")
    bestFitCoef = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    goodEnough = 0.01
    market = returns
    market.append(0)
    while generations < 10:    

        print "Generation: " + str(generations) + " Best Fit: " + str(bestFit)
        print bestFitCoef
        if abs(bestFit) <= goodEnough:
            break
        
        population = nextGen(population, market, sentiment)
        bestOfGen = population[0]
        if fitness(bestOfGen, market, sentiment) < bestFit:
            
            bestFit = fitness(bestOfGen, market, sentiment)
            bestFitCoef = list(bestOfGen)
            print bestFit
            print bestFitCoef
            print fitness(bestFitCoef, market, sentiment)

        generations = generations + 1

    print bestFit
    print bestFitCoef
    print fitness(bestFitCoef, market, sentiment)

    sentimentDisp = [market[0]]
    for i in range(0, len(sentiment)):
        tmp = 0
        for k in range(0, 10):
            tmp = tmp + bestFitCoef[k]*float(sentiment[i][k+3])
        sentimentDisp.append(sentimentDisp[len(sentimentDisp)-1]+tmp)
    
    senXPoints = range(0,datarange)
    for i in range(0, len(senXPoints)):
        senXPoints[i] = senXPoints[i] - 1
    rightDay = 0
    wrongDay = 0
    for i in range(1, len(market)-1):
        daySign = market[i] - market[i+1]
        predSign = sentimentDisp[i-1] - sentimentDisp[i]
        if (daySign <0 and  predSign <0) or (daySign >0 and predSign>0):
            rightDay = rightDay + 1
        else:
            wrongDay = wrongDay + 1
    print "Right: " + str(rightDay)
    print "Wrong: " + str(wrongDay)
    print len(market)
    print len(sentimentDisp)
    print len(senXPoints)
    print datarange
    sentimentDisp.reverse()
    market.reverse()
    plt.plot(senXPoints, sentimentDisp)
    plt.plot(range(0,datarange), market)

    plt.xlabel('Days since 2015-03-01')
    plt.ylabel('S&P 500 Daily Returns')

    plt.show()

if __name__ == "__main__":
    import cProfile
    import re
    #cProfile.run('main()')
    main()
