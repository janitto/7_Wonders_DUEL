import cv2
import os
import time
import random
import numpy as np
from itertools import cycle, islice
import logging
import json
import shutil
import seven_wonders_divy
import seven_wonders_tokeny
import seven_wonders_cards

monitor_sirka = 1800
monitor_vyska = 880
karta_sirka = 80
karta_vyska = 125
div_vyska = 150
div_sirka = int(div_vyska * 1.5)
token_rozmer = 80
horny_okraj_global = 50


class SevenWondersPrvyVek:

    myList = os.listdir("karty/vek_1")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() == ".jpg":
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_cards.%s" % (x,x))

    myList = os.listdir("karty/divy")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() == ".jpeg":
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_divy.%s" % (x,x))

    myList = os.listdir("karty/tokeny")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() == ".png":
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_tokeny.%s" % (x,x))

    lavy_okraj = []         # sa zistuje v "zisti_rohy"

    hrac_1_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_zlte = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_modre = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_cervene = int(monitor_vyska / 2) + 15
    hrac_1_horny_okraj_zelene = int(monitor_vyska / 2) + 15
    #hrac_1_lavy_okraj = [30, 120, 210, 300, 390]
    hrac_1_lavy_okraj = [num for num in np.arange(30,400,karta_sirka+10)]

    hrac_2_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_zlte = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_modre = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_cervene = int(monitor_vyska / 2) + 15
    hrac_2_horny_okraj_zelene = int(monitor_vyska / 2) + 15
    hrac_2_lavy_okraj = [1320, 1410, 1500, 1590, monitor_sirka - 30 - karta_sirka - 10]

    herne_karty_meno = []
    herne_karty_alias = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t"]

    odhodene_karty = []
    boje_stav = 9
    boje_zrus_peniaze = [None, 5, 5, 5, 2, 2, 2, None, None, None, None, None, 2, 2, 2, 5, 5, 5, None]
    herne_tokeny_meno = []
    neherne_tokeny_meno = []

    hra_id = None
    tah = 0
    hraci_mena = ["Jany", "Mima"]
    hraci = []
    aktivny_hrac = []

    hrac_1_peniaze = 7
    hrac_2_peniaze = 7
    hrac_1_body = 0
    hrac_2_body = 0
    hrac_1_karty = []
    hrac_2_karty = []
    hrac_1_suroviny = []
    hrac_2_suroviny = []
    hrac_1_divy_meno = []
    hrac_1_divy_aktivne = []
    hrac_2_divy_meno = []
    hrac_2_divy_aktivne = []
    hrac_1_tokeny = []
    hrac_2_tokeny = []


    def __init__(self, hra_id):

        self.hra_id = hra_id

        logging.info(f" Hra s ID: {self.hra_id} zacala.")
        self.zisti_rohy()

        # ak niesu metadata, vyber nove herne karty, tokeny a divy.
        if not os.path.exists(f"archiv_hier/input_metadata_{self.hra_id}.json"):
            self.vyber_herne_karty()
            logging.debug("Herne karty, tokeny a divy boli nanovo vygenerovane.")
        else:
            with open(f"archiv_hier/input_metadata_{self.hra_id}.json") as metadata:
                data = json.load(metadata)
                tah = data["tah"]
                metadata.close()
                if tah == 0:
                    self.vyber_herne_karty()
                    logging.debug("Predosla hra bola prazdna, Generujem novu.")
                else:
                    logging.debug("Metadata predoslej hry najdene. Obnovujem.")


        cv2.namedWindow("7wonders")
        cv2.moveWindow("7wonders", int(monitor_sirka - monitor_sirka*0.97), int(monitor_vyska - monitor_vyska*0.94))

        #   startuj prve kolo hry, ktore bude nasledne volat dalsie
        self.nakresli_vek()

    def zisti_rohy(self):
        lavy_okraj = []
        okraj_karty = int(monitor_sirka / 2 - int(monitor_sirka * 0.01)) - karta_sirka
        lavy_okraj.append(okraj_karty)

        for i in range(1, 20):
            if i in [2, 5, 9, 14]:
                if i == 2: okraj_karty = lavy_okraj[0] - int(karta_sirka * 0.8)
                if i == 5: okraj_karty = lavy_okraj[2] - int(karta_sirka * 0.8)
                if i == 9: okraj_karty = lavy_okraj[5] - int(karta_sirka * 0.8)
                if i == 14: okraj_karty = lavy_okraj[9] - int(karta_sirka * 0.8)
            else:
                okraj_karty = lavy_okraj[i - 1] + int(karta_sirka * 1.4)
            lavy_okraj.append(okraj_karty)

        self.lavy_okraj = lavy_okraj

    def vyber_herne_karty(self):
        #   herne karty
        vsetky_karty = []
        vsetky_karty_meno = []
        herne_karty_meno = []
        myList = os.listdir("karty/vek_1")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                curImg = cv2.imread(f"karty/vek_1/{karta}")
                curImg = cv2.resize(curImg, (karta_sirka, karta_vyska))
                vsetky_karty.append(curImg)
                vsetky_karty_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu jpg ani jpeg.")

        for i in range(0, 20):
            pick_id = random.randint(0, len(vsetky_karty) - 1)
            herne_karty_meno.append(vsetky_karty_meno[pick_id])
            vsetky_karty.pop(pick_id)
            vsetky_karty_meno.pop(pick_id)

        self.herne_karty_meno = herne_karty_meno

        #   herne divy pre hraca 1 a 2
        vsetky_divy = []
        vsetky_divy_meno = []
        myList = os.listdir("karty/divy")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                curImg = cv2.imread(f"karty/divy/{karta}")
                curImg = cv2.resize(curImg, (div_sirka, div_vyska))
                vsetky_divy.append(curImg)
                vsetky_divy_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu jpg ani jpeg.")

        for i in range(0, 4):
            pick_id = random.randint(0, len(vsetky_divy) - 1)
            self.hrac_1_divy_meno.append(vsetky_divy_meno[pick_id])
            self.hrac_1_divy_aktivne.append(False)
            vsetky_divy.pop(pick_id)
            vsetky_divy_meno.pop(pick_id)

        for i in range(0, 4):
            pick_id = random.randint(0, len(vsetky_divy) - 1)
            self.hrac_2_divy_meno.append(vsetky_divy_meno[pick_id])
            self.hrac_2_divy_aktivne.append(False)
            vsetky_divy.pop(pick_id)
            vsetky_divy_meno.pop(pick_id)

        #   tokeny
        vsetky_tokeny_meno = []
        myList = os.listdir("karty/tokeny")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.png'):
                vsetky_tokeny_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu png.")

        for i in range(0, 5):
            pick_id = random.randint(0, len(vsetky_tokeny_meno) - 1)
            self.herne_tokeny_meno.append(vsetky_tokeny_meno[pick_id])
            vsetky_tokeny_meno.pop(pick_id)

        #self.neherne_tokeny = vsetky_tokeny
        self.neherne_tokeny_meno = vsetky_tokeny_meno
        logging.debug(f"Herne tokeny: {self.herne_tokeny_meno}")

    def nakresli_vek(self):
        self.read_from_meta(f"archiv_hier/input_metadata_{self.hra_id}.json")

        self.tah = self.tah + 1

        self.aktivny_hrac = next(self.hraci)

        logging.debug(f"Aktivny hrac: {self.aktivny_hrac}")
        logging.debug(f"Tah cislo: {self.tah}")


        img = np.zeros((monitor_vyska, monitor_sirka, 3), np.uint8)

        #   nakresli titulok

        cv2.putText(img, f"7 Wonders DUEL - id hry: {self.hra_id}- tah: {self.tah}", (self.lavy_okraj[14], 35), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

        #   nakresli karty
        horny_okraj = horny_okraj_global
        for i in range(0, len(self.herne_karty_meno)):

            #   nastav hodnotu horneho okraja, aby sa karty poukladali do riadkov

            if i in [2, 5, 9, 14]:
                horny_okraj = horny_okraj + int(karta_vyska * 0.8)

            #   v riadkoch kde ma byt karta stale otocena ju nakresli otocenu, ale iba ak este nebola vybrana

            if i not in [2, 3, 4, 9, 10, 11, 12, 13]:

                #print(f"Karta {self.herne_karty_alias[i]} je {self.herne_karty_meno[i]}")

                if self.herne_karty_meno[i] is not None:
                    karta_img = cv2.imread(f"karty/vek_1/{self.herne_karty_meno[i]}.jpg")
                    karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
                    img[horny_okraj:horny_okraj + karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                    cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

            #   v ostatnych riadkoch zisti, ci karta nebola pouziva a ak nie, tak ci je validna na vyber. ak ano, zobraz ju otocenu.

            else:

                if self.herne_karty_meno[i] is not None:
                    if self.herne_karty_alias[i] in self.validne_karty():
                        karta_img = cv2.imread(f"karty/vek_1/{self.herne_karty_meno[i]}.jpg")
                        karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
                        img[horny_okraj:horny_okraj + karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj + 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                    else:
                        karta = cv2.imread("karty/ine/zadna_strana_vek_1_regular.jpeg")
                        karta = cv2.resize(karta, (karta_sirka, karta_vyska))
                        img[horny_okraj:horny_okraj + karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

        #   nakresli divy sveta hrac 1
        horny_okraj, lavy_okaj = horny_okraj_global, self.hrac_1_lavy_okraj[0]
        for idx, div in enumerate(self.hrac_1_divy_meno):
            div_img = cv2.imread(f"karty/divy/{div}.jpeg")
            div_img = cv2.resize(div_img, (div_sirka, div_vyska))
            if div in self.hrac_1_divy_aktivne:
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            else:
                div_img = cv2.cvtColor(div_img, cv2.COLOR_BGR2GRAY)
                div_img = np.stack((div_img,)*3, axis=-1)
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            if idx == 0:
                lavy_okaj = lavy_okaj + div_sirka + 20
            elif idx == 1:
                horny_okraj = horny_okraj + div_vyska + 20
                lavy_okaj = lavy_okaj - div_sirka - 20
            elif idx == 2:
                lavy_okaj = lavy_okaj + div_sirka + 20

        #   nakresli divy sveta hrac 2
        horny_okraj, lavy_okaj = horny_okraj_global, self.hrac_2_lavy_okraj[0]-20
        for idx, div in enumerate(self.hrac_2_divy_meno):
            div_img = cv2.imread(f"karty/divy/{div}.jpeg")
            div_img = cv2.resize(div_img, (div_sirka, div_vyska))
            if div in self.hrac_2_divy_aktivne:
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            else:
                div_img = cv2.cvtColor(div_img, cv2.COLOR_BGR2GRAY)
                div_img = np.stack((div_img,) * 3, axis=-1)
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            if idx == 0:
                lavy_okaj = lavy_okaj + div_sirka + 20
            elif idx == 1:
                horny_okraj = horny_okraj + div_vyska + 20
                lavy_okaj = lavy_okaj - div_sirka - 20
            elif idx == 2:
                lavy_okaj = lavy_okaj + div_sirka + 20

        #   nakresli zonu hraca 1 a 2 a zvyrazni aktivneho
        if self.aktivny_hrac == self.hraci_mena[0]:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[19] + 80 + karta_sirka, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)), (self.lavy_okraj[14] - 40, int(monitor_vyska * 0.9)), (0, 0, 255), 2)
            cv2.rectangle(img, (self.lavy_okraj[19] + 80 + karta_sirka, int(monitor_vyska / 2)), (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
        else:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[19] + 80 + karta_sirka, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)), (self.lavy_okraj[14] - 40, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
            cv2.rectangle(img, (self.lavy_okraj[19] + 80 + karta_sirka, int(monitor_vyska / 2)), (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 255), 2)

        #   nakresli peniaze a body
        cv2.putText(img, "Pen:" +str(self.hrac_1_peniaze), (self.lavy_okraj[14] - 130, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
        cv2.putText(img, "Body:" +str(self.hrac_1_body), (self.lavy_okraj[14] - 260, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 51, 51), 1)
        cv2.putText(img, "Pen:" + str(self.hrac_2_peniaze), (monitor_sirka - 130, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
        cv2.putText(img, "Body:" + str(self.hrac_2_body), (monitor_sirka - 260, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 51, 51), 1)

        #   nakresli majetok hraca 1 aj s tokenami
        sivohnedy_okraj = self.hrac_1_horny_okraj_sivohnede
        zlty_okraj = self.hrac_1_horny_okraj_zlte
        modry_okraj = self.hrac_1_horny_okraj_modre
        cerveny_okraj = self.hrac_1_horny_okraj_cervene
        zeleny_okraj = self.hrac_1_horny_okraj_zelene

        for karta in self.hrac_1_karty:
            karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
            # img[hore:dole, lavo:pravo]
            if eval("self."+karta.lower()+".farba") == "hneda" or eval("self."+karta.lower()+".farba") == "siva":
                img[sivohnedy_okraj:sivohnedy_okraj + karta_vyska, self.hrac_1_lavy_okraj[0]:self.hrac_1_lavy_okraj[0] + karta_sirka] = karta_img
                sivohnedy_okraj += 25
            elif eval("self."+karta.lower()+".farba") == "zlta":
                img[zlty_okraj:zlty_okraj + karta_vyska, self.hrac_1_lavy_okraj[1]:self.hrac_1_lavy_okraj[1] + karta_sirka] = karta_img
                zlty_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "modra":
                img[modry_okraj:modry_okraj + karta_vyska, self.hrac_1_lavy_okraj[2]:self.hrac_1_lavy_okraj[2] + karta_sirka] = karta_img
                modry_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "cervena":
                img[cerveny_okraj:cerveny_okraj + karta_vyska, self.hrac_1_lavy_okraj[3]:self.hrac_1_lavy_okraj[3] + karta_sirka] = karta_img
                cerveny_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zelena":
                img[zeleny_okraj:zeleny_okraj + karta_vyska, self.hrac_1_lavy_okraj[4]:self.hrac_1_lavy_okraj[4] + karta_sirka] = karta_img
                zeleny_okraj += 25

        h_okraj = int(monitor_vyska * 0.80)
        l_okraj = 30
        for token in self.hrac_1_tokeny:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj + token_rozmer, l_okraj:l_okraj + token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   nakresli majetok hraca 2 aj s tokenami
        sivohnedy_okraj = self.hrac_2_horny_okraj_sivohnede
        zlty_okraj = self.hrac_2_horny_okraj_zlte
        modry_okraj = self.hrac_2_horny_okraj_modre
        cerveny_okraj = self.hrac_2_horny_okraj_cervene
        zeleny_okraj = self.hrac_2_horny_okraj_zelene

        for karta in self.hrac_2_karty:
            karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
            # img[hore:dole, lavo:pravo]
            if eval("self." + karta.lower() + ".farba") == "hneda" or eval(
                    "self." + karta.lower() + ".farba") == "siva":
                img[sivohnedy_okraj:sivohnedy_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[0]:self.hrac_2_lavy_okraj[0] + karta_sirka] = karta_img
                sivohnedy_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zlta":
                img[zlty_okraj:zlty_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[1]:self.hrac_2_lavy_okraj[1] + karta_sirka] = karta_img
                zlty_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "modra":
                img[modry_okraj:modry_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[2]:self.hrac_2_lavy_okraj[2] + karta_sirka] = karta_img
                modry_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "cervena":
                img[cerveny_okraj:cerveny_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[3]:self.hrac_2_lavy_okraj[3] + karta_sirka] = karta_img
                cerveny_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zelena":
                img[zeleny_okraj:zeleny_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[4]:self.hrac_2_lavy_okraj[4] + karta_sirka] = karta_img
                zeleny_okraj += 25

        h_okraj = int(monitor_vyska * 0.80)
        l_okraj = self.hrac_2_lavy_okraj[0]-20
        for token in self.hrac_2_tokeny:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj + token_rozmer, l_okraj:l_okraj + token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   nakresli odhodene karty
        h_okraj = int(monitor_vyska * 0.7)
        l_okraj = int((self.lavy_okraj[15] + self.lavy_okraj[14]) / 2 - 10)
        cv2.line(img, (l_okraj + 28, h_okraj - 10), (self.lavy_okraj[19] + karta_sirka, h_okraj - 10), (0, 102, 204), 1)
        cv2.putText(img, "Discard", (self.lavy_okraj[14], h_okraj - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 102, 204), 1)
        for karta in self.odhodene_karty:
            karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
            img[h_okraj:h_okraj + karta_vyska, l_okraj:l_okraj + karta_sirka] = karta_img
            l_okraj = l_okraj + 50


        #   nakresli boje
        h_okraj = int(monitor_vyska * 0.87)
        l_okraj = self.lavy_okraj[15] - 40
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

        #   nakresli tokeny
        h_okraj = int(monitor_vyska * 0.90)
        l_okraj = self.lavy_okraj[15]
        for token in self.herne_tokeny_meno:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj+token_rozmer, l_okraj:l_okraj+token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   dokresli podpis
        cv2.putText(img, "Vytvorene Jan @ Strompl 28.10.2020", (int(monitor_sirka * 0.8), monitor_vyska - 22), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(img, "Aktualizovane 30.11.2020", (int(monitor_sirka * 0.8), monitor_vyska - 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("7wonders", img)

        logging.debug(f"Cakam na vyber. Validne karty: {self.validne_karty()}")
        if self.validne_karty():
            key = cv2.waitKey(0)
            if chr(key) in self.herne_karty_alias:
                meno_karty = self.herne_karty_meno[self.herne_karty_alias.index(chr(key))]
                logging.debug(f"Stlacena klavesa: {chr(key)} {self.aktivny_hrac} chce vykonat akciu s kartou: {meno_karty}")
                self.vyber_a_aktivuj_kartu(chr(key))
                #self.nakresli_vek()
            else:
                logging.error(f"Vyber karty - {chr(key)} - je nevalidna. Validne karty su: {self.validne_karty()}")
                ukaz_error("nespravna_volba")
                next(self.hraci)
                self.tah = self.tah - 1
                self.nakresli_vek()
        else:
            #os.remove(f"archiv_hier/input_metadata_{self.hra_id}.json")
            logging.info("Koniec veku 1.")

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

    def vyber_a_aktivuj_kartu(self, karta):
        if karta in self.validne_karty():
            zvolena_karta = self.herne_karty_meno[self.herne_karty_alias.index(karta)]
            akcia = self.zvol_mozosti(zvolena_karta)
            self.vykonaj_akciu(zvolena_karta, akcia)
            self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
            self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
            self.metadata_to_json(f"archiv_hier/input_metadata_{self.hra_id}.json")
            self.nakresli_vek()
        else:
            logging.error(f"Karta {self.herne_karty_meno[self.herne_karty_alias.index(karta)]} nie je plne odkryta, preto ju nie je mozne zahrat. Znova.")
            ukaz_error("nevalidna_karta")
            next(self.hraci)
            self.tah = self.tah - 1
            #self.metadata_to_json("input_metadata.json")
            self.nakresli_vek()

    def zvol_mozosti(self, zvolena_karta):
        cv2.namedWindow("Zvolena karta.")
        zvolena_karta_pozadie = np.zeros((karta_vyska * 3, karta_sirka * 6, 3), np.uint8)
        zvolena_karta_img = cv2.imread(f"karty/vek_1/{zvolena_karta}.jpg")
        zvolena_karta_img = cv2.resize(zvolena_karta_img, (karta_sirka * 2, karta_vyska * 2))
        zvolena_karta_pozadie[50:50+(karta_vyska*2), 20:20+(karta_sirka*2)] = zvolena_karta_img
        cv2.putText(zvolena_karta_pozadie, "(o) Odhod", (int(karta_sirka * 2.5), 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(k) Kup", (int(karta_sirka * 2.5), 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(d) Postav div:", (int(karta_sirka * 2.5), 210), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(c) Vyber inu kartu:", (int(karta_sirka * 2.5), 270), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.moveWindow("Zvolena karta.", int(monitor_sirka / 3), int(monitor_vyska / 2))
        cv2.imshow("Zvolena karta.", zvolena_karta_pozadie)
        key = cv2.waitKey()
        if chr(key) == "o":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: odhod")
            cv2.destroyWindow("Zvolena karta.")
            return "odhod"
        elif chr(key) == "k":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: kup")
            cv2.destroyWindow("Zvolena karta.")
            return "kup"
        elif chr(key) == "d":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: postav_div")
            cv2.destroyWindow("Zvolena karta.")
            return "postav_div"
        elif chr(key) == "c":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: storno_vyberu")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Zvolena karta.")
            self.nakresli_vek()
        else:
            logging.error(f"Stlacena klavesa: {chr(key)} Tato akcia nie je povolena.")
            cv2.destroyWindow("Zvolena karta.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            self.nakresli_vek()
            #self.zvol_mozosti(zvolena_karta)

    def vykonaj_akciu(self, meno_karty, akcia):
        if self.aktivny_hrac == self.hraci_mena[0]:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        if akcia == "odhod":
            exec(f"self.hrac_{hrac}_peniaze = self.hrac_{hrac}_peniaze + 2 + self.zrataj_karty({hrac}, 'zlta')")
            novy_stav = eval(f"self.hrac_{hrac}_peniaze")
            logging.info(f"{self.aktivny_hrac} ohodil {meno_karty} za {2 + self.zrataj_karty(hrac, 'zlta')} panezi. Novy stav penazi {novy_stav}")
            self.odhodene_karty.append(meno_karty)

        if akcia == "kup":
            if self.mozem_kupit(hrac, meno_karty):
                self.kup_kartu(hrac, meno_karty, typ="kartu")
            else:
                logging.error(f"Kartu {meno_karty} si nemozem kupit. Nedostatok penazi. Zvol inu kartu.")
                ukaz_error("nedostatok_penazi")
                next(self.hraci)
                self.tah = self.tah - 1
                self.nakresli_vek()

        if akcia == "postav_div":
            suradnice_sirka = [50, 50+div_sirka + 20, 50, 50+div_sirka + 20]
            suradnice_vyska = [50, 50, 50+div_vyska + 20, 50+div_vyska + 20]
            cv2.namedWindow("Vyber div")
            vyber_div_pozadie = np.zeros((div_vyska * 3, div_sirka * 3 - 50, 3), np.uint8)
            for idx, div in enumerate(eval(f"self.hrac_{hrac}_divy_meno")):
                div = cv2.imread(f"karty/divy/{div}.jpeg")
                div = cv2.resize(div, (div_sirka, div_vyska))
                vyber_div_pozadie[suradnice_vyska[idx]:suradnice_vyska[idx] + div_vyska, suradnice_sirka[idx]:suradnice_sirka[idx] + div_sirka] = div
                cv2.putText(vyber_div_pozadie, str(idx+1), (suradnice_sirka[idx], suradnice_vyska[idx]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.imshow("Vyber div", vyber_div_pozadie)
            key = cv2.waitKey()
            if chr(key) in ("1", "2", "3", "4"):
                div_meno = eval(f"self.hrac_{hrac}_divy_meno[int(chr({key}))-1]")
                logging.debug(f"Stlacena klavesa: {chr(key)} Vybany div: {div_meno}")
                if self.mozem_kupit(hrac, div_meno):
                    self.kup_kartu(hrac, div_meno, typ="div")
                    self.vyhodnot_div(hrac, div_meno)
                    eval(f"self.hrac_{hrac}_divy_aktivne.append('{div_meno}')")
                    cv2.destroyWindow("Vyber div")
                else:
                    ukaz_error("nedostatok_penazi")
                    next(self.hraci)
                    self.tah = self.tah - 1
                    cv2.destroyWindow("Vyber div")
                    self.nakresli_vek()
            else:
                logging.error(f"Volba {chr(key)} nie je povolena. Vyber z [1, 2, 3, 4]. Znova.")
                ukaz_error("nespravna_volba")
                next(self.hraci)
                self.tah = self.tah - 1
                cv2.destroyWindow("Vyber div")
                self.nakresli_vek()

    def mozem_kupit(self, hrac, meno_karty):
        cena = eval("self." + meno_karty.lower() + ".cena")

        #   ak div, tak len taky ktory este nemam.
        if meno_karty in eval(f"self.hrac_{hrac}_divy_aktivne"):
            logging.error(f"Hrac {self.aktivny_hrac} uz div {meno_karty} vlastni.")
            return False

        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        suroviny_mam = eval(f"self.hrac_{hrac}_suroviny").copy()
        peniaze_mam = eval(f"self.hrac_{hrac}_peniaze")
        logging.debug(f"Cena suroviny: {cena}")
        logging.debug(f"Peniaze k dispozicii na zaciatku: {peniaze_mam}")
        # ak je cena len penazna
        if type(cena) == int:
            if peniaze_mam >= cena:
                return True
            else:
                logging.error(f"Hrac {self.aktivny_hrac} nema dost penazi na kupu {meno_karty}")
                return False

            # ak je cena kombinovana
        else:
            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "modra" and "Zednarstvi" in eval(f"self.hrac_{hrac}_tokeny"):
                suroviny_mam.append("X")
                suroviny_mam.append("X")
                logging.debug(f"Hrac vlastni Zednarstvi, do poolu surovin som pridal [X, X]")

            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "div" and "Architektura" in eval(f"self.hrac_{hrac}_tokeny"):
                suroviny_mam.append("Y")
                suroviny_mam.append("Y")
                logging.debug(f"Hrac vlastni Architektura, do poolu surovin som pridal [Y, Y]")

            for surovina in cena:
                try:
                    surovina = int(surovina)
                except:
                    surovina = surovina
                logging.debug(f"Typ suroviny {surovina}: {type(surovina)}")
                if type(surovina) == int:
                    if peniaze_mam >= surovina:
                        peniaze_mam -= surovina
                        logging.debug(f"Po pouziti suroviny {surovina} mi ostava {peniaze_mam} penazi na kupu dalsich surovin.")
                        pass
                    else:
                        logging.warning(f"Karta {meno_karty} sa neda kupit. Nedostatok peniazi.")
                        return False
                else:
                    logging.debug(f"Suroviny mam pred kontrolou: {suroviny_mam}")
                    if (suroviny_mam is not None) and (surovina in suroviny_mam):
                        suroviny_mam.remove(surovina)
                        logging.debug(f"Pouzil som: {surovina} z vlastnych zdrojov. Ostalo mi: {suroviny_mam}")
                        pass
                    elif surovina in ("D", "H", "K") and "W" in suroviny_mam:
                        surovina = "W"
                        suroviny_mam.remove(surovina)
                        logging.debug(f"Pouzil som {surovina}, z divu Velky majak. Ostalo mi: {suroviny_mam}")
                        pass
                    elif surovina in ("P", "S") and "U" in suroviny_mam:
                        surovina = "U"
                        suroviny_mam.remove(surovina)
                        logging.debug(f"Pouzil som {surovina} z divu Piraeus. Ostao mi: {suroviny_mam}")
                        pass
                    elif surovina == "D" and "Zasobarna_dreva" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Zasobarna dreva za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina} hoc je zlacnena Zasobarnou dreva.")
                            return False
                    elif surovina == "H" and "Zasobarna_hliny" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Zasobarna hliny za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina}  hoc je zlacnena Zasobarnou hliny.")
                            return False
                    elif surovina == "K" and "Zasobarna_kamene" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Zasobarna kamene za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina} hoc je zlacnena Zasobarnou kamene.")
                            return False
                    elif surovina in ("P", "S") and "Hostinec" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Hostinec za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina} hoc je zlacnena kartou Hostinec.")
                            return False
                    elif "X" in suroviny_mam:
                        suroviny_mam.remove("X")
                        logging.debug(f"Pouzil som zlacnenie modrej karty tokenom Zednarstvi.")
                        pass
                    elif "Y" in suroviny_mam:
                        suroviny_mam.remove("Y")
                        logging.debug(f"Pouzil som zlacnenie postavenia divu tokenom Architektura.")
                        pass
                    else:
                        cena_suroviny = eval(f"self.hrac_{oponent}_suroviny.count('{surovina}') + 2")
                        logging.debug(f"Surovinu nemam, ani si ju neviem zlacniet. Jej cena je: {cena_suroviny} a mam {peniaze_mam}")
                        if peniaze_mam >= cena_suroviny:
                            peniaze_mam -= cena_suroviny
                            logging.debug(f"Surovina {surovina} kupena za {cena_suroviny} Ostalo mi {peniaze_mam}")
                            pass
                        else:
                            logging.warning(f"Na surovinu {surovina}, nemam peniaze. Znova vyber karty.")
                            return False
            return True

    def kup_kartu(self, hrac, meno_karty, typ="kartu", zlacnene=None):

        #   prv vyskusam zaskat metadata: kolo bodov, penazi, bojov a bojov mi karta da.

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
        kelo_placela = 0 # zrata kolo penazi zaplati za nakup surovin banke
        if type(cena_karty) == int:
            cena = cena_karty
        else:
            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "modra" and "Zednarstvi" in eval(f"self.hrac_{hrac}_tokeny"):
                co_mam.append("X")
                co_mam.append("X")

            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "div" and "Architektura" in eval(f"self.hrac_{hrac}_tokeny"):
                co_mam.append("Y")
                co_mam.append("Y")
            for surovina in cena_karty:
                try:
                    surovina = int(surovina)
                except:
                    surovina = surovina
                if type(surovina) == int:
                    cena = cena + surovina
                else:
                    if (co_mam is not None) and (surovina in co_mam):
                        co_mam.remove(surovina)
                    elif surovina in ("D", "H", "K") and "W" in co_mam:
                        surovina = "W"
                        #print("DEBUG: pouzil som", surovina, "z divu Velky majak")
                        co_mam.remove(surovina)
                    elif surovina in ("P", "S") and "U" in co_mam:
                        surovina = "U"
                        #print("DEBUG: pouzil som", surovina, "z divu Piraeus")
                        co_mam.remove(surovina)
                    elif surovina == "D" and "Zasobarna_dreva" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif surovina == "H" and "Zasobarna_hliny" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif surovina == "K" and "Zasobarna_kamene" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif surovina in ("P", "S") and "Hostinec" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif "X" in co_mam:
                        co_mam.remove("X")
                    elif "Y" in co_mam:
                        co_mam.remove("Y")
                    else:
                        prirazka = eval(f"self.hrac_{oponent}_suroviny.count('{surovina}') + 2")
                        cena = cena + prirazka
                        kelo_placela += prirazka

        if zlacnene is None:
            logging.debug(f"Karta nie je zlacnena Divmi alebo Tokenmi. Jej cena je: {cena}")
            cena = cena

        else:
            logging.debug(f"Karta je zlacnena na {zlacnene}")
            cena = zlacnene
        exec(f"self.hrac_{hrac}_peniaze -= {cena}")

        #   ak oponent vlastni token Ekonomie, dam mu peniaze za suroviny
        if "Ekonomie" in eval(f"self.hrac_{oponent}_tokeny"):
            exec(f"self.hrac_{oponent}_peniaze += {kelo_placela}")
            logging.info(f"Oponent vlastni token Ekonomie, dal som mu {kelo_placela} penazi.")

        # dostanem
        #   body
        exec(f"self.hrac_{hrac}_body += {body_gain}")
        #   peniaze
        exec(f"self.hrac_{hrac}_peniaze += {peniaze_gain}")
        #   suroviny ak je karta siva alebo hneda
        if karta_farba in ("hneda", "siva", "div") :
            for sur in suroviny_gain:
                exec(f"self.hrac_{hrac}_suroviny.append('{sur}')")
        #   boje

        #   ak vlastnim token Strategie, zosilnim boje
        if "Strategie" in eval(f"self.hrac_{hrac}_tokeny"):
            boje_gain += 1
            logging.info(f"Vlastnim token Strategie, zosilnil som ucinok bojov o 1.")

        if hrac == 1:   self.boje_stav = self.boje_stav + boje_gain
        if hrac == 2:   self.boje_stav = self.boje_stav - boje_gain
        #   zrusim peniaze
        kolko_penazi_zrus = self.boje_zrus_peniaze[self.boje_stav]
        if kolko_penazi_zrus is not None:
            if eval(f"self.hrac_{oponent}_peniaze") < kolko_penazi_zrus:
                exec(f"self.hrac_{oponent}_peniaze = 0")
            else:
                exec(f"self.hrac_{oponent}_peniaze -= {kolko_penazi_zrus}")
            logging.info(f"Efekt bojov zrusil {kolko_penazi_zrus} penazi.")
            if self.boje_stav in (1, 2, 3):
                self.boje_zrus_peniaze[1:4] = None, None, None
            elif self.boje_stav in (4, 5, 6):
                self.boje_zrus_peniaze[4:7] = None, None, None
            elif self.boje_stav in (12, 13, 14):
                self.boje_zrus_peniaze[12:15] = None, None, None
            else:
                self.boje_zrus_peniaze[15:18] = None, None, None

        #   samotnu kartu
        if typ == "kartu":  eval(f"self.hrac_{hrac}_karty.append(meno_karty)")
        elif typ == "div":  eval(f"self.hrac_{hrac}_divy_aktivne.append(meno_karty)")
        elif typ == "token":  eval(f"self.hrac_{hrac}_tokeny.append(meno_karty)")
        else:   pass
        logging.info(
            f"{self.aktivny_hrac} kupuje {typ} {meno_karty} za {cena}. Dostal {body_gain} bodov, {peniaze_gain} penazi, suroviny: {suroviny_gain} a boje: {boje_gain}")

    def vyhodnot_div(self, hrac, div_meno):
        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        efekty = eval(f"self.{div_meno.lower()}.efekt")

        #   ak mam token Teologie a div nema repeater, pridam mu.
        if "repeat" not in efekty and "Teologie" in eval(f"self.hrac_{hrac}_tokeny"):
            efekty.append("repeat")
            logging.debug(f"Vlastnim token Teologie a div nema efekt - repeat - tak efekt bol pridany.")

        for efekt in efekty:
            logging.info(f"Efekt divu: {div_meno} - {efekt}")
            if efekt == "repeat":
                logging.info(f"{self.aktivny_hrac} ide znovu.")
                if hrac == 1: self.aktivny_hrac = self.hraci_mena[1]
                if hrac == 2: self.aktivny_hrac = self.hraci_mena[0]
                #next(self.hraci)
                self.metadata_to_json(f"archiv_hier/input_metadata_{self.hra_id}.json")
            if efekt == "noefekt":
                pass
            if efekt == "oponent-3p":
                logging.info(f"Oponentovi odoberam 3 peniaze.")
                exec(f"self.hrac_{oponent}_peniaze -= 3")
            if efekt == "vezmi_kartu_z_discartu":
                if len(self.odhodene_karty) != 0:
                    self.vezmi_kartu_z_disartu(hrac)
                else:
                    logging.info("Diskart je prazdny. Efekt prepadol.")
            if efekt == "odhod_oponentovi_hnedu":
                if self.zrataj_karty(oponent, "hneda") != 0:
                    self.odhod_hracovi_kartu(oponent, "hneda")
                else:
                    logging.info("Oponent nema ziadne hnede karty. Efekt prepadol.")
            if efekt == "odhod_oponentovi_sivu":
                if self.zrataj_karty(oponent, "siva") != 0:
                    self.odhod_hracovi_kartu(oponent, "siva")
                else:
                    logging.info("Oponent nema ziadne hnede karty. Efekt prepadol.")
            if efekt == "vezmi_odhodeny_zeleny_zeton":
                self.vezmi_odhodeny_zeleny_token(hrac)

    def vezmi_kartu_z_disartu(self, hrac):
        cv2.namedWindow("Diskart")
        diskart_img = np.zeros((200, int(monitor_sirka/2), 3), np.uint8)
        y = 10
        validne_klavesy = []
        for idx, odhodena_karta in enumerate(self.odhodene_karty):
            odhodena_karta = cv2.imread(f"karty/vek_1/{odhodena_karta}.jpg")
            odhodena_karta = cv2.resize(odhodena_karta, (karta_sirka, karta_vyska))
            diskart_img[20:20+karta_vyska, y:y+karta_sirka] = odhodena_karta
            cv2.putText(diskart_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Diskart", diskart_img)
        logging.debug(f"Validne karty na vyber z odhodenych karat su: {validne_klavesy}")
        key = cv2.waitKey()
        logging.debug(f"Vyber klavesy: {chr(key)}")
        if chr(key) in validne_klavesy:
            logging.info(f"Z diskartu sa berie: {self.odhodene_karty[int(chr(key))]}")
            self.kup_kartu(hrac, self.odhodene_karty[int(chr(key))], zlacnene=0)
            self.odhodene_karty.pop(int(chr(key)))
            cv2.destroyWindow("Diskart")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Diskart")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def odhod_hracovi_kartu(self, hrac, typ):
        cv2.namedWindow("Hracove karty")
        oponentove_karty_img = np.zeros((200, int(monitor_sirka / 2), 3), np.uint8)
        y = 10
        validne_klavesy = []
        hracove_karty = []

        for karta in eval(f"self.hrac_{hrac}_karty"):
            if eval("self." + karta.lower() + ".farba") == typ:
                hracove_karty.append(karta)

        logging.debug(f"Hracove karty typu {typ} su: {hracove_karty}")
        for idx, karta in enumerate(hracove_karty):
            karta = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta = cv2.resize(karta, (karta_sirka, karta_vyska))
            oponentove_karty_img[20:20 + karta_vyska, y:y + karta_sirka] = karta
            cv2.putText(oponentove_karty_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Hracove karty", oponentove_karty_img)
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.info(f"Oponentovi rusim: {hracove_karty[int(chr(key))]}")
            eval(f"self.hrac_{hrac}_karty.remove('{hracove_karty[int(chr(key))]}')")
            cv2.destroyWindow("Hracove karty")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Hracove karty")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def vezmi_odhodeny_zeleny_token(self, hrac):
        cv2.namedWindow("Neherne tokeny")
        neherne_tokeny_img = np.zeros((130, 500, 3), np.uint8)
        y = 30
        validne_klavesy = []

        tri_vybrane = random.sample(self.neherne_tokeny_meno, 3)
        logging.debug(f"3 vybrane tokeny mimo hry: {tri_vybrane}")


        for idx, token in enumerate(tri_vybrane):
            token = cv2.imread(f"karty/tokeny/{token}.png")
            token = cv2.resize(token, (token_rozmer, token_rozmer))
            neherne_tokeny_img[20:20 + token_rozmer, y:y + token_rozmer] = token
            cv2.putText(neherne_tokeny_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += token_rozmer + 10
            validne_klavesy.append(str(idx))

        cv2.imshow("Neherne tokeny", neherne_tokeny_img)
        logging.debug(f"validne klavesy: {validne_klavesy}")
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.debug(f"Stlacena klavesa: {chr(key)} Beriem si token: {tri_vybrane[int(chr(key))]}")
            #eval(f"self.hrac_{hrac}_tokeny.append('{self.neherne_tokeny_meno[int(chr(key))]}')")
            self.kup_kartu(hrac, tri_vybrane[int(chr(key))], typ="token", zlacnene=0)
            self.vyhodnot_token(hrac, tri_vybrane[int(chr(key))])
            self.neherne_tokeny_meno.remove(tri_vybrane[int(chr(key))])
            cv2.destroyWindow("Neherne tokeny")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Neherne tokeny")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def vyhodnot_token(self, hrac, token_meno):
        logging.info(f"Vyhodnocujem token: {token_meno}")
        try:
            efekt_tokenu = eval("self." + token_meno.lower() + ".efekt_tokenu")
            logging.debug(f"Efekt tokenu: {efekt_tokenu}")
        except:
            efekt_tokenu = None
            logging.debug("Token nema specialny efekt.")

        if efekt_tokenu:
            if efekt_tokenu == "zlacni_divy":
                #   hotovo v mozem_kupit()
                pass
            if efekt_tokenu == "kelo_placela":
                #   hotovo z kup_kartu()
                pass
            if efekt_tokenu == "3_za_kazdy_token":
                #   vyhodnoti sa na konci hry.
                pass
            if efekt_tokenu == "boje+1":
                #   hotovo v kup_kartu()
                pass
            if efekt_tokenu == "repeater_divom":
                # hotovo v vyhodnot_div()
                pass
            if efekt_tokenu == "ak_zadarmo_potom+4p":
                pass
            if efekt_tokenu == "pridaj_zeleny_symbol":
                pass
            if efekt_tokenu == "zlacni_modre":
                #   hotovo v mozem_kupit()
                pass

    def zrataj_karty(self, hrac, farba):
        count = 0
        for meno_karty in eval("self.hrac_"+str(hrac)+"_karty"):
            if eval("self."+meno_karty.lower()+".farba") == farba:
                count = count +1
        #logging.debug(f"{hrac} ma {count} kariet farby {farba}")
        return count

    def metadata_to_json(self, metadatafile):
        logging.debug(f"Obnovujem metadata...")
        vars_to_json = {"rozohrana_hra": "Ano",
                        "vek": 1,
                        "cas_hry": time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime()),
                        "hra_id": self.hra_id,
                        "herne_karty_meno": self.herne_karty_meno,
                        "herne_karty_alias": self.herne_karty_alias,
                        "odhodene_karty": self.odhodene_karty,
                        "boje_stav": self.boje_stav,
                        "boje_zrus_peniaze": self.boje_zrus_peniaze,
                        "herne_tokeny_meno": self.herne_tokeny_meno,
                        "neherne_tokeny_meno": self.neherne_tokeny_meno,
                        "tah": self.tah,
                        "hraci_mena": self.hraci_mena,
                        "aktivny_hrac": self.aktivny_hrac,
                        "hrac_1_peniaze": self.hrac_1_peniaze,
                        "hrac_2_peniaze": self.hrac_2_peniaze,
                        "hrac_1_body": self.hrac_1_body,
                        "hrac_2_body": self.hrac_2_body,
                        "hrac_1_karty": self.hrac_1_karty,
                        "hrac_2_karty": self.hrac_2_karty,
                        "hrac_1_suroviny": self.hrac_1_suroviny,
                        "hrac_2_suroviny": self.hrac_2_suroviny,
                        "hrac_1_divy_meno": self.hrac_1_divy_meno,
                        "hrac_1_divy_aktivne": self.hrac_1_divy_aktivne,
                        "hrac_2_divy_meno": self.hrac_2_divy_meno,
                        "hrac_2_divy_aktivne": self.hrac_2_divy_aktivne,
                        "hrac_1_tokeny": self.hrac_1_tokeny,
                        "hrac_2_tokeny": self.hrac_2_tokeny}

        with open(metadatafile, 'w') as f:
            json.dump(vars_to_json, f, indent=2)

    def read_from_meta(self, metadatafile):
        if not os.path.exists(metadatafile):
            shutil.copy("meta/default_metadata.json", metadatafile)
        with open(metadatafile) as metadata:
            data = json.load(metadata)
            if data["hra_id"] != 0:
                self.hra_id = data["hra_id"]
            if len(data["herne_karty_meno"]) != 0:
                self.herne_karty_meno = data["herne_karty_meno"]
            self.herne_karty_alias = data["herne_karty_alias"]
            self.odhodene_karty = data["odhodene_karty"]
            self.boje_stav = data["boje_stav"]
            self.boje_zrus_peniaze = data["boje_zrus_peniaze"]
            if len(data["herne_tokeny_meno"]) != 0:
                self.herne_tokeny_meno = data["herne_tokeny_meno"]
            if len(data["neherne_tokeny_meno"]) != 0:
                self.neherne_tokeny_meno = data["neherne_tokeny_meno"]
            self.tah = data["tah"]
            self.hraci_mena = data["hraci_mena"]
            id_hrac = self.hraci_mena.index(data["aktivny_hrac"])
            self.hraci = cycle(self.hraci_mena)
            self.aktivny_hrac = islice(self.hraci, id_hrac, None)
            next(self.aktivny_hrac)
            self.hrac_1_peniaze = data["hrac_1_peniaze"]
            self.hrac_2_peniaze = data["hrac_2_peniaze"]
            self.hrac_1_body = data["hrac_1_body"]
            self.hrac_2_body = data["hrac_2_body"]
            self.hrac_1_karty = data["hrac_1_karty"]
            self.hrac_2_karty = data["hrac_2_karty"]
            self.hrac_1_suroviny = data["hrac_1_suroviny"]
            self.hrac_2_suroviny = data["hrac_2_suroviny"]
            if len(data["hrac_1_divy_meno"]) != 0:
                self.hrac_1_divy_meno = data["hrac_1_divy_meno"]
            self.hrac_1_divy_aktivne = data["hrac_1_divy_aktivne"]
            if len(data["hrac_2_divy_meno"]) != 0:
                self.hrac_2_divy_meno = data["hrac_2_divy_meno"]
            self.hrac_2_divy_aktivne = data["hrac_2_divy_aktivne"]
            self.hrac_1_tokeny = data["hrac_1_tokeny"]
            self.hrac_2_tokeny = data["hrac_2_tokeny"]
            metadata.close()

class SevenWondersDruhyVek:

    myList = os.listdir("karty/vek_1")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_cards.%s" % (x, x))

    myList = os.listdir("karty/vek_2")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_cards.%s" % (x, x))

    myList = os.listdir("karty/divy")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() == ".jpeg":
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_divy.%s" % (x, x))

    myList = os.listdir("karty/tokeny")
    for karta in myList:
        if os.path.splitext(karta)[1].lower() == ".png":
            x = karta.split(".")[0].lower()
            exec("%s = seven_wonders_tokeny.%s" % (x, x))

    def __init__(self, hra_id):
        logging.info("Zacal vek 2.")

        self.lavy_okraj = []

        self.hrac_1_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_zlte = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_modre = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_cervene = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_zelene = int(monitor_vyska / 2) + 15
        self.hrac_1_lavy_okraj = [num for num in np.arange(30,400,karta_sirka+10)]
        self.hrac_2_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
        self.hrac_2_horny_okraj_zlte = int(monitor_vyska / 2) + 15
        self.hrac_2_horny_okraj_modre = int(monitor_vyska / 2) + 15
        self.hrac_2_horny_okraj_cervene = int(monitor_vyska / 2) + 15
        self.hrac_2_horny_okraj_zelene = int(monitor_vyska / 2) + 15
        self.hrac_2_lavy_okraj = [1320, 1410, 1500, 1590, monitor_sirka - 30 - karta_sirka - 10]

        self.herne_karty_meno = []
        self.herne_karty_alias = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r","s", "t"]

        self.herne_tokeny_meno = []
        self.neherne_tokeny_meno = []
        self.hra_id = hra_id


        self.zisti_rohy()
        self.vyber_herne_karty()
        self.nakresli_vek()

    def zisti_rohy(self):
        lavy_okraj = []
        okraj_karty = int(monitor_sirka / 3 + 50) - karta_sirka
        lavy_okraj.append(okraj_karty)

        for i in range(1, 20):
            if i in [6, 11, 15, 18]:
                if i == 6: okraj_karty = lavy_okraj[0] + int(karta_sirka * 0.8)
                if i == 11: okraj_karty = lavy_okraj[6] + int(karta_sirka * 0.8)
                if i == 15: okraj_karty = lavy_okraj[11] + int(karta_sirka * 0.8)
                if i == 18: okraj_karty = lavy_okraj[15] + int(karta_sirka * 0.8)
            else:
                okraj_karty = lavy_okraj[i - 1] + int(karta_sirka * 1.4)
            lavy_okraj.append(okraj_karty)
        self.lavy_okraj = lavy_okraj

    def vyber_herne_karty(self):
        #   herne karty
        vsetky_karty = []
        vsetky_karty_meno = []
        herne_karty_meno = []
        myList = os.listdir("karty/vek_2")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                curImg = cv2.imread(f"karty/vek_2/{karta}")
                curImg = cv2.resize(curImg, (karta_sirka, karta_vyska))
                vsetky_karty.append(curImg)
                vsetky_karty_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu jpg ani jpeg.")

        for i in range(0, 20):
            pick_id = random.randint(0, len(vsetky_karty) - 1)
            herne_karty_meno.append(vsetky_karty_meno[pick_id])
            vsetky_karty.pop(pick_id)
            vsetky_karty_meno.pop(pick_id)

        self.herne_karty_meno = herne_karty_meno

    def nakresli_vek(self):
        self.read_from_meta(f"archiv_hier/input_metadata_{self.hra_id}.json")

        self.tah = self.tah + 1
        self.aktivny_hrac = next(self.hraci)

        logging.debug(f"Aktivny hrac: {self.aktivny_hrac}")
        logging.debug(f"Tah cislo: {self.tah}")

        img = np.zeros((monitor_vyska, monitor_sirka, 3), np.uint8)
        cv2.putText(img, f"7 Wonders DUEL - id hry: {self.hra_id}- tah: {self.tah}", (self.lavy_okraj[0]-35, 35), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)


        horny_okraj = horny_okraj_global
        for i in range(0, len(self.herne_karty_meno)):
            #   nastav hodnotu horneho okraja, aby sa karty poukladali do riadkov

            if i in [6, 11, 15, 18]:
                horny_okraj = horny_okraj + int(karta_vyska * 0.8)

            #   v riadkoch kde ma byt karta stale otocena ju nakresli otocenu, ale iba ak este nebola vybrana

            if i not in [6, 7, 8, 9, 10, 15, 16, 17]:

                # print(f"Karta {self.herne_karty_alias[i]} je {self.herne_karty_meno[i]}")

                if self.herne_karty_meno[i] is not None:
                    karta_img = cv2.imread(f"karty/vek_2/{self.herne_karty_meno[i]}.jpeg")
                    karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
                    img[horny_okraj:horny_okraj + karta_vyska,
                    self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                    cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj + 10),
                                cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

                #   v ostatnych riadkoch zisti, ci karta nebola pouziva a ak nie, tak ci je validna na vyber. ak ano, zobraz ju otocenu.

            else:

                if self.herne_karty_meno[i] is not None:
                    if self.herne_karty_alias[i] in self.validne_karty():
                        karta_img = cv2.imread(f"karty/vek_2/{self.herne_karty_meno[i]}.jpeg")
                        karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
                        img[horny_okraj:horny_okraj + karta_vyska,
                        self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj + 10),
                                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                    else:
                        karta = cv2.imread("karty/ine/zadna_strana_vek_2_regular.jpeg")
                        karta = cv2.resize(karta, (karta_sirka, karta_vyska))
                        img[horny_okraj:horny_okraj + karta_vyska,
                        self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj + 10),
                                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

            #   nakresli divy sveta hrac 1
        horny_okraj, lavy_okaj = horny_okraj_global, self.hrac_1_lavy_okraj[0]
        for idx, div in enumerate(self.hrac_1_divy_meno):
            div_img = cv2.imread(f"karty/divy/{div}.jpeg")
            div_img = cv2.resize(div_img, (div_sirka, div_vyska))
            if div in self.hrac_1_divy_aktivne:
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            else:
                div_img = cv2.cvtColor(div_img, cv2.COLOR_BGR2GRAY)
                div_img = np.stack((div_img,) * 3, axis=-1)
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            if idx == 0:
                lavy_okaj = lavy_okaj + div_sirka + 20
            elif idx == 1:
                horny_okraj = horny_okraj + div_vyska + 20
                lavy_okaj = lavy_okaj - div_sirka - 20
            elif idx == 2:
                lavy_okaj = lavy_okaj + div_sirka + 20

        #   nakresli divy sveta hrac 2
        horny_okraj, lavy_okaj = horny_okraj_global, self.hrac_2_lavy_okraj[0] - 20
        for idx, div in enumerate(self.hrac_2_divy_meno):
            div_img = cv2.imread(f"karty/divy/{div}.jpeg")
            div_img = cv2.resize(div_img, (div_sirka, div_vyska))
            if div in self.hrac_2_divy_aktivne:
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            else:
                div_img = cv2.cvtColor(div_img, cv2.COLOR_BGR2GRAY)
                div_img = np.stack((div_img,) * 3, axis=-1)
                img[horny_okraj:horny_okraj + div_vyska, lavy_okaj:lavy_okaj + div_sirka] = div_img
            if idx == 0:
                lavy_okaj = lavy_okaj + div_sirka + 20
            elif idx == 1:
                horny_okraj = horny_okraj + div_vyska + 20
                lavy_okaj = lavy_okaj - div_sirka - 20
            elif idx == 2:
                lavy_okaj = lavy_okaj + div_sirka + 20

        #   nakresli zonu hraca 1 a 2 a zvyrazni aktivneho
        if self.aktivny_hrac == self.hraci_mena[0]:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2) - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, self.hraci_mena[1],
                        (self.lavy_okraj[5] + 80 + karta_sirka, int(monitor_vyska / 2) - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)),
                          (self.lavy_okraj[0] - 40, int(monitor_vyska * 0.9)), (0, 0, 255), 2)
            cv2.rectangle(img, (self.lavy_okraj[5] + 80 + karta_sirka, int(monitor_vyska / 2)),
                          (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
        else:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2) - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.putText(img, self.hraci_mena[1],
                        (self.lavy_okraj[5] + 80 + karta_sirka, int(monitor_vyska / 2) - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)),
                          (self.lavy_okraj[0] - 40, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
            cv2.rectangle(img, (self.lavy_okraj[5] + 80 + karta_sirka, int(monitor_vyska / 2)),
                          (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 255), 2)

        #   nakresli peniaze a body
        cv2.putText(img, "Pen:" + str(self.hrac_1_peniaze),
                    (self.lavy_okraj[0] - 130, int(monitor_vyska / 2) - 10), cv2.FONT_HERSHEY_DUPLEX, 1,
                    (0, 255, 255), 1)
        cv2.putText(img, "Body:" + str(self.hrac_1_body),
                    (self.lavy_okraj[0] - 260, int(monitor_vyska / 2) - 10), cv2.FONT_HERSHEY_DUPLEX, 1,
                    (255, 51, 51), 1)
        cv2.putText(img, "Pen:" + str(self.hrac_2_peniaze),
                    (monitor_sirka - 130, int(monitor_vyska / 2) - 10), cv2.FONT_HERSHEY_DUPLEX, 1,
                    (0, 255, 255), 1)
        cv2.putText(img, "Body:" + str(self.hrac_2_body),
                    (monitor_sirka - 260, int(monitor_vyska / 2) - 10), cv2.FONT_HERSHEY_DUPLEX, 1,
                    (255, 51, 51), 1)

        #   nakresli majetok hraca 1 aj s tokenami
        sivohnedy_okraj = self.hrac_1_horny_okraj_sivohnede
        zlty_okraj = self.hrac_1_horny_okraj_zlte
        modry_okraj = self.hrac_1_horny_okraj_modre
        cerveny_okraj = self.hrac_1_horny_okraj_cervene
        zeleny_okraj = self.hrac_1_horny_okraj_zelene

        for karta in self.hrac_1_karty:
            if os.path.exists(f"karty/vek_1/{karta}.jpg"):
                karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            elif os.path.exists(f"karty/vek_2/{karta}.jpeg"):
                karta_img = cv2.imread(f"karty/vek_2/{karta}.jpeg")
            else:
                logging.error("Karta nie je ani vo veku 1 ani vo veku 2")

            karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
            # img[hore:dole, lavo:pravo]
            if eval("self." + karta.lower() + ".farba") == "hneda" or eval(
                    "self." + karta.lower() + ".farba") == "siva":
                img[sivohnedy_okraj:sivohnedy_okraj + karta_vyska,
                self.hrac_1_lavy_okraj[0]:self.hrac_1_lavy_okraj[0] + karta_sirka] = karta_img
                sivohnedy_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zlta":
                img[zlty_okraj:zlty_okraj + karta_vyska,
                self.hrac_1_lavy_okraj[1]:self.hrac_1_lavy_okraj[1] + karta_sirka] = karta_img
                zlty_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "modra":
                img[modry_okraj:modry_okraj + karta_vyska,
                self.hrac_1_lavy_okraj[2]:self.hrac_1_lavy_okraj[2] + karta_sirka] = karta_img
                modry_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "cervena":
                img[cerveny_okraj:cerveny_okraj + karta_vyska,
                self.hrac_1_lavy_okraj[3]:self.hrac_1_lavy_okraj[3] + karta_sirka] = karta_img
                cerveny_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zelena":
                img[zeleny_okraj:zeleny_okraj + karta_vyska,
                self.hrac_1_lavy_okraj[4]:self.hrac_1_lavy_okraj[4] + karta_sirka] = karta_img
                zeleny_okraj += 25

        h_okraj = int(monitor_vyska * 0.80)
        l_okraj = 30
        for token in self.hrac_1_tokeny:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj + token_rozmer, l_okraj:l_okraj + token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   nakresli majetok hraca 2 aj s tokenami
        sivohnedy_okraj = self.hrac_2_horny_okraj_sivohnede
        zlty_okraj = self.hrac_2_horny_okraj_zlte
        modry_okraj = self.hrac_2_horny_okraj_modre
        cerveny_okraj = self.hrac_2_horny_okraj_cervene
        zeleny_okraj = self.hrac_2_horny_okraj_zelene

        for karta in self.hrac_2_karty:
            if os.path.exists(f"karty/vek_1/{karta}.jpg"):
                karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            elif os.path.exists(f"karty/vek_2/{karta}.jpeg"):
                karta_img = cv2.imread(f"karty/vek_2/{karta}.jpeg")
            else:
                logging.error("Karta nie je ani vo veku 1 ani vo veku 2")

            karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
            # img[hore:dole, lavo:pravo]
            if eval("self." + karta.lower() + ".farba") == "hneda" or eval(
                    "self." + karta.lower() + ".farba") == "siva":
                img[sivohnedy_okraj:sivohnedy_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[0]:self.hrac_2_lavy_okraj[0] + karta_sirka] = karta_img
                sivohnedy_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zlta":
                img[zlty_okraj:zlty_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[1]:self.hrac_2_lavy_okraj[1] + karta_sirka] = karta_img
                zlty_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "modra":
                img[modry_okraj:modry_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[2]:self.hrac_2_lavy_okraj[2] + karta_sirka] = karta_img
                modry_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "cervena":
                img[cerveny_okraj:cerveny_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[3]:self.hrac_2_lavy_okraj[3] + karta_sirka] = karta_img
                cerveny_okraj += 25
            elif eval("self." + karta.lower() + ".farba") == "zelena":
                img[zeleny_okraj:zeleny_okraj + karta_vyska,
                self.hrac_2_lavy_okraj[4]:self.hrac_2_lavy_okraj[4] + karta_sirka] = karta_img
                zeleny_okraj += 25

        h_okraj = int(monitor_vyska * 0.80)
        l_okraj = self.hrac_2_lavy_okraj[0] - 20
        for token in self.hrac_2_tokeny:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj + token_rozmer, l_okraj:l_okraj + token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   nakresli odhodene karty
        h_okraj = int(monitor_vyska * 0.7)
        l_okraj = int((self.lavy_okraj[1] + self.lavy_okraj[0]) / 2 - 10)
        cv2.line(img, (l_okraj + 28, h_okraj - 10), (self.lavy_okraj[5] + karta_sirka, h_okraj - 10),
                 (0, 102, 204), 1)
        cv2.putText(img, "Discard", (self.lavy_okraj[0], h_okraj - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 102, 204), 1)
        for karta in self.odhodene_karty:
            if os.path.exists(f"karty/vek_1/{karta}.jpg"):
                karta_img = cv2.imread(f"karty/vek_1/{karta}.jpg")
            elif os.path.exists(f"karty/vek_2/{karta}.jpeg"):
                karta_img = cv2.imread(f"karty/vek_2/{karta}.jpeg")
            else:
                logging.error("Karta nie je ani vo veku 1 ani vo veku 2")

            karta_img = cv2.resize(karta_img, (karta_sirka, karta_vyska))
            img[h_okraj:h_okraj + karta_vyska, l_okraj:l_okraj + karta_sirka] = karta_img
            l_okraj = l_okraj + 50

        #   nakresli boje
        h_okraj = int(monitor_vyska * 0.87)
        l_okraj = self.lavy_okraj[1] - 40
        cv2.putText(img, "Boje", (self.lavy_okraj[0], h_okraj), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 204), 1)
        for x in range(0, 19):
            if x in [0, 3, 6, 8, 9, 11, 14, 17]:
                cv2.line(img, (l_okraj + 15, h_okraj - 15), (l_okraj + 15, h_okraj + 15), (0, 0, 204), 1)

            if x == self.boje_stav:
                cv2.circle(img, (l_okraj, h_okraj), 10, (255, 255, 255), cv2.FILLED)
                cv2.putText(img, str(abs(self.boje_stav - 9)), (l_okraj - 7, h_okraj + 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 204), 2)
                l_okraj = l_okraj + 30
            else:
                cv2.circle(img, (l_okraj, h_okraj), 10, (0, 0, 255), cv2.FILLED)
                l_okraj = l_okraj + 30

        #   nakresli tokeny
        h_okraj = int(monitor_vyska * 0.90)
        l_okraj = self.lavy_okraj[1]
        for token in self.herne_tokeny_meno:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj + token_rozmer, l_okraj:l_okraj + token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   dokresli podpis
        cv2.putText(img, "Vytvorene Jan @ Strompl 28.10.2020",
                    (int(monitor_sirka * 0.8), monitor_vyska - 22), cv2.FONT_HERSHEY_DUPLEX, 0.3,
                    (0, 255, 0), 1)
        cv2.putText(img, "Aktualizovane 30.11.2020", (int(monitor_sirka * 0.8), monitor_vyska - 10),
                    cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("7wonders", img)

        logging.debug(f"Cakam na vyber. Validne karty: {self.validne_karty()}")
        if self.validne_karty():
            key = cv2.waitKey(0)
            if chr(key) in self.herne_karty_alias:
                meno_karty = self.herne_karty_meno[self.herne_karty_alias.index(chr(key))]
                logging.debug(
                    f"Stlacena klavesa: {chr(key)} {self.aktivny_hrac} chce vykonat akciu s kartou: {meno_karty}")
                self.vyber_a_aktivuj_kartu(chr(key))
                # self.nakresli_vek()
            else:
                logging.error(f"Vyber karty - {chr(key)} - je nevalidna. Validne karty su: {self.validne_karty()}")
                ukaz_error("nespravna_volba")
                next(self.hraci)
                self.tah = self.tah - 1
                self.nakresli_vek()
        else:
            # os.remove(f"archiv_hier/input_metadata_{self.hra_id}.json")
            logging.info("Koniec veku 2.")

    def validne_karty(self):
        validne_karty = []
        for idx, karta_alias in enumerate(self.herne_karty_alias):
            if karta_alias is not None:
                if idx == 0:
                    if self.herne_karty_alias[6] is None:
                        validne_karty.append(karta_alias)
                if idx == 1:
                    if self.herne_karty_alias[6] is None and self.herne_karty_alias[7] is None:
                        validne_karty.append(karta_alias)
                if idx == 2:
                    if self.herne_karty_alias[7] is None and self.herne_karty_alias[8] is None:
                        validne_karty.append(karta_alias)
                if idx == 3:
                    if self.herne_karty_alias[8] is None and self.herne_karty_alias[9] is None:
                        validne_karty.append(karta_alias)
                if idx == 4:
                    if self.herne_karty_alias[9] is None and self.herne_karty_alias[10] is None:
                        validne_karty.append(karta_alias)
                if idx == 5:
                    if self.herne_karty_alias[10] is None:
                        validne_karty.append(karta_alias)
                if idx == 6:
                    if self.herne_karty_alias[11] is None:
                        validne_karty.append(karta_alias)
                if idx == 7:
                    if self.herne_karty_alias[11] is None and self.herne_karty_alias[12] is None:
                        validne_karty.append(karta_alias)
                if idx == 8:
                    if self.herne_karty_alias[12] is None and self.herne_karty_alias[13] is None:
                        validne_karty.append(karta_alias)
                if idx == 9:
                    if self.herne_karty_alias[13] is None and self.herne_karty_alias[14] is None:
                        validne_karty.append(karta_alias)
                if idx == 10:
                    if self.herne_karty_alias[14] is None:
                        validne_karty.append(karta_alias)
                if idx == 11:
                    if self.herne_karty_alias[15] is None:
                        validne_karty.append(karta_alias)
                if idx == 12:
                    if self.herne_karty_alias[15] is None and self.herne_karty_alias[16] is None:
                        validne_karty.append(karta_alias)
                if idx == 13:
                    if self.herne_karty_alias[16] is None and self.herne_karty_alias[17] is None:
                        validne_karty.append(karta_alias)
                if idx == 14:
                    if self.herne_karty_alias[17] is None:
                        validne_karty.append(karta_alias)
                if idx == 15:
                    if self.herne_karty_alias[18] is None:
                        validne_karty.append(karta_alias)
                if idx == 16:
                    if self.herne_karty_alias[18] is None and self.herne_karty_alias[19] is None:
                        validne_karty.append(karta_alias)
                if idx == 17:
                    if self.herne_karty_alias[19] is None:
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

    def vyber_a_aktivuj_kartu(self, karta):
        if karta in self.validne_karty():
            zvolena_karta = self.herne_karty_meno[self.herne_karty_alias.index(karta)]
            akcia = self.zvol_mozosti(zvolena_karta)
            self.vykonaj_akciu(zvolena_karta, akcia)
            self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
            self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
            self.metadata_to_json(f"archiv_hier/input_metadata_{self.hra_id}.json")
            self.nakresli_vek()
        else:
            logging.error(f"Karta {self.herne_karty_meno[self.herne_karty_alias.index(karta)]} nie je plne odkryta, preto ju nie je mozne zahrat. Znova.")
            ukaz_error("nevalidna_karta")
            next(self.hraci)
            self.tah = self.tah - 1
            #self.metadata_to_json("input_metadata.json")
            self.nakresli_vek()

    def zvol_mozosti(self, zvolena_karta):
        cv2.namedWindow("Zvolena karta.")
        zvolena_karta_pozadie = np.zeros((karta_vyska * 3, karta_sirka * 6, 3), np.uint8)
        zvolena_karta_img = cv2.imread(f"karty/vek_2/{zvolena_karta}.jpeg")
        zvolena_karta_img = cv2.resize(zvolena_karta_img, (karta_sirka * 2, karta_vyska * 2))
        zvolena_karta_pozadie[50:50+(karta_vyska*2), 20:20+(karta_sirka*2)] = zvolena_karta_img
        cv2.putText(zvolena_karta_pozadie, "(o) Odhod", (int(karta_sirka * 2.5), 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(k) Kup", (int(karta_sirka * 2.5), 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(d) Postav div:", (int(karta_sirka * 2.5), 210), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(c) Vyber inu kartu:", (int(karta_sirka * 2.5), 270), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.moveWindow("Zvolena karta.", int(monitor_sirka / 3), int(monitor_vyska / 2))
        cv2.imshow("Zvolena karta.", zvolena_karta_pozadie)
        key = cv2.waitKey()
        if chr(key) == "o":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: odhod")
            cv2.destroyWindow("Zvolena karta.")
            return "odhod"
        elif chr(key) == "k":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: kup")
            cv2.destroyWindow("Zvolena karta.")
            return "kup"
        elif chr(key) == "d":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: postav_div")
            cv2.destroyWindow("Zvolena karta.")
            return "postav_div"
        elif chr(key) == "c":
            logging.debug(f"Stlacena klavesa: {chr(key)} Zvolena akcia: storno_vyberu")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Zvolena karta.")
            self.nakresli_vek()
        else:
            logging.error(f"Stlacena klavesa: {chr(key)} Tato akcia nie je povolena.")
            cv2.destroyWindow("Zvolena karta.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            self.zvol_mozosti(zvolena_karta)

    def read_from_meta(self, metadatafile):
        if not os.path.exists(metadatafile):
            shutil.copy("meta/default_metadata.json", metadatafile)
        with open(metadatafile) as metadata:
            data = json.load(metadata)
            if data["hra_id"] != 0:
                self.hra_id = data["hra_id"]
            if not all(x is None for x in data["herne_karty_meno"]):
                self.herne_karty_meno = data["herne_karty_meno"]
                self.herne_karty_alias = data["herne_karty_alias"]
            self.odhodene_karty = data["odhodene_karty"]
            self.boje_stav = data["boje_stav"]
            self.boje_zrus_peniaze = data["boje_zrus_peniaze"]
            if len(data["herne_tokeny_meno"]) != 0:
                self.herne_tokeny_meno = data["herne_tokeny_meno"]
            if len(data["neherne_tokeny_meno"]) != 0:
                self.neherne_tokeny_meno = data["neherne_tokeny_meno"]
            self.tah = data["tah"]
            self.hraci_mena = data["hraci_mena"]
            id_hrac = self.hraci_mena.index(data["aktivny_hrac"])
            self.hraci = cycle(self.hraci_mena)
            self.aktivny_hrac = islice(self.hraci, id_hrac, None)
            next(self.aktivny_hrac)
            self.hrac_1_peniaze = data["hrac_1_peniaze"]
            self.hrac_2_peniaze = data["hrac_2_peniaze"]
            self.hrac_1_body = data["hrac_1_body"]
            self.hrac_2_body = data["hrac_2_body"]
            self.hrac_1_karty = data["hrac_1_karty"]
            self.hrac_2_karty = data["hrac_2_karty"]
            self.hrac_1_suroviny = data["hrac_1_suroviny"]
            self.hrac_2_suroviny = data["hrac_2_suroviny"]
            if len(data["hrac_1_divy_meno"]) != 0:
                self.hrac_1_divy_meno = data["hrac_1_divy_meno"]
            self.hrac_1_divy_aktivne = data["hrac_1_divy_aktivne"]
            if len(data["hrac_2_divy_meno"]) != 0:
                self.hrac_2_divy_meno = data["hrac_2_divy_meno"]
            self.hrac_2_divy_aktivne = data["hrac_2_divy_aktivne"]
            self.hrac_1_tokeny = data["hrac_1_tokeny"]
            self.hrac_2_tokeny = data["hrac_2_tokeny"]
            metadata.close()

    def metadata_to_json(self, metadatafile):
        logging.debug(f"Obnovujem metadata...")
        vars_to_json = {#"herne_karty": self.herne_karty,
                        "rozohrana_hra": "Ano",
                        "vek": 2,
                        "cas_hry": time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime()),
                        "hra_id": self.hra_id,
                        "herne_karty_meno": self.herne_karty_meno,
                        "herne_karty_alias": self.herne_karty_alias,
                        "odhodene_karty": self.odhodene_karty,
                        "boje_stav": self.boje_stav,
                        "boje_zrus_peniaze": self.boje_zrus_peniaze,
                        "herne_tokeny_meno": self.herne_tokeny_meno,
                        "neherne_tokeny_meno": self.neherne_tokeny_meno,
                        "tah": self.tah,
                        "hraci_mena": self.hraci_mena,
                        "aktivny_hrac": self.aktivny_hrac,
                        "hrac_1_peniaze": self.hrac_1_peniaze,
                        "hrac_2_peniaze": self.hrac_2_peniaze,
                        "hrac_1_body": self.hrac_1_body,
                        "hrac_2_body": self.hrac_2_body,
                        "hrac_1_karty": self.hrac_1_karty,
                        "hrac_2_karty": self.hrac_2_karty,
                        "hrac_1_suroviny": self.hrac_1_suroviny,
                        "hrac_2_suroviny": self.hrac_2_suroviny,
                        "hrac_1_divy_meno": self.hrac_1_divy_meno,
                        "hrac_1_divy_aktivne": self.hrac_1_divy_aktivne,
                        "hrac_2_divy_meno": self.hrac_2_divy_meno,
                        "hrac_2_divy_aktivne": self.hrac_2_divy_aktivne,
                        "hrac_1_tokeny": self.hrac_1_tokeny,
                        "hrac_2_tokeny": self.hrac_2_tokeny}

        with open(metadatafile, 'w') as f:
            json.dump(vars_to_json, f, indent=2)

    def vykonaj_akciu(self, meno_karty, akcia):
        if self.aktivny_hrac == self.hraci_mena[0]:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        if akcia == "odhod":
            exec(f"self.hrac_{hrac}_peniaze = self.hrac_{hrac}_peniaze + 2 + self.zrataj_karty({hrac}, 'zlta')")
            novy_stav = eval(f"self.hrac_{hrac}_peniaze")
            logging.info(f"{self.aktivny_hrac} ohodil {meno_karty} za {2 + self.zrataj_karty(hrac, 'zlta')} panezi. Novy stav penazi {novy_stav}")
            self.odhodene_karty.append(meno_karty)

        if akcia == "kup":
            if self.mozem_kupit(hrac, meno_karty):
                self.kup_kartu(hrac, meno_karty, typ="kartu")
            else:
                logging.error(f"Kartu {meno_karty} si nemozem kupit. Nedostatok penazi. Zvol inu kartu.")
                ukaz_error("nedostatok_penazi")
                next(self.hraci)
                self.tah = self.tah - 1
                self.nakresli_vek()

        if akcia == "postav_div":
            suradnice_sirka = [50, 50+div_sirka + 20, 50, 50+div_sirka + 20]
            suradnice_vyska = [50, 50, 50+div_vyska + 20, 50+div_vyska + 20]
            cv2.namedWindow("Vyber div")
            vyber_div_pozadie = np.zeros((div_vyska * 3, div_sirka * 3 - 50, 3), np.uint8)
            for idx, div in enumerate(eval(f"self.hrac_{hrac}_divy_meno")):
                div = cv2.imread(f"karty/divy/{div}.jpeg")
                div = cv2.resize(div, (div_sirka, div_vyska))
                vyber_div_pozadie[suradnice_vyska[idx]:suradnice_vyska[idx] + div_vyska, suradnice_sirka[idx]:suradnice_sirka[idx] + div_sirka] = div
                cv2.putText(vyber_div_pozadie, str(idx+1), (suradnice_sirka[idx], suradnice_vyska[idx]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.imshow("Vyber div", vyber_div_pozadie)
            key = cv2.waitKey()
            if chr(key) in ("1", "2", "3", "4"):
                div_meno = eval(f"self.hrac_{hrac}_divy_meno[int(chr({key}))-1]")
                logging.debug(f"Stlacena klavesa: {chr(key)} Vybany div: {div_meno}")
                if self.mozem_kupit(hrac, div_meno):
                    self.kup_kartu(hrac, div_meno, typ="div")
                    self.vyhodnot_div(hrac, div_meno)
                    eval(f"self.hrac_{hrac}_divy_aktivne.append('{div_meno}')")
                    cv2.destroyWindow("Vyber div")
                else:
                    ukaz_error("nedostatok_penazi")
                    next(self.hraci)
                    self.tah = self.tah - 1
                    cv2.destroyWindow("Vyber div")
                    self.nakresli_vek()
            else:
                logging.error(f"Volba {chr(key)} nie je povolena. Vyber z [1, 2, 3, 4]. Znova.")
                ukaz_error("nespravna_volba")
                next(self.hraci)
                self.tah = self.tah - 1
                cv2.destroyWindow("Vyber div")
                self.nakresli_vek()

    def mozem_kupit(self, hrac, meno_karty):
        cena = eval("self." + meno_karty.lower() + ".cena")

        #   ak div, tak len taky ktory este nemam.
        if meno_karty in eval(f"self.hrac_{hrac}_divy_aktivne"):
            logging.error(f"Hrac {self.aktivny_hrac} uz div {meno_karty} vlastni.")
            return False

        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        suroviny_mam = eval(f"self.hrac_{hrac}_suroviny").copy()
        peniaze_mam = eval(f"self.hrac_{hrac}_peniaze")
        logging.debug(f"Peniaze k dispozicii na zaciatku: {peniaze_mam}")

        if type(cena) == list:
            if len(cena) == 2:
                alternativna_cena = cena[1]
                if alternativna_cena in eval(f"self.hrac_{hrac}_karty"):
                    return True
                else:
                    cena = cena[0]

        logging.debug(f"Cena suroviny: {cena}")

        # ak je cena len penazna
        if type(cena) == int:
            if peniaze_mam >= cena:
                return True
            else:
                logging.error(f"Hrac {self.aktivny_hrac} nema dost penazi na kupu {meno_karty}")
                return False

            # ak je cena kombinovana
        else:
            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "modra" and "Zednarstvi" in eval(f"self.hrac_{hrac}_tokeny"):
                suroviny_mam.append("X")
                suroviny_mam.append("X")
                logging.debug(f"Hrac vlastni Zednarstvi, do poolu surovin som pridal [X, X]")

            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "div" and "Architektura" in eval(f"self.hrac_{hrac}_tokeny"):
                suroviny_mam.append("Y")
                suroviny_mam.append("Y")
                logging.debug(f"Hrac vlastni Architektura, do poolu surovin som pridal [Y, Y]")

            for surovina in cena:
                try:
                    surovina = int(surovina)
                except:
                    surovina = surovina
                logging.debug(f"Typ suroviny {surovina}: {type(surovina)}")
                if type(surovina) == int:
                    if peniaze_mam >= surovina:
                        peniaze_mam -= surovina
                        logging.debug(f"Po pouziti suroviny {surovina} mi ostava {peniaze_mam} penazi na kupu dalsich surovin.")
                        pass
                    else:
                        logging.warning(f"Karta {meno_karty} sa neda kupit. Nedostatok peniazi.")
                        return False
                else:
                    logging.debug(f"Suroviny mam pred kontrolou: {suroviny_mam}")
                    if (suroviny_mam is not None) and (surovina in suroviny_mam):
                        suroviny_mam.remove(surovina)
                        logging.debug(f"Pouzil som: {surovina} z vlastnych zdrojov. Ostalo mi: {suroviny_mam}")
                        pass
                    elif surovina in ("D", "H", "K") and "W" in suroviny_mam:
                        surovina = "W"
                        suroviny_mam.remove(surovina)
                        logging.debug(f"Pouzil som {surovina}, z divu Velky majak. Ostalo mi: {suroviny_mam}")
                        pass
                    elif surovina in ("P", "S") and "U" in suroviny_mam:
                        surovina = "U"
                        suroviny_mam.remove(surovina)
                        logging.debug(f"Pouzil som {surovina} z divu Piraeus. Ostao mi: {suroviny_mam}")
                        pass
                    elif surovina == "D" and "Zasobarna_dreva" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Zasobarna dreva za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina} hoc je zlacnena Zasobarnou dreva.")
                            return False
                    elif surovina == "H" and "Zasobarna_hliny" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Zasobarna hliny za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina}  hoc je zlacnena Zasobarnou hliny.")
                            return False
                    elif surovina == "K" and "Zasobarna_kamene" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Zasobarna kamene za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina} hoc je zlacnena Zasobarnou kamene.")
                            return False
                    elif surovina in ("P", "S") and "Hostinec" in eval("self.hrac_"+str(hrac)+"_karty"):
                        if peniaze_mam >= 1:
                            peniaze_mam -= 1
                            logging.debug(f"Kupil som {surovina} zlacnene kvoli zltej karte Hostinec za 1. Ostalo mi {peniaze_mam} penazi.")
                            pass
                        else:
                            logging.warning(f"Nedostatok penazi na kupu suroviny {surovina} hoc je zlacnena kartou Hostinec.")
                            return False
                    elif "X" in suroviny_mam:
                        suroviny_mam.remove("X")
                        logging.debug(f"Pouzil som zlacnenie modrej karty tokenom Zednarstvi.")
                        pass
                    elif "Y" in suroviny_mam:
                        suroviny_mam.remove("Y")
                        logging.debug(f"Pouzil som zlacnenie postavenia divu tokenom Architektura.")
                        pass
                    else:
                        cena_suroviny = eval(f"self.hrac_{oponent}_suroviny.count('{surovina}') + 2")
                        logging.debug(f"Surovinu nemam, ani si ju neviem zlacniet. Jej cena je: {cena_suroviny} a mam {peniaze_mam}")
                        if peniaze_mam >= cena_suroviny:
                            peniaze_mam -= cena_suroviny
                            logging.debug(f"Surovina {surovina} kupena za {cena_suroviny} Ostalo mi {peniaze_mam}")
                            pass
                        else:
                            logging.warning(f"Na surovinu {surovina}, nemam peniaze. Znova vyber karty.")
                            return False
            return True

    def kup_kartu(self, hrac, meno_karty, typ="kartu", zlacnene=None):

        #   prv vyskusam zaskat metadata: kolo bodov, penazi, bojov a bojov mi karta da.

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
        kelo_placela = 0 # zrata kolo penazi zaplati za nakup surovin banke

        if type(cena_karty) == list:
            if len(cena_karty) == 2:
                alternativna_cena = cena_karty[1]
                if alternativna_cena in eval(f"self.hrac_{hrac}_karty"):
                    cena_karty = 0
                    logging.debug(f"Hrac vlastni {alternativna_cena}, preto stavia {meno_karty} zadarmo.")
                else:
                    cena_karty = cena_karty[0]

        if type(cena_karty) == int:
            cena = cena_karty
        else:
            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "modra" and "Zednarstvi" in eval(f"self.hrac_{hrac}_tokeny"):
                co_mam.append("X")
                co_mam.append("X")

            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "div" and "Architektura" in eval(f"self.hrac_{hrac}_tokeny"):
                co_mam.append("Y")
                co_mam.append("Y")


            for surovina in cena_karty:
                try:
                    surovina = int(surovina)
                except:
                    surovina = surovina
                if type(surovina) == int:
                    cena = cena + surovina
                else:
                    #logging.debug(f"Surovina: {surovina} Co mam: {co_mam}")
                    if (co_mam is not None) and (surovina in co_mam):
                        co_mam.remove(surovina)
                    elif surovina in ("D", "H", "K") and "W" in co_mam:
                        surovina = "W"
                        #print("DEBUG: pouzil som", surovina, "z divu Velky majak")
                        co_mam.remove(surovina)
                    elif surovina in ("P", "S") and "U" in co_mam:
                        surovina = "U"
                        #print("DEBUG: pouzil som", surovina, "z divu Piraeus")
                        co_mam.remove(surovina)
                    elif surovina == "D" and "Zasobarna_dreva" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif surovina == "H" and "Zasobarna_hliny" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif surovina == "K" and "Zasobarna_kamene" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif surovina in ("P", "S") and "Hostinec" in eval(f"self.hrac_{hrac}_karty"):
                        cena = cena + 1
                        kelo_placela += 1
                    elif "X" in co_mam:
                        co_mam.remove("X")
                    elif "Y" in co_mam:
                        co_mam.remove("Y")
                    else:
                        prirazka = eval(f"self.hrac_{oponent}_suroviny.count('{surovina}') + 2")
                        cena = cena + prirazka
                        kelo_placela += prirazka

        if zlacnene is None:
            logging.debug(f"Karta nie je zlacnena Divmi alebo Tokenmi. Jej cena je: {cena}")
            cena = cena

        else:
            logging.debug(f"Karta je zlacnena na {zlacnene}")
            cena = zlacnene
        exec(f"self.hrac_{hrac}_peniaze -= {cena}")

        #   ak oponent vlastni token Ekonomie, dam mu peniaze za suroviny
        if "Ekonomie" in eval(f"self.hrac_{oponent}_tokeny"):
            exec(f"self.hrac_{oponent}_peniaze += {kelo_placela}")
            logging.info(f"Oponent vlastni token Ekonomie, dal som mu {kelo_placela} penazi.")

        # dostanem
        #   body
        exec(f"self.hrac_{hrac}_body += {body_gain}")
        #   peniaze
        exec(f"self.hrac_{hrac}_peniaze += {peniaze_gain}")
        #   suroviny ak je karta siva alebo hneda
        if karta_farba in ("hneda", "siva", "div") :
            for sur in suroviny_gain:
                exec(f"self.hrac_{hrac}_suroviny.append('{sur}')")
        #   boje

        #   ak vlastnim token Strategie, zosilnim boje
        if "Strategie" in eval(f"self.hrac_{hrac}_tokeny"):
            boje_gain += 1
            logging.info(f"Vlastnim token Strategie, zosilnil som ucinok bojov o 1.")

        if hrac == 1:   self.boje_stav = self.boje_stav + boje_gain
        if hrac == 2:   self.boje_stav = self.boje_stav - boje_gain
        #   zrusim peniaze
        kolko_penazi_zrus = self.boje_zrus_peniaze[self.boje_stav]
        if kolko_penazi_zrus is not None:
            if eval(f"self.hrac_{oponent}_peniaze") < kolko_penazi_zrus:
                exec(f"self.hrac_{oponent}_peniaze = 0")
            else:
                exec(f"self.hrac_{oponent}_peniaze -= {kolko_penazi_zrus}")
            logging.info(f"Efekt bojov zrusil {kolko_penazi_zrus} penazi.")
            if self.boje_stav in (1, 2, 3):
                self.boje_zrus_peniaze[1:4] = None, None, None
            elif self.boje_stav in (4, 5, 6):
                self.boje_zrus_peniaze[4:7] = None, None, None
            elif self.boje_stav in (12, 13, 14):
                self.boje_zrus_peniaze[12:15] = None, None, None
            else:
                self.boje_zrus_peniaze[15:18] = None, None, None

        #   samotnu kartu
        if typ == "kartu":  eval(f"self.hrac_{hrac}_karty.append(meno_karty)")
        elif typ == "div":  eval(f"self.hrac_{hrac}_divy_aktivne.append(meno_karty)")
        elif typ == "token":  eval(f"self.hrac_{hrac}_tokeny.append(meno_karty)")
        else:   pass
        logging.info(f"{self.aktivny_hrac} kupuje {typ} {meno_karty} za {cena}. "
                     f"Dostal {body_gain} bodov, {peniaze_gain} penazi, "
                     f"suroviny: {suroviny_gain} a boje: {boje_gain}")

        # ak je karta zelena, checkni jej dvojicku.
        if karta_farba == "zelena":
            dvojicka = eval("self." + meno_karty.lower() + ".dvojicka")
            if dvojicka in eval(f"self.hrac_{hrac}_karty"):
                self.vezmi_herny_zeleny_token(hrac)

    def vyhodnot_div(self, hrac, div_meno):
        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        efekty = eval(f"self.{div_meno.lower()}.efekt")

        #   ak mam token Teologie a div nema repeater, pridam mu.
        if "repeat" not in efekty and "Teologie" in eval(f"self.hrac_{hrac}_tokeny"):
            efekty.append("repeat")
            logging.debug(f"Vlastnim token Teologie a div nema efekt - repeat - tak efekt bol pridany.")

        for efekt in efekty:
            logging.info(f"Efekt divu: {div_meno} - {efekt}")
            if efekt == "repeat":
                logging.info(f"{self.aktivny_hrac} ide znovu.")
                if hrac == 1: self.aktivny_hrac = self.hraci_mena[1]
                if hrac == 2: self.aktivny_hrac = self.hraci_mena[0]
                #next(self.hraci)
                self.metadata_to_json(f"archiv_hier/input_metadata_{self.hra_id}.json")
            if efekt == "noefekt":
                pass
            if efekt == "oponent-3p":
                logging.info(f"Oponentovi odoberam 3 peniaze.")
                exec(f"self.hrac_{oponent}_peniaze -= 3")
            if efekt == "vezmi_kartu_z_discartu":
                if len(self.odhodene_karty) != 0:
                    self.vezmi_kartu_z_disartu(hrac)
                else:
                    logging.info("Diskart je prazdny. Efekt prepadol.")
            if efekt == "odhod_oponentovi_hnedu":
                if self.zrataj_karty(oponent, "hneda") != 0:
                    self.odhod_hracovi_kartu(oponent, "hneda")
                else:
                    logging.info("Oponent nema ziadne hnede karty. Efekt prepadol.")
            if efekt == "odhod_oponentovi_sivu":
                if self.zrataj_karty(oponent, "siva") != 0:
                    self.odhod_hracovi_kartu(oponent, "siva")
                else:
                    logging.info("Oponent nema ziadne hnede karty. Efekt prepadol.")
            if efekt == "vezmi_odhodeny_zeleny_zeton":
                self.vezmi_odhodeny_zeleny_token(hrac)

    def vezmi_kartu_z_disartu(self, hrac):
        cv2.namedWindow("Diskart")
        diskart_img = np.zeros((200, int(monitor_sirka/2), 3), np.uint8)
        y = 10
        validne_klavesy = []
        for idx, odhodena_karta in enumerate(self.odhodene_karty):
            odhodena_karta = cv2.imread(f"karty/vek_1/{odhodena_karta}.jpg")
            odhodena_karta = cv2.resize(odhodena_karta, (karta_sirka, karta_vyska))
            diskart_img[20:20+karta_vyska, y:y+karta_sirka] = odhodena_karta
            cv2.putText(diskart_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Diskart", diskart_img)
        logging.debug(f"Validne karty na vyber z odhodenych karat su: {validne_klavesy}")
        key = cv2.waitKey()
        logging.debug(f"Vyber klavesy: {chr(key)}")
        if chr(key) in validne_klavesy:
            logging.info(f"Z diskartu sa berie: {self.odhodene_karty[int(chr(key))]}")
            self.kup_kartu(hrac, self.odhodene_karty[int(chr(key))], zlacnene=0)
            self.odhodene_karty.pop(int(chr(key)))
            cv2.destroyWindow("Diskart")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Diskart")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def odhod_hracovi_kartu(self, hrac, typ):
        cv2.namedWindow("Hracove karty")
        oponentove_karty_img = np.zeros((200, int(monitor_sirka / 2), 3), np.uint8)
        y = 10
        validne_klavesy = []
        hracove_karty = []

        for karta in eval(f"self.hrac_{hrac}_karty"):
            if eval("self." + karta.lower() + ".farba") == typ:
                hracove_karty.append(karta)

        logging.debug(f"Hracove karty typu {typ} su: {hracove_karty}")
        for idx, karta in enumerate(hracove_karty):
            karta = cv2.imread(f"karty/vek_1/{karta}.jpg")
            karta = cv2.resize(karta, (karta_sirka, karta_vyska))
            oponentove_karty_img[20:20 + karta_vyska, y:y + karta_sirka] = karta
            cv2.putText(oponentove_karty_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Hracove karty", oponentove_karty_img)
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.info(f"Oponentovi rusim: {hracove_karty[int(chr(key))]}")
            eval(f"self.hrac_{hrac}_karty.remove('{hracove_karty[int(chr(key))]}')")
            cv2.destroyWindow("Hracove karty")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Hracove karty")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def vezmi_odhodeny_zeleny_token(self, hrac):
        cv2.namedWindow("Neherne tokeny")
        neherne_tokeny_img = np.zeros((130, 500, 3), np.uint8)
        y = 30
        validne_klavesy = []

        tri_vybrane = random.sample(self.neherne_tokeny_meno, 3)
        logging.debug(f"3 vybrane tokeny mimo hry: {tri_vybrane}")


        for idx, token in enumerate(tri_vybrane):
            token = cv2.imread(f"karty/tokeny/{token}.png")
            token = cv2.resize(token, (token_rozmer, token_rozmer))
            neherne_tokeny_img[20:20 + token_rozmer, y:y + token_rozmer] = token
            cv2.putText(neherne_tokeny_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += token_rozmer + 10
            validne_klavesy.append(str(idx))

        cv2.imshow("Neherne tokeny", neherne_tokeny_img)
        logging.debug(f"validne klavesy: {validne_klavesy}")
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.debug(f"Stlacena klavesa: {chr(key)} Beriem si token: {tri_vybrane[int(chr(key))]}")
            #eval(f"self.hrac_{hrac}_tokeny.append('{self.neherne_tokeny_meno[int(chr(key))]}')")
            self.kup_kartu(hrac, tri_vybrane[int(chr(key))], typ="token", zlacnene=0)
            self.vyhodnot_token(hrac, tri_vybrane[int(chr(key))])
            self.neherne_tokeny_meno.remove(tri_vybrane[int(chr(key))])
            cv2.destroyWindow("Neherne tokeny")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Neherne tokeny")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def vezmi_herny_zeleny_token(self, hrac):
        cv2.namedWindow("Herne tokeny")
        herne_tokeny_img = np.zeros((130, 600, 3), np.uint8)
        y = 30
        validne_klavesy = []

        for idx, token in enumerate(self.herne_tokeny_meno):
            token = cv2.imread(f"karty/tokeny/{token}.png")
            token = cv2.resize(token, (token_rozmer, token_rozmer))
            herne_tokeny_img[20:20 + token_rozmer, y:y + token_rozmer] = token
            cv2.putText(herne_tokeny_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += token_rozmer + 10
            validne_klavesy.append(str(idx))

        cv2.imshow("Herne tokeny", herne_tokeny_img)
        logging.debug(f"validne klavesy: {validne_klavesy}")
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.debug(f"Stlacena klavesa: {chr(key)} Beriem si token: {self.herne_tokeny_meno[int(chr(key))]}")
            # eval(f"self.hrac_{hrac}_tokeny.append('{self.neherne_tokeny_meno[int(chr(key))]}')")
            self.kup_kartu(hrac, self.herne_tokeny_meno[int(chr(key))], typ="token", zlacnene=0)
            self.vyhodnot_token(hrac, self.herne_tokeny_meno[int(chr(key))])
            self.herne_tokeny_meno.remove(self.herne_tokeny_meno[int(chr(key))])
            cv2.destroyWindow("Herne tokeny")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            next(self.hraci)
            self.tah = self.tah - 1
            cv2.destroyWindow("Herne tokeny")
            cv2.destroyWindow("Vyber div")
            self.nakresli_vek()

    def vyhodnot_token(self, hrac, token_meno):
        logging.info(f"Vyhodnocujem token: {token_meno}")
        try:
            efekt_tokenu = eval("self." + token_meno.lower() + ".efekt_tokenu")
            logging.debug(f"Efekt tokenu: {efekt_tokenu}")
        except:
            efekt_tokenu = None
            logging.debug("Token nema specialny efekt.")

        if efekt_tokenu:
            if efekt_tokenu == "zlacni_divy":
                #   hotovo v mozem_kupit()
                pass
            if efekt_tokenu == "kelo_placela":
                #   hotovo z kup_kartu()
                pass
            if efekt_tokenu == "3_za_kazdy_token":
                #   vyhodnoti sa na konci hry.
                pass
            if efekt_tokenu == "boje+1":
                #   hotovo v kup_kartu()
                pass
            if efekt_tokenu == "repeater_divom":
                # hotovo v vyhodnot_div()
                pass
            if efekt_tokenu == "ak_zadarmo_potom+4p":
                pass
            if efekt_tokenu == "pridaj_zeleny_symbol":
                pass
            if efekt_tokenu == "zlacni_modre":
                #   hotovo v mozem_kupit()
                pass

    def zrataj_karty(self, hrac, farba):
        count = 0
        for meno_karty in eval("self.hrac_"+str(hrac)+"_karty"):
            if eval("self."+meno_karty.lower()+".farba") == farba:
                count = count +1
        #logging.debug(f"{hrac} ma {count} kariet farby {farba}")
        return count

def ukaz_error(typ_erroru):
        cv2.namedWindow("Error!")
        if typ_erroru == "nevalidna_karta":
            error_img = np.zeros((100, 600, 3), np.uint8)
            cv2.putText(error_img, "Karta nie je uplne odokryta. Zvol si inu!", (10, 45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            cv2.moveWindow("Error!", int(monitor_sirka/3), int(monitor_vyska/2))
            cv2.imshow("Error!", error_img)
            cv2.waitKey(2500)
            cv2.destroyWindow("Error!")
        if typ_erroru == "nespravna_volba":
            error_img = np.zeros((100, 850, 3), np.uint8)
            cv2.putText(error_img, "Nespravna volba! Mozes zvolit len z ponukanych moznosti.", (10, 45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            cv2.moveWindow("Error!", int(monitor_sirka/3.5), int(monitor_vyska/2))
            cv2.imshow("Error!", error_img)
            cv2.waitKey(2500)
            cv2.destroyWindow("Error!")
        if typ_erroru == "nedostatok_penazi":
            error_img = np.zeros((100, 800, 3), np.uint8)
            cv2.putText(error_img, "Nedostatok penazi na kupu karty, alebo duplicitna karta.", (10, 45), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            cv2.moveWindow("Error!", int(monitor_sirka/3), int(monitor_vyska/2))
            cv2.imshow("Error!", error_img)
            cv2.waitKey(2500)
            cv2.destroyWindow("Error!")
