from multiprocessing import process_parallel, setup
import random

def func(a, c):
    a1,a2 = a[0], a[1]
    return a1*a2**2 * c

class MyClass:

    def __init__(self, param):
        self.param = param


    def my_func(self, a, obj):
        self.param = a[1]
        print(random.random())
        return self.param * a[0] * obj.param **2

if __name__=='__main__':

    mp_config = setup(1,2,3)

    obj = MyClass(2)
    obj2 = MyClass(3)

    results = process_parallel(obj.my_func, function_kwargs={
        'obj': obj2
    }, jobs=[(1,1),(2,3),(3,5),(4,9),(5,2),(6,5)], mp_config={})

    print(results)

    import random

    random.seed(2)
    print(random.random())
    print(random.random())