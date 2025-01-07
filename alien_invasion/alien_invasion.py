import pygame
from pygame import mixer
from pygame.locals import *
import random
import pygame.locals



pygame.mixer.pre_init(44100,-16,2,512 )
mixer.init()
pygame.init() #predefine to use mixer properities

#define fps
clock = pygame.time.Clock()
fps = 60

rows=4
cols=4
alien_cooldown = 1000 #bullet cooldown
last_alein_shot = pygame.time.get_ticks()
countdown = 3
last_count  = pygame.time.get_ticks()  
game_over= 0 #0 is no game over, 1 means win, -1 means lost

screen_width=500
screen_height=600

font30=pygame.font.SysFont('Constantia',30)
font20=pygame.font.SysFont('Constantia',20)

red=(255,0,0)
green=(0,255,0)
white = (255,255,255)

screen=pygame.display.set_mode((screen_width,screen_height))
#for screen size
pygame.display.set_caption("space invaders")
#for screen caption which appears on top left


#load sounds
explosion_fx = pygame.mixer.Sound("explosion.wav")
explosion_fx.set_volume(0.15)

explosion2_fx = pygame.mixer.Sound("explosion2.wav")
explosion2_fx.set_volume(0.15)

laser_fx = pygame.mixer.Sound("laser.wav")
laser_fx.set_volume(0.15)

#for loading image
bg=pygame.image.load("bg.png")

def draw_bg():
    screen.blit(bg, (0, 0)) #blit for adding images, starting coordinates, top left.

def draw_text(text,font,text_col,x,y):
    img = font.render(text, True, text_col) #convert text to image
    screen.blit(img,(x,y))


class Spaceship(pygame.sprite.Sprite): #this is a subclass of pygame.sprite.Sprite 
    def __init__(self, x, y,health): #coordinates of spaceship in screen
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("spaceship.png") 
        self.rect = self.image.get_rect() #convert image to rectangle 
        self.rect.center=[x,y] #coordinates 
        self.heath_start = health
        self.health_remaining= health
        self.last_shot=pygame.time.get_ticks() 
    
    def update(self):
        speed = 8 #movement speed
        cooldown = 500 #500 ms gap between each bullet fired
        #get key press
        game_over=0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left>0: 
            self.rect.x-=speed #limit so that it doesnt escape the screen
        if key[pygame.K_RIGHT] and self.rect.right<screen_width:
            self.rect.x+=speed

        #record current time 
        time_now = pygame.time.get_ticks() 
        #for shooting 
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullet=Bullets(self.rect.centerx,self.rect.top)
            bullet_group.add(bullet)
            self.last_shot= time_now
        
        self.mask= pygame.mask.from_surface(self.image) #creates mask. at first we had rectangle of our spaceship,we are changing it to mask for collision purpose. mask is essentially the pixels which are not transparent


        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 10)) #here x coord is same as ship and y coord is lil lower than ship, width i s same as ship and height is 15 
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining/ self.heath_start)), 10))
        elif self.health_remaining<=0:
            explosion = Explosion(self.rect.centerx,self.rect.centery,3)
            explosion_group.add(explosion)
            self.kill()
            game_over=-1
        return game_over



class Bullets(pygame.sprite.Sprite): #bullets class similar to spaceship
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center=[x,y]
    def update(self):
        self.rect.y -= 5 #move up 5 coordinates  understanf again 
        if self.rect.bottom < 0:
            self.kill() #remove from group when it goes off screen
        if pygame.sprite.spritecollide(self,alien_group,True): #this function checks the collision between bullets and aliens in alien groups, third arg is do_kill, which is set to true, which means the aliens will be destroyed from their groups and from the screen
            self.kill() #kills the bullet too 
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx,self.rect.centery,3)
            explosion_group.add(explosion)



class alien_Bullets(pygame.sprite.Sprite): #bullets class similar to spaceship
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center=[x,y]
    def update(self):
        self.rect.y += 2 #move down 2 coordinates  understanf again 
        if self.rect.top > screen_height:
            self.kill() #remove from group when it goes off screen
        if pygame.sprite.spritecollide(self,spaceship_group,False,pygame.sprite.collide_mask): #here, it checks collision between alien bullets and ship, he we set the do_kill to false cus we dont to immediately remove the ship from screen. the last arg is deafult set to rect, but now we set it to mask
            self.kill() #kills the bullet too
            explosion2_fx.play()
            spaceship.health_remaining -=1
            explosion = Explosion(self.rect.centerx,self.rect.centery,2)
            explosion_group.add(explosion)


class Explosion(pygame.sprite.Sprite): #animation in sprite is just list of individual still pictures which we cycle thru quickly
    def __init__(self, x, y,size): 
        pygame.sprite.Sprite.__init__(self)
        self.images=[]
        for num in range(1,6):
            img=pygame.image.load(f"exp{num}.png")
            if size ==1:
                img=pygame.transform.scale(img,(10,10))
            if size == 2:
                img=pygame.transform.scale(img,(20,20))
            if size == 3:
                img=pygame.transform.scale(img,(60,60))
            self.images.append(img)
        self.index=0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center=[x,y]
        self.counter=0
    def update(self):
        explosion_speed=3 #this is like the threshold value,if the counter exceeds this speed, image gets changed
        self.counter += 1
        if self.counter >= explosion_speed and self.index<len(self.images) -1:
            self.index += 1
            self.counter=0
            self.image = self.images[self.index] #the images are being updated
        #if the animation is complete, delete explosion
        if self.index >= len(self.images) -1 and self.counter >= explosion_speed:
            self.kill()




class Aliens(pygame.sprite.Sprite):
    def __init__(self, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("alien"+ str(random.randint(1,5))+".png")
        self.rect= self.image.get_rect()
        self.rect.center=[x,y]
        self.move_counter=0
        self.move_direction=1
    def update(self):
        self.rect.x+= self.move_direction  #move in right direction first
        self.move_counter +=1 #update counter
        if abs(self.move_counter) >58: 
            self.move_direction *= -1 #make the direction reverse by multiplying it to -1
            self.move_counter *= self.move_direction #update the counter understanf later  we can also set to zero

    

spaceship_group= pygame.sprite.Group() #creating groups which are similar to lists. in groups we can store many sprites. we can add, delete , update etc
bullet_group=pygame.sprite.Group()
alien_group=pygame.sprite.Group() #here we are first creating sprite classes then making these groups where we can add those instances of classes. after adding into groups we display them onto the screen uing draw fucntion
alien_bullet_group=pygame.sprite.Group()
explosion_group= pygame.sprite.Group()


spaceship=Spaceship(int(screen_width/2),screen_height-100,3) #create player ie instance 
spaceship_group.add(spaceship) #add spaceship to group, group has inbuilt option to draw on screen 



def create_aliens(): #here we have many aliens so we are creating a function which iterates and generates aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(80 + item * 110, 80+row*60) #80 refers to some space being left instead of starting from border and *110 and 60 tells the gap btw each alien and their rows 
            alien_group.add(alien)

create_aliens() #we are calling outside our main loop cus we dont want aliens to create many times, we just want them on screen once 

run = True
while run:
    clock.tick(fps) # set frame rate to 60 everytime we open game window
    draw_bg() # every time we open window bg image is added
    if countdown==0:
        #create random alien bullets 
        #record current time
        time_now = pygame.time.get_ticks()
        #shot
        if time_now - last_alein_shot > alien_cooldown and len(alien_bullet_group) <5 and len(alien_group)>0:  #if the time between last shot and cuurent shot is greater than cooldown then shoot, cus we cant have it shooting everytime. and the amt of bullets it can shoot is 5 before going off the screen, ie it can shoot a group of 5 bullets once. if only alien instances are present that is aliens are present then bullets are produced, if the aliens are killed then bullets are stopped
            attacking_alien=random.choice(alien_group.sprites())   #choosing one random alien from group
            alien_bullet = alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom) #making bullet instance by calling class and giving locations. bullets will start from centre of alien and bottom of alien
            alien_bullet_group.add(alien_bullet) # add instance to groups
            last_alein_shot = time_now 
        if len(alien_group) == 0:
            game_over=1
        if game_over==0:
        #only when game is not over we need all those functionalities
            game_over=spaceship.update()
            bullet_group.update()
            alien_group.update()
            alien_bullet_group.update()
        else:
            if game_over==1:
                draw_text('YOU WIN!!',font30,white, int(screen_width / 2 -100), int(screen_height / 2) + 40)
            elif game_over==-1:
                draw_text('GAME OVER!',font30,white, int(screen_width / 2 -100), int(screen_height / 2) + 40)
            
    
    explosion_group.update()

    spaceship_group.draw(screen) #using draw of groups
    bullet_group.draw(screen) #update sprite groups 
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    if countdown > 0:
        draw_text('GET READY!!',font30,white, int(screen_width / 2 -100), int(screen_height / 2) + 50)
        draw_text(str(countdown),font20,white, int(screen_width / 2 -10), int(screen_height / 2) + 80)
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown-=1
            last_count = count_timer

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()# for smooth running, or updtaes every action performed
pygame.quit()

 
