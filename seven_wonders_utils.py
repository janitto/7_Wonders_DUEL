import cv2
import os
import random
import numpy as np
from itertools import cycle
import seven_wonders_cards

class SevenWondersPrvyVek:


    myList = os.listdir("karty/vek_1")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_cards.%s" % (x,x))


    monitor_sirka = 1800
    monitor_vyska = 880
    karta_sirka = 80
    karta_vyska = 125
    div_vyska = 150
    div_sirka = int(div_vyska * 1.5)
    lavy_okraj = []         # sa zistuje v "zisti_rohy"

    hrac_1_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_zlte = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_modre = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_cervene = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_zelene = int(monitor_vyska / 2) + 15
    hrac_1_lavy_okraj = [30, 120, 210, 300, 390]
    hrac_1_lavy_okraj_div = [30, 360]

    hrac_2_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_zlte = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_modre = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_cervene = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_zelene = int(monitor_vyska / 2) + 15
    hrac_2_lavy_okraj = [1320, 1410, 1500, 1590, monitor_sirka - 30 - karta_sirka - 10]

    horny_okraj = 50        # o kolko zhora posunieme herny plan
    herne_karty = []        # sa zistuje v "vyber_herne_karty"
    herne_karty_meno = []   # sa zistuje v "vyber_herne_karty"
    herne_karty_alias = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t"]

    odhodene_katy = []
    boje_stav = 9

    tah = 0
    hraci_mena = ["Jany", "Mima"]
    hraci = cycle(hraci_mena)
    aktivny_hrac = []

    hrac_1_peniaze = 7
    hrac_2_peniaze = 7
    hrac_1_body = 0
    hrac_2_body = 0
    hrac_1_karty = []
    hrac_2_karty = []
    hrac_1_suroviny = []
    hrac_2_suroviny = []
    hrac_1_divy = []
    hrac_1_divy_meno = []
    hrac_1_divy_aktivne = []
    hrac_2_divy = []
    hrac_2_divy_meno = []
    hrac_2_divy_aktivne = []


    def __init__(self):

        self.zisti_rohy()
        self.vyber_herne_karty()
        cv2.namedWindow("7wonders")
        cv2.moveWindow("7wonders", int(self.monitor_sirka - self.monitor_sirka*0.97), int(self.monitor_vyska - self.monitor_vyska*0.94))

        #   startuj prve kolo hry, ktore bude nasledne volat dalsie
        self.nakresli_vek()

    def zisti_rohy(self):
        lavy_okraj = []
        okraj_karty = int(self.monitor_sirka / 2 - int(self.monitor_sirka * 0.01)) - self.karta_sirka
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
        myList = os.listdir("karty/vek_1")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                curImg = cv2.imread(f"karty/vek_1/{karta}")
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

        vsetky_divy = []
        vsetky_divy_meno = []
        myList = os.listdir("karty/divy")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                curImg = cv2.imread(f"karty/divy/{karta}")
                curImg = cv2.resize(curImg, (self.div_sirka, self.div_vyska))
                vsetky_divy.append(curImg)
                vsetky_divy_meno.append(karta.split(".")[0])

        for i in range(0, 4):
            pick_id = random.randint(0, len(vsetky_divy) - 1)
            self.hrac_1_divy.append(vsetky_divy[pick_id])
            self.hrac_1_divy_meno.append(vsetky_divy_meno[pick_id])
            self.hrac_1_divy_aktivne.append(False)
            vsetky_divy.pop(pick_id)
            vsetky_divy_meno.pop(pick_id)

        for i in range(0, 4):
            pick_id = random.randint(0, len(vsetky_divy) - 1)
            self.hrac_2_divy.append(vsetky_divy[pick_id])
            self.hrac_2_divy_meno.append(vsetky_divy_meno[pick_id])
            self.hrac_2_divy_aktivne.append(False)
            vsetky_divy.pop(pick_id)
            vsetky_divy_meno.pop(pick_id)

    def nakresli_vek(self):
        self.tah = self.tah + 1
        self.aktivny_hrac = next(self.hraci)
        img = np.zeros((self.monitor_vyska, self.monitor_sirka, 3), np.uint8)

        #   nakresli titulok

        cv2.putText(img, f"Toto je 7 Wonders DUEL - tah: {self.tah}", (self.lavy_okraj[9], 35), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 3)

        #   nakresli karty

        horny_okraj = self.horny_okraj
        for i in range(0, len(self.herne_karty)):

            #   nastav hodnotu horneho okraja, aby sa karty poukladali do riadkov

            if i in [2, 5, 9, 14]:
                horny_okraj = horny_okraj + int(self.karta_vyska * 0.8)

            #   v riadkoch kde ma byt karta stale otocena ju nakresli otocenu, ale iba ak este nebola vybrana

            if i not in [2, 3, 4, 9, 10, 11, 12, 13]:

                #print(f"Karta {self.herne_karty_alias[i]} je {self.herne_karty_meno[i]}")

                if self.herne_karty_meno[i] is not None:
                    img[horny_okraj:horny_okraj + self.karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + self.karta_sirka] = self.herne_karty[i]
                    cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

            #   v ostatnych riadkoch zisti, ci karta nebola pouziva a ak nie, tak ci je validna na vyber. ak ano, zobraz ju otocenu.

            else:

                #print(f"Karta {self.herne_karty_alias[i]} je {self.herne_karty_meno[i]}")

                if self.herne_karty_meno[i] is not None:
                    if self.herne_karty_alias[i] in self.validne_karty():
                        img[horny_okraj:horny_okraj + self.karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + self.karta_sirka] = self.herne_karty[i]
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj + 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                    else:
                        karta = cv2.imread("karty/ine/zadna_strana_vek_3_regular.jpg")
                        karta = cv2.resize(karta, (self.karta_sirka, self.karta_vyska))
                        img[horny_okraj:horny_okraj + self.karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + self.karta_sirka] = karta
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

        #   nakresli divy sveta hrac 1
        horny_okraj, lavy_okaj = self.horny_okraj, self.hrac_1_lavy_okraj[0]
        for idx, div in enumerate(self.hrac_1_divy_meno):
            div_img = cv2.imread(f"karty/divy/{div}.jpeg")
            div_img = cv2.resize(div_img, (self.div_sirka, self.div_vyska))
            if div in self.hrac_1_divy_aktivne:
                img[horny_okraj:horny_okraj + self.div_vyska, lavy_okaj:lavy_okaj + self.div_sirka] = div_img
            else:
                div_img = cv2.cvtColor(div_img, cv2.COLOR_BGR2GRAY)
                div_img = np.stack((div_img,)*3, axis=-1)
                img[horny_okraj:horny_okraj + self.div_vyska, lavy_okaj:lavy_okaj + self.div_sirka] = div_img
            if idx == 0:
                lavy_okaj = lavy_okaj + self.div_sirka + 20
            elif idx == 1:
                horny_okraj = horny_okraj + self.div_vyska + 20
                lavy_okaj = lavy_okaj - self.div_sirka - 20
            elif idx == 2:
                lavy_okaj = lavy_okaj + self.div_sirka + 20

        #   nakresli divy sveta hrac 2
        horny_okraj, lavy_okaj = self.horny_okraj, self.hrac_2_lavy_okraj[0]-20
        for idx, div in enumerate(self.hrac_2_divy_meno):
            div_img = cv2.imread(f"karty/divy/{div}.jpeg")
            div_img = cv2.resize(div_img, (self.div_sirka, self.div_vyska))
            if div in self.hrac_2_divy_aktivne:
                img[horny_okraj:horny_okraj + self.div_vyska, lavy_okaj:lavy_okaj + self.div_sirka] = div_img
            else:
                div_img = cv2.cvtColor(div_img, cv2.COLOR_BGR2GRAY)
                div_img = np.stack((div_img,) * 3, axis=-1)
                img[horny_okraj:horny_okraj + self.div_vyska, lavy_okaj:lavy_okaj + self.div_sirka] = div_img
            if idx == 0:
                lavy_okaj = lavy_okaj + self.div_sirka + 20
            elif idx == 1:
                horny_okraj = horny_okraj + self.div_vyska + 20
                lavy_okaj = lavy_okaj - self.div_sirka - 20
            elif idx == 2:
                lavy_okaj = lavy_okaj + self.div_sirka + 20



        #   nakresli zonu hraca 1 a 2 a zvyrazni aktivneho

        if self.aktivny_hrac == self.hraci_mena[0]:
            cv2.putText(img, self.hraci_mena[0], (20, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[19] + 80 + self.karta_sirka, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.rectangle(img, (20, int(self.monitor_vyska / 2)), (self.lavy_okraj[14] - 40, int(self.monitor_vyska * 0.9)), (0, 0, 255), 2)
            cv2.rectangle(img, (self.lavy_okraj[19] + 80 + self.karta_sirka, int(self.monitor_vyska / 2)), (self.monitor_sirka - 20, int(self.monitor_vyska * 0.9)), (0, 0, 100), 0)
        else:
            cv2.putText(img, self.hraci_mena[0], (20, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[19] + 80 + self.karta_sirka, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, int(self.monitor_vyska / 2)), (self.lavy_okraj[14] - 40, int(self.monitor_vyska * 0.9)), (0, 0, 100), 0)
            cv2.rectangle(img, (self.lavy_okraj[19] + 80 + self.karta_sirka, int(self.monitor_vyska / 2)), (self.monitor_sirka - 20, int(self.monitor_vyska * 0.9)), (0, 0, 255), 2)

        #   nakresli peniaze a body
        cv2.putText(img, "Pen:" +str(self.hrac_1_peniaze), (self.lavy_okraj[14] - 130, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
        cv2.putText(img, "Body:" +str(self.hrac_1_body), (self.lavy_okraj[14] - 260, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 51, 51), 1)
        #cv2.putText(img, "Sur:" +str(self.hrac_1_suroviny), (20, int(self.monitor_vyska / 2)-50), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 76, 153), 1)
        cv2.putText(img, "Pen:" + str(self.hrac_2_peniaze), (self.monitor_sirka - 130, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
        cv2.putText(img, "Body:" + str(self.hrac_2_body), (self.monitor_sirka - 260, int(self.monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 51, 51), 1)
        #cv2.putText(img, "Sur:" +str(self.hrac_2_suroviny), (self.lavy_okraj[19] + 80 + self.karta_sirka, int(self.monitor_vyska / 2)-50), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 76, 153), 1)

        #   nakresli majetok hraca 1

        sivohnedy_okraj = self.hrac_1_horny_okraj_sivohnede
        zlty_okraj = self.hrac_1_horny_okraj_zlte
        modry_okraj = self.hrac_1_horny_okraj_modre
        cerveny_okraj = self.hrac_1_horny_okraj_cervene
        zeleny_okraj = self.hrac_1_horny_okraj_zelene

        for karta in self.hrac_1_karty:
            karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta_img = cv2.resize(karta_img, (self.karta_sirka, self.karta_vyska))
            # img[hore:dole, lavo:pravo]
            if eval("self."+karta.lower()+".farba") == "hneda" or eval("self."+karta.lower()+".farba") == "siva":
                img[sivohnedy_okraj:sivohnedy_okraj + self.karta_vyska, self.hrac_1_lavy_okraj[0]:self.hrac_1_lavy_okraj[0] + self.karta_sirka] = karta_img
                sivohnedy_okraj += 25
            elif eval("self."+karta.lower()+".farba") == "zlta":
                img[zlty_okraj:zlty_okraj + self.karta_vyska, self.hrac_1_lavy_okraj[1]:self.hrac_1_lavy_okraj[1] + self.karta_sirka] = karta_img
                zlty_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "modra":
                img[modry_okraj:modry_okraj + self.karta_vyska, self.hrac_1_lavy_okraj[2]:self.hrac_1_lavy_okraj[2] + self.karta_sirka] = karta_img
                modry_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "cervena":
                img[cerveny_okraj:cerveny_okraj + self.karta_vyska, self.hrac_1_lavy_okraj[3]:self.hrac_1_lavy_okraj[3] + self.karta_sirka] = karta_img
                cerveny_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zelena":
                img[zeleny_okraj:zeleny_okraj + self.karta_vyska, self.hrac_1_lavy_okraj[4]:self.hrac_1_lavy_okraj[4] + self.karta_sirka] = karta_img
                zeleny_okraj += 25

            #   nakresli majetok hraca 2

        #   nakresli majetok hraca 2

        sivohnedy_okraj = self.hrac_2_horny_okraj_sivohnede
        zlty_okraj = self.hrac_2_horny_okraj_zlte
        modry_okraj = self.hrac_2_horny_okraj_modre
        cerveny_okraj = self.hrac_2_horny_okraj_cervene
        zeleny_okraj = self.hrac_2_horny_okraj_zelene

        for karta in self.hrac_2_karty:
            karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta_img = cv2.resize(karta_img, (self.karta_sirka, self.karta_vyska))
            # img[hore:dole, lavo:pravo]
            if eval("self." + karta.lower() + ".farba") == "hneda" or eval(
                    "self." + karta.lower() + ".farba") == "siva":
                img[sivohnedy_okraj:sivohnedy_okraj + self.karta_vyska,
                self.hrac_2_lavy_okraj[0]:self.hrac_2_lavy_okraj[0] + self.karta_sirka] = karta_img
                sivohnedy_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zlta":
                img[zlty_okraj:zlty_okraj + self.karta_vyska,
                self.hrac_2_lavy_okraj[1]:self.hrac_2_lavy_okraj[1] + self.karta_sirka] = karta_img
                zlty_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "modra":
                img[modry_okraj:modry_okraj + self.karta_vyska,
                self.hrac_2_lavy_okraj[2]:self.hrac_2_lavy_okraj[2] + self.karta_sirka] = karta_img
                modry_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "cervena":
                img[cerveny_okraj:cerveny_okraj + self.karta_vyska,
                self.hrac_2_lavy_okraj[3]:self.hrac_2_lavy_okraj[3] + self.karta_sirka] = karta_img
                cerveny_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zelena":
                img[zeleny_okraj:zeleny_okraj + self.karta_vyska,
                self.hrac_2_lavy_okraj[4]:self.hrac_2_lavy_okraj[4] + self.karta_sirka] = karta_img
                zeleny_okraj += 25

        #   nakresli odhodene karty

        h_okraj = int(self.monitor_vyska * 0.7)
        l_okraj = int((self.lavy_okraj[15] + self.lavy_okraj[14]) / 2 - 10)
        cv2.line(img, (l_okraj + 28, h_okraj - 10), (self.lavy_okraj[19] + self.karta_sirka, h_okraj - 10), (0, 102, 204), 1)
        cv2.putText(img, "Discard", (self.lavy_okraj[14], h_okraj - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 102, 204), 1)
        for karta in self.odhodene_katy:
            karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta_img = cv2.resize(karta_img, (self.karta_sirka, self.karta_vyska))
            img[h_okraj:h_okraj+self.karta_vyska, l_okraj:l_okraj+self.karta_sirka] = karta_img
            l_okraj = l_okraj + 50


        #   nakresli boje

        h_okraj = int(self.monitor_vyska * 0.9)
        l_okraj = self.lavy_okraj[15] - 40
        #cv2.line(img, (l_okraj + 28, h_okraj - 10), (self.lavy_okraj[19] + self.karta_sirka, h_okraj - 10), (0, 0, 204), 1)
        cv2.putText(img, "Boje", (self.lavy_okraj[14], h_okraj), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 204), 1)
        for x in range(0,19):
            if x in [0, 3, 6, 8, 9, 11, 14, 17]:
                cv2.line(img, (l_okraj+15, h_okraj-15), (l_okraj+15, h_okraj+15), (0, 0, 204), 1)

            if x == self.boje_stav:
                cv2.circle(img, (l_okraj, h_okraj), 10, (255, 255, 255), cv2.FILLED)
                cv2.putText(img, str(abs(self.boje_stav-9)), (l_okraj-7, h_okraj+6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 204), 2)
                l_okraj = l_okraj + 30
            else:
                cv2.circle(img, (l_okraj, h_okraj), 10, (0, 0, 255), cv2.FILLED)
                l_okraj = l_okraj + 30


        #   dokresli podpis

        cv2.putText(img, "Vytvorene Jan @ Strompl 28.10.2020", (int(self.monitor_sirka * 0.8), self.monitor_vyska - 22), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(img, "Aktualizovane 30.11.2020", (int(self.monitor_sirka * 0.8), self.monitor_vyska - 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("7wonders", img)

        if self.validne_karty():
            key = cv2.waitKey(0)
            if chr(key) in self.herne_karty_alias:
                #print(f"Vybral som kartu {self.herne_karty_alias.index(chr(key))} s aliasom {chr(key)}")
                self.vyber_a_aktivuj_kartu(chr(key))
            else:
                print("Nevalidny vyber.")
                self.ukaz_error("nespravna_volba")
                self.nakresli_vek()
        else:
            print("Koniec veku.")

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

        if len(validne_karty) == 0:
            return False
        else:
            return validne_karty

    def zvol_mozosti(self, zvolena_karta):
        cv2.namedWindow("Zvolena karta.")
        zvolena_karta_pozadie = np.zeros((self.karta_vyska * 3, self.karta_sirka * 6, 3), np.uint8)
        zvolena_karta_img = cv2.imread(f"karty/vek_1/{zvolena_karta}.jpg")
        zvolena_karta_img = cv2.resize(zvolena_karta_img, (self.karta_sirka * 2, self.karta_vyska * 2))
        zvolena_karta_pozadie[50:50+(self.karta_vyska*2), 20:20+(self.karta_sirka*2)] = zvolena_karta_img
        cv2.putText(zvolena_karta_pozadie, "(o) Odhod", (int(self.karta_sirka * 2.5), 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(k) Kup", (int(self.karta_sirka * 2.5), 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(d) Postav div:", (int(self.karta_sirka * 2.5), 210), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(c) Vyber inu kartu:", (int(self.karta_sirka * 2.5), 270), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.moveWindow("Zvolena karta.", int(self.monitor_sirka / 3), int(self.monitor_vyska / 2))
        cv2.imshow("Zvolena karta.", zvolena_karta_pozadie)
        key = cv2.waitKey()
        if chr(key) == "o":
            cv2.destroyWindow("Zvolena karta.")
            return "odhod"
        elif chr(key) == "k":
            cv2.destroyWindow("Zvolena karta.")
            return "kup"
        elif chr(key) == "d":
            cv2.destroyWindow("Zvolena karta.")
            return "postav_div"
        elif chr(key) == "c":
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Zvolena karta.")
            self.nakresli_vek()
        else:
            cv2.destroyWindow("Zvolena karta.")
            self.ukaz_error("nespravna_volba")
            self.zvol_mozosti(zvolena_karta)

    def vyber_a_aktivuj_kartu(self, karta):
        if karta in self.validne_karty():
            zvolena_karta = self.herne_karty_meno[self.herne_karty_alias.index(karta)]
            akcia = self.zvol_mozosti(zvolena_karta)
            self.vykonaj_akciu(zvolena_karta, akcia)
            self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
            self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
            self.nakresli_vek()
        else:
            self.ukaz_error("nevalidna_karta")
            self.nakresli_vek()

    def vykonaj_akciu(self, meno_karty, akcia):
        if self.aktivny_hrac == self.hraci_mena[0]:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        if akcia == "odhod":
            exec(f"self.hrac_{hrac}_peniaze = self.hrac_{hrac}_peniaze + 2 + self.zrataj_karty({hrac}, 'zlta')")
            print(f"{self.aktivny_hrac} ohodil {meno_karty} za {2 + self.zrataj_karty(hrac, 'zlta')} panezi.")
            self.odhodene_katy.append(meno_karty)

        if akcia == "kup":
            if self.mozem_kupit(hrac, meno_karty):
                self.kup_kartu(hrac, meno_karty)

        if akcia == "postav_div":
            suradnice_sirka = [50, 50+self.div_sirka + 20, 50, 50+self.div_sirka + 20]
            suradnice_vyska = [50, 50, 50+self.div_vyska + 20, 50+self.div_vyska + 20]
            cv2.namedWindow("Vyber div")
            vyber_div_pozadie = np.zeros((self.div_vyska * 3, self.div_sirka * 3 - 50, 3), np.uint8)
            for idx, div in enumerate(eval(f"self.hrac_{hrac}_divy_meno")):
                div = cv2.imread(f"karty/divy/{div}.jpeg")
                div = cv2.resize(div, (self.div_sirka, self.div_vyska))
                vyber_div_pozadie[suradnice_vyska[idx]:suradnice_vyska[idx] + self.div_vyska, suradnice_sirka[idx]:suradnice_sirka[idx] + self.div_sirka] = div
            cv2.imshow("Vyber div", vyber_div_pozadie)
            key = cv2.waitKey()
            if chr(key) in ("1", "2", "3", "4"):
                div = eval(f"self.hrac_{hrac}_divy_meno[int(chr({key}))-1]")
                self.postav_div(hrac, div)
                eval(f"self.hrac_{hrac}_divy_aktivne.append('{div}')")
                cv2.destroyWindow("Vyber div")
            else:
                self.ukaz_error("nespravna_volba")
                cv2.destroyWindow("Vyber div")
                self.nakresli_vek()

    def mozem_kupit(self, hrac, meno_karty):
        cena = eval("self." + meno_karty.lower() + ".cena")

        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        suroviny_mam = eval(f"self.hrac_{hrac}_suroviny").copy()
        peniaze_mam = eval(f"self.hrac_{hrac}_peniaze")
        # ak je cena len penazna
        if type(cena) == int:
            if peniaze_mam >= cena:
                return True
            else:
                print(f"Hrac {self.aktivny_hrac} nema dost penazi na kupu {meno_karty}")
            return False

            # ak je cena kombinovana
        else:
            for surovina in cena:
                try:
                    surovina = int(surovina)
                except:
                    surovina = surovina
                if type(surovina) == int:
                    if peniaze_mam >= surovina:
                        peniaze_mam -= surovina
                        pass
                    else:
                        return False
                else:
                    if surovina in suroviny_mam:
                        suroviny_mam = suroviny_mam.remove(surovina)
                        pass
                    elif surovina == "D" and "Zasobarna_dreva" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            pass
                        else:
                            return False
                    elif surovina == "H" and "Zasobarna_hliny" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            pass
                        else:
                            return False
                    elif surovina == "K" and "Zasobarna_kamene" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            pass
                        else:
                            return False
                    elif (surovina == "P" or surovina == "S") and "Hostinec" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            pass
                        else:
                            return False
                    else:
                        if peniaze_mam >= eval("self.hrac_"+str(oponent)+"_suroviny.count(surovina) + 2"):
                            pass
                        else:
                            return False
            return True

    def kup_kartu(self, hrac, meno_karty):
        try:
            body_gain = eval("self." + meno_karty.lower() + ".body")
        except:
            body_gain = 0
        try:
            peniaze_gain = eval("self." + meno_karty.lower() + ".peniaze")
        except:
            peniaze_gain = 0
        try:
            suroviny_gain = eval("self." + meno_karty.lower() + ".suroviny")
        except:
            suroviny_gain = []
        try:
            boje_gain = eval("self." + meno_karty.lower() + ".boje")
        except:
            boje_gain = 0
        karta_farba = eval("self." + meno_karty.lower() + ".farba")

        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        co_mam = eval(f"self.hrac_{hrac}_suroviny").copy()
        cena_karty = eval("self." + meno_karty.lower() + ".cena")
        cena = 0
        if type(cena_karty) == int:
            cena = cena_karty
        else:
            for surovina in cena_karty:
                try:
                    surovina = int(surovina)
                except:
                    surovina = surovina
                if type(surovina) == int:
                    cena = cena + surovina
                else:
                    if surovina in co_mam:
                        cena = cena + 0
                        co_mam.remove(surovina)
                        print("Pouzil som", surovina, "mam uz len", co_mam)
                    elif surovina == "D" and "Zasobarna_dreva" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                    elif surovina == "H" and "Zasobarna_hliny" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                    elif surovina == "K" and "Zasobarna_kamene" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                    elif (surovina == "P" or surovina == "S") and "Hostinec" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                    else:
                        prirazka = eval(f"self.hrac_{oponent}_suroviny.count('{surovina}') + 2")
                        cena = cena + prirazka

        exec(f"self.hrac_{hrac}_peniaze -= {cena}")
        # dostanem
        #   body
        exec(f"self.hrac_{hrac}_body += {body_gain}")
        #   peniaze
        exec(f"self.hrac_{hrac}_peniaze += {peniaze_gain}")
        #   suroviny ak je karta siva alebo hneda
        if karta_farba == "hneda" or karta_farba == "siva":
            for sur in suroviny_gain:
                exec(f"self.hrac_{hrac}_suroviny.append('{sur}')")
        #   boje
        if hrac == 1:   self.boje_stav = self.boje_stav + boje_gain
        if hrac == 2:   self.boje_stav = self.boje_stav - boje_gain
        #   samotnu kartu
        eval(f"self.hrac_{hrac}_karty.append(meno_karty)")

        print(
            f"{self.aktivny_hrac} kupuje {meno_karty}. Dostal {body_gain} bodov, {peniaze_gain} penazi, suroviny: {suroviny_gain} a boje: {boje_gain}")

    def postav_div(self, hrac, meno_divu):
        print(f"Hrac {self.aktivny_hrac} postavil div: {meno_divu}")

    def zrataj_karty(self, hrac, farba):
        count = 0
        for meno_karty in eval("self.hrac_"+str(hrac)+"_karty"):
            if eval("self."+meno_karty.lower()+".farba") == farba:
                count = count +1
        return count

    def ukaz_error(self, typ_erroru):
        next(self.hraci)
        self.tah = self.tah - 1
        cv2.namedWindow("Error!")
        if typ_erroru == "nevalidna_karta":
            error_img = np.zeros((100, 600, 3), np.uint8)
            cv2.putText(error_img, "Karta nie je uplne odokryta. Zvol si inu!", (10, 45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            cv2.moveWindow("Error!", int(self.monitor_sirka/3), int(self.monitor_vyska/2))
            cv2.imshow("Error!", error_img)
            cv2.waitKey(2500)
            cv2.destroyWindow("Error!")
        if typ_erroru == "nespravna_volba":
            error_img = np.zeros((100, 850, 3), np.uint8)
            cv2.putText(error_img, "Nespravna volba! Mozes zvolit len z ponukanych moznosti.", (10, 45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            cv2.moveWindow("Error!", int(self.monitor_sirka/3.5), int(self.monitor_vyska/2))
            cv2.imshow("Error!", error_img)
            cv2.waitKey(2500)
            cv2.destroyWindow("Error!")
        if typ_erroru == "nedostatok_penazi":
            error_img = np.zeros((100, 600, 3), np.uint8)
            cv2.putText(error_img, "Nedostatok penazi na kupu karty.", (10, 45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            cv2.moveWindow("Error!", int(self.monitor_sirka/3), int(self.monitor_vyska/2))
            cv2.imshow("Error!", error_img)
            cv2.waitKey(2500)
            cv2.destroyWindow("Error!")

