import pygame
import random
import sys

# Pygame başlatma
pygame.init()

# Ekran boyutları
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Uzay Savaşı")

# Renkler
white = (255, 255, 255)
red = (255, 0, 0)

# Araba karakterin başlangıç özellikleri
ship_width, ship_height = 40, 60  # Gemi boyutunu küçültüyoruz
ship_x = width // 2 - ship_width // 2
ship_y = height - ship_height - 10

# Arka plan resmi yükleme
background_image = pygame.image.load(r"space-1164579_1280.png")
background_image = pygame.transform.scale(background_image, (width, height))

# Gemi resmini yükle
ship_image = pygame.image.load(r"rocket-7424294_1280 (1).png")
ship_image = pygame.transform.scale(ship_image, (ship_width, ship_height))

# Boom efekti resmi
destruction_image = pygame.image.load(r"explosion-417894_1280.png")
destruction_image = pygame.transform.scale(destruction_image, (ship_width * 1.5, ship_height * 1.5))  # Efekt boyutunu küçültüyoruz

# Düşman gemilerini yükle
enemy_images = [
    pygame.image.load(r"rocket-5965740_1280.png"),
    pygame.image.load(r"space-ship-148536_1280.png"),
    pygame.image.load(r"ufo-2121470_1280.png"),
    pygame.image.load(r"ufo-4778062_1280.png")
]

# Düşman gemilerini boyutlandır
enemy_images = [pygame.transform.scale(img, (ship_width, ship_height)) for img in enemy_images]

# Mermi ayarları
bullet_width, bullet_height = 10, 20  # Mermilerin boyutunu arttırdık
bullet_speed = -15  # Mermilerin hızını arttırdık
bullets = []

# Lazer resmi yükle
laser_image = pygame.image.load(r"Ekran görüntüsü 2024-12-23 200916.png")
laser_image = pygame.transform.scale(laser_image, (bullet_width, bullet_height * 2))

# Düşman mermi ayarları
enemy_bullet_width, enemy_bullet_height = 5, 15
enemy_bullet_speed = 10
enemy_bullets = []

# Engel ayarları
enemy_speed = 5
enemies = []
last_enemy_time = 0
enemy_delay = 1000  # 1000 ms yani 1 saniyede bir yeni düşman gelsin

# Puan Sistemi
score = 0
font = pygame.font.Font(None, 48)

# FPS ayarları
clock = pygame.time.Clock()

# Arka plan hareket değişkenleri
bg_speed = 5  # Arka planın hareket hızı
bg_y1 = 0  # Arka planın Y koordinatı
bg_y2 = -height  # İkinci arka plan hemen üstten başlasın

# Patlama efektleri listesi
explosions = []
player_explosion = None

# Düşman oluşturma fonksiyonu
def create_enemy():
    enemy_width = ship_width
    x_position = random.randint(0, width - enemy_width)
    x_speed = random.choice([-3, 3])  # Düşmanın sağa veya sola hareket etmesi için rastgele bir hız
    return (x_position, -ship_height, random.choice(enemy_images), x_speed)

# Oyun döngüsü
game_over = False  # Oyunun bitip bitmediğini kontrol etmek için değişken
running = True
explosion_time = 0  # Patlama zamanı
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        # Mermi ateşleme
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
            bullets.append((ship_x + ship_width // 2 - bullet_width // 2, ship_y))

    if not game_over:
        # Klavye ile gemi hareketi
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and ship_x > 0:
            ship_x -= 5
        if keys[pygame.K_RIGHT] and ship_x < width - ship_width:
            ship_x += 5

        # Zamanlayıcı kontrolü ile düşman oluşturma
        if pygame.time.get_ticks() - last_enemy_time > enemy_delay:
            enemies.append(create_enemy())
            last_enemy_time = pygame.time.get_ticks()

        # Düşman hareketi
        for i in range(len(enemies)):
            enemy_x, enemy_y, enemy_image, x_speed = enemies[i]
            enemy_y += enemy_speed
            enemy_x += x_speed  # Düşmanın x ekseninde sağa sola kayması

            # Eğer düşman ekranın dışına çıkarsa yönünü değiştir
            if enemy_x < 0 or enemy_x > width - ship_width:
                x_speed *= -1

            enemies[i] = (enemy_x, enemy_y, enemy_image, x_speed)

            if enemy_y > height:
                enemies.pop(i)
                break

        # Hız arttırma ve düşman sayısının artması
        if score % 5 == 0 and score != 0:
            enemy_speed += 0.001 + (score // 50) * 0.0001  # Hızın daha orantılı artması
            enemy_delay = max(500, enemy_delay - 50)  # Düşman oluşturma süresi kısalıyor
            for _ in range(score // 8):  # Her 5 puanda yeni düşman sayısını arttırma
                enemies.append(create_enemy())

        # Mermileri hareket ettir
        for i in range(len(bullets)):
            bullet_x, bullet_y = bullets[i]
            bullet_y += bullet_speed
            bullets[i] = (bullet_x, bullet_y)

            # Ekranın dışına çıkan mermileri sil
            if bullet_y < 0:
                bullets.pop(i)
                break

        # Düşman mermisi ateşleme
        if random.random() < 0.02:  # Düşmanların rastgele ateş etme şansı
            if enemies:
                shooting_enemy = random.choice(enemies)
                enemy_bullets.append((shooting_enemy[0] + ship_width // 2 - enemy_bullet_width // 2, shooting_enemy[1] + ship_height))

        # Düşman mermilerini hareket ettir
        for i in range(len(enemy_bullets)):
            enemy_bullet_x, enemy_bullet_y = enemy_bullets[i]
            enemy_bullet_y += enemy_bullet_speed
            enemy_bullets[i] = (enemy_bullet_x, enemy_bullet_y)

            # Ekranın dışına çıkan mermileri sil
            if enemy_bullet_y > height:
                enemy_bullets.pop(i)
                break

        # Mermi ve düşman çarpışma kontrolü
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], ship_width, ship_height)
                if bullet_rect.colliderect(enemy_rect):
                    enemies.remove(enemy)
                    bullets.remove(bullet)

                    # Patlama efekti için pozisyon ve süre ekle
                    explosions.append({
                        "pos": (enemy[0] - ship_width // 2, enemy[1] - ship_height // 2),
                        "time": pygame.time.get_ticks()
                    })
                    score += 1
                    break

        # Düşman mermisi ve oyuncu çarpışma kontrolü
        for enemy_bullet in enemy_bullets[:]:
            enemy_bullet_rect = pygame.Rect(enemy_bullet[0], enemy_bullet[1], enemy_bullet_width, enemy_bullet_height)
            player_rect = pygame.Rect(ship_x, ship_y, ship_width, ship_height)
            if enemy_bullet_rect.colliderect(player_rect):
                # Oyuncu gemisi patlıyor, patlama efekti ekle
                player_explosion = {"pos": (ship_x - ship_width // 2, ship_y - ship_height // 2), "time": pygame.time.get_ticks()}
                game_over = True
                explosion_time = pygame.time.get_ticks()  # Patlama zamanını kaydet
                break

        # Arka plan hareketi
        bg_y1 += bg_speed
        bg_y2 += bg_speed

        # Arka plan döngüsü
        if bg_y1 >= height:
            bg_y1 = -height
        if bg_y2 >= height:
            bg_y2 = -height

        # Ekranı temizle
        screen.fill((0, 0, 0))

                # Arka planı ekrana çiz
        screen.blit(background_image, (0, bg_y1))
        screen.blit(background_image, (0, bg_y2))

        # Patlama efektlerini çiz ve sürelerini kontrol et
        for explosion in explosions[:]:
            if pygame.time.get_ticks() - explosion["time"] < 1000:  # 1 saniye boyunca göster
                screen.blit(destruction_image, explosion["pos"])
            else:
                explosions.remove(explosion)

        # Düşmanları çiz
        for enemy_x, enemy_y, enemy_image, _ in enemies:
            screen.blit(enemy_image, (enemy_x, enemy_y))

        # Düşman mermilerini çiz
        for enemy_bullet_x, enemy_bullet_y in enemy_bullets:
            pygame.draw.rect(screen, red, (enemy_bullet_x, enemy_bullet_y, enemy_bullet_width, enemy_bullet_height))

        # Mermileri çiz
        for bullet_x, bullet_y in bullets:
            screen.blit(laser_image, (bullet_x, bullet_y))

        # Gemi karakterini ekrana çiz
        screen.blit(ship_image, (ship_x, ship_y))

        # Çarpışma kontrolü
        for enemy_x, enemy_y, enemy_image, _ in enemies:
            enemy_rect = pygame.Rect(enemy_x, enemy_y, ship_width, ship_height)
            player_rect = pygame.Rect(ship_x, ship_y, ship_width, ship_height)
            if enemy_rect.colliderect(player_rect):
                # Oyuncu gemisi patlıyor, patlama efekti ekle
                player_explosion = {"pos": (ship_x - ship_width // 2, ship_y - ship_height // 2), "time": pygame.time.get_ticks()}
                game_over = True
                explosion_time = pygame.time.get_ticks()  # Patlama zamanını kaydet
                break

    # Eğer oyuncu gemisi patladıysa, patlama efekti göster ve "Game Over" mesajını çiz
    else:
        if player_explosion:
            screen.blit(destruction_image, player_explosion["pos"])
            if pygame.time.get_ticks() - explosion_time > 3000:  # 3 saniye sonra oyun biter
                screen.fill((0, 0, 0))  # Ekranı temizle
                game_over_text = font.render("Game Over!", True, red)
                score_text = font.render(f"Score: {score}", True, red)
                screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 3))
                screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
                pygame.display.flip()
                continue

    # Puanı göster
    score_text = font.render(f"Score: {score}", True, red)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)  # FPS ayarı
