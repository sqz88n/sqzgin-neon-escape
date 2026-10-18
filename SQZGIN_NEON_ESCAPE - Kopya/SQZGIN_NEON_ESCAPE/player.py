import math, pygame
from settings import CYAN, BLUE, WHITE

class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.radius = 19
        self.speed = 340.0
        self.vx = self.vy = 0.0
        self.dash_left = 0.0
        self.dash_cooldown = 0.0
        self.shield = 0.0
        self.magnet = 0.0
        self.slow = 0.0
        self.multiplier = 0.0
        self.invulnerable = 0.0
        self.trail = []

    def dash(self, dx, dy):
        if self.dash_cooldown > 0: return False
        if dx == 0 and dy == 0: dy = -1
        length = math.hypot(dx, dy) or 1
        self.vx, self.vy = dx/length * 900, dy/length * 900
        self.dash_left, self.dash_cooldown = .16, 1.4
        self.invulnerable = .22
        return True

    def update(self, dt, keys, width, height, touch_vector=(0,0)):
        dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(keys[pygame.K_w] or keys[pygame.K_UP])
        dx += touch_vector[0]; dy += touch_vector[1]
        length = math.hypot(dx,dy)
        if length: dx,dy=dx/length,dy/length
        if self.dash_left > 0:
            self.x += self.vx*dt; self.y += self.vy*dt; self.dash_left=max(0,self.dash_left-dt)
        else:
            self.x += dx*self.speed*dt; self.y += dy*self.speed*dt
        self.dash_cooldown=max(0,self.dash_cooldown-dt)
        for attr in ("shield","magnet","slow","multiplier","invulnerable"):
            setattr(self, attr, max(0, getattr(self,attr)-dt))
        self.x=max(self.radius+8,min(width-self.radius-8,self.x))
        self.y=max(110,min(height-100,self.y))
        self.trail.append((self.x,self.y))
        if len(self.trail)>12: self.trail.pop(0)

    def draw(self, surface, t, color=CYAN):
        for i,(x,y) in enumerate(self.trail[:-1]):
            alpha=(i+1)/len(self.trail)
            r=max(2,int(self.radius*.45*alpha))
            pygame.draw.circle(surface, (int(color[0]*alpha*.5),int(color[1]*alpha*.5),int(color[2]*alpha*.5)),(int(x),int(y)),r)
        x,y=int(self.x),int(self.y)
        points=[(x,y-self.radius-7),(x+self.radius,y),(x,y+self.radius+7),(x-self.radius,y)]
        pygame.draw.polygon(surface,(10,45,72),points)
        pygame.draw.polygon(surface,color,points,3)
        pygame.draw.circle(surface,WHITE,(x,y),7)
        pygame.draw.circle(surface,(100,250,255),(x,y),3)
        if self.shield>0:
            pygame.draw.circle(surface,(94,190,255),(x,y),self.radius+10,2)
