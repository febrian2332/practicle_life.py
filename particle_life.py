
import pygame
import numpy as np

LEBAR, TINGGI = 1000, 700
FPS = 60

JUMLAH_JENIS = 6
PARTIKEL_PER_JENIS = 70
JUMLAH_TOTAL = JUMLAH_JENIS * PARTIKEL_PER_JENIS

RADIUS_INTERAKSI = 80.0
RADIUS_TOLAK = 18.0
GESEKAN = 0.94
KEKUATAN = 0.55

WARNA_JENIS = [
    (255, 70, 90), (70, 200, 255), (255, 220, 60),
    (170, 90, 255), (70, 255, 160), (255, 150, 40),
]


def buat_aturan_acak():
    return np.random.uniform(-1, 1, (JUMLAH_JENIS, JUMLAH_JENIS))


def sebar_partikel():
    posisi = np.random.uniform([0, 0], [LEBAR, TINGGI], (JUMLAH_TOTAL, 2))
    kecepatan = np.zeros((JUMLAH_TOTAL, 2))
    jenis = np.repeat(np.arange(JUMLAH_JENIS), PARTIKEL_PER_JENIS)
    return posisi, kecepatan, jenis


def hitung_gaya(posisi, jenis, aturan):
    
    # Selisih posisi antar semua pasangan partikel sekaligus (matriks NxNx2)
    delta = posisi[np.newaxis, :, :] - posisi[:, np.newaxis, :]

    # Wrap-around (dunia menyambung di tepi, kayak Pac-Man)
    delta[:, :, 0] -= LEBAR * np.round(delta[:, :, 0] / LEBAR)
    delta[:, :, 1] -= TINGGI * np.round(delta[:, :, 1] / TINGGI)

    jarak = np.sqrt(np.sum(delta ** 2, axis=2)) + 1e-9
    arah = delta / jarak[:, :, np.newaxis]

    # Ambil kekuatan tarik/tolak sesuai jenis kedua partikel dari matriks aturan
    faktor_aturan = aturan[jenis[:, np.newaxis], jenis[np.newaxis, :]]

    # Gaya tolak keras kalau kejauhan deket, gaya sesuai aturan kalau di zona interaksi
    dalam_radius = jarak < RADIUS_INTERAKSI
    dalam_tolak = jarak < RADIUS_TOLAK

    gaya_tarik = faktor_aturan * (1 - jarak / RADIUS_INTERAKSI)
    gaya_tarik = np.where(dalam_radius, gaya_tarik, 0.0)

    gaya_tolak = -(1 - jarak / RADIUS_TOLAK) * 2.0
    gaya_tolak = np.where(dalam_tolak, gaya_tolak, 0.0)

    gaya_total_skalar = gaya_tarik + gaya_tolak
    np.fill_diagonal(gaya_total_skalar, 0.0)

    gaya_vektor = arah * gaya_total_skalar[:, :, np.newaxis]
    return np.sum(gaya_vektor, axis=1) * KEKUATAN


def main():
    pygame.init()
    layar = pygame.display.set_mode((LEBAR, TINGGI))
    pygame.display.set_caption("Particle Life - Emergent Behavior")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    aturan = buat_aturan_acak()
    posisi, kecepatan, jenis = sebar_partikel()

    canvas = pygame.Surface((LEBAR, TINGGI))
    canvas.fill((5, 5, 10))

    jalan = True
    pause_info = 180

    while jalan:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jalan = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    jalan = False
                elif event.key == pygame.K_SPACE:
                    aturan = buat_aturan_acak()
                    pause_info = 120
                elif event.key == pygame.K_r:
                    posisi, kecepatan, jenis = sebar_partikel()
                    pause_info = 120

        gaya = hitung_gaya(posisi, jenis, aturan)
        kecepatan = (kecepatan + gaya) * GESEKAN
        posisi = (posisi + kecepatan) % [LEBAR, TINGGI]

        # Fade halus biar ada jejak/trail tipis, bukan diclear total
        fade = pygame.Surface((LEBAR, TINGGI))
        fade.set_alpha(35)
        fade.fill((5, 5, 10))
        canvas.blit(fade, (0, 0))

        for i in range(JUMLAH_TOTAL):
            x, y = posisi[i]
            warna = WARNA_JENIS[jenis[i]]
            s = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(s, (*warna, 90), (5, 5), 5)
            canvas.blit(s, (int(x - 5), int(y - 5)), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.circle(canvas, warna, (int(x), int(y)), 2)

        layar.blit(canvas, (0, 0))

        teks1 = font.render("SPASI = aturan baru (dapat 'makhluk' beda)   R = sebar ulang   ESC = keluar",
                             True, (180, 180, 180))
        layar.blit(teks1, (10, TINGGI - 24))

        if pause_info > 0:
            teks2 = font.render(
                f"{JUMLAH_TOTAL} partikel, {JUMLAH_JENIS} jenis - pola muncul dari aturan tarik/tolak acak",
                True, (255, 255, 255)
            )
            layar.blit(teks2, (10, 10))
            pause_info -= 1

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
