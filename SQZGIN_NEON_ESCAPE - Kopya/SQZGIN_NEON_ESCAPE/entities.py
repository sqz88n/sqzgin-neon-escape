# -*- coding: utf-8 -*-
import math, random, pygame
from settings import CYAN, PURPLE, GOLD, RED, PINK, BLUE

class Particle:
    def __init__(self,x,y,color):
        a=random.random()*math.tau; speed=random.uniform(35,210)
        self.x,self.y=x,y; self.vx,self.vy=math.cos(a)*speed,math.sin(a)*speed
        self.life=self.max_life=random.uniform(.25,.65); self.color=color
    def update(self,dt):
        self.life-=dt; self.x+=self.vx*dt; self.y+=self.vy*dt; self.vx*=.98; self.vy*=.98
    def draw(self,s):
        if self.life>0:
            r=max(1,int(4*self.life/self.max_life))
            pygame.draw.circle(s,self.color,(int(self.x),int(self.y)),r)

class Obstacle:
    def __init__(self, x, y, w, h, kind, speed):
        self.x,self.y,self.w,self.h,self.kind,self.speed=x,y,w,h,kind,speed
        self.phase=random.random()*6.28
    def update(self,dt,t):
        self.y+=self.speed*dt
        if self.kind=="moving": self.x+=math.sin(t*2+self.phase)*90*dt
    def rect(self):
        return pygame.Rect(int(self.x),int(self.y),int(self.w),int(self.h))
    def draw(self,s,t):
        r=self.rect(); col=PURPLE if self.kind=="moving" else PINK if self.kind=="spike" else (255,65,94)
        if self.kind=="spike":
            pts=[(r.centerx,r.top),(r.right,r.bottom),(r.left,r.bottom)]
            pygame.draw.polygon(s,(60,12,48),pts); pygame.draw.polygon(s,col,pts,3)
        else:
            pygame.draw.rect(s,(35,12,52),r,border_radius=7)
            pygame.draw.rect(s,col,r,2,border_radius=7)
            pygame.draw.line(s,col,(r.left+5,r.centery),(r.right-5,r.centery),2)

class Crystal:
    COLORS={
        "cyan":CYAN,
        "purple":PURPLE,
        "gold":GOLD,
        "energy":BLUE,
        "shield":(95,180,255),
        "magnet":PINK,
        "slow":(120,255,160),
        "multiplier":(255,130,65),
        "hp":(50,255,100),       # Can paketi
        "ulti_coin":GOLD         # ULTI kristali
    }
    VALUE={
        "cyan":10,
        "purple":25,
        "gold":75,
        "energy":15,
        "shield":15,
        "magnet":15,
        "slow":15,
        "multiplier":25,
        "hp":0,
        "ulti_coin":50
    }
    def __init__(self,x,y,kind="cyan",speed=190):
        self.x,self.y,self.kind,self.speed=x,y,kind,speed
        self.phase=random.random()*6.28
        self.radius=12 if kind!="gold" else 15
    def update(self,dt,t):
        self.y+=self.speed*dt; self.phase+=dt*3
    def draw(self,s,t):
        col=self.COLORS.get(self.kind, CYAN); x,y=int(self.x),int(self.y+math.sin(self.phase)*3); r=self.radius
        pts=[(x,y-r),(x+r,y),(x,y+r),(x-r,y)]
        pygame.draw.polygon(s,tuple(c//4 for c in col),pts)
        pygame.draw.polygon(s,col,pts,2)
        pygame.draw.circle(s,col,(x,y),3)