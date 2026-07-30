from random import *
from numpy import *
import matplotlib.pyplot as plt
import os
import dill as pickle


##############

class Creature:
    
    # Constructor
    def __init__(self, genome, design, location, color):

        self.genome = genome.copy()
        self.design = design.copy()
        self.depth = len(self.design)
        self.birthpoint = location.copy()
        self.location = location.copy()
        self.direction = array([0,0])
        self.color = color.copy()
        self.age = 0

        self.sensors = zeros(design[0])
        self.motors = zeros(design[-1])
        self.weights = [ zeros((x,y)) for x,y in zip(self.design[1:],self.design[:-1]) ]
        self.biases = [ zeros(x) for x in self.design[1:] ]
        
        Creature.initialize(self)

    # Genes -> Network Parametrs
    def initialize(self):
        for gene in self.genome:
            if gene[0]==0:
                self.weights[gene[1]][gene[3]][gene[2]]+= gene[4]*gene[5]
            elif gene[0]==1:
                self.biases[gene[1]][gene[3]]+= gene[4]*gene[5]

    # Observations -> Sensors
    def observe(self):
        location = self.location
        sensors = self.sensors
        direction = self.direction
        age = self.age

        sensors[0] = ((2*location[0]/args["width"])+1)/2
        sensors[1] = ((2*location[1]/args["height"])+1)/2

        try:
            sensors[2] = (direction[0]+1)/2
            sensors[3] = (direction[1]+1)/2

            Xmax_bdr_dist = args["width"]/2
            Ymax_bdr_dist = args["height"]/2
            max_bdr_dist = max(args["width"],args["height"])/2
            Xmin_bdr_dist, Ymin_bdr_dist, min_bdr_dist = get_bdr_dist(location, args["width"], args["height"])
            
            sensors[4] = 1-Xmin_bdr_dist/Xmax_bdr_dist
            sensors[5] = 1-Ymin_bdr_dist/Ymax_bdr_dist
            sensors[6] = 1-min_bdr_dist/max_bdr_dist
            
            sensors[7] = age/(args["simsteps"]-1)
            sensors[8] = (sin(pi*age/args["period"]-pi/2)+1)/2
            sensors[9] = uniform(0,1)
            global sflag
            if sflag == True:
                print(">> Senosrs OK")
                sflag = False
        except:
            pass
            
        return sensors.copy()

    # Sensors -> Motors
    def forward(self):
        inners = self.sensors.copy()
        for layer in range(self.depth-1):
            inners = tanh(dot(self.weights[layer],inners)+self.biases[layer])
        self.motors = inners.copy()
        return self.motors.copy()

    # Motors -> Actions
    def respond(self):

        motors = self.motors
        direction = self.direction
        
        dX = motors[0].copy()
        dY = motors[1].copy()

        try:       
            dX += ReLU(motors[2])
            dX -= ReLU(motors[3])
            dY += ReLU(motors[4])
            dY -= ReLU(motors[5])

            dX += ReLU(motors[6])*direction[0]
            dY += ReLU(motors[6])*direction[1]
            
            dX -= ReLU(motors[7])*direction[0]
            dY -= ReLU(motors[7])*direction[1]

            ndir = rotate(direction,90)
            dX += ReLU(motors[8])*ndir[0]
            dY += ReLU(motors[8])*ndir[1]
        
            ndir = rotate(direction,-90)
            dX += ReLU(motors[9])*ndir[0]
            dY += ReLU(motors[9])*ndir[1]

            [rx,ry] = choice([[0,1],[0,-1],[1,0],[-1,0],[1,1],[1,-1],[-1,1],[-1,-1]])
            dX += ReLU(motors[10])*rx
            dY += ReLU(motors[10])*ry
        
            level = motors[11]
            level = choices([0,1],[level,1-level]) if level>0 else 1
            dX, dY = level*dX, level*dY
            global mflag
            if mflag == True:
                print(">> Motors OK")
                mflag = False
        except:
            pass
        
        vX = tanh(dX)
        vY = tanh(dY)
        DX = sign(vX)*choices([0,1], [1-abs(vX),abs(vX)])[0]
        DY = sign(vY)*choices([0,1], [1-abs(vY),abs(vY)])[0]
        
        return array([DX,DY])

    # Actions -> New State
    def feedback(self,response):
        self.direction = response.copy()
        self.location= self.location+args["speed"]*self.direction

        # Toplogical Boundary Check
        BDR = [args["width"]/2,args["height"]/2]
        location = self.location
        for i in range(2):
            if location[i]>BDR[i]:
                location[i]=BDR[i]
            elif self.location[i]<-BDR[i]:
                location[i]=-BDR[i]
        return location.copy, self.direction.copy

    # All Four in One
    def revise(self):
        self.observe()
        self.forward()
        response = self.respond()
        self.feedback(response)

        
##############

def sign(val):
    if val>0:
        return 1
    elif val<0:
        return -1
    elif val==0:
        return 0
    else:
        return None

def ReLU(val):
    if val<=0:
        return 0
    else:
        return val
    
def rotate(vector,angle):
    angle = angle*pi/180
    num = (vector[0]+1j*vector[1])
    exp = e**((0+1j)*angle)
    new = num*exp
    nvec = zeros(2)
    nvec[0] = int(round(new.real))
    nvec[1] = int(round(new.imag))
    return nvec

def count_biases(design, depth):
    count = 0
    for i in range(1,depth):
        count += design[i]
    return count

def count_weights(design, depth):
    count = 0
    for i in range(0,depth-1):
        count += design[i]*design[i+1]
    return count

def get_bdr_dist(location, width,height):
    
        east_dist = width/2-location[0]
        west_dist = width/2+location[0]
        north_dist = height/2-location[1]
        south_dist = height/2+location[1]
        
        Xmin_bdr_dist = min(east_dist,west_dist)
        Ymin_bdr_dist = min(north_dist,south_dist)
        min_bdr_dist = min(Xmin_bdr_dist,Ymin_bdr_dist)
      
        return [Xmin_bdr_dist,Ymin_bdr_dist,min_bdr_dist]

def manhattan(A,B):
    dist = 0
    for i in range(len(A)):
        dist += abs(A[i]-B[i])
    return dist

def chebyshev(A,B):
    dist = 0
    for i in range(len(A)):
        if abs(A[i]-B[i])>dist:
            dist=abs(A[i]-B[i])
    return dist

def euclidian(A,B):
    dist = 0
    for i in range(len(A)):
        dist+=(A[i]-B[i])**2
    return dist**(0.5)

def graph(srates):
    xcoords = [i for i in range(len(srates))]
    plt.figure("Graph",figsize=(12,5.5))
    plt.title("Evolution Growth",fontsize=20)
    plt.xlabel("Generation", fontsize=15)
    plt.ylabel("Surival Rate",fontsize=15)
    if len(srates) == 1:
        plt.scatter(xcoords,srates)
    else:
        plt.plot(xcoords,srates)
    plt.show()

def show_gene_count(selected_list, top=float("inf")):
    print("# Gene Count")
    gene_dict = {}
    for creature in selected_list:
        for gene in creature.genome:
            if gene_dict.get(gene):
                gene_dict[gene] += 1
            else:
                gene_dict[gene] = 1
    sorted_dict = sorted(gene_dict.items(), key = lambda item : item[1],reverse=True)
    limit = min(top,len(sorted_dict))
    for i in range(limit):
        print(f">> {i+1}.",sorted_dict[i][0],":",sorted_dict[i][1])
    
    

##############

def create_gene():
                                                                                                                                       #
    T = choices([0,1], [probW, 1-probW])[0]                                                             # 0. Network Parameter Type : 0 -> Weight, 1 -> Bias
    L = randint(0,depth-2)                                                                                           # 1. Network Layer Index
    if T==0:
        S = randint(0,args["design"][L]-1)                                                                    # 2. Souce of Connection for Weight
    else:
        S = None                                                                                                              # 2. Souce of Connection for Bias is None                                                                                                      
    D = randint(0,args["design"][L+1]-1)                                                                   # 3. Destination of Connection
    P = choice([-1,1])                                                                                                     # 4. Parity of Parameter
    if T==0:
        V =uniform(0, args["rangeW"])                                                                         # 5. Absolute Value of Parameter (Weight)                                                    
    elif T==1:
        V = uniform(0, args["rangeB"])                                                                          # 5. Absolute Value of Parameter (Bias)   
    gene = (T,L,S,D,P,V)
    return gene

def create_genome():
    return [create_gene() for i in range(args["gsize"])]

def generate_population():
    
    creatures_list = []
    for i in range(args["psize"]):
        location = array([randint(-args["width"]/2,args["width"]/2),randint(-args["height"]/2,args["height"]/2)])
        color = [randint(0,255),randint(0,255),random.randint(0,255)]
        creature = Creature(create_genome(),args["design"],location,color)
        creatures_list.append(creature)
    return creatures_list.copy()


#############

def advance(initial_list):
    for creature in initial_list:
        creature.revise()

def simulate(initial_list):
    for step in range(args["simsteps"]):
        advance(initial_list)

def select(initial_list):
    selected_list = []
    for creature in initial_list:
        if check[args["criteria"]](creature.location) and chebyshev(creature.location,creature.birthpoint)>1:
            selected_list.append(creature)
    return selected_list.copy()

def reproduce(C0,C1):
    genome = choices(C0.genome,k=int(args["gsize"]/2))+choices(C1.genome,k=int(args["gsize"]/2))
    location = array([randint(-args["width"]/2,args["width"]/2),random.randint(-args["height"]/2,args["height"]/2)])
    color = []
    for i in range(3):
        c = choice([C0.color[i],C1.color[i]])+randint(-10,10)
        if c>255:
            c=255
        elif c<0:
            c=0
        color.append(c)
    return Creature(genome,args["design"],location,color)

def get_children(selected_list):
    children_list = []
    for i in range(args["psize"]):
        [C0,C1] = choices(selected_list,k=2)
        C3 = reproduce(C0,C1)
        children_list.append(C3)
    return children_list.copy()

def mutate(children_list):
    limit = int(ceil(args["mrate"]*args["psize"]*args["gsize"]))
    count = 0
    flag = True
    for g in range(args["gsize"]):
        for p in range(args["psize"]):
            if count >= limit:
                flag = False
                break
            child = children_list[p]
            child.genome[g] = create_gene()
            child.color[g%3] = randint(0,255)
            children_list[p] = child
            count+=1
        if flag == False:
            break
        
    return children_list.copy()

def evolve(initial_list,gen):
    simulate(initial_list)
    selected_list = select(initial_list)
    srate = len(selected_list)*100/args["psize"]
    print(f"# Surival Rate of Gen-{gen} :",round(srate,5),"%")
    initial_list = mutate(get_children(selected_list))
    return initial_list.copy(), srate
    
        
##############

def show_modes():
    print("# Chose a Mode")
    while True:
        print("1. New Simulation")
        print("2. Saved Simulation")
        mode = input(">> Enter Your Choice : ")
        if mode in ["1","2"]:
            print("-"*97)
            break
        print("-"*97)
        print("!! ERROR : INVALID CHOICE !!")
    return mode

def show_saves():
    global args, initial_list, filepath
    print("# Chose a File")
    while True:
        for i in range(0,fcount):
            filename = f"{file_list[i].name}"
            print(f"{i+1}. {filename}")
        idx = input(">> Enter Your Choice : ")
        filepath = file_list[int(idx)-1].path
        if idx in [ str(i) for i in range(1,fcount+1)]:
            with open(f"{filepath}","rb") as f:
                data = pickle.load(f)
            args = data["args"]
            initial_list = data["initial_list"]
            print("-"*97)
            break
        print("-"*97)
        print("!! ERROR : INVALID CHOICE !!")

def show_criterias():
    global args
    print("# Chose a Criteria")
    while True:
        i = 0
        keys = []
        for key in check.keys():
            print(f"{i+1}. {key}")
            keys.append(key)
            i+=1
        idx = input(">> Enter Your Choice : ")
        if idx in [ str(i) for i in range(1,len(keys)+1)]:
            args["criteria"] = keys[int(idx)-1]
            print("-"*97)
            break
        print("-"*97)
        print("!! ERROR : INVALID CHOICE !!")


##############

# Parameters

args = {
    "design" : [10,12],
    "gsize" : 50,
    "rangeW" : 4,
    "rangeB" : 4,
    "width" : 128,
    "height" : 128,
    "psize" : 500,
    "period" : 25,
    "simsteps" : 300,
    "speed" : 1,
    "mrate" : 1/100,
    "criteria" : "RIGHT",
    "generation": 0,
    "srates" : []
    }

check = {
    "LEFT": lambda loc : True if -args["width"]/4>=loc[0] else False,
    "RIGHT": lambda loc : True if args["width"]/4<=loc[0] else False,
    "UP&DOWN": lambda loc : True if args["height"]/3<=loc[1] or -args["height"]/3>=loc[1] else False,  
    "CORNERS": lambda loc : True if (args["width"]/3<=loc[0] or -args["width"]/3>=loc[0]) and (args["height"]/3<=loc[1] or -args["height"]/3>=loc[1]) else False,
    "EXTERIOR": lambda loc : True if not (-args["width"]/2.5<=loc[0]<=args["width"]/2.5 and -args["height"]/2.5<=loc[1]<=args["height"]/2.5) else False,
    "CENTER": lambda loc : True if (-args["width"]/4<=loc[0]<=args["width"]/4) and (-args["height"]/4<=loc[1]<=args["height"]/4) else False,
    "MIDDLE": lambda loc : True if (-args["width"]/8<=loc[0]<=args["width"]/8) else False,
    "RING": lambda loc : True if (-args["width"]/3<=loc[0]<=args["width"]/3 and -args["height"]/3<=loc[1]<=args["height"]/3) and not (-args["width"]/6<=loc[0]<=args["width"]/6 and -args["height"]/6<=loc[1]<=args["height"]/6) else False,
    "AXIAL" : lambda loc : True if  (-args["width"]/8<=loc[0]<=args["width"]/8) or (-args["height"]/8<=loc[1]<=args["height"]/8) else False,
    "EDGES": lambda loc : True if abs(loc[0])==args["width"]/2 or abs(loc[1])==args["height"]/2 else False
    }

depth = len(args["design"])
countW = count_weights(args["design"],depth)
countB = count_biases(args["design"],depth)
probW = countW/(countW+countB)
sflag = True
mflag = True

directory = "C://Users//Aditya Mehta//Desktop//Evolution Simulator//Saves"
file_list = list(os.scandir(directory))
fcount = len(file_list)
filepath = directory+f"//save{fcount+1}.pkl"
initial_list = generate_population()


print("-"*97)
if fcount==0:
    show_criterias() 
elif fcount!=0:
    mode = show_modes()
    if mode=="1":
        show_criterias()
    if mode=="2":
        show_saves()
        
        
##############

if __name__ == "__main__":
    
    print("!!! Evolution has Started !!!")

    while True:
        
        initial_list, srate = evolve(initial_list,args["generation"])
        args["srates"].append(srate)
        args["generation"]+=1
        data = {"args":args,"initial_list":initial_list}

        with open(f"{filepath}","wb") as f:
            pickle.dump(data,f)

        if args["generation"]%5==1 and args["generation"]!=1:
            k = input(">> Wanna Quit : ").lower()
            if k=="yes" :
                break
            
    print("!!! Evolution is Completed !!!")
    print("-"*97)
    show_gene_count(initial_list,10)
    print("-"*97)
    graph(args["srates"])
    
    
    
    




