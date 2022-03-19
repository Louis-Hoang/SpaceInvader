from typing import runtime_checkable
import pygame
from pygame.locals import *
import sys
import os
import random
import time

pygame.font.init()
pygame.mixer.init()

bullet_sound = pygame.mixer.Sound(os.path.join("music", 'Laser_shot.wav'))
bullet_sound.set_volume(0.7) 
crash_sound = pygame.mixer.Sound(os.path.join("music", 'crash.wav'))
crash_sound.set_volume(0.5) 

def menu_music():
  pygame.mixer.music.stop()
  pygame.mixer.music.load(os.path.join("music", 'spacetheme_menu.ogg'))
  pygame.mixer.music.play(-1)

def ingame_music():
  pygame.mixer.music.stop()
  pygame.mixer.music.load(os.path.join("music", 'sound1.ogg'))
  pygame.mixer.music.play(-1)

def quit():
    sys.exit()


WIDTH, HEIGHT = 800,800 #Screen size 

WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invader")

#Enemy
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","green.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","blue.png"))

#Player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","purple.png"))


#Laser
RED_LASER = pygame.image.load(os.path.join("assets","15.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","16.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","17.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","player_laser.png"))



#Background img
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "corona_dn.png")),(WIDTH,HEIGHT)) 

class Laser:
  def __init__(self, x, y, img):
    self.x = x
    self.y = y
    self.img = img
    self.mask = pygame.mask.from_surface(self.img)

  def draw(self,window):
    window.blit(self.img, (self.x, self.y))

  def move (self, vel):
    self.y +=vel 
  
  def off_screen(self, height):
    return not(self.y <= height and self.y >=0)

  def collision(self,obj):
    return collide(self,obj)


class Ship:

  COOLDOWN = 20

  def __init__(self,x,y,health=100):
      self.x = x
      self.y = y
      self.health = health
      self.ship_img = None
      self.laser_img = None
      self.lasers=[]
      self.cool_down_counter = 0

  def draw(self, window):
    window.blit(self.ship_img, (self.x , self.y))
    for laser in self.lasers:
      laser.draw(window)
  
  def move_lasers(self,vel,obj):
    self.cooldown()
    for laser in self.lasers:
      laser.move(vel)
      if laser.off_screen(HEIGHT):
        self.lasers.remove(laser)
      elif laser.collision(obj):
        obj.health -=10
        self.lasers.remove(laser)
        

  def cooldown(self):
    if self.cool_down_counter >= self.COOLDOWN:
      self.cool_down_counter =0
    elif self.cool_down_counter >0:
      self.cool_down_counter +=1
    
  def shoot(self):
    if self.cool_down_counter == 0:
      laser = Laser(self.x, self.y, self.laser_img)
      self.lasers.append(laser)
      self.cool_down_counter =1

  def get_width(self):
    return self.ship_img.get_width()

  def get_height(self):
    return self.ship_img.get_height() 

class Player(Ship):
  def __init__(self, x, y, health=100):
      super().__init__(x, y, health=health)
      self.ship_img= YELLOW_SPACE_SHIP
      self.laser_img = YELLOW_LASER
      self.mask = pygame.mask.from_surface(self.ship_img)
      self.max_health = health

  def shoot(self):
    if self.cool_down_counter == 0:
      laser = Laser(self.x+13, self.y, self.laser_img)
      self.lasers.append(laser)
      self.cool_down_counter =1

  def move_lasers(self,vel,objs): #The movement of the laser 
    self.cooldown()
    for laser in self.lasers:
      laser.move(vel)
      if laser.off_screen(HEIGHT): #If the laser reach the border of the screen then remove it 
        self.lasers.remove(laser)
      else: 
        for obj in objs:
          if laser.collision(obj):
            objs.remove(obj)
            if laser in self.lasers:
              self.lasers.remove(laser)

  def draw(self,window):
    super().draw(window)
    self.healthbar(window)    

  def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))    


class Enemy(Ship):
  COLOR_MAP = {
    "red":(RED_SPACE_SHIP,RED_LASER),
    "green" : (GREEN_SPACE_SHIP, GREEN_LASER),
    "blue": (BLUE_SPACE_SHIP,BLUE_LASER)
     }

  def __init__(self,x,y,color,health=100):
    super().__init__(x,y,health)
    self.ship_img, self.laser_img = self.COLOR_MAP[color]
    self.mask = pygame.mask.from_surface(self.ship_img)

  def move(self,vel):
    self.y += vel

  def shoot(self):
    if self.cool_down_counter == 0:
      laser = Laser(self.x+5, self.y, self.laser_img)
      self.lasers.append(laser)
      self.cool_down_counter =1
      


#collide function to check collision between two object
def collide(obj1, obj2):
  offset_x = obj2.x - obj1.x
  offset_y = obj2.y - obj1.y
  return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
  ingame_music() 
  run = True
  FPS=60
  level=0
  lives=3
  main_font=pygame.font.SysFont("comicsans",50) #main menu word
  lost_font = pygame.font.SysFont("comicsans", 60) #losing declare word
  laser_vel = 6 #laser velocity
  enemies = []
  wave_length=1
  enemy_vel=4


  player = Player(300, 650)


  clock=pygame.time.Clock()

  lost = False

  lost_count = 0



  def redraw_window():
    WIN.blit(BG, (0,0))
    level_label = main_font.render(f"Level: {level}", 1, (255,0,0)) #Print "Level" word on screen
    lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) #Print "Lives" word on screen
    WIN.blit(lives_label, (10,10))
    WIN.blit(level_label, (WIDTH-level_label.get_width()-10,10))

    for enemy in enemies:
      enemy.draw(WIN)

    player.draw(WIN)
    
    if lost:
      lost_label = lost_font .render("YOU LOST!", 1, (255,255,255))
      WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2,350))

    pygame.display.update()

  while run:
    clock.tick(FPS)
    redraw_window()
    if lives <= 0 or player.health <= 0:
    
      lost=True
      lost_count +=1
    
      if lost:
        menu_music()
        if lost_count > FPS*2:
          run =False 
        else:
          continue 


    if len(enemies)==0:
      level += 1
      wave_length += 2
      for i in range(wave_length):
        enemy = Enemy(random.randrange(50, WIDTH -100), random.randrange(-1500,-100), random.choice(["red", "blue", "green"]))
        enemies.append(enemy)


    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        quit()
 

    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0)) #invisible cursor

    (mouseX, mouseY) = pygame.mouse.get_pos()
 
    player.x, player.y = mouseX-player.ship_img.get_width()/2, mouseY-player.ship_img.get_height()/2  #Moving the spaceship following your cursor


    mouse_presses = pygame.mouse.get_pressed()
    if mouse_presses[0]: #If we left click then we will shoot a bullet
        player.shoot()
        bullet_sound.play()

    for enemy in enemies[:]:
      enemy.move(enemy_vel)
      enemy.move_lasers(laser_vel,player)

      if random.randrange(0, 2*60) == 1:
        enemy.shoot()

      if collide(enemy,player): #if the spaceship of player crash with spaceship of enemy 
        player.health -= 10
        enemies.remove(enemy)
        crash_sound.play()
      elif enemy.y + enemy.get_height() > HEIGHT: #if the enemy reach the bottom of the screen 
        lives -= 1
        enemies.remove(enemy)

    player.move_lasers(-laser_vel, enemies)

def main_menu():
  menu_music()
  title_font = pygame.font.SysFont("comicsans", 55)
  run = True
  while run:
    WIN.blit(BG, (0,0))
    title_label = title_font.render("Press the mouse to begin...",1,(255,255,255))
    WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2,350))
    pygame.display.update()
    for event in pygame.event.get():
      if event.type == pygame.QUIT: #
        run = False
      if event.type ==pygame.MOUSEBUTTONDOWN:
        main()
        

  pygame.quit()  

main_menu()      
     