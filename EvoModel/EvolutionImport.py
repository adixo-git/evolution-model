from random import *
from numpy import *

# SELECTION CRITERIAS :
# 1. Position -> ON
# 2. Color -> ON
# 3. Weight -> OFF

class Creature:
    
    alive = []

    def __init__(self,name,genome,design, position = array([0,0])):

        self.name = name
        self.genome = genome
        self.design = design
        self.sensors = position.copy()
        self.motors = zeros(self.design[-1])
        self.weights = [ zeros((x,y)) for x,y in zip(self.design[1:],self.design[:-1]) ]
        self.biases = [ zeros((x)) for x in self.design[1:] ]
        self.speed = 0
        self.velocity = [0,0]
        self.color = Creature.paint(self)
        
        Creature.build(self)
        Creature.alive.append(self)

    def show(self):
        h = [hexa(gene) for gene in self.genome]
        return h
    
    def paint(self):
        r = 0
        g = 0
        b = 0
        for gene in self.genome:
            gene = gene[2:]
            r+= inta(gene[0:8])
            g+= inta(gene[8:16])
            b += inta(gene[16:])
        r = r%256
        g = g%256
        b = b%256
        color = [r,g,b]
        return color

    def build(self):
        genome = self.genome 
        sensors = self.sensors
        weights = self.weights
        biases = self.biases
        """
        x_sum = 0
        y_sum = 0
        for gene in genome:
            gene  = gene[2:]
            x_sum = x_sum + sign(gene[0])*inta(gene[1:12])
            y_sum =y_sum + sign(gene[12])*inta(gene[13:24])
        sensors[0] = int(x_sum/10)
        sensors[1] = int(y_sum/10)
        """
        for i in range(2):
            count = 0
            for j in range(shape(weights[i])[0]):
                for k in range(shape(weights[i])[1]):
                    gene = genome[count]
                    gene = gene[2:]
                    if i==0:
                        gene = gene[0:12]
                    else:
                        gene = gene[12:24]
                    weights[i][j][k] = sign(gene[0])*inta(gene[1:12])/1000
                    count+=1
        

        dna = []
        speed = 0
        for gene in genome:
           dna.append(sign(gene[2])*inta(gene[3:])/(10**6))
           speed+= inta(gene[2:])/(10**6)
        self.speed= round(speed/20)

    
        biases[0][0] = dna[0]+dna[1]
        biases[0][1] = dna[2]+dna[3]
        biases[0][2] = dna[4]+dna[5]

        biases[1][0] = dna[0]+dna[1]+dna[2]
        biases[1][1] = dna[3]+dna[4]+dna[5]
       
                  
    def sense(self):
        sensors = self.sensors
        weights = self.weights
        biases = self.biases
        inners = sensors.copy()
        for i in range(2):
            inners = dot(weights[i],inners)
        self.motors = inners.copy()
        return  self.motors
    
    def feedback(self):
        #self.sensors += self.speed*normalize(self.motors)[:2]
        
        self.velocity = [int(self.motors[0])%4+1,  int(self.motors[1])%4+1 ]
        self.sensors[0] += self.velocity[0]*normalize(self.motors[0])
        self.sensors[1] += self.velocity[1]*normalize(self.motors[1])
        
        for i in range(2):
            if self.sensors[i]>=600:
                self.sensors[i]=-600+10
            elif self.sensors[i]<=-600:
                self.sensors[i]=600-10
            
        return self.sensors
        
def make(size):
    string = "0b"
    for i in range(size):
        bit = randint(0,1)
        string += f"{bit}"
    return string

def create(size, num):
    return [make(size) for i in range(num)]

def generate(population,size,num):
    for i in range(population):
        G = create(size,num)
        position = [random.randint(-600,600),random.randint(-600,600)]
        Creature(naming(),G,design,position)

def naming():
    i = randint(0,1)
    p0 = choice(list(empty.union({list(starters)[i]})))
    p1 = choice(list(vowels))
    p2 = choice(list(mid1))
    p3 = choice(list(vowels.union(doubles)))
    p4 = choice(list(mid2))
    p5 = choice(list(vowels))
    i = randint(0,1)
    p6 = choice(list(empty.union({list(enders)[i]})))
    s = p0+p1+p2+p3+p4+p5+p6
    if s[-3:]== "aio":
        s= s[:-4]+s[-3:]
    s = s.capitalize()
    return s

def hexa(b_string):
    return hex(int(b_string,2))

def inta(d_string):
    return int("0b"+d_string,2)

def sign(b):
    return 1 if int(b)==1 else -1

def normalize(x):
    return 1 if x>=0 else -1  

def action(creature,age):
    for i in range(age):
        creature.sense()
        creature.feedback()

def select(original_list):
    selected_list = []
    for creature in original_list:
        s = creature.sensors
        c = creature.color
        """
        w = creature.weights
        w_sum = 0
        for i in range(2):
            for j in range(shape(w[i])[0]):
                for k in range(shape(w[i])[1]):
                    w_sum += w[i][j][k]
        """
        
        #if c[2]>=150:
        if (s[0]<=-100 and s[0]>=-400 and s[1]<=-100 and s[1]>=-400) or (s[0]>=100 and s[0]<=400 and s[1]>=100 and s[1]<=400):
            selected_list.append(creature)
            
    return selected_list

def reproduce(C0,C1):
    G0 = C0.genome
    G1 = C1.genome
    shuffle(G0)
    shuffle(G1)
    G3 = [x[inx := randrange(0,2)] for x in zip(G0,G1)]
    position = [random.randint(-600,600),random.randint(-600,600)]
    C3 = Creature(naming(),G3,design,position)
    return C3

def evolve(original_list,gen):

        selected_list = select(original_list).copy()
        
        L = len(selected_list)
        global survival
        survival = round((L/population)*100,2)
        
        print(f"# Survival Rate of Gen - {gen} : {survival}%")

        Creature.alive = []
        children_list = []
        count = 0
        while count<population:
            shuffle(selected_list)
            parents = list(zip(selected_list[:-1],selected_list[1:]))
            for (C0,C1) in parents:
                if count>population-1:
                    break
                C3 = reproduce(C0,C1)
                #if count%mrate==0 and count!=population:
                    #mutate(C3)
                children_list.append(C3)
                count+=1
                
        original_list = children_list.copy()

        return original_list,selected_list

def mutate(C):
    G = create(size,num)
    C.genome = G.copy()
    return C

vowels = {"a","e","i","o","u"}
doubles = {"ai","au","ia","io","ju","oi","ua"}
starters = {"m","n","p","b","t","d","k","g","ts","ch","ĝ","r","l","s","z","sh","f","v","h","j"}
mid1 = {"m","n","p","b","t","d","k","g","ts","ch","ĝ","r","l","s","z","sh","f","v"}
mid2 =  {"m","n","p","b","t","d","k","g","ch","r","l","s","z","v","sh"}
enders = {"m","n","p","b","t","d","k","g","r","l","s","z","v","aio"}
empty = {""}

g = 90
size = 24
num = 6
population = 1000
design = [2,3,2]
age = 200
generation = 1000
frate = 1
mrate = 10
survival = None

"""
generate(population,size,num)
C= Creature.alive[0]
C.sensors = [100,100]
print(C.sensors)
print(C.weights)
C.sense()
print(C.motors)
C.feedback()
print(C.velocity)
print(C.sensors)
"""
