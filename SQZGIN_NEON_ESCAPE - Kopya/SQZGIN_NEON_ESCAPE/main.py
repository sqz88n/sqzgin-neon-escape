import pygame, sys
from settings import WIDTH, HEIGHT, FPS, TITLE
from save_manager import load_profile, save_profile
from audio_manager import AudioManager
from game import Game

def main():
    pygame.init()
    profile=load_profile()
    flags=pygame.FULLSCREEN if profile["settings"].get("fullscreen") else pygame.RESIZABLE
    screen=pygame.display.set_mode((WIDTH,HEIGHT),flags)
    pygame.display.set_caption(TITLE)
    clock=pygame.time.Clock()
    audio=AudioManager(profile)
    game=Game(screen,profile,audio,lambda: save_profile(profile))
    running=True
    while running:
        dt=min(clock.tick(FPS)/1000.0,.04)
        events=pygame.event.get()
        for event in events:
            if event.type==pygame.QUIT:running=False
            elif event.type==pygame.VIDEORESIZE and not profile["settings"].get("fullscreen"):
                screen=pygame.display.set_mode((max(480,event.w),max(640,event.h)),pygame.RESIZABLE)
                game.screen=screen; game.ui.screen=screen
        game.update(dt,events)
        game.draw()
        pygame.display.flip()
    save_profile(profile)
    pygame.quit()
    sys.exit(0)

if __name__=="__main__": main()
