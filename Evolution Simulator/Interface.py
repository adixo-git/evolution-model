import  pygame as pyg
import EvolutionModel as evo
import dill as pickle

pyg.init()

def display_creatures(position,color):
    pyg.draw.circle(screen,(color[0],color[1],color[2]),(position[0],position[1]),rad,0)

def write_gen(generation,x,y):
    text = font.render(f"Gen : {generation}",True,(0,0,255))
    screen.blit(text,(x,y))

def write_age(age,x,y):
        text = font.render(f"Age : {age}",True,(128,0,255))
        screen.blit(text,(x,y))

def write_rate(srate,x,y):
    if srate!=None:
        text = font.render(f"Survived : {srate}%",True,(255,100,100))
        screen.blit(text,(x,y))

def convert(location):
    x = location[0]
    y = location[1]
    oW = evo.args["width"]
    oH = evo.args["height"]
    position = [0,0]
    position[0] = (x+oW/2)*(W-2*rad)/oW+rad
    position[1] = H - (y+oH/2)*(H-2*rad)/oH-rad
    return position.copy()

def draw_area():
    color = (0,255,150)
    criteria = evo.args["criteria"]
    if criteria =="LEFT":
        pyg.draw.rect(screen,color,(0,0,W/4,H))
    elif criteria =="RIGHT":
        pyg.draw.rect(screen,color,(3*W/4,0,W/4,H))
    elif criteria =="UP&DOWN":
        pyg.draw.rect(screen,color,(0,0,W,H/6))
        pyg.draw.rect(screen,color,(0,5*H/6,W,H/6))
    elif criteria =="CORNERS":
        pyg.draw.rect(screen,color,(0,0,W/6,H/6))
        pyg.draw.rect(screen,color,(5*W/6,0,W/6,H/6))
        pyg.draw.rect(screen,color,(0,5*H/6,W/6,H/6))
        pyg.draw.rect(screen,color,(5*W/6,5*H/6,W/6,H/6))
    elif criteria =="EXTERIOR":
        pyg.draw.rect(screen,color,(0,0,W/10,H))
        pyg.draw.rect(screen,color,(9*W/10,0,W/10,H))
        pyg.draw.rect(screen,color,(0,0,W,H/10))
        pyg.draw.rect(screen,color,(0,9*H/10,W,H/10))
    elif criteria =="CENTER":
        pyg.draw.rect(screen,color,(W/4,H/4,W/2,H/2))
    elif criteria =="MIDDLE":
        pyg.draw.rect(screen,color,(3*W/8,0,W/4,H))
    elif criteria =="RING":
        pyg.draw.rect(screen,color,(1*W/6,1*H/6,2*W/3,2*H/3))
        pyg.draw.rect(screen,(192,255,255),(2*W/6,2*H/6,W/3,H/3))
    elif criteria =="AXIAL":
        pyg.draw.rect(screen,color,(3*W/8,0,W/4,H))
        pyg.draw.rect(screen,color,(0,3*H/8,W,H/4))
    elif criteria =="EDGES":
        pyg.draw.rect(screen,color,(0,0,2*rad,H))
        pyg.draw.rect(screen,color,(W-2*rad,0,2*rad,H))
        pyg.draw.rect(screen,color,(0,0,W,2*rad))
        pyg.draw.rect(screen,color,(0,H-2*rad,W,2*rad))
        

W = 1300
H = 650
rad = 4
title = "Simulator"
pyg.display.set_caption(title)
screen = pyg.display.set_mode((W,H))
font = pyg.font.Font("freesansbold.ttf",32)
srate = None
pauseA = 200
pauseB = 400
frame = -pauseA
state = True
flag = None

initial_list = evo.initial_list
print("!!! Evolution has Started !!!")
running = True
while running:

    screen.fill((192,255,255))
    draw_area()
    
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        if event.type == pyg.KEYDOWN and flag!=None:
            if event.key == pyg.K_SPACE:
                state = not(state)
            if state==False and event.key ==pyg.K_RIGHT:
                if flag == 0:
                    flag = 1
                    frame = 1
                elif flag == 1:
                    if frame==evo.args["simsteps"]:
                        selected_list = evo.select(initial_list)
                        srate = len(selected_list)*100/evo.args["psize"]
                        print(f"# Surival Rate of Gen-{evo.args['generation']} :",srate,"%")
                        initial_list = evo.mutate(evo.get_children(selected_list))
                        flag = 2
                    else:
                        for creature in initial_list:
                            creature.revise()
                    frame+=1
                elif flag == 3:
                    flag = 4
                    frame = -pauseA
                    evo.args["srates"].append(srate)
                    evo.args["generation"]+=1
                    data = {"args":evo.args,"initial_list":initial_list}
                    with open(f"{evo.filepath}","wb") as f:
                        pickle.dump(data,f)        

    
    if state:
        if frame<0:
            flag = 0 
            for creature in initial_list:
                position = convert(creature.location)
                display_creatures(position,creature.color)
                
        elif frame<evo.args["simsteps"]:
            flag = 1
            for creature in initial_list:
                position = convert(creature.location)
                display_creatures(position,creature.color)
                creature.revise()
            write_age(frame+1,10,600) 

        elif frame==evo.args["simsteps"]:
            flag = 2
            selected_list = evo.select(initial_list)
            srate = len(selected_list)*100/evo.args["psize"]
            print(f"# Surival Rate of Gen-{evo.args['generation']} :",srate,"%")
            initial_list = evo.mutate(evo.get_children(selected_list))
                        
        elif frame<evo.args["simsteps"]+pauseB:
            flag = 3
            for creature in selected_list:
                position = convert(creature.location)
                display_creatures(position,creature.color)
                                
        elif frame==evo.args["simsteps"]+pauseB:
            flag = 4
            frame = -pauseA
            evo.args["srates"].append(srate)
            evo.args["generation"]+=1
            data = {"args":evo.args,"initial_list":initial_list}
            with open(f"{evo.filepath}","wb") as f:
                pickle.dump(data,f)
                
        frame+=1
        
    else:
        if flag == 0:
            for creature in initial_list:
                position = convert(creature.location)
                display_creatures(position,creature.color)

        elif flag == 1:
            for creature in initial_list:
                position = convert(creature.location)
                display_creatures(position,creature.color)
            write_age(frame,10,600)

        elif flag == 2:
            flag = 3 

        elif flag == 3:
            for creature in selected_list:
                position = convert(creature.location)
                display_creatures(position,creature.color) 

        elif flag == 4:
            flag = 0  
    
    write_gen(evo.args["generation"],10,10)
    write_rate(srate,1020,10)
    
    pyg.display.update()

pyg.quit()

print("!!! Evolution is Completed !!!")
print("-"*97)
evo.show_gene_count(selected_list,10)
print("-"*97)
evo.graph(evo.args["srates"])





