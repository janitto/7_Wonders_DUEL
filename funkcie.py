import os
import cv2
import numpy as np
import random


def zisti_rohy(monitor_sirka, karta_sirka, novy_riadok_karta):
    lavy_okraj = []
    okraj_karty = int(monitor_sirka / 2 - int(monitor_sirka * 0.02)) - karta_sirka
    lavy_okraj.append(okraj_karty)

    for i in range(1, 20):
        if i in novy_riadok_karta:
            if i == 2: okraj_karty = lavy_okraj[0] - int(karta_sirka * 0.8)
            if i == 5: okraj_karty = lavy_okraj[2] - int(karta_sirka * 0.8)
            if i == 9: okraj_karty = lavy_okraj[5] - int(karta_sirka * 0.8)
            if i == 14: okraj_karty = lavy_okraj[9] - int(karta_sirka * 0.8)
        else:
            okraj_karty = lavy_okraj[i - 1] + int(karta_sirka * 1.4)
        lavy_okraj.append(okraj_karty)

    return lavy_okraj


def removearray(vsetko,nieco):
    ind = 0
    size = len(vsetko)
    while ind != size and not np.array_equal(vsetko[ind],nieco):
        ind += 1
    if ind != size:
        vsetko.pop(ind)
    else:
        raise ValueError('array not found in list.')
    return vsetko


def vyber_kartu(herne_karty):
    karta_cislo = np.random.randint(len(herne_karty))
    vybrana_karta = herne_karty[karta_cislo]
    return karta_cislo, vybrana_karta


def vyber_herne_karty(karta_sirka, karta_vyska):
    vsetky_karty = []
    vsetky_karty_meno = []
    herne_karty = []
    herne_karty_meno = []
    myList = os.listdir("karty/vek_1")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
            curImg = cv2.imread(f"karty/vek_1/{karta}")
            curImg = cv2.resize(curImg, (karta_sirka, karta_vyska))
            vsetky_karty.append(curImg)
            vsetky_karty_meno.append(karta.split(".")[0])


    for i in range(0, 20):
        pick_id = random.randint(0, len(vsetky_karty)-1)
        herne_karty.append(vsetky_karty[pick_id])
        herne_karty_meno.append(vsetky_karty_meno[pick_id])
        vsetky_karty.pop(pick_id)
        vsetky_karty_meno.pop(pick_id)

    #herne_karty = random.sample(vsetky_karty, 20)

    return herne_karty, herne_karty_meno


def nakresli_hru(lavy_okraj, horny_okraj, karta_vyska, monitor_vyska, karta_sirka, monitor_sirka, novy_riadok_karta, herne_karty, herne_karty_meno):
    img = np.zeros((monitor_vyska, monitor_sirka, 3), np.uint8)
    for i in range(0,20):
        if i in novy_riadok_karta:
            horny_okraj = horny_okraj + int(karta_vyska * 0.8)
        if i not in [2,3,4,9,10,11,12,13]:
            karta_cislo, karta = vyber_kartu(herne_karty)
            img[horny_okraj:horny_okraj + karta_vyska, lavy_okraj[i]:lavy_okraj[i] + karta_sirka] = karta
            herne_karty = removearray(herne_karty, karta)
            print(f"Karta {i} je {herne_karty_meno[karta_cislo]}")
            herne_karty_meno.pop(karta_cislo)
        else:
            karta_cislo, karta = vyber_kartu(herne_karty)
            herne_karty = removearray(herne_karty, karta)
            print(f"Karta {i} je {herne_karty_meno[karta_cislo]}")
            herne_karty_meno.pop(karta_cislo)
            karta = cv2.imread("karty/ine/zadna_strana_vek_3_regular.jpg")
            karta = cv2.resize(karta, (karta_sirka, karta_vyska))
            img[horny_okraj:horny_okraj + karta_vyska, lavy_okraj[i]:lavy_okraj[i] + karta_sirka] = karta


    cv2.putText(img, "Toto je 7 Wonders DUEL", (lavy_okraj[5], 35), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 3)
    cv2.putText(img, "Vytvorene Jan @ Strompl 28.10.2020", (int(monitor_sirka * 0.8), monitor_vyska - 22), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)
    cv2.putText(img, "Aktualizovane 28.11.2020", (int(monitor_sirka * 0.8), monitor_vyska - 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

    cv2.imshow("Image", img)
    cv2.waitKey(0)
