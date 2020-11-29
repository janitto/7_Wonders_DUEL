import cv2
import os
import random
import numpy as np

class SevenWondersPrvyVek:

    monitor_sirka = 1800
    monitor_vyska = 880
    karta_sirka = 80
    karta_vyska = 125
    lavy_okraj = []         # sa zistuje v "zisti_rohy"
    horny_okraj = 50        # o kolko zhora posunieme herny plan
    herne_karty = []        # sa zistuje v "vyber_herne_karty"
    herne_karty_meno = []   # sa zistuje v "vyber_herne_karty"
    herne_karty_alias = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                         "t"]

    tah = 0

    def __init__(self):

        self.zisti_rohy()
        self.vyber_herne_karty()
        self.nakresli_vek()

    def zisti_rohy(self):
        lavy_okraj = []
        okraj_karty = int(self.monitor_sirka / 2 - int(self.monitor_sirka * 0.02)) - self.karta_sirka
        lavy_okraj.append(okraj_karty)

        for i in range(1, 20):
            if i in [2, 5, 9, 14]:
                if i == 2: okraj_karty = lavy_okraj[0] - int(self.karta_sirka * 0.8)
                if i == 5: okraj_karty = lavy_okraj[2] - int(self.karta_sirka * 0.8)
                if i == 9: okraj_karty = lavy_okraj[5] - int(self.karta_sirka * 0.8)
                if i == 14: okraj_karty = lavy_okraj[9] - int(self.karta_sirka * 0.8)
            else:
                okraj_karty = lavy_okraj[i - 1] + int(self.karta_sirka * 1.4)
            lavy_okraj.append(okraj_karty)

        self.lavy_okraj = lavy_okraj

    def vyber_herne_karty(self):
        vsetky_karty = []
        vsetky_karty_meno = []
        herne_karty = []
        herne_karty_meno = []
        myList = os.listdir("karty/cropped")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                curImg = cv2.imread(f"karty/cropped/{karta}")
                curImg = cv2.resize(curImg, (self.karta_sirka, self.karta_vyska))
                vsetky_karty.append(curImg)
                vsetky_karty_meno.append(karta.split(".")[0])

        for i in range(0, 20):
            pick_id = random.randint(0, len(vsetky_karty) - 1)
            herne_karty.append(vsetky_karty[pick_id])
            herne_karty_meno.append(vsetky_karty_meno[pick_id])
            vsetky_karty.pop(pick_id)
            vsetky_karty_meno.pop(pick_id)

        self.herne_karty = herne_karty
        self.herne_karty_meno = herne_karty_meno

    def nakresli_vek(self):
        self.tah = self.tah + 1
        #   nakresli karty

        img = np.zeros((self.monitor_vyska, self.monitor_sirka, 3), np.uint8)
        horny_okraj = self.horny_okraj
        for i in range(0, len(self.herne_karty)):
            if i in [2, 5, 9, 14]:
                horny_okraj = horny_okraj + int(self.karta_vyska * 0.8)

            if i not in [2, 3, 4, 9, 10, 11, 12, 13]:
                img[horny_okraj:horny_okraj + self.karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + self.karta_sirka] = self.herne_karty[i]
                if self.herne_karty_meno[i] is not None:
                    cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)

                print(f"Karta {i} je {self.herne_karty_meno[i]}")
            else:
                print(f"Karta {i} je {self.herne_karty_meno[i]}")
                karta = cv2.imread("karty/ine/zadna_strana_vek_3_regular.jpg")
                karta = cv2.resize(karta, (self.karta_sirka, self.karta_vyska))
                img[horny_okraj:horny_okraj + self.karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + self.karta_sirka] = karta
                cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)

        print("------Begin")
        print(self.herne_karty_meno)
        print(self.herne_karty_alias)
        print(self.validne_karty())
        print("------End")

        #   nakresli peniaze


        #   dokresli podpis

        cv2.putText(img, f"Toto je 7 Wonders DUEL: tah {self.tah}", (self.lavy_okraj[5], 35), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(img, "Vytvorene Jan @ Strompl 28.10.2020", (int(self.monitor_sirka * 0.8), self.monitor_vyska - 22), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(img, "Aktualizovane 28.11.2020", (int(self.monitor_sirka * 0.8), self.monitor_vyska - 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("Image", img)

        key = cv2.waitKey(0)
        try: self.aktivuj_kartu(chr(key))
        except: print("Nespravna volba")

    def aktivuj_kartu(self, karta):
        print(f"Aktivujem kartu {self.herne_karty_alias.index(karta)} s aliasom {karta}")
        if karta in self.validne_karty():
            print("Karta validna, aktivujem.")
            self.herne_karty[self.herne_karty_alias.index(karta)] = np.zeros((self.karta_vyska, self.karta_sirka, 3), np.uint8)
            self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
            self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
            self.nakresli_vek()
        else:
            print("Karta nevalidna.")

    def validne_karty(self):
        validne_karty = []
        for idx, karta_alias in enumerate(self.herne_karty_alias):
            if karta_alias is not None:
                if idx == 0:
                    if self.herne_karty_alias[2] is None and self.herne_karty_alias[3] is None:
                        validne_karty.append(karta_alias)
                if idx == 1:
                    if self.herne_karty_alias[3] is None and self.herne_karty_alias[4] is None:
                        validne_karty.append(karta_alias)
                if idx == 2:
                    if self.herne_karty_alias[5] is None and self.herne_karty_alias[6] is None:
                        validne_karty.append(karta_alias)
                if idx == 3:
                    if self.herne_karty_alias[6] is None and self.herne_karty_alias[7] is None:
                        validne_karty.append(karta_alias)
                if idx == 4:
                    if self.herne_karty_alias[7] is None and self.herne_karty_alias[8] is None:
                        validne_karty.append(karta_alias)
                if idx == 5:
                    if self.herne_karty_alias[9] is None and self.herne_karty_alias[10] is None:
                        validne_karty.append(karta_alias)
                if idx == 6:
                    if self.herne_karty_alias[10] is None and self.herne_karty_alias[11] is None:
                        validne_karty.append(karta_alias)
                if idx == 7:
                    if self.herne_karty_alias[11] is None and self.herne_karty_alias[12] is None:
                        validne_karty.append(karta_alias)
                if idx == 8:
                    if self.herne_karty_alias[12] is None and self.herne_karty_alias[13] is None:
                        validne_karty.append(karta_alias)
                if idx == 9:
                    if self.herne_karty_alias[14] is None and self.herne_karty_alias[15] is None:
                        validne_karty.append(karta_alias)
                if idx == 10:
                    if self.herne_karty_alias[15] is None and self.herne_karty_alias[16] is None:
                        validne_karty.append(karta_alias)
                if idx == 11:
                    if self.herne_karty_alias[16] is None and self.herne_karty_alias[17] is None:
                        validne_karty.append(karta_alias)
                if idx == 12:
                    if self.herne_karty_alias[17] is None and self.herne_karty_alias[18] is None:
                        validne_karty.append(karta_alias)
                if idx == 13:
                    if self.herne_karty_alias[18] is None and self.herne_karty_alias[19] is None:
                        validne_karty.append(karta_alias)
                if idx == 14:
                    if self.herne_karty_alias[14] is not None:
                        validne_karty.append(karta_alias)
                if idx == 15:
                    if self.herne_karty_alias[15] is not None:
                        validne_karty.append(karta_alias)
                if idx == 16:
                    if self.herne_karty_alias[16] is not None:
                        validne_karty.append(karta_alias)
                if idx == 17:
                    if self.herne_karty_alias[17] is not None:
                        validne_karty.append(karta_alias)
                if idx == 18:
                    if self.herne_karty_alias[18] is not None:
                        validne_karty.append(karta_alias)
                if idx == 19:
                    if self.herne_karty_alias[19] is not None:
                        validne_karty.append(karta_alias)
        return validne_karty