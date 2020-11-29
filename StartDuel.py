import funkcie
import numpy as np
import cv2

monitor_sirka = 1000                # sirka monitora
monitor_vyska = 600                 # vyska monitora
karta_sirka = 80                    # karta sirka
karta_vyska = 125                   # karta vyska
horny_okraj = 50                    # ako daleko od horneho okraju sa zacnu karty ukladat
novy_riadok_karta = [2, 5, 9, 14]   # definuje, ktora karta je prva v nasledujucom riadku. Karty su cislovane od 0


#   zistime x suradnice kazdej karty
lavy_okraj = funkcie.zisti_rohy(monitor_sirka, karta_sirka, novy_riadok_karta)

#   vyberie 20 nahodnych karat z balicka
herne_karty, herne_karty_meno = funkcie.vyber_herne_karty(karta_sirka, karta_vyska)
print(herne_karty_meno)

funkcie.nakresli_hru(lavy_okraj, horny_okraj, karta_vyska, monitor_vyska, karta_sirka, monitor_sirka, novy_riadok_karta, herne_karty, herne_karty_meno)
