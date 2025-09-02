from queue import Queue
from threading import Thread
import random
import string

class Pessoa:
    def __init__(self, _name: str, _age: int):
        self.name = _name
        self.age = _age

    def info(self):
        print(f' nome: {self.name} - idade: {self.age}')
    
    def __repr__(self):
        return f'{self.name} - {self.age}'

person_queue: Queue[Pessoa] = Queue()

def random_string():
    tamanho = 10
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choices(caracteres, k=tamanho))

def coloca_pessoa():
    while True:
        try:
            person_queue.put(random_string(), random.randint(0,50))
        except:
            pass

def remove_pessoa():
    while True:
        try:
            print(person_queue.get())
        except:
            pass
    

thread1 = Thread(target=coloca_pessoa)
thread2 = Thread(target=remove_pessoa)

thread1.start()
thread2.start()
