# -*- coding: utf-8 -*-
import pygame
import math
from settings import *


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.fonts = {}
        self.touch_controls = TouchControls(screen)

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = pygame.font.SysFont("consolas", size, bold=bold)
        return self.fonts[key]

    def text(self, txt, x, y, size=22, color=WHITE, center=False, bold=False):
        surf = self.font(size, bold).render(str(txt), True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (int(x), int(y))
        else:
            rect.topleft = (int(x), int(y))
        self.screen.blit(surf, rect)
        return rect

    def button(self, txt, rect, mouse, selected=False, enabled=True):
        r = pygame.Rect(rect)
        hover = r.collidepoint(mouse)
        col = CYAN if hover or selected else (55, 100, 145)
        if not enabled:
            col = (45, 58, 75)
        pygame.draw.rect(self.screen, (8, 20, 42), r, border_radius=10)
        pygame.draw.rect(self.screen, col, r, 2, border_radius=10)
        muted_color = globals().get("MUTED", (100, 100, 100))
        self.text(txt, r.centerx, r.centery, 20, col if enabled else muted_color, True, True)
        return r

    def panel(self, rect):
        pygame.draw.rect(self.screen, (8, 16, 38), rect, border_radius=18)
        pygame.draw.rect(self.screen, (37, 100, 139), rect, 2, border_radius=18)

    def background(self, t):
        s = self.screen
        s.fill(BG)
        w, h = s.get_size()

        for i in range(55):
            x = (i * 137 + int(t * (12 + i % 5) * 3)) % w
            y = (i * 83 + int(t * (24 + i % 4) * 4)) % h
            pygame.draw.circle(s, (20, 65, 95), (x, y), 1 + (i % 3 == 0))

        horizon = int(h * 0.43)
        for i in range(12):
            y = horizon + int(((i / 12) ** 1.7) * (h - horizon))
            pygame.draw.line(s, (10, 35, 62), (0, y), (w, y), 1)

        for x in range(-w, w * 2, 70):
            pygame.draw.line(s, (9, 30, 55), (w // 2, horizon), (x, h), 1)

        for i in range(13):
            bw = 30 + (i * 17) % 48
            bh = 55 + (i * 31) % 120
            x = i * w // 13
            pygame.draw.rect(s, (7, 14, 34), (x, horizon - bh, bw, bh))
            for wy in range(horizon - bh + 12, horizon - 8, 18):
                pygame.draw.rect(s, (12, 58, 80), (x + 7, wy, 4, 5))


class TouchControls:
    """Görev Çubuğunun Üstüne Çıkarılmış Tam D-Pad ve Mobil Butonlar"""

    def __init__(self, screen):
        w, h = screen.get_size()
        self.w, self.h = w, h

        # D-Pad Merkez Konumu
        self.cx, self.cy = 130, h - 180
        self.arm_w = 54
        self.arm_l = 150

        half_w = self.arm_w // 2
        half_l = self.arm_l // 2

        self.btn_up = pygame.Rect(self.cx - half_w, self.cy - half_l, self.arm_w, half_l - 10)
        self.btn_down = pygame.Rect(self.cx - half_w, self.cy + 10, self.arm_w, half_l - 10)
        self.btn_left = pygame.Rect(self.cx - half_l, self.cy - half_w, half_l - 10, self.arm_w)
        self.btn_right = pygame.Rect(self.cx + 10, self.cy - half_w, half_l - 10, self.arm_w)

        # Sağ taraftaki Dash butonu
        self.btn_dash = pygame.Rect(w - 95, h - 180, 75, 75)

        # Sağ taraftaki ULTI Butonu (Dash'in solunda)
        self.btn_ulti = pygame.Rect(w - 185, h - 180, 80, 75)

        self.ulti_charge = 0.0

        # Pygame font nesnelerini doğrudan burada güvenli şekilde oluşturuyoruz
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_charge = pygame.font.SysFont("Arial", 14, bold=True)

    def draw(self, surface):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        cx, cy = self.cx, self.cy
        w = self.arm_w
        l = self.arm_l

        # Birleşik Artı Gövdesi
        dpad_color = (25, 35, 48, 220)
        border_color = CYAN

        v_rect = pygame.Rect(cx - w // 2, cy - l // 2, w, l)
        h_rect = pygame.Rect(cx - l // 2, cy - w // 2, l, w)

        pygame.draw.rect(overlay, dpad_color, v_rect, border_radius=18)
        pygame.draw.rect(overlay, dpad_color, h_rect, border_radius=18)
        pygame.draw.rect(overlay, border_color, v_rect, 2, border_radius=18)
        pygame.draw.rect(overlay, border_color, h_rect, 2, border_radius=18)

        # Ortadaki Siyah Yuvarlak Göbek
        pygame.draw.circle(overlay, (15, 20, 28, 240), (cx, cy), 14)
        pygame.draw.circle(overlay, (40, 60, 80), (cx, cy), 14, 1)

        # Yön Üçgenleri
        pygame.draw.polygon(overlay, WHITE,
                            [(cx, cy - l // 2 + 10), (cx - 11, cy - l // 2 + 27), (cx + 11, cy - l // 2 + 27)])
        pygame.draw.polygon(overlay, WHITE,
                            [(cx, cy + l // 2 - 10), (cx - 11, cy + l // 2 - 27), (cx + 11, cy + l // 2 - 27)])
        pygame.draw.polygon(overlay, WHITE,
                            [(cx - l // 2 + 10, cy), (cx - l // 2 + 27, cy - 11), (cx - l // 2 + 27, cy + 11)])
        pygame.draw.polygon(overlay, WHITE,
                            [(cx + l // 2 - 10, cy), (cx + l // 2 - 27, cy - 11), (cx + l // 2 - 27, cy + 11)])

        # Dash Butonu
        pygame.draw.rect(overlay, (255, 0, 127, 90), self.btn_dash, border_radius=18)
        pygame.draw.rect(overlay, (255, 0, 127), self.btn_dash, 2, border_radius=18)

        # ULTI Butonu Arka Planı (Şarj durumuna göre renk değişimi)
        is_ready = self.ulti_charge >= 100.0
        ulti_bg = (255, 180, 0, 160) if is_ready else (45, 60, 90, 140)
        ulti_border = GOLD if is_ready else CYAN

        pygame.draw.rect(overlay, ulti_bg, self.btn_ulti, border_radius=18)
        pygame.draw.rect(overlay, ulti_border, self.btn_ulti, 2, border_radius=18)

        surface.blit(overlay, (0, 0))

        # DASH Yazısı
        surface.blit(self.font.render("DASH", True, WHITE), (self.btn_dash.centerx - 24, self.btn_dash.centery - 10))

        # ULTI Butonunun İçine İki Satır Halinde Tertemiz Yazıyoruz (Üstte Başlık, Altta Yüzde/Hazır)
        title_surf = self.font_charge.render("ULTI", True, GOLD if is_ready else WHITE)
        surface.blit(title_surf, (self.btn_ulti.centerx - title_surf.get_width() // 2, self.btn_ulti.centery - 20))

        charge_str = "HAZIR!" if is_ready else f"%{int(self.ulti_charge)}"
        charge_surf = self.font_charge.render(charge_str, True, GOLD if is_ready else CYAN)
        surface.blit(charge_surf, (self.btn_ulti.centerx - charge_surf.get_width() // 2, self.btn_ulti.centery + 2))

    def get_active_inputs(self):
        inputs = {"left": False, "right": False, "up": False, "down": False, "dash": False, "ulti": False}
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if mouse_pressed[0]:
            if self.btn_left.collidepoint(mouse_pos):
                inputs["left"] = True
            if self.btn_right.collidepoint(mouse_pos):
                inputs["right"] = True
            if self.btn_up.collidepoint(mouse_pos):
                inputs["up"] = True
            if self.btn_down.collidepoint(mouse_pos):
                inputs["down"] = True
            if self.btn_dash.collidepoint(mouse_pos):
                inputs["dash"] = True
            if self.btn_ulti.collidepoint(mouse_pos):
                inputs["ulti"] = True

        return inputs