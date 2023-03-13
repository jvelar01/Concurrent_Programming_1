from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
from random import random, randint

N = 3 #veces que produces
NPROD = 3 #nproductores


def delay(factor = 3):
    sleep(random()/factor)


def producer(posicion,storage, empty_i, non_empty_i):
    
    #haz el for, que al final produzca un -1 y ala
    v=randint(1,6) 
    for j in range(N):
        delay(6)
        empty_i.acquire()
        print (f"producer {current_process().name} produciendo")
        v=v*(j+1)
        if v>10000:
            v=9999
            print ("los valores aleatorios se han pasado de rango")
        print ("voy a meter", v)
        storage[posicion]=v
        print ("el storage queda",storage[:])
        print (f"producer {current_process().name} almacenado {v}")
        non_empty_i.release()
        delay(6)
    
    empty_i.acquire()
    print (f"producer {current_process().name} terminando")
    storage[posicion]=-1
    print (f"producer {current_process().name} terminado")
    print ("el storage queda",storage[:])
    non_empty_i.release()
    

def minimo (lista): #devuelve la posicion del minimo en una lista
    long=len(lista)
    pos=-1
    val=10000 #limite de los valores que se puedn crear
    for i in range(long):
        if lista[i]>=0:
            if lista[i]<val:
                val=lista[i]
                pos=i
    return pos
        
        
    

def consumer(storage, listEmpty, listNon_empty):
    print("entra en consumer")
    for i in range(NPROD):
        listNon_empty[i].acquire() #vemos si podemos consumir (la verdad que esto no lo tengo muy claro)
    print ("desalmacenando")
    
    listaBuena=[] #lista en la que el consumidor va a almacenar lo que consuma 
    unos=[-1 for i in range(NPROD)]
    i =1
    while list(storage)!=unos:
        print ("storage en el while numero ",i, "del consumer, ha entrado con el storage siendo: ", storage[:])
        i=i+1
        # si es igual a unos, entonces todos los procesos han terminado
        
        posicion= minimo (storage)#cogemos la posicion del elemento que nos interesa consumir
        
        dato = storage[posicion]
        print("el valor que se va a consumir es",dato)
        listaBuena.append(dato)    
        print ("lista ordenada: ", listaBuena[:])
        storage[posicion]=-2
        print ("el storage queda", storage[:])
        delay()
        listEmpty[posicion].release() #notificamos que hemos consumido al productor i
        listNon_empty[posicion].acquire()
        
        delay()

def main():
    storage =Array('i', NPROD)
    
    for i in range(NPROD):
            storage[i] = -2

    print ("almacen inicial" f'{i}', storage[:], "indice prod"f'{i}')
    
    listNon_empty = [Semaphore(0)  for i in range(NPROD) ]
    listEmpty = [Lock()  for i in range(NPROD) ]


    prodlst = [ Process(target=producer, #lista de productores
                        name=f'prod_{i}',
                        args=(i, storage, listEmpty[i], listNon_empty[i]))
                for i in range(NPROD) ]

    consumr= Process(target=consumer,
                      name='consmr',
                      args=(storage, listEmpty, listNon_empty))

    consumr.start()
    
    for p in prodlst:
        p.start()
    
    for p in prodlst:
        p.join()
        
    consumr.join()

    

if __name__ == '__main__':
    main()
