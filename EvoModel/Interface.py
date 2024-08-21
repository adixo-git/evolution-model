import pygame
import sys
import EvolutionImport as E

pygame.init()

def update():
    pygame.display.update()

def display(color,position):
    pygame.draw.circle(screen,(color[0],color[1],color[2]),(position[0],position[1]),r,0)

def write_gen(gen,x,y):
    text = font.render(f"Gen : {gen}",True,(0,0,255))
    screen.blit(text,(x,y))

def write_rate(survival,x,y):
    if survival!=None:
        text = font.render(f"Survived : {survival}%",True,(255,100,100))
        screen.blit(text,(x,y))

def write_speed(speed,x,y):
    if speed!=None:
        text = font.render(f"Speed : {speed}",True,(128,0,255))
        screen.blit(text,(x,y))



W = 1300
H = 650
screen = pygame.display.set_mode((W,H))
clock = pygame.time.Clock()

r = 4
count = 0
gen = 0
E.generate(E.population,E.size,E.num)
original_list = E.Creature.alive.copy()

font = pygame.font.Font("freesansbold.ttf",32)

while True:
    
    screen.fill((192,255,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if count<=650:
        speed = 0
        for creature in original_list:

            position = [int((creature.sensors[0]+600)*(W/1200)),int((creature.sensors[1]+600)*(H/1200))]
            display(creature.color,position.copy())

            
            speed += round((creature.velocity[0]**2+creature.velocity[1]**2)**0.5,2)
            
            if 200<count<400:
                E.action(creature,1)
        speed = round(speed/1000,2)
    
    if count == 650:
        alpha,beta = E.evolve(original_list,gen)
        original_list = alpha.copy()
    elif 650<count<=900:
        for creature in beta:
            position = [int((creature.sensors[0]+600)*(W/1200)),int((creature.sensors[1]+600)*(H/1200))]
            display(creature.color,position.copy())
        if count==900:
            count = 0
            gen+=1
            
    write_gen(gen,10,10)
    write_rate(E.survival,1020,10)
    write_speed(speed,10,600)
    count+=1
    
    update()







    






