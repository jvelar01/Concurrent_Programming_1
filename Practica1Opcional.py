from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


N = 5 #veces que produces
K = 10 #tamaño del buffer de cada productor
NPROD = 3
NCONS = 1

def delay(factor = 3):
    sleep(random()/factor)


def add_data(storagei, indexi, data, mutex):
    mutex.acquire()
    try:
        storagei[indexi.value] = data
        delay(6)
        indexi.value = indexi.value + 1
    finally:
        mutex.release()


def get_data(storage, index, mutex,i):
    mutex.acquire()
    try:
        data = storage[i][0] 
        index[i].value = index[i].value - 1
        delay()
        for j in range(index[i].value):
            storage[i][j] = storage[i][j + 1]
        storage[i][index[i].value] = -2
    finally:
        mutex.release()
    return data


def producer(storagei, indexi, emptyi, non_emptyi, mutex):
    v=0
    for i in range(N):
        print (f"producer {current_process().name} produciendo")
        delay(6)
        v=v+randint(0,6)
        emptyi.acquire()
        add_data(storagei, indexi, v, mutex)
        non_emptyi.release()
        print (f"producer {current_process().name} almacenado {v}")
        delay(6)
        
    emptyi.acquire()
    print (f"producer {current_process().name} terminando")
    add_data(storagei, indexi, -1, mutex)
    print (f"producer {current_process().name} terminado")
    non_emptyi.release()
    

def minimo (lista): #devuelve la posicion del minimo en una lista
    long=len(lista)
    pos=-1
    val=10000 
    for i in range(long):
        if lista[i]>=0:
            if lista[i]<val:
                val=lista[i]
                pos=i
    return pos

def consumer(storage, index, empty, non_empty, mutex):
    unos=[-1 for i in range(NPROD)]
    Disponibles=Array('i',NPROD) #estos van a ser los que puedes coger, esto es, el primero de cada productor
    listaBuena=[]
    for i in range(NPROD):
        non_empty[i].acquire()
    
    j=1
    for i in range(NPROD):
        Disponibles[i]=storage[i][0]
    while list(Disponibles)!=unos:
        print ("disponibles en el while numero ",j, "del consumer, ha entrado con los disponibles siendo: ", Disponibles[:])
        j=j+1
        print ("consumer desalmacenando")
        posicion= minimo (Disponibles)
        dato =get_data(storage, index, mutex,posicion)
        print (f"consumer consumiendo {dato}")
        listaBuena.append(dato)
        print (f"consumer ha condumido {dato}")
        print("la lista queda",listaBuena[:])
        for i in range(NPROD):
            Disponibles[i]=storage[i][0]
        empty[posicion].release()
        non_empty[posicion].acquire
        delay()

def main():
    storage = [Array('i', K) for i in range(NPROD)]
    index = [Value('i', 0) for i in range(NPROD)]
    for j in range(NPROD):
        for i in range(K):
            storage[j][i] = -2
    

    listnon_empty = [Semaphore(0) for i in range(NPROD)]
    listempty = [BoundedSemaphore(K) for i in range(NPROD)]
    mutex = Lock()

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage[i], index[i], listempty[i], listnon_empty[i], mutex))
                for i in range(NPROD) ]

    consumr= Process(target=consumer,
                      name='consmr',
                      args=(storage, index, listempty, listnon_empty,mutex))

    consumr.start()
    
    for p in prodlst:
        p.start()
    
    for p in prodlst:
        p.join()
        
    consumr.join()


if __name__ == '__main__':
    main()
