#################################################################################
## Abstraction of a Systolic Array  HW
##
##
##################################################################################


from collections import namedtuple


MatrixElement = namedtuple(
    'MatrixElement', [
        'value',
        'row',
        'column'
    ]
)

Matrix = namedtuple(
    'Matrix', [
        'elements',
        'M',
        'N'
    ]
)

###
## if last row >= current row
##     == it means that I am stuck with a vector composed of only one element
##     >  drop of index means that we went back in the sequence
###
def row_marker(last, current):
    return last.row >= current.row

###
## if last column >= current column
##     == it means that I am stuck with a vector composed of only one element
##     >  drop of index means that we went back in the sequence
###
def column_marker(last, current):
    return last.column >= current.column




class FIFOQueue:
    ## N length
    ## x possible contents
    ## marker function to tell me when the contents have reached the  end
    def __init__(self,
                 N,
                 x=None,
                 marker =None):
        self.max = N
        self.fifo = [] if x is None else x
        self.m = marker
        self.ghost = None

        
    def reset(self):
        return False
    def insert(self,x):
        if len(self.fifo)< self.max:
            self.fifo.append(x)
            return x
        return None

    def pop(self):
        if (len(self.fifo)>0):
            self.ghost = self.fifo[0]
            return self.fifo.pop(0)
        return None

    def top(self):
        if (len(self.fifo)>0):
            return self.fifo[0]
        return None
    
    def last(self):
        return len(self.fifo)==1 

    def empty(self):
        return len(self.fifo)==0 

    def marker(self):
        if self.empty() or  self.ghost is None :
            return False
        
        return self.m(self.ghost,self.fifo[0])
               
    
class CircularQueue:
    ## N length
    ## x vector of length N
    def __init__(self,x, marker=None):
        self.max = len(X)
        self.X = x
        self.index=0
        self.m = marker
        self.ghost = None
        
    def top(self):
        return self.X[self.index]
        
    def pop(self):
        self.ghost = self.X[self.index]
        self.index +=1
        self.index  = self.index % self.max
        return self.X[self.index]
    def insert(self,x):
        self.X[self.index] =x
        self.index +=1
        self.index  = self.index % self.max
        
    def reset(self,X=None):
        if not X is None:
            self.X = X
            self.max = len(X)
        self.index=0
        return True
    def last(self):
        return len(self.X)==self.index+1 

    def empty(self):
        return len(self.X)==self.index+1 

    def marker(self):
        if self.empty() or  self.ghost is None :
            return False
        
        return self.m(self.ghost,self.top())

##
## a += b*c graph style 
##
def mul(a,b):
    return a+b
def add(a,b):
    return min(a,b)


def multiplyadd(a,b,c):
    return add(a, mul(b.value+c.value))

def identity():
    return int(float("inf"))
        
class SystolicElement:
    ## X Queue (left horizontal input)
    ## Y Queue (up vertical input)
    ## Z Queue (down vertical output)
    ## Out Queue to accumulate
    def __init__(self,
                 X, ## circular 
                 Y,
                 Z,
                 Out,
                 func = multiplyadd
                 identity = identity()
    ):
        
        self.left = X
        self.up = Y
        self.down = Z
        self.output = Out
        self.func   = func
        self.pushstalls = 0
        self.pullstalls = 0
        self.accumulator = identity()
        self.identity = identity

    ###
    ## Computation step
    ###
    def compute(self):
        count = 0
        ## If either input is empty, nothing to do
        ## We wait for the data to come.
        if self.up.empty():
            self.pullstalls = self.pullstalls +  1
            return 0

        ## if left is empty ... we are pretty much done 
        if self.left.empty():
            return -1
        

        x = self.left.top() ## row vector(s)
        y = self.up.top() ## column vector
        
        if x.row < y.col:
            self.left.pop()
        elif x.row > y.col:
        
            zip = self.down.append(y)
            if zip:
                self.up.pop()
                count += 1
            else:
                self.pushstalls = self.pushstalls +  1 

        elif x.row == y.col:
            zip = self.down.append(y)
            if zip:
                count +=1
                self.accumulator = self.func(self.accumulator,x,y)
                self.left.pop()
                self.up.pop()
                
        if self.left.marker() or self.up.marker()<0:
            self.output.insert(MatrixElement(self.accumulator,x.row,y.col))
            self.accumulator  = self.identity()
            l = self.left.marker()
            u = self.up.marker()
            if l: self.up.reset()
            if False and u: self.left.reset()
            
        return count
            
class SystolicArray:
    ## X Matrix 
    ## y vector
    ## x = Xy 
    ## N number of systolic elements
    def __init__(self,
                 X, 
                 y,
                 N
    ):

        self.y = CircularQueue(y,column_marker)
        self.z = FIFOQueue(N*N,column_marker)
        self.Xs = SystolicArray.split(X,N) # circular queue
        self.N = N


    def split(X,N):
        active=1

        E = X.elements[0]
        for e in X.elements:
            if e.row != E.row:
                active +=1
                E =e
        
        M = active // N 
        
