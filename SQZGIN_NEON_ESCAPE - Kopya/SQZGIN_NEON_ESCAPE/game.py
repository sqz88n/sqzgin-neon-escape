# -*- coding: utf-8 -*-
import math, random, pygame
from settings import *
from player import Player
from entities import Particle, Obstacle, Crystal
from ui import UI
from server import FrameStore, start_server


class Boss:
    def __init__(self, w, level_num):
        self.w = w
        self.x = w / 2
        self.y = 120
        self.max_hp = 300 + (level_num // 5) * 100
        self.hp = self.max_hp
        self.speed = 140
        self.dir = 1
        self.shoot_timer = 0.0
        self.lasers = []

    def update(self, dt, player_x):
        self.x += self.speed * self.dir * dt
        if self.x < 80:
            self.x = 80
            self.dir = 1
        elif self.x > self.w - 80:
            self.x = self.w - 80
            self.dir = -1

        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = random.uniform(1.0, 1.8)
            self.lasers.append({"x": self.x, "y": self.y + 30, "speed": 350})

        for l in self.lasers:
            l["y"] += l["speed"] * dt
        self.lasers = [l for l in self.lasers if l["y"] < 900]

    def draw(self, surface, t):
        size = 45 + math.sin(t * 5) * 5
        pts = [
            (self.x, self.y - size),
            (self.x + size, self.y),
            (self.x, self.y + size),
            (self.x - size, self.y)
        ]
        pygame.draw.polygon(surface, RED, pts, 3)
        pygame.draw.polygon(surface, (255, 100, 100), pts, 0)

        bar_w = 220
        bar_h = 14
        bx = (self.w / 2) - (bar_w / 2)
        by = 25
        pygame.draw.rect(surface, (40, 10, 20), (bx, by, bar_w, bar_h), border_radius=4)
        pct = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, RED, (bx, by, bar_w * pct, bar_h), border_radius=4)
        pygame.draw.rect(surface, WHITE, (bx, by, bar_w, bar_h), 1, border_radius=4)

        for l in self.lasers:
            pygame.draw.circle(surface, RED, (int(l["x"]), int(l["y"])), 9)
            pygame.draw.circle(surface, WHITE, (int(l["x"]), int(l["y"])), 4)


class Game:
    def __init__(self, screen, profile, audio, save_callback):
        self.screen = screen
        self.profile = profile
        self.audio = audio
        self.save_callback = save_callback
        self.ui = UI(screen)
        self.state = "menu"
        self.mode = "classic"
        self.t = 0
        self.mouse = (0, 0)
        self.buttons = []
        self.last_run = None
        self.shop_page = 0
        self.levels_page = 0
        self.current_level = 1
        self.code_input = ""
        self.code_message = ""
        self.boss = None
        self.player_hp = 2000
        self.max_player_hp = 2000
        self.ulti_charge = 0.0

        if "unlocked_levels" not in self.profile:
            self.profile["unlocked_levels"] = 1
            self.save_callback()

        self.shop_items = [
            ("item_shield", "NEON KALKAN ŞARJI", 50, "Oyuna 15s kalkanla başla"),
            ("item_magnet", "KUANTUM MIKNATISI", 80, "Oyuna 20s mıknatısla başla"),
            ("item_mult", "PLAZMA ÇARPANI (X2)", 120, "İlk 25s 2 kat fazla coin kazandırır"),
            ("item_speed", "SİBER HIZLANDIRICI", 100, "İlk 20s ekstra oyuncu hızı verir"),
            ("item_aura", "AURA SİNYALİ", 150, "Oyuncunun etrafında neon halka oluşturur"),
            ("item_laser_nerf", "LAZER NÖTRLEYİCİ", 200, "Lazerin yükselme hızını yavaşlatır"),
            ("item_slow_matrix", "MATRİX YAVAŞLATICI", 130, "Engeller %20 daha yavaş düşer"),
            ("item_crystal_bat", "KRİSTAL BATARYASI", 90, "Özel kristalleri daha sık çıkarır"),
            ("item_vip", "SQZ VIP BİLET", 500, "Tüm koşularda ekstra %50 skor bonusu"),
            ("item_trail", "ALEVLİ İZ EFEKTİ", 220, "Arka planda özel alev efekti bırakır"),
            ("item_shadow_dash", "GÖLGE DASH MODU", 300, "Dash atarken engellerin içinden geçer"),
            ("item_sound_wave", "SİBER SES DALGASI", 175, "Kristal toplayınca patlama efekti yapar"),
            ("item_mega_mag", "MEGA MIKNATIS PRO", 250, "Mıknatıs süresini 2 katına çıkarır"),
            ("item_luck", "ŞANS KRİSTALİ", 110, "Nadir kristal çıkma ihtimalini artırır"),
            ("item_overclock", "OVERCLOCK ÇİPİ", 400, "Dash bekleme süresini 3sn'ye düşürür")
        ]
        self.reset_run()

        # RAM tabanlı ultra hızlı MJPEG akış deposu ve sunucusu
        self.stream_store = FrameStore()
        self.stream_server = start_server(self.stream_store)

    def get_level_info(self, lvl):
        is_boss = (lvl % 5 == 0)
        target_score = lvl * 150
        target_crystals = 10 + lvl * 2
        return {"is_boss": is_boss, "target_score": target_score, "target_crystals": target_crystals}

    def reset_run(self, mode=None):
        if mode: self.mode = mode
        w, h = self.screen.get_size()
        self.player = Player(w / 2, h * .68)
        self.player_hp = 2000
        self.max_player_hp = 2000
        self.ulti_charge = 0.0

        unlocked = self.profile.setdefault("shop_items", [])

        self.shop_shield_timer = 15.0 if "item_shield" in unlocked else 0.0
        self.shop_magnet_timer = 20.0 if "item_magnet" in unlocked else 0.0
        self.shop_mult_timer = 25.0 if "item_mult" in unlocked else 0.0
        self.shop_speed_timer = 20.0 if "item_speed" in unlocked else 0.0

        if self.shop_shield_timer > 0:
            self.player.shield = self.shop_shield_timer

        self.obstacles = []
        self.crystals = []
        self.particles = []
        self.elapsed = 0
        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.collected = 0
        self.distance = 0
        self.laser_y = h + 100
        self.spawn_timer = .7
        self.crystal_timer = .4
        self.shake = 0
        self.ended = False
        self.run_coins = 0
        self.near_misses = 0
        self.target_time = 60 if self.mode == "time" else 0
        self.target_crystals = 30 if self.mode == "crystal" else 0

        if self.mode == "level":
            lvl_info = self.get_level_info(self.current_level)
            if lvl_info["is_boss"]:
                self.boss = Boss(w, self.current_level)
            else:
                self.boss = None
        else:
            self.boss = None

    def start(self, mode="classic", level=1):
        self.current_level = level
        self.reset_run(mode)
        self.state = "play"

    def burst(self, x, y, color, count=14):
        if not self.profile["settings"].get("particles", True): return
        for _ in range(min(count, 80)):
            if len(self.particles) < 260: self.particles.append(Particle(x, y, color))

    def trigger_ulti(self):
        if self.ulti_charge >= 100.0:
            self.ulti_charge = 0.0
            self.audio.play("dash")
            w, h = self.screen.get_size()

            cleared_count = len(self.obstacles)
            for o in self.obstacles:
                self.burst(o.x + o.w / 2, o.y + o.h / 2, GOLD, 18)
            self.obstacles.clear()

            self.score += cleared_count * 100
            self.run_coins += cleared_count * 3

            if self.boss:
                self.boss.hp -= 200

            self.burst(w / 2, h / 2, GOLD, 60)

    def finish(self, victory=False):
        if self.ended: return
        self.ended = True
        self.state = "gameover"

        final_coins = self.run_coins
        if self.shop_mult_timer > 0 or self.player.multiplier > 0:
            final_coins *= 2

        final_score = int(self.score)
        if "item_vip" in self.profile.setdefault("shop_items", []):
            final_score = int(final_score * 1.5)

        if self.mode == "level" and victory:
            max_unlocked = self.profile.get("unlocked_levels", 1)
            if self.current_level >= max_unlocked and self.current_level < 30:
                self.profile["unlocked_levels"] = self.current_level + 1
            completed = self.profile.setdefault("completed_levels", [])
            if self.current_level not in completed:
                completed.append(self.current_level)
            self.save_callback()

        self.profile["last_score"] = final_score
        self.profile["high_score"] = max(self.profile["high_score"], final_score)
        self.profile["games"] += 1
        self.profile["total_seconds"] += self.elapsed
        self.profile["total_crystals"] += self.collected
        self.profile["coins"] += final_coins
        self.profile["best_combo"] = max(self.profile.get("best_combo", 0), self.best_combo)

        ach = self.profile.setdefault("achievements", [])
        for key, cond in [("İlk Koşu", self.profile["games"] >= 1),
                          ("Kristal Avcısı", self.profile["total_crystals"] >= 50),
                          ("Uzun Mesafe", self.profile["high_score"] >= 1000), ("Kombo Ustası", self.best_combo >= 10)]:
            if cond and key not in ach: ach.append(key)
        self.save_callback()
        self.last_run = {"score": final_score, "time": self.elapsed, "crystals": self.collected,
                         "combo": self.best_combo, "coins": final_coins, "victory": victory}
        self.audio.play("hit")

    def update(self, dt, events):
        self.t += dt
        self.mouse = pygame.mouse.get_pos()
        w, h = self.screen.get_size()
        touch_inputs = self.ui.touch_controls.get_active_inputs()

        unlocked = self.profile.setdefault("shop_items", [])

        if self.state == "play":
            keys = pygame.key.get_pressed()
            if any(e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE for e in events): self.state = "pause"; return

            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.ui.touch_controls.btn_ulti.collidepoint(e.pos):
                        self.trigger_ulti()

            if self.shop_shield_timer > 0:
                self.shop_shield_timer -= dt
                if self.shop_shield_timer <= 0 and self.player.shield <= 15.0: self.player.shield = 0
            if self.shop_magnet_timer > 0: self.shop_magnet_timer -= dt
            if self.shop_mult_timer > 0: self.shop_mult_timer -= dt
            if self.shop_speed_timer > 0:
                self.shop_speed_timer -= dt
                current_speed = self.player.speed * 1.25
            else:
                current_speed = self.player.speed

            space_pressed = any(e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE for e in events) or touch_inputs[
                "dash"] or touch_inputs.get("ulti", False)

            if touch_inputs.get("ulti", False) and self.ulti_charge >= 100.0:
                self.trigger_ulti()

            if space_pressed:
                left_pressed = keys[pygame.K_a] or keys[pygame.K_LEFT] or touch_inputs["left"]
                right_pressed = keys[pygame.K_d] or keys[pygame.K_RIGHT] or touch_inputs["right"]
                up_pressed = keys[pygame.K_w] or keys[pygame.K_UP] or touch_inputs["up"]
                down_pressed = keys[pygame.K_s] or keys[pygame.K_DOWN] or touch_inputs["down"]

                dx = float(right_pressed) - float(left_pressed)
                dy = float(down_pressed) - float(up_pressed)
                if dx == 0 and dy == 0:
                    dx = 1
                try:
                    cd = 3.0 if "item_overclock" in unlocked else 5.0
                    if self.player.dash(dx, dy):
                        self.audio.play("dash")
                        self.burst(self.player.x, self.player.y, CYAN, 12)
                        self.player.dash_cooldown = cd
                        if self.boss:
                            if math.hypot(self.player.x - self.boss.x, self.player.y - self.boss.y) < 90:
                                self.boss.hp -= 40
                except Exception:
                    pass

            self.elapsed += dt
            self.distance += dt * 10
            self.player.update(dt, keys, w, h)

            if touch_inputs["left"]:
                self.player.x -= current_speed * dt
            if touch_inputs["right"]:
                self.player.x += current_speed * dt
            if touch_inputs["up"]:
                self.player.y -= current_speed * dt
            if touch_inputs["down"]:
                self.player.y += current_speed * dt

            self.player.x = max(self.player.radius, min(w - self.player.radius, self.player.x))
            self.player.y = max(h * 0.10, min(h - self.player.radius, self.player.y))

            difficulty = min(2.5, self.elapsed / 55)
            slow = .45 if self.player.slow > 0 else 1

            laser_speed_mult = 0.8 if "item_laser_nerf" in unlocked else 1.0
            self.laser_y -= (12 + self.elapsed * 0.18) * dt * laser_speed_mult

            if self.boss:
                self.boss.update(dt, self.player.x)
                self.boss.hp -= dt * 3.0
                for l in self.boss.lasers:
                    if math.hypot(self.player.x - l["x"], self.player.y - l["y"]) < self.player.radius + 8:
                        if self.player.shield > 0:
                            self.player.shield = 0
                            self.shop_shield_timer = 0
                        else:
                            if self.mode == "level":
                                self.player_hp -= 150
                                self.burst(self.player.x, self.player.y, RED, 15)
                                if self.player_hp <= 0:
                                    self.finish(victory=False)
                                    return
                            else:
                                self.finish(victory=False)
                                return
                if self.boss.hp <= 0:
                    self.finish(victory=True)
                    return

            self.spawn_timer -= dt
            interval = max(.42, 1.05 - difficulty * .22)
            if self.spawn_timer <= 0:
                self.spawn_timer = interval * random.uniform(.78, 1.2)
                lane = random.randint(0, 5)
                ow = random.randint(58, 105)
                ox = max(12, min(w - ow - 12, lane * w / 6 + random.randint(-12, 12)))
                kind = random.choices(["block", "moving", "spike"], [.55, .25, .20])[0]
                px = self.player.x
                if abs((ox + ow / 2) - px) > 105:
                    obs_speed_mult = 0.8 if "item_slow_matrix" in unlocked else 1.0
                    self.obstacles.append(Obstacle(ox, -75, ow, random.randint(28, 52), kind,
                                                   (210 + difficulty * 55) * slow * obs_speed_mult))
            self.crystal_timer -= dt
            if self.crystal_timer <= 0:
                self.crystal_timer = random.uniform(.4, .7)
                kind = random.choices(
                    ["cyan", "purple", "gold", "energy", "shield", "magnet", "slow", "multiplier", "ulti_coin"],
                    [.30, .12, .06, .06, .05, .04, .04, .03, .24])[0]
                self.crystals.append(Crystal(random.randint(35, w - 35), -25, kind, (170 + difficulty * 28) * slow))
            for o in self.obstacles: o.update(dt, self.elapsed)
            for c in self.crystals: c.update(dt, self.elapsed)
            self.obstacles = [o for o in self.obstacles if o.y < h + 100]
            self.crystals = [c for c in self.crystals if c.y < h + 60]
            for p in self.particles: p.update(dt)
            self.particles = [p for p in self.particles if p.life > 0]
            pr = pygame.Rect(int(self.player.x - 14), int(self.player.y - 14), 28, 28)
            hit = None
            for o in self.obstacles:
                if pr.colliderect(o.rect()): hit = o; break
            if hit and self.mode != "training":
                if self.player.shield > 0:
                    self.player.shield = 0
                    self.shop_shield_timer = 0
                    self.obstacles.remove(hit)
                    self.burst(self.player.x, self.player.y, BLUE, 24)
                elif self.player.invulnerable <= 0:
                    if self.mode == "level":
                        self.player_hp -= 300
                        self.obstacles.remove(hit)
                        self.burst(self.player.x, self.player.y, RED, 25)
                        if self.player_hp <= 0:
                            self.finish(victory=False)
                            return
                    else:
                        self.finish(victory=False)
                        return
            for c in self.crystals[:]:
                magnet_active = (self.player.magnet > 0) or (self.shop_magnet_timer > 0)
                magnet_range = 520 if "item_mega_mag" in unlocked else 260
                mag_time = 14 if "item_mega_mag" in unlocked else 7

                if magnet_active:
                    dx, dy = self.player.x - c.x, self.player.y - c.y
                    dist = math.hypot(dx, dy)
                    if 0 < dist < magnet_range:
                        c.x += (dx / dist) * 260 * dt
                        c.y += (dy / dist) * 260 * dt

                if math.hypot(self.player.x - c.x, self.player.y - c.y) < self.player.radius + c.radius:
                    self.crystals.remove(c)
                    self.collected += 1
                    self.combo += 1
                    self.best_combo = max(self.best_combo, self.combo)
                    mult = 2 if (self.player.multiplier > 0 or self.shop_mult_timer > 0) else 1

                    if c.kind == "ulti_coin":
                        self.ulti_charge = min(100.0, self.ulti_charge + 25.0)
                        self.audio.play("coin")
                        self.burst(c.x, c.y, GOLD, 18)
                    elif c.kind == "hp" and self.mode == "level":
                        self.player_hp = min(self.max_player_hp, self.player_hp + 500)
                        self.audio.play("coin")
                        self.burst(c.x, c.y, GREEN, 15)
                    else:
                        if c.kind != "hp":
                            self.score += Crystal.VALUE[c.kind] * mult
                            self.run_coins += max(1, Crystal.VALUE[c.kind] // 10)
                            if c.kind == "shield":
                                self.player.shield = 6.0
                            elif c.kind == "magnet":
                                self.player.magnet = mag_time
                            elif c.kind == "slow":
                                self.player.slow = 5.0
                            elif c.kind == "multiplier":
                                self.player.multiplier = 8.0
                            elif c.kind == "energy":
                                self.player.dash_cooldown = 0
                            if self.boss: self.boss.hp -= 15.0
                            self.audio.play("coin")
                            self.burst(c.x, c.y, Crystal.COLORS[c.kind], 12)
                elif c.y > self.player.y + 100:
                    self.combo = 0
            self.score += dt * (5 + min(10, self.elapsed / 12))
            if self.laser_y <= self.player.y + self.player.radius:
                if self.player.shield > 0:
                    self.player.shield = 0
                    self.shop_shield_timer = 0
                    self.laser_y = self.player.y + 90
                else:
                    if self.mode == "level":
                        self.player_hp -= 400
                        self.laser_y += 100
                        if self.player_hp <= 0:
                            self.finish(victory=False)
                            return
                    else:
                        self.finish(victory=False)
                        return
            if self.mode == "time" and self.elapsed >= self.target_time: self.finish(victory=True)
            if self.mode == "crystal" and self.collected >= self.target_crystals: self.finish(victory=True)

            if self.mode == "level" and not self.boss:
                info = self.get_level_info(self.current_level)
                if self.score >= info["target_score"] and self.collected >= info["target_crystals"]:
                    self.finish(victory=True)

        elif self.state == "menu":
            for e in events:
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE): self.start()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    for label, rect, action in self.buttons:
                        if rect.collidepoint(e.pos): self.activate(action)
        elif self.state in ("pause", "gameover", "settings", "garage", "missions", "achievements", "stats", "howto",
                            "shop", "sq_cod", "levels"):
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.state = "play" if self.state == "pause" else "menu"
                if self.state == "sq_cod":
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_BACKSPACE:
                            self.code_input = self.code_input[:-1]
                        elif e.key == pygame.K_RETURN:
                            self.check_code()
                        elif e.unicode.isprintable() and len(self.code_input) < 20:
                            self.code_input += e.unicode
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    for label, rect, action in self.buttons:
                        if rect.collidepoint(e.pos): self.activate(action)

    def check_code(self):
        val = self.code_input.strip().lower()
        if val == "sqjeton8888":
            self.profile["coins"] += 8888888
            self.save_callback()
            self.code_message = "KOD BAŞARILI! +8,888,888 SQ-JETON EKLENDİ!"
        elif val == "sqsifirla8888":
            self.profile["shop_items"] = []
            self.profile["unlocked_levels"] = 1
            self.profile["completed_levels"] = []
            self.save_callback()
            self.code_message = "TÜM İLERLEME VE MAĞAZA SIFIRLANDI!"
        else:
            self.code_message = "GEÇERSİZ VEYA YANLIŞ KOD!"

    def activate(self, action):
        self.audio.play("click")
        if action == "play":
            self.start("classic")
        elif action == "time":
            self.start("time")
        elif action == "crystal":
            self.start("crystal")
        elif action == "training":
            self.start("training")
        elif action == "hardcore":
            self.start("hardcore")
        elif action == "resume":
            self.state = "play"
        elif action == "restart":
            self.start(self.mode, self.current_level)
        elif action == "menu":
            self.state = "menu"
        elif action == "quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif action == "settings":
            self.state = "settings"
        elif action == "garage":
            self.state = "garage"
        elif action == "shop":
            self.state = "shop"
        elif action == "levels":
            self.state = "levels"
        elif action == "sq_cod":
            self.state = "sq_cod"
            self.code_input = ""
            self.code_message = ""
        elif action == "submit_code":
            self.check_code()
        elif action == "shop_next":
            self.shop_page = (self.shop_page + 1) % 3
        elif action == "shop_prev":
            self.shop_page = (self.shop_page - 1) % 3
        elif action == "lvl_next":
            self.levels_page = (self.levels_page + 1) % 3
        elif action == "lvl_prev":
            self.levels_page = (self.levels_page - 1) % 3
        elif action == "missions":
            self.state = "missions"
        elif action == "achievements":
            self.state = "achievements"
        elif action == "stats":
            self.state = "stats"
        elif action == "howto":
            self.state = "howto"
        elif action == "shake":
            self.profile["settings"]["shake"] = not self.profile["settings"]["shake"]
            self.save_callback()
        elif action == "particles":
            self.profile["settings"]["particles"] = not self.profile["settings"]["particles"]
            self.save_callback()
        elif action.startswith("play_level:"):
            lvl = int(action.split(":")[1])
            self.start("level", lvl)
        elif action.startswith("buy_item:"):
            item_id = action.split(":", 1)[1]
            unlocked = self.profile.setdefault("shop_items", [])
            for item in self.shop_items:
                if item[0] == item_id and item_id not in unlocked:
                    if self.profile["coins"] >= item[2]:
                        self.profile["coins"] -= item[2]
                        unlocked.append(item_id)
                        self.save_callback()
        elif action.startswith("claim_mission:"):
            m_id = int(action.split(":")[1])
            claimed = self.profile.setdefault("claimed_missions", [])
            if m_id not in claimed:
                rewards = [100, 150, 200]
                self.profile["coins"] += rewards[m_id]
                claimed.append(m_id)
                self.save_callback()
        elif action.startswith("skin:"):
            skin = action.split(":", 1)[1]
            costs = {"cyan": 0, "purple": 100, "gold": 250, "pink": 180}
            if skin in self.profile["unlocked"] or self.profile["coins"] >= costs[skin]:
                if skin not in self.profile["unlocked"]:
                    self.profile["coins"] -= costs[skin]
                    self.profile["unlocked"].append(skin)
                self.profile["skin"] = skin
                self.save_callback()

    def draw(self):
        s = self.screen
        w, h = s.get_size()
        self.ui.background(self.t)
        self.buttons = []
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "play":
            self.draw_play()
        elif self.state == "pause":
            self.draw_play()
            self.draw_overlay("DURAKLATILDI", [("DEVAM ET", "resume"), ("TEKRAR OYNA", "restart"), ("ANA MENÜ", "menu")])
        elif self.state == "gameover":
            self.draw_gameover()
        else:
            self.draw_submenu()

        # Ekrandaki kareyi RAM'deki akış deposuna doğrudan yayınlar
        self.stream_store.publish(self.screen)

    def add_button(self, label, action, y, width=300, x=None, enabled=True):
        w = self.screen.get_width()
        x = (w - width) // 2 if x is None else x
        r = self.ui.button(label, (x, y, width, 44), self.mouse, enabled=enabled)
        if enabled:
            self.buttons.append((label, r, action))

    def draw_menu(self):
        w, h = self.screen.get_size()
        self.ui.text("SQZGIN BOI", w / 2, 80, 52, CYAN, True, True)
        self.ui.text("N E O N   E S C A P E", w / 2, 130, 20, PURPLE, True, True)
        self.ui.text("SURVIVE THE SIGNAL", w / 2, 170, 13, MUTED, True)
        self.ui.text(f"REKOR  {self.profile['high_score']}     SQZ COINS  {self.profile['coins']}", w / 2, 205, 16, GOLD, True)

        entries = [
            ("BÖLÜMLER (30 BÖLÜM)", "levels"), ("SONSUZ KOŞU", "play"),
            ("ZAMAN SALDIRISI", "time"), ("KRİSTAL AVI", "crystal"),
            ("SQ-MAĞAZA", "shop"), ("SQ-COD", "sq_cod"),
            ("GARAJ", "garage"), ("HARDCORE", "hardcore"),
            ("GÖREVLER", "missions"), ("BAŞARIMLAR", "achievements"),
            ("İSTATİSTİKLER", "stats"), ("AYARLAR", "settings"),
            ("ANTRENMAN", "training"), ("NASIL OYNANIR?", "howto")
        ]
        gap = 48
        start = 240
        for i, (label, act) in enumerate(entries):
            col = i % 2
            row = i // 2
            x = (w // 2) - 310 + col * 320
            y = start + row * gap
            self.add_button(label, act, y, 290, x)

    def draw_submenu(self):
        w, h = self.screen.get_size()
        state_title = self.state.upper()
        self.ui.text(state_title, w / 2, 50, 36, CYAN, True, True)

        if self.state == "levels":
            self.ui.text(f"BÖLÜMLER - SAYFA {self.levels_page + 1}", w / 2, 100, 18, WHITE, True)
            max_unlocked = self.profile.get("unlocked_levels", 1)
            start_idx = self.levels_page * 10
            for i in range(start_idx, min(start_idx + 10, 30)):
                lvl = i + 1
                col = i % 2
                row = (i - start_idx) // 2
                bx = (w // 2) - 150 + col * 160
                by = 150 + row * 55
                unlocked = lvl <= max_unlocked
                label = f"BÖLÜM {lvl}" if unlocked else "KİLİTLİ"
                self.add_button(label, f"play_level:{lvl}", by, 140, bx, enabled=unlocked)
            self.add_button("ÖNCEKİ", "lvl_prev", h - 80, 130, (w // 2) - 140)
            self.add_button("SONRAKİ", "lvl_next", h - 80, 130, (w // 2) + 10)
        elif self.state == "shop":
            self.ui.text(f"SQ-MAĞAZA (COIN: {self.profile['coins']})", w / 2, 100, 18, GOLD, True)
            unlocked = self.profile.setdefault("shop_items", [])
            start_idx = self.shop_page * 5
            for i, item in enumerate(self.shop_items[start_idx:start_idx+5]):
                item_id, name, cost, desc = item
                is_unlocked = item_id in unlocked
                label = f"{name} ({cost}C)" if not is_unlocked else f"{name} [ALINDI]"
                by = 150 + i * 65
                self.add_button(label, f"buy_item:{item_id}", by, 360, enabled=not is_unlocked)
            self.add_button("ÖNCEKİ", "shop_prev", h - 80, 130, (w // 2) - 140)
            self.add_button("SONRAKİ", "shop_next", h - 80, 130, (w // 2) + 10)
        elif self.state == "sq_cod":
            self.ui.text("SQ-COD ÖZEL KOD PANELİ", w / 2, 120, 22, PURPLE, True, True)
            self.ui.text(f"GİRİLEN KOD: {self.code_input}_", w / 2, 180, 18, WHITE, True)
            if self.code_message:
                self.ui.text(self.code_message, w / 2, 230, 14, GREEN if "BAŞARILI" in self.code_message else RED, True)
            self.add_button("KODU ONAYLA", "submit_code", 300, 300)
        elif self.state == "settings":
            shake_status = "AÇIK" if self.profile["settings"].get("shake", True) else "KAPALI"
            part_status = "AÇIK" if self.profile["settings"].get("particles", True) else "KAPALI"
            self.add_button(f"EKRAN SALLANTISI: {shake_status}", "shake", 180, 320)
            self.add_button(f"PARÇACIKLAR: {part_status}", "particles", 250, 320)
        elif self.state == "stats":
            self.ui.text(f"TOPLAM OYUN: {self.profile.get('games', 0)}", w / 2, 160, 16, WHITE, True)
            self.ui.text(f"EN YÜKSEK SKOR: {self.profile.get('high_score', 0)}", w / 2, 200, 16, GOLD, True)
            self.ui.text(f"TOPLAM KRİSTAL: {self.profile.get('total_crystals', 0)}", w / 2, 240, 16, CYAN, True)

        self.add_button("ANA MENÜ", "menu", h - 70, 260)

    def draw_play(self):
        s = self.screen
        w, h = s.get_size()
        ly = int(self.laser_y)
        if ly < h:
            pygame.draw.rect(s, (75, 8, 28), (0, ly, w, h - ly))
            pygame.draw.line(s, RED, (0, ly), (w, ly), 5)
            pygame.draw.line(s, (255, 135, 155), (0, ly - 5), (w, ly - 5), 2)
        for o in self.obstacles: o.draw(s, self.t)

        for c in self.crystals:
            c.draw(s, self.t)
            if c.kind == "hp" and self.mode == "level":
                self.ui.text("+", c.x - 6, c.y - 8, 16, GREEN, False, True)
            elif c.kind == "ulti_coin":
                self.ui.text("⚡", c.x - 6, c.y - 9, 14, GOLD, False, True)

        for p in self.particles: p.draw(s)

        if self.boss:
            self.boss.draw(s, self.t)

        colors = {"cyan": CYAN, "purple": PURPLE, "gold": GOLD, "pink": PINK}
        self.player.draw(s, self.t, colors.get(self.profile["skin"], CYAN))

        self.ui.touch_controls.ulti_charge = self.ulti_charge
        self.ui.touch_controls.draw(s)

        self.ui.text(f"SKOR {int(self.score):06d}", 20, 18, 23, WHITE, False, True)

        if self.mode == "level":
            self.ui.text(f"CAN HP: {self.player_hp}/{self.max_player_hp}", 20, 48, 16, GREEN, False)

        if self.mode == "level":
            info = self.get_level_info(self.current_level)
            lvl_type = f"BOSS BÖLÜMÜ {self.current_level}" if info["is_boss"] else f"BÖLÜM {self.current_level}"
            self.ui.text(lvl_type, w - 20, 18, 16, RED if info["is_boss"] else GOLD, False, True)
            if not info["is_boss"]:
                self.ui.text(f"HEDEF: {info['target_score']} Skor / {info['target_crystals']} Kristal", w - 20, 45, 12, WHITE, False)
        else:
            self.ui.text(f"{self.mode.upper()}  {int(self.elapsed)} sn", w - 20, 18, 15, MUTED, False)

        dash_text = "HAZIR" if self.player.dash_cooldown <= 0 else f"{round(self.player.dash_cooldown, 1)}s"
        self.ui.text(f"DASH {dash_text}", w - 20, 70, 14, BLUE)

        active_buffs = []
        if self.player.shield > 0: active_buffs.append(f"KALKAN: {round(self.player.shield, 1)}s")
        if self.shop_shield_timer > 0: active_buffs.append(f"MAĞAZA KALKAN: {round(self.shop_shield_timer, 1)}s")
        if self.player.magnet > 0 or self.shop_magnet_timer > 0: active_buffs.append(f"MIKNATIS: {round(max(self.player.magnet, self.shop_magnet_timer), 1)}s")
        if self.player.multiplier > 0 or self.shop_mult_timer > 0: active_buffs.append(f"X2 COIN: {round(max(self.player.multiplier, self.shop_mult_timer), 1)}s")
        if self.shop_speed_timer > 0: active_buffs.append(f"HIZ: {round(self.shop_speed_timer, 1)}s")

        for idx, buff_text in enumerate(active_buffs):
            self.ui.text(buff_text, 20, 105 + idx * 22, 13, GOLD, False, True)

        if self.player.dash_cooldown > 0:
            pygame.draw.rect(s, (20, 40, 60), (w - 150, 92, 120, 6))
            pygame.draw.rect(s, BLUE, (w - 150, 92, 120 * (1 - self.player.dash_cooldown / 5.0), 6))

    def draw_overlay(self, title, items):
        w, h = self.screen.get_size()
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((2, 5, 18, 205))
        self.screen.blit(shade, (0, 0))
        self.ui.panel(pygame.Rect((w // 2) - 210, (h // 2) - 190, 420, 380))
        self.ui.text(title, w / 2, (h / 2) - 135, 30, CYAN, True, True)
        for i, (label, act) in enumerate(items): self.add_button(label, act, (h // 2) - 85 + i * 62, 300)

    def draw_gameover(self):
        self.draw_play()
        w, h = self.screen.get_size()
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((2, 4, 16, 225))
        s = self.screen
        s.blit(shade, (0, 0))
        self.ui.panel(pygame.Rect((w // 2) - 240, (h // 2) - 285, 480, 570))
        run = self.last_run or {"score": int(self.score), "time": self.elapsed, "crystals": self.collected, "combo": self.best_combo, "coins": self.run_coins, "victory": False}
        self.ui.text("OYUN BİTTİ", w / 2, (h // 2) - 235, 32, RED, True, True)
        self.ui.text(f"SKOR: {run['score']}", w / 2, (h // 2) - 180, 20, WHITE, True)
        self.ui.text(f"TOPLANAN KRİSTAL: {run['crystals']}", w / 2, (h // 2) - 145, 16, CYAN, True)
        self.ui.text(f"EN İYİ KOMBO: {run['combo']}", w / 2, (h // 2) - 115, 16, GOLD, True)
        self.ui.text(f"KAZANILAN COIN: +{run['coins']}", w / 2, (h // 2) - 85, 16, GREEN, True)
        self.add_button("TEKRAR OYNA", "restart", (h // 2) + 140, 300)
        self.add_button("ANA MENÜ", "menu", (h // 2) + 200, 300)