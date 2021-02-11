import cv2
import os
import time
import random
import numpy as np
import logging
import json
import sys
import seven_wonders_divy
import seven_wonders_tokeny
import seven_wonders_cards


monitor_sirka = 1900
monitor_vyska = 980
karta_sirka = 82
karta_vyska = int(karta_sirka*1.5)
div_vyska = 170
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

    hrac_1_divy_meno = []
    hrac_1_divy_aktivne = []
    hrac_2_divy_meno = []
    hrac_2_divy_aktivne = []

    def __init__(self, net, hra_id, ja_som):
        #logging.info(f" Hra s ID: {hra_id} zacala.")
        self.net = net
        self.ja_som = ja_som
        self.lavy_okraj = []

        self.hrac_1_horny_okraj_sivohnede = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_zlte = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_modre = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_cervene = int(monitor_vyska / 2) + 15
        self.hrac_1_horny_okraj_zelene = int(monitor_vyska / 2) + 15
        self.hrac_1_lavy_okraj = [num for num in np.arange(30, 400, karta_sirka + 10)]
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

        # nacitaj metadata
        self.read_from_meta()
        #   definujem aktivneho hraca aby som mohol updatnut metadata (aby update nehodil error)
        self.aktivny_hrac = self.naposledy_hral
        self.metadata_to_json()


        #   Ak je moznost vyberu karty, nakresli vek.
        while True:
            self.read_from_meta()
            #   v metadatach je uvedene posledne odohrane cislo tahu a kto odohral dany tah, preto inkrementujem
            if self.validne_karty() and self.vek == 1:
                self.tah += 1
                self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
                if self.aktivny_hrac == self.ja_som:
                    print("Hrajem.")
                    self.nakresli_vek(active=True)
                    logging.debug(f"Cakam na vyber. Validne karty: {self.validne_karty()}")
                    key = cv2.waitKey(0)
                    if chr(key) in self.herne_karty_alias:
                        meno_karty = self.herne_karty_meno[self.herne_karty_alias.index(chr(key))]
                        logging.debug(
                            f"Stlacena klavesa - {chr(key)} - {self.aktivny_hrac} chce vykonat akciu s kartou: {meno_karty}")
                        self.vyber_a_aktivuj_kartu(chr(key))
                    else:
                        logging.error(f"Stlacena klavesa - {chr(key)} - je nevalidna. Validne klavesy su: {self.validne_karty()}")
                        ukaz_error("nespravna_volba")
                        #self.aktivny_hrac = self.naposledy_hral
                        #self.tah = self.tah - 1
                else:
                    print("Hraje oponent... cakam...")
                    self.nakresli_vek(active=False)
                    cv2.waitKey(5000)
            else:
                print("Skoncil vek.")
                logging.info("Koniecu veku 1.")
                #print("Vek dohral", self.aktivny_hrac, "ja som: ",  self.ja_som)
                if self.aktivny_hrac == self.ja_som:
                    print("Aktualizujem metadata.")
                    if self.boje_stav < 9:
                        logging.info(f"Vek 2 zacne {self.hraci_mena[0]}, lebo prehrava na boje.")
                        self.aktivny_hrac = self.hraci_mena[1]
                    elif self.boje_stav > 9:
                        logging.info(f"Vek 2 zacne {self.hraci_mena[1]}, lebo prehrava na boje.")
                        self.aktivny_hrac = self.hraci_mena[0]
                    else:
                        self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
                    self.metadata_to_json()
                break

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
        vsetky_karty_meno = []
        herne_karty_meno = []
        myList = os.listdir("karty/vek_1")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                vsetky_karty_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu jpg ani jpeg.")

        for i in range(0, 20):
            pick_id = random.randint(0, len(vsetky_karty_meno) - 1)
            herne_karty_meno.append(vsetky_karty_meno[pick_id])
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

    def nakresli_vek(self, active=False):

        if active:
            logging.debug(f"Aktivny hrac: {self.aktivny_hrac}")
            logging.debug(f"Tah cislo: {self.tah}")
            gamer = self.naposledy_hral
        else:
            gamer = self.aktivny_hrac

        img = np.zeros((monitor_vyska, monitor_sirka, 3), np.uint8)

        # ukaz poslednu akciu

        if os.path.exists(f'logs/gamelog_{self.hra_id}_{gamer}.log'):
            with open(f'logs/gamelog_{self.hra_id}_{gamer}.log', 'r') as f:
                lines = f.read().splitlines()
                last_line = lines[-1].split(":")[2].split(".")[0]
        else:
            last_line = "Neviem ziskat oponentove logy..."

        cv2.putText(img, last_line, (10, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)



        #   nakresli titulok
        if not active:
            farba = (160, 160, 160)
            header = "        Cakam na oponentov tah..."
        else:
            farba = (0, 255, 0)
            header = f"7 Wonders DUEL - id hry: {self.hra_id}- tah: {self.tah}-{self.ja_som}"

        cv2.putText(img, header, (self.lavy_okraj[14], 35), cv2.FONT_HERSHEY_DUPLEX, 1, farba, 2)

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
                    karta_img = najdi_kartu(self.herne_karty_meno[i])
                    img[horny_okraj:horny_okraj + karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                    cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

            #   v ostatnych riadkoch zisti, ci karta nebola pouziva a ak nie, tak ci je validna na vyber. ak ano, zobraz ju otocenu.

            else:

                if self.herne_karty_meno[i] is not None:
                    if self.herne_karty_alias[i] in self.validne_karty():
                        karta_img = najdi_kartu(self.herne_karty_meno[i])
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
        horny_okraj, lavy_okaj = horny_okraj_global, self.hrac_2_lavy_okraj[0]
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
            cv2.rectangle(img, (self.lavy_okraj[19] + 70 + karta_sirka, int(monitor_vyska / 2)), (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
        else:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[19] + 80 + karta_sirka, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)), (self.lavy_okraj[14] - 40, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
            cv2.rectangle(img, (self.lavy_okraj[19] + 70 + karta_sirka, int(monitor_vyska / 2)), (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 255), 2)

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
            karta_img = najdi_kartu(karta)
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
            karta_img = najdi_kartu(karta)
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
        l_okraj = self.hrac_2_lavy_okraj[0] + 10
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
            karta_img = najdi_kartu(karta)
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
        cv2.putText(img, "Dokoncene 11.02.2021", (int(monitor_sirka * 0.8), monitor_vyska - 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("7wonders", img)

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
            if akcia != "cancel":
                vysledok_akcie = self.vykonaj_akciu(zvolena_karta, akcia)
                if vysledok_akcie == "ok":
                    self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
                    self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
                    self.metadata_to_json()
                    #self.tah = self.tah + 1
                    #self.aktivny_hrac = nasledujuci_hrac(self.aktivny_hrac, self.hraci_mena)
        else:
            logging.error(f"Karta {self.herne_karty_meno[self.herne_karty_alias.index(karta)]} nie je plne odkryta, preto ju nie je mozne zahrat. Znova.")
            ukaz_error("nevalidna_karta")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1

    def zvol_mozosti(self, zvolena_karta):
        cv2.namedWindow("Zvolena karta.")
        zvolena_karta_pozadie = np.zeros((karta_vyska * 3, karta_sirka * 6, 3), np.uint8)
        zvolena_karta_img = najdi_kartu(zvolena_karta, karta_sirka=karta_sirka*2, karta_vyska=karta_vyska*2)
        zvolena_karta_pozadie[50:50+(karta_vyska*2), 20:20+(karta_sirka*2)] = zvolena_karta_img
        cv2.putText(zvolena_karta_pozadie, "(o) Odhod", (int(karta_sirka * 2.5), 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(k) Kup", (int(karta_sirka * 2.5), 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(d) Postav div:", (int(karta_sirka * 2.5), 210), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(c) Vyber inu kartu:", (int(karta_sirka * 2.5), 270), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.moveWindow("Zvolena karta.", int(monitor_sirka / 3), int(monitor_vyska / 3))
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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Zvolena karta.")
            return "cancel"
        else:
            logging.error(f"Stlacena klavesa: {chr(key)} Tato akcia nie je povolena.")
            cv2.destroyWindow("Zvolena karta.")
            ukaz_error("nespravna_volba")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            return "cancel"

    def vykonaj_akciu(self, meno_karty, akcia):
        if self.aktivny_hrac == self.hraci_mena[0]:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1

        if akcia == "odhod":
            stary_stav = eval(f"self.hrac_{hrac}_peniaze")
            exec(f"self.hrac_{hrac}_peniaze = self.hrac_{hrac}_peniaze + 2 + self.zrataj_karty({hrac}, 'zlta')")
            novy_stav = eval(f"self.hrac_{hrac}_peniaze")
            logging.info(f"{self.aktivny_hrac} ohodil {meno_karty} za {2 + self.zrataj_karty(hrac, 'zlta')} panezi. Stary stav penazi: {stary_stav}, Novy stav penazi: {novy_stav}")
            self.odhodene_karty.append(meno_karty)
            return "ok"

        if akcia == "kup":
            if self.mozem_kupit(hrac, meno_karty):
                self.kup_kartu(hrac, meno_karty, typ="kartu")
                return "ok"
            else:
                logging.error(f"Kartu {meno_karty} si nemozem kupit. Nedostatok penazi. Zvol inu kartu.")
                ukaz_error("nedostatok_penazi")
                self.aktivny_hrac = self.naposledy_hral
                self.tah = self.tah - 1
                return "cancel"

        if akcia == "postav_div":
            suradnice_sirka = [50, 50+div_sirka + 20, 50, 50+div_sirka + 20]
            suradnice_vyska = [50, 50, 50+div_vyska + 20, 50+div_vyska + 20]
            cv2.namedWindow("Vyber div")
            vyber_div_pozadie = np.zeros((div_vyska * 3, div_sirka * 3 - 50, 3), np.uint8)
            validne_klavesy = []
            for idx, div in enumerate(eval(f"self.hrac_{hrac}_divy_meno")):
                if div not in eval(f"self.hrac_{hrac}_divy_aktivne"):
                    div = cv2.imread(f"karty/divy/{div}.jpeg")
                    div = cv2.resize(div, (div_sirka, div_vyska))
                    vyber_div_pozadie[suradnice_vyska[idx]:suradnice_vyska[idx] + div_vyska, suradnice_sirka[idx]:suradnice_sirka[idx] + div_sirka] = div
                    cv2.putText(vyber_div_pozadie, str(idx+1), (suradnice_sirka[idx], suradnice_vyska[idx]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    validne_klavesy.append(str(idx+1))
            cv2.imshow("Vyber div", vyber_div_pozadie)
            key = cv2.waitKey()
            if chr(key) in validne_klavesy:
                div_meno = eval(f"self.hrac_{hrac}_divy_meno[int(chr({key}))-1]")
                logging.debug(f"Stlacena klavesa: {chr(key)} Vybany div: {div_meno}")
                if self.mozem_kupit(hrac, div_meno):
                    self.kup_kartu(hrac, div_meno, typ="div")
                    self.vyhodnot_div(hrac, div_meno)
                    cv2.destroyWindow("Vyber div")
                    return "ok"
                else:
                    ukaz_error("nedostatok_penazi")
                    cv2.destroyWindow("Vyber div")
                    return "cancel"
            else:
                logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
                ukaz_error("nespravna_volba")
                cv2.destroyWindow("Vyber div")

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

        #   ak vlastnim token Strategie, zosilnim boje tym kartam, ktore davaju boje, vynimka su divy
        if boje_gain != 0:
            if eval("self." + meno_karty.lower() + ".farba") != "div":
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
            f"{self.aktivny_hrac} kupil {typ} {meno_karty} za {cena}. Dostal {body_gain} bodov, {peniaze_gain} penazi, suroviny: {suroviny_gain} a boje: {boje_gain}")

        # ak je karta zelena, checkni jej dvojicku.
        if karta_farba == "zelena":
            dvojicka = eval("self." + meno_karty.lower() + ".dvojicka")
            if dvojicka in eval(f"self.hrac_{hrac}_karty"):
                self.vezmi_herny_zeleny_token(hrac)

            # zisti, ci nemam 2 rovnake symboly aby som vyhral
            symbol = eval("self." + meno_karty.lower() + ".symbol")
            eval(f"self.hrac_{hrac}_symboly.append('{symbol}')")
            logging.debug(f"Kvoli zelenej karte {meno_karty} ziskavam symbol {symbol}")
            if len(set(eval(f"self.hrac_{hrac}_symboly"))) == 6:
                logging.info(f"Hrac {hrac} vyhral na symboly ekonomie.")
                sys.exit(0)

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
                #self.metadata_to_json(f"archiv_hier/input_metadata_{self.hra_id}.json")
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
            odhodena_karta = najdi_kartu(odhodena_karta)
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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Diskart")
            cv2.destroyWindow("Vyber div")

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
            karta = najdi_kartu(karta)
            oponentove_karty_img[20:20 + karta_vyska, y:y + karta_sirka] = karta
            cv2.putText(oponentove_karty_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Hracove karty", oponentove_karty_img)
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.info(f"Oponentovi rusim: {hracove_karty[int(chr(key))]}")
            #   rusim kartu
            eval(f"self.hrac_{hrac}_karty.remove('{hracove_karty[int(chr(key))]}')")
            #   rusim suroviny
            suroviny = eval(f"self.{hracove_karty[int(chr(key))].lower()}.suroviny")
            eval(f"self.hrac_{hrac}_suroviny.remove('{suroviny}')")
            #   pridavam do diskartu
            eval(f"self.odhodene_karty.append('{hracove_karty[int(chr(key))]}')")
            cv2.destroyWindow("Hracove karty")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            cv2.destroyWindow("Hracove karty")
            cv2.destroyWindow("Vyber div")

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
            self.kup_kartu(hrac, tri_vybrane[int(chr(key))], typ="token", zlacnene=0)
            self.vyhodnot_token(hrac, tri_vybrane[int(chr(key))])
            self.neherne_tokeny_meno.remove(tri_vybrane[int(chr(key))])
            cv2.destroyWindow("Neherne tokeny")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Neherne tokeny")
            cv2.destroyWindow("Vyber div")

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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Herne tokeny")
            cv2.destroyWindow("Vyber div")

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
                # hotovo v kup kartu
                pass
            if efekt_tokenu == "pridaj_zeleny_symbol":
                eval(f"self.hrac_{hrac}_symboly.append('zakon')")
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

    def metadata_to_json(self):
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
                        "naposledy_hral": self.aktivny_hrac,
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
                        "hrac_1_symboly": self.hrac_1_symboly,
                        "hrac_2_tokeny": self.hrac_2_tokeny,
                        "hrac_2_symboly": self.hrac_2_symboly}

        self.net.send(json.dumps(vars_to_json))

    def read_from_meta(self):
        data = self.net.get()

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
        self.vek = data["vek"]
        self.hraci_mena = data["hraci_mena"]
        self.naposledy_hral = data["naposledy_hral"]
        #self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
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
        self.hrac_1_symboly = data["hrac_1_symboly"]
        self.hrac_2_tokeny = data["hrac_2_tokeny"]
        self.hrac_2_symboly = data["hrac_2_symboly"]

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

    def __init__(self, net, hra_id, ja_som):
        logging.info("Zacal vek 2.")
        self.net = net
        self.ja_som = ja_som
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

        self.read_from_meta()
        self.aktivny_hrac = self.naposledy_hral
        self.metadata_to_json()

        #   Ak je moznost vyberu karty, nakresli vek.
        while True:
            self.read_from_meta()

            #   v druhej dobe sa uz da vyhrat na boje:
            if self.boje_stav <= 0:
                logging.info(f"Hrac {self.hraci_mena[1]} vyhral na boje.")
                vyhra_na_boje(self.hraci_mena[1])
            elif self.boje_stav >= 18:
                logging.info(f"Hrac {self.hraci_mena[0]} vyhral na boje.")
                vyhra_na_boje(self.hraci_mena[0])
            else:
                pass

            if self.validne_karty() and self.vek == 2:
                self.tah += 1
                self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
                if self.aktivny_hrac == self.ja_som:
                    print("Hrajem.")
                    self.nakresli_vek(active=True)
                    logging.debug(f"Cakam na vyber. Validne karty: {self.validne_karty()}")
                    key = cv2.waitKey(0)
                    if chr(key) in self.herne_karty_alias:
                        meno_karty = self.herne_karty_meno[self.herne_karty_alias.index(chr(key))]
                        logging.debug(
                            f"Stlacena klavesa - {chr(key)} - {self.aktivny_hrac} chce vykonat akciu s kartou: {meno_karty}")
                        self.vyber_a_aktivuj_kartu(chr(key))
                    else:
                        logging.error(
                            f"Stlacena klavesa - {chr(key)} - je nevalidna. Validne klavesy su: {self.validne_karty()}")
                        ukaz_error("nespravna_volba")

                else:
                    print("Hraje oponent... cakam...")
                    self.nakresli_vek(active=False)
                    cv2.waitKey(5000)
            else:
                print("Skoncil vek.")
                logging.info("Koniecu veku 2.")
                # print("Vek dohral", self.aktivny_hrac, "ja som: ",  self.ja_som)
                if self.aktivny_hrac == self.ja_som:
                    print("Aktualizujem metadata.")
                    if self.boje_stav < 9:
                        logging.info(f"Vek 3 zacne {self.hraci_mena[0]}, lebo prehrava na boje.")
                        self.aktivny_hrac = self.hraci_mena[1]
                    elif self.boje_stav > 9:
                        logging.info(f"Vek 3 zacne {self.hraci_mena[1]}, lebo prehrava na boje.")
                        self.aktivny_hrac = self.hraci_mena[0]
                    else:
                        self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
                    self.metadata_to_json()
                break

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
        vsetky_karty_meno = []
        herne_karty_meno = []
        myList = os.listdir("karty/vek_2")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                vsetky_karty_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu jpg ani jpeg.")

        for i in range(0, 20):
            pick_id = random.randint(0, len(vsetky_karty_meno) - 1)
            herne_karty_meno.append(vsetky_karty_meno[pick_id])
            vsetky_karty_meno.pop(pick_id)

        self.herne_karty_meno = herne_karty_meno

    def nakresli_vek(self, active=False):

        if active:
            logging.debug(f"Aktivny hrac: {self.aktivny_hrac}")
            logging.debug(f"Tah cislo: {self.tah}")
            gamer = self.naposledy_hral
        else:
            gamer = self.aktivny_hrac

        img = np.zeros((monitor_vyska, monitor_sirka, 3), np.uint8)

        # ukaz poslednu akciu

        if os.path.exists(f'logs/gamelog_{self.hra_id}_{gamer}.log'):
            with open(f'logs/gamelog_{self.hra_id}_{gamer}.log', 'r') as f:
                lines = f.read().splitlines()
                last_line = lines[-1].split(":")[2].split(".")[0]
        else:
            last_line = "Neviem ziskat oponentove logy..."

        cv2.putText(img, last_line, (10, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)

        #   nakresli titulok
        if not active:
            farba = (160, 160, 160)
            header = "        Cakam na oponentov tah..."
        else:
            farba = (0, 255, 0)
            header = f"7 Wonders DUEL - id hry: {self.hra_id}- tah: {self.tah}-{self.ja_som}"

        cv2.putText(img, header, (self.lavy_okraj[0]-20, 35), cv2.FONT_HERSHEY_DUPLEX, 1, farba, 2)


        horny_okraj = horny_okraj_global
        for i in range(0, len(self.herne_karty_meno)):
            #   nastav hodnotu horneho okraja, aby sa karty poukladali do riadkov

            if i in [6, 11, 15, 18]:
                horny_okraj = horny_okraj + int(karta_vyska * 0.8)

            #   v riadkoch kde ma byt karta stale otocena ju nakresli otocenu, ale iba ak este nebola vybrana

            if i not in [6, 7, 8, 9, 10, 15, 16, 17]:

                # print(f"Karta {self.herne_karty_alias[i]} je {self.herne_karty_meno[i]}")

                if self.herne_karty_meno[i] is not None:
                    karta_img = najdi_kartu(self.herne_karty_meno[i])
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
                        karta_img = najdi_kartu(self.herne_karty_meno[i])
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
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2) - 10),cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, self.hraci_mena[1],(self.lavy_okraj[5] + 80 + karta_sirka, int(monitor_vyska / 2) - 10),cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)),(self.lavy_okraj[0] - 40, int(monitor_vyska * 0.9)), (0, 0, 255), 2)
            cv2.rectangle(img, (self.lavy_okraj[5] + 60 + karta_sirka, int(monitor_vyska / 2)),(monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
        else:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2) - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.putText(img, self.hraci_mena[1],
                        (self.lavy_okraj[5] + 80 + karta_sirka, int(monitor_vyska / 2) - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)),
                          (self.lavy_okraj[0] - 40, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
            cv2.rectangle(img, (self.lavy_okraj[5] + 60 + karta_sirka, int(monitor_vyska / 2)),
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
            karta_img = najdi_kartu(karta)
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
            karta_img = najdi_kartu(karta)
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
        l_okraj = self.hrac_2_lavy_okraj[0] + 10
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
            karta_img = najdi_kartu(karta)
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
        cv2.putText(img, "Dokoncene 11.02.2021", (int(monitor_sirka * 0.8), monitor_vyska - 10),
                    cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("7wonders", img)

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
            if akcia != "cancel":
                vysledok_akcie = self.vykonaj_akciu(zvolena_karta, akcia)
                if vysledok_akcie == "ok":
                    self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
                    self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
                    self.metadata_to_json()
        else:
            logging.error(f"Karta {self.herne_karty_meno[self.herne_karty_alias.index(karta)]} nie je plne odkryta, preto ju nie je mozne zahrat. Znova.")
            ukaz_error("nevalidna_karta")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1

    def zvol_mozosti(self, zvolena_karta):
        cv2.namedWindow("Zvolena karta.")
        zvolena_karta_pozadie = np.zeros((karta_vyska * 3, karta_sirka * 6, 3), np.uint8)
        zvolena_karta_img = najdi_kartu(zvolena_karta, karta_sirka=karta_sirka*2, karta_vyska=karta_vyska*2)
        zvolena_karta_pozadie[50:50+(karta_vyska*2), 20:20+(karta_sirka*2)] = zvolena_karta_img
        cv2.putText(zvolena_karta_pozadie, "(o) Odhod", (int(karta_sirka * 2.5), 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(k) Kup", (int(karta_sirka * 2.5), 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(d) Postav div:", (int(karta_sirka * 2.5), 210), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(c) Vyber inu kartu:", (int(karta_sirka * 2.5), 270), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.moveWindow("Zvolena karta.", int(monitor_sirka / 3), int(monitor_vyska / 3))
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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Zvolena karta.")
            return "cancel"
        else:
            logging.error(f"Stlacena klavesa: {chr(key)} Tato akcia nie je povolena.")
            cv2.destroyWindow("Zvolena karta.")
            ukaz_error("nespravna_volba")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            return "cancel"

    def read_from_meta(self):
        data = self.net.get()

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
        self.vek = data["vek"]
        self.hraci_mena = data["hraci_mena"]
        self.naposledy_hral = data["naposledy_hral"]
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
        self.hrac_1_symboly = data["hrac_1_symboly"]
        self.hrac_2_tokeny = data["hrac_2_tokeny"]
        self.hrac_2_symboly = data["hrac_2_symboly"]

    def metadata_to_json(self):
        logging.debug(f"Obnovujem metadata...")
        vars_to_json = {"rozohrana_hra": "Ano",
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
                        "naposledy_hral": self.aktivny_hrac,
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
                        "hrac_1_symboly": self.hrac_1_symboly,
                        "hrac_2_tokeny": self.hrac_2_tokeny,
                        "hrac_2_symboly": self.hrac_2_symboly}

        self.net.send(json.dumps(vars_to_json))

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
            return "ok"

        if akcia == "kup":
            if self.mozem_kupit(hrac, meno_karty):
                self.kup_kartu(hrac, meno_karty, typ="kartu")
                return "ok"
            else:
                logging.error(f"Kartu {meno_karty} si nemozem kupit. Nedostatok penazi. Zvol inu kartu.")
                ukaz_error("nedostatok_penazi")
                return "cancel"

        if akcia == "postav_div":
            suradnice_sirka = [50, 50+div_sirka + 20, 50, 50+div_sirka + 20]
            suradnice_vyska = [50, 50, 50+div_vyska + 20, 50+div_vyska + 20]
            cv2.namedWindow("Vyber div")
            vyber_div_pozadie = np.zeros((div_vyska * 3, div_sirka * 3 - 50, 3), np.uint8)
            validne_klavesy = []
            for idx, div in enumerate(eval(f"self.hrac_{hrac}_divy_meno")):
                if div not in eval(f"self.hrac_{hrac}_divy_aktivne"):
                    div = cv2.imread(f"karty/divy/{div}.jpeg")
                    div = cv2.resize(div, (div_sirka, div_vyska))
                    vyber_div_pozadie[suradnice_vyska[idx]:suradnice_vyska[idx] + div_vyska, suradnice_sirka[idx]:suradnice_sirka[idx] + div_sirka] = div
                    cv2.putText(vyber_div_pozadie, str(idx+1), (suradnice_sirka[idx], suradnice_vyska[idx]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    validne_klavesy.append(str(idx+1))
            cv2.imshow("Vyber div", vyber_div_pozadie)
            key = cv2.waitKey()
            if chr(key) in validne_klavesy:
                div_meno = eval(f"self.hrac_{hrac}_divy_meno[int(chr({key}))-1]")
                logging.debug(f"Stlacena klavesa: {chr(key)} Vybany div: {div_meno}")
                if self.mozem_kupit(hrac, div_meno):
                    self.kup_kartu(hrac, div_meno, typ="div")
                    self.vyhodnot_div(hrac, div_meno)
                    cv2.destroyWindow("Vyber div")
                    return "ok"
                else:
                    ukaz_error("nedostatok_penazi")
                    cv2.destroyWindow("Vyber div")
                    return "cancel"
            else:
                logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
                ukaz_error("nespravna_volba")
                cv2.destroyWindow("Vyber div")

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
                    #   ak aktivny hrac vlastni urbanismus, dostava 4 peniaze
                    if "Urbanismus" in eval(f"self.hrac_{hrac}_tokeny"):
                        exec(f"self.hrac_{hrac}_peniaze += 4")
                        logging.debug(f"Hrac vlastni token Urbanismus, dostava 4 peniaze.")
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
        if karta_farba in ("hneda", "siva", "div", "zlta") :
            for sur in suroviny_gain:
                exec(f"self.hrac_{hrac}_suroviny.append('{sur}')")
        #   boje

        #   ak vlastnim token Strategie, zosilnim boje tym kartam, ktore davaju boje, vynimka su divy
        if boje_gain != 0:
            if eval("self." + meno_karty.lower() + ".farba") != "div":
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

            # zisti, ci nemam 2 rovnake symboly aby som vyhral
            symbol = eval("self." + meno_karty.lower() + ".symbol")
            eval(f"self.hrac_{hrac}_symboly.append('{symbol}')")
            logging.debug(f"Kvoli zelenej karte {meno_karty} ziskavam symbol {symbol}")
            if len(set(eval(f"self.hrac_{hrac}_symboly"))) == 6:
                logging.info(f"Hrac {hrac} vyhral na symboly ekonomie.")
                sys.exit(0)

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
        diskart_img = np.zeros((200, monitor_sirka, 3), np.uint8)
        y = 10
        validne_klavesy = []
        for idx, odhodena_karta in enumerate(self.odhodene_karty):
            odhodena_karta = najdi_kartu(odhodena_karta)
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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Diskart")
            cv2.destroyWindow("Vyber div")

    def odhod_hracovi_kartu(self, hrac, typ):
        cv2.namedWindow("Hracove karty")
        oponentove_karty_img = np.zeros((200, monitor_sirka, 3), np.uint8)
        y = 10
        validne_klavesy = []
        hracove_karty = []

        for karta in eval(f"self.hrac_{hrac}_karty"):
            if eval("self." + karta.lower() + ".farba") == typ:
                hracove_karty.append(karta)

        logging.debug(f"Hracove karty typu {typ} su: {hracove_karty}")
        for idx, karta in enumerate(hracove_karty):
            karta = najdi_kartu(karta)
            oponentove_karty_img[20:20 + karta_vyska, y:y + karta_sirka] = karta
            cv2.putText(oponentove_karty_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Hracove karty", oponentove_karty_img)
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.info(f"Oponentovi rusim: {hracove_karty[int(chr(key))]}")
            #   rusim kartu
            eval(f"self.hrac_{hrac}_karty.remove('{hracove_karty[int(chr(key))]}')")
            #   rusim suroviny
            suroviny = eval(f"self.{hracove_karty[int(chr(key))].lower()}.suroviny")
            eval(f"self.hrac_{hrac}_suroviny.remove('{suroviny}')")
            #   pridavam do diskartu
            eval(f"self.odhodene_karty.append('{hracove_karty[int(chr(key))]}')")
            cv2.destroyWindow("Hracove karty")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            cv2.destroyWindow("Hracove karty")
            cv2.destroyWindow("Vyber div")

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
            self.kup_kartu(hrac, tri_vybrane[int(chr(key))], typ="token", zlacnene=0)
            self.vyhodnot_token(hrac, tri_vybrane[int(chr(key))])
            self.neherne_tokeny_meno.remove(tri_vybrane[int(chr(key))])
            cv2.destroyWindow("Neherne tokeny")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            cv2.destroyWindow("Neherne tokeny")
            cv2.destroyWindow("Vyber div")

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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Herne tokeny")
            cv2.destroyWindow("Vyber div")

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
                # hotovo v kup kartu
                pass
            if efekt_tokenu == "pridaj_zeleny_symbol":
                eval(f"self.hrac_{hrac}_symboly.append('zakon')")
                if len(set(eval(f"self.hrac_{hrac}_symboly"))) == 6:
                    logging.info(f"Hrac {hrac} vyhral na symboly ekonomie.")
                    sys.exit(0)
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

class SevenWondersTretiVek:

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

    myList = os.listdir("karty/vek_3")
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

    def __init__(self, net, hra_id, ja_som):
        logging.info("Zacal vek 3.")
        self.net = net
        self.ja_som = ja_som
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

        self.read_from_meta()
        self.aktivny_hrac = self.naposledy_hral
        self.metadata_to_json()

        #   Ak je moznost vyberu karty, nakresli vek.
        while True:
            self.read_from_meta()

            #   vyhra na symboly

            if len(set(self.hrac_1_symboly)) == 6:
                logging.info(f"Hrac {self.hraci_mena[0]} vyhral na symboly ekonomie.")
                vyhra_na_symboly(self.hraci_mena[0])

            if len(set(self.hrac_2_symboly)) == 6:
                logging.info(f"Hrac {self.hraci_mena[1]} vyhral na symboly ekonomie.")
                vyhra_na_symboly(self.hraci_mena[1])

            #   vyhra na boje:
            if self.boje_stav <= 0:
                logging.info(f"Hrac {self.hraci_mena[1]} vyhral na boje.")
                vyhra_na_boje(self.hraci_mena[1])
            elif self.boje_stav >= 18:
                logging.info(f"Hrac {self.hraci_mena[0]} vyhral na boje.")
                vyhra_na_boje(self.hraci_mena[0])
            else:
                pass

            if self.validne_karty() and self.vek == 3:
                self.tah += 1
                self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
                if self.aktivny_hrac == self.ja_som:
                    print("Hrajem.")
                    self.nakresli_vek(active=True)
                    logging.debug(f"Cakam na vyber. Validne karty: {self.validne_karty()}")
                    key = cv2.waitKey(0)
                    if chr(key) in self.herne_karty_alias:
                        meno_karty = self.herne_karty_meno[self.herne_karty_alias.index(chr(key))]
                        logging.debug(
                            f"Stlacena klavesa - {chr(key)} - {self.aktivny_hrac} chce vykonat akciu s kartou: {meno_karty}")
                        self.vyber_a_aktivuj_kartu(chr(key))
                    else:
                        logging.error(
                            f"Stlacena klavesa - {chr(key)} - je nevalidna. Validne klavesy su: {self.validne_karty()}")
                        ukaz_error("nespravna_volba")

                else:
                    print("Hraje oponent... cakam...")
                    self.nakresli_vek(active=False)
                    cv2.waitKey(5000)
            else:
                print("Skoncil vek.")
                logging.info("Koniec veku 3. Koniec hry. Vyhodnocujem.")
                break

        self.dopln_body()
        self.metadata_to_json()
        self.vyhodnot_hru()

    def dopln_body(self):
        if "Cech_lichvaru" in self.hrac_1_karty:
            if self.hrac_1_peniaze > self.hrac_2_peniaze:
                self.hrac_1_body += int(self.hrac_1_peniaze / 3)
                logging.debug(
                    f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu lichvaru {int(self.hrac_1_peniaze / 3)} bodov.")
            else:
                self.hrac_1_body += int(self.hrac_2_peniaze / 3)
                logging.debug(
                    f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu lichvaru {int(self.hrac_2_peniaze / 3)} bodov.")
        if "Cech_lichvaru" in self.hrac_2_karty:
            if self.hrac_1_peniaze > self.hrac_2_peniaze:
                self.hrac_2_body += int(self.hrac_1_peniaze / 3)
                logging.debug(
                    f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu lichvaru {int(self.hrac_1_peniaze / 3)} bodov.")
            else:
                self.hrac_2_body += int(self.hrac_2_peniaze / 3)
                logging.debug(
                    f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu lichvaru {int(self.hrac_2_peniaze / 3)} bodov.")

        if "Cech_lodaru" in self.hrac_1_karty:
            hrac_1_sivohnede = self.zrataj_karty(1, "siva") + self.zrataj_karty(1, "hneda")
            hrac_2_sivohnede = self.zrataj_karty(2, "siva") + self.zrataj_karty(2, "hneda")
            if hrac_1_sivohnede > hrac_2_sivohnede:
                self.hrac_1_body += hrac_1_sivohnede
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu lodaru {hrac_1_sivohnede} bodov.")
            else:
                self.hrac_1_body += hrac_2_sivohnede
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu lodaru {hrac_2_sivohnede} bodov.")
        if "Cech_lodaru" in self.hrac_2_karty:
            hrac_1_sivohnede = self.zrataj_karty(1, "siva") + self.zrataj_karty(1, "hneda")
            hrac_2_sivohnede = self.zrataj_karty(2, "siva") + self.zrataj_karty(2, "hneda")
            if hrac_1_sivohnede > hrac_2_sivohnede:
                self.hrac_2_body += hrac_1_sivohnede
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu lodaru {hrac_1_sivohnede} bodov.")
            else:
                self.hrac_2_body += hrac_2_sivohnede
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu lodaru {hrac_2_sivohnede} bodov.")

        if "Cech_obchodniku" in self.hrac_1_karty:
            hrac_1_zlte = self.zrataj_karty(1, "zlta")
            hrac_2_zlte = self.zrataj_karty(2, "zlta")
            if hrac_1_zlte > hrac_2_zlte:
                self.hrac_1_body += hrac_1_zlte
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu obchodniku {hrac_1_zlte} bodov.")
            else:
                self.hrac_1_body += hrac_2_zlte
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu obchodniku {hrac_2_zlte} bodov.")
        if "Cech_obchodniku" in self.hrac_2_karty:
            hrac_1_zlte = self.zrataj_karty(1, "zlta")
            hrac_2_zlte = self.zrataj_karty(2, "zlta")
            if hrac_1_zlte > hrac_2_zlte:
                self.hrac_2_body += hrac_1_zlte
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu obchodniku {hrac_1_zlte} bodov.")
            else:
                self.hrac_2_body += hrac_2_zlte
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu obchodniku {hrac_2_zlte} bodov.")

        if "Cech_stavitelu" in self.hrac_1_karty:
            hrac_1_pocet_divov = self.zrataj_karty(1, "div")
            hrac_2_pocet_divov = self.zrataj_karty(2, "div")
            if hrac_1_pocet_divov > hrac_2_pocet_divov:
                self.hrac_1_body += hrac_1_pocet_divov * 2
                logging.debug(
                    f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu stavitelu {hrac_1_pocet_divov * 2} bodov.")
            else:
                self.hrac_1_body += hrac_2_pocet_divov * 2
                logging.debug(
                    f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu stavitelu {hrac_2_pocet_divov * 2} bodov.")
        if "Cech_stavitelu" in self.hrac_2_karty:
            hrac_1_pocet_divov = self.zrataj_karty(1, "div")
            hrac_2_pocet_divov = self.zrataj_karty(2, "div")
            if hrac_1_pocet_divov > hrac_2_pocet_divov:
                self.hrac_2_body += hrac_1_pocet_divov * 2
                logging.debug(
                    f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu stavitelu {hrac_1_pocet_divov * 2} bodov.")
            else:
                self.hrac_2_body += hrac_2_pocet_divov * 2
                logging.debug(
                    f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu stavitelu {hrac_2_pocet_divov * 2} bodov.")

        if "Cech_vedcu" in self.hrac_1_karty:
            hrac_1_zelene = self.zrataj_karty(1, "zelena")
            hrac_2_zelene = self.zrataj_karty(2, "zelena")
            if hrac_1_zelene > hrac_2_zelene:
                self.hrac_1_body += hrac_1_zelene
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu vedcu {hrac_1_zelene} bodov.")
            else:
                self.hrac_1_body += hrac_2_zelene
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu vedcu {hrac_2_zelene} bodov.")
        if "Cech_vedcu" in self.hrac_2_karty:
            hrac_1_zelene = self.zrataj_karty(1, "zelena")
            hrac_2_zelene = self.zrataj_karty(2, "zelena")
            if hrac_1_zelene > hrac_2_zelene:
                self.hrac_2_body += hrac_1_zelene
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu vedcu {hrac_1_zelene} bodov.")
            else:
                self.hrac_2_body += hrac_2_zelene
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu vedcu {hrac_2_zelene} bodov.")

        if "Cech_uredniku" in self.hrac_1_karty:
            hrac_1_modra = self.zrataj_karty(1, "modra")
            hrac_2_modra = self.zrataj_karty(2, "modra")
            if hrac_1_modra > hrac_2_modra:
                self.hrac_1_body += hrac_1_modra
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu uredniku {hrac_1_modra} bodov.")
            else:
                self.hrac_1_body += hrac_2_modra
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu uredniku {hrac_2_modra} bodov.")
        if "Cech_uredniku" in self.hrac_2_karty:
            hrac_1_modra = self.zrataj_karty(1, "modra")
            hrac_2_modra = self.zrataj_karty(2, "modra")
            if hrac_1_modra > hrac_2_modra:
                self.hrac_2_body += hrac_1_modra
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu uredniku {hrac_1_modra} bodov.")
            else:
                self.hrac_2_body += hrac_2_modra
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu uredniku {hrac_2_modra} bodov.")

        if "Cech_taktiku" in self.hrac_1_karty:
            hrac_1_cervene = self.zrataj_karty(1, "cervena")
            hrac_2_cervene = self.zrataj_karty(2, "cervena")
            if hrac_1_cervene > hrac_2_cervene:
                self.hrac_1_body += hrac_1_cervene
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu taktiku {hrac_1_cervene} bodov.")
            else:
                self.hrac_1_body += hrac_2_cervene
                logging.debug(f"Hrac {self.hraci_mena[0]} ziskala kvoli Cechu taktiku {hrac_2_cervene} bodov.")
        if "Cech_taktiku" in self.hrac_2_karty:
            hrac_1_cervene = self.zrataj_karty(1, "cervena")
            hrac_2_cervene = self.zrataj_karty(2, "cervena")
            if hrac_1_cervene > hrac_2_cervene:
                self.hrac_2_body += hrac_1_cervene
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu taktiku {hrac_1_cervene} bodov.")
            else:
                self.hrac_2_body += hrac_2_cervene
                logging.debug(f"Hrac {self.hraci_mena[1]} ziskala kvoli Cechu taktiku {hrac_2_cervene} bodov.")

        if "Matematika" in self.hrac_1_tokeny:
            pocet_tokeny = self.zrataj_karty(1, "token") * 3
            self.hrac_1_body += pocet_tokeny
            logging.debug(f"Hrac {self.hraci_mena[0]} ziskal {pocet_tokeny * 3} bodov za token Matematika")
        if "Matematika" in self.hrac_2_tokeny:
            pocet_tokeny = self.zrataj_karty(2, "token") * 3
            self.hrac_1_body += pocet_tokeny
            logging.debug(f"Hrac {self.hraci_mena[1]} ziskal {pocet_tokeny * 3} bodov za token Matematika")

    def vyhodnot_hru(self):
        scorecard = cv2.imread("karty/ine/scorecard.png")
        cv2.imshow("Scorecard", scorecard)
        cv2.waitKey(0)
        cv2.destroyWindow("Scorecard")

    def zisti_rohy(self):
        lavy_okraj = []
        okraj_karty = int(monitor_sirka / 2 - int(monitor_sirka * 0.01)) - karta_sirka
        lavy_okraj.append(okraj_karty)

        for i in range(1, 20):
            if i in [2, 5, 9, 10, 11, 15, 18]:
                if i == 2: okraj_karty = lavy_okraj[0] - int(karta_sirka * 0.8)
                if i == 5: okraj_karty = lavy_okraj[2] - int(karta_sirka * 0.8)
                if i == 9: okraj_karty = lavy_okraj[2]
                if i == 10: okraj_karty = lavy_okraj[4]
                if i == 11: okraj_karty = lavy_okraj[5]
                if i == 15: okraj_karty = lavy_okraj[2]
                if i == 18: okraj_karty = lavy_okraj[0]
            else:
                okraj_karty = lavy_okraj[i - 1] + int(karta_sirka * 1.4)
            lavy_okraj.append(okraj_karty)

        self.lavy_okraj = lavy_okraj

    def vyber_herne_karty(self):
        vsetky_karty_meno = []
        cechy = []
        herne_karty_meno = []
        myList = os.listdir("karty/vek_3")
        for karta in myList:
            if os.path.splitext(karta)[1].lower() in ('.jpg', '.jpeg'):
                if karta.split("_")[0] == "Cech":
                    cechy.append(karta.split(".")[0])
                else:
                    vsetky_karty_meno.append(karta.split(".")[0])
            else:
                logging.warning(f"{karta} ignorovana. Nema priponu jpg ani jpeg.")

        for i in range(0, 17):
            pick_id = random.randint(0, len(vsetky_karty_meno) - 1)
            herne_karty_meno.append(vsetky_karty_meno[pick_id])
            vsetky_karty_meno.pop(pick_id)

        for i in range(0, 3):
            pick_id = random.randint(0, len(cechy) - 1)
            herne_karty_meno.append(cechy[pick_id])
            cechy.pop(pick_id)

        random.shuffle(herne_karty_meno)

        self.herne_karty_meno = herne_karty_meno

    def nakresli_vek(self, active=False):

        if active:
            logging.debug(f"Aktivny hrac: {self.aktivny_hrac}")
            logging.debug(f"Tah cislo: {self.tah}")
            gamer = self.naposledy_hral
        else:
            gamer = self.aktivny_hrac

        img = np.zeros((monitor_vyska, monitor_sirka, 3), np.uint8)

        # ukaz poslednu akciu

        if os.path.exists(f'logs/gamelog_{self.hra_id}_{gamer}.log'):
            with open(f'logs/gamelog_{self.hra_id}_{gamer}.log', 'r') as f:
                lines = f.read().splitlines()
                last_line = lines[-1].split(":")[2].split(".")[0]
        else:
            last_line = "Neviem ziskat oponentove logy..."

        cv2.putText(img, last_line, (10, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)

        #   nakresli titulok
        if not active:
            farba = (160, 160, 160)
            header = "        Cakam na oponentov tah..."
        else:
            farba = (0, 255, 0)
            header = f"7 Wonders DUEL - id hry: {self.hra_id}- tah: {self.tah}-{self.ja_som}"

        cv2.putText(img, header, (self.lavy_okraj[5]-80, 35), cv2.FONT_HERSHEY_DUPLEX, 1, farba, 2)

        #   nakresli karty
        horny_okraj = horny_okraj_global
        for i in range(0, len(self.herne_karty_meno)):
            #   nastav hodnotu horneho okraja, aby sa karty poukladali do riadkov

            if i in [2, 5, 9, 11, 15, 18]:
                horny_okraj = horny_okraj + int(karta_vyska * 0.7)

            #   v riadkoch kde ma byt karta stale otocena ju nakresli otocenu, ale iba ak este nebola vybrana

            if i not in [2, 3, 4, 9, 10, 15, 16, 17]:

                #print(f"Karta {self.herne_karty_alias[i]} je {self.herne_karty_meno[i]}")

                if self.herne_karty_meno[i] is not None:
                    karta_img = najdi_kartu(self.herne_karty_meno[i])
                    img[horny_okraj:horny_okraj + karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                    cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj+10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                else:
                    pass

            #   v ostatnych riadkoch zisti, ci karta nebola pouziva a ak nie, tak ci je validna na vyber. ak ano, zobraz ju otocenu.

            else:

                if self.herne_karty_meno[i] is not None:
                    if self.herne_karty_alias[i] in self.validne_karty():
                        karta_img = najdi_kartu(self.herne_karty_meno[i])
                        img[horny_okraj:horny_okraj + karta_vyska, self.lavy_okraj[i]:self.lavy_okraj[i] + karta_sirka] = karta_img
                        cv2.putText(img, self.herne_karty_alias[i], (self.lavy_okraj[i], horny_okraj + 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
                    else:
                        if self.herne_karty_meno[i].split("_")[0] == "Cech":
                            karta = cv2.imread("karty/ine/zadna_strana_cech_regular.jpeg")
                        else:
                            karta = cv2.imread("karty/ine/zadna_strana_vek_3_regular.jpg")
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
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[8] + 150 + karta_sirka, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)), (self.lavy_okraj[5] - 200, int(monitor_vyska * 0.9)), (0, 0, 255), 2)
            cv2.rectangle(img, (self.lavy_okraj[8] + 150 + karta_sirka, int(monitor_vyska / 2)), (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
        else:
            cv2.putText(img, self.hraci_mena[0], (20, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 0)
            cv2.putText(img, self.hraci_mena[1], (self.lavy_okraj[8] + 150 + karta_sirka, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(img, (20, int(monitor_vyska / 2)), (self.lavy_okraj[5] - 200, int(monitor_vyska * 0.9)), (0, 0, 100), 0)
            cv2.rectangle(img, (self.lavy_okraj[8] + 150 + karta_sirka, int(monitor_vyska / 2)), (monitor_sirka - 20, int(monitor_vyska * 0.9)), (0, 0, 255), 2)

        #   nakresli peniaze a body
        cv2.putText(img, "Pen:" +str(self.hrac_1_peniaze), (self.lavy_okraj[5] - 280, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
        cv2.putText(img, "Body:" +str(self.hrac_1_body), (self.lavy_okraj[5] - 410, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 51, 51), 1)
        cv2.putText(img, "Pen:" + str(self.hrac_2_peniaze), (monitor_sirka - 130, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
        cv2.putText(img, "Body:" + str(self.hrac_2_body), (monitor_sirka - 260, int(monitor_vyska / 2)-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 51, 51), 1)

        #   nakresli majetok hraca 1 aj s tokenami
        sivohnedy_okraj = self.hrac_1_horny_okraj_sivohnede
        zlty_okraj = self.hrac_1_horny_okraj_zlte
        modry_okraj = self.hrac_1_horny_okraj_modre
        cerveny_okraj = self.hrac_1_horny_okraj_cervene
        zeleny_okraj = self.hrac_1_horny_okraj_zelene

        for karta in self.hrac_1_karty:
            karta_img = najdi_kartu(karta)
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
            elif eval("self." + karta.lower() + ".farba") == "zelena" or eval("self." + karta.lower() + ".farba") == "fialova":
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
            karta_img = najdi_kartu(karta)
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
            elif eval("self." + karta.lower() + ".farba") == "zelena" or eval("self." + karta.lower() + ".farba") == "fialova":
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
        l_okraj = int(self.lavy_okraj[5] - 120)
        cv2.line(img, (l_okraj + 90, h_okraj - 10), (self.lavy_okraj[8] + karta_sirka, h_okraj - 10), (0, 102, 204), 1)
        cv2.putText(img, "Discard", (l_okraj, h_okraj - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 102, 204), 1)
        for karta in self.odhodene_karty:
            karta_img = najdi_kartu(karta)
            img[h_okraj:h_okraj + karta_vyska, l_okraj:l_okraj + karta_sirka] = karta_img
            l_okraj = l_okraj + 50


        #   nakresli boje
        h_okraj = int(monitor_vyska * 0.87)
        l_okraj = self.lavy_okraj[5] - 90
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
        l_okraj = self.lavy_okraj[5]
        for token in self.herne_tokeny_meno:
            token_img = cv2.imread(f"karty/tokeny/{token}.png")
            token_img = cv2.resize(token_img, (token_rozmer, token_rozmer))
            img[h_okraj:h_okraj+token_rozmer, l_okraj:l_okraj+token_rozmer] = token_img
            l_okraj = l_okraj + token_rozmer + 10

        #   dokresli podpis
        cv2.putText(img, "Vytvorene Jan @ Strompl 28.10.2020", (int(monitor_sirka * 0.8), monitor_vyska - 22), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(img, "Dokoncene 11.02.2021", (int(monitor_sirka * 0.8), monitor_vyska - 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, (0, 255, 0), 1)

        cv2.imshow("7wonders", img)

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
                    if self.herne_karty_alias[9] is None:
                        validne_karty.append(karta_alias)
                if idx == 6:
                    if self.herne_karty_alias[9] is None:
                        validne_karty.append(karta_alias)
                if idx == 7:
                    if self.herne_karty_alias[10] is None:
                        validne_karty.append(karta_alias)
                if idx == 8:
                    if self.herne_karty_alias[10] is None:
                        validne_karty.append(karta_alias)
                if idx == 9:
                    if self.herne_karty_alias[11] is None and self.herne_karty_alias[12] is None:
                        validne_karty.append(karta_alias)
                if idx == 10:
                    if self.herne_karty_alias[13] is None and self.herne_karty_alias[14] is None:
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
            if akcia != "cancel":
                vysledok_akcie = self.vykonaj_akciu(zvolena_karta, akcia)
                if vysledok_akcie == "ok":
                    self.herne_karty_meno[self.herne_karty_alias.index(karta)] = None
                    self.herne_karty_alias[self.herne_karty_alias.index(karta)] = None
                    self.metadata_to_json()
        else:
            logging.error(f"Karta {self.herne_karty_meno[self.herne_karty_alias.index(karta)]} nie je plne odkryta, preto ju nie je mozne zahrat. Znova.")
            ukaz_error("nevalidna_karta")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1

    def zvol_mozosti(self, zvolena_karta):
        cv2.namedWindow("Zvolena karta.")
        zvolena_karta_pozadie = np.zeros((karta_vyska * 3, karta_sirka * 6, 3), np.uint8)
        zvolena_karta_img = najdi_kartu(zvolena_karta, karta_sirka=karta_sirka*2, karta_vyska=karta_vyska*2)
        zvolena_karta_pozadie[50:50+(karta_vyska*2), 20:20+(karta_sirka*2)] = zvolena_karta_img
        cv2.putText(zvolena_karta_pozadie, "(o) Odhod", (int(karta_sirka * 2.5), 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(k) Kup", (int(karta_sirka * 2.5), 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(d) Postav div:", (int(karta_sirka * 2.5), 210), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.putText(zvolena_karta_pozadie, "(c) Vyber inu kartu:", (int(karta_sirka * 2.5), 270), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
        cv2.moveWindow("Zvolena karta.", int(monitor_sirka / 3), int(monitor_vyska / 3))
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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Zvolena karta.")
            return "cancel"
        else:
            logging.error(f"Stlacena klavesa: {chr(key)} Tato akcia nie je povolena.")
            cv2.destroyWindow("Zvolena karta.")
            ukaz_error("nespravna_volba")
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            return "cancel"

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
            return "ok"

        if akcia == "kup":
            if self.mozem_kupit(hrac, meno_karty):
                self.kup_kartu(hrac, meno_karty, typ="kartu")
                return "ok"
            else:
                logging.error(f"Kartu {meno_karty} si nemozem kupit. Nedostatok penazi. Zvol inu kartu.")
                ukaz_error("nedostatok_penazi")
                return "cancel"

        if akcia == "postav_div":
            suradnice_sirka = [50, 50+div_sirka + 20, 50, 50+div_sirka + 20]
            suradnice_vyska = [50, 50, 50+div_vyska + 20, 50+div_vyska + 20]
            cv2.namedWindow("Vyber div")
            vyber_div_pozadie = np.zeros((div_vyska * 3, div_sirka * 3 - 50, 3), np.uint8)
            validne_karty = []
            for idx, div in enumerate(eval(f"self.hrac_{hrac}_divy_meno")):
                if div not in eval(f"self.hrac_{hrac}_divy_aktivne"):
                    div = cv2.imread(f"karty/divy/{div}.jpeg")
                    div = cv2.resize(div, (div_sirka, div_vyska))
                    vyber_div_pozadie[suradnice_vyska[idx]:suradnice_vyska[idx] + div_vyska, suradnice_sirka[idx]:suradnice_sirka[idx] + div_sirka] = div
                    cv2.putText(vyber_div_pozadie, str(idx+1), (suradnice_sirka[idx], suradnice_vyska[idx]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    validne_karty.append(str(idx+1))
            cv2.imshow("Vyber div", vyber_div_pozadie)
            key = cv2.waitKey()
            if chr(key) in validne_karty:
                div_meno = eval(f"self.hrac_{hrac}_divy_meno[int(chr({key}))-1]")
                logging.debug(f"Stlacena klavesa: {chr(key)} Vybany div: {div_meno}")
                if self.mozem_kupit(hrac, div_meno):
                    self.kup_kartu(hrac, div_meno, typ="div")
                    self.vyhodnot_div(hrac, div_meno)
                    cv2.destroyWindow("Vyber div")
                    return "ok"
                else:
                    ukaz_error("nedostatok_penazi")
                    cv2.destroyWindow("Vyber div")
                    return "cancel"
            else:
                logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_karty}. Znova.")
                ukaz_error("nespravna_volba")
                cv2.destroyWindow("Vyber div")

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

            #   ak mam div "Architektura pridam si 2 suroviny Y do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "div" and "Architektura" in eval(f"self.hrac_{hrac}_tokeny"):
                suroviny_mam.append("Y")
                suroviny_mam.append("Y")
                logging.debug(f"Hrac vlastni Architektura, do poolu surovin som pridal [Y, Y]")

            # ak mam Forum, pridam


            # ak mam Stanoviste Karavan, pridam

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

        if hrac == 1:
            hrac = 1
            oponent = 2
        else:
            hrac = 2
            oponent = 1
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

        # karty, ktore nemaju pevne urcenu penaznu odmenu
        if peniaze_gain == "?":
            if meno_karty == "Pristav":
                parameter = self.zrataj_karty(hrac, "hneda")
            elif meno_karty == "Arena":
                parameter = self.zrataj_karty(hrac, "div")
            elif meno_karty == "Majak":
                parameter = self.zrataj_karty(hrac, "zlta")
            elif meno_karty == "Obchodni_komora":
                parameter = self.zrataj_karty(hrac, "siva")
            elif meno_karty == "Zbrojnice":
                parameter = self.zrataj_karty(hrac, "cervena")
            elif meno_karty == "Cech_lodaru":
                hrac_param = self.zrataj_karty(hrac, "hnede") + self.zrataj_karty(hrac, "sive")
                oponent_param = self.zrataj_karty(oponent, "hnede") + self.zrataj_karty(oponent, "sive")
                if hrac_param >= oponent_param:
                    parameter = hrac_param
                    logging.debug(f"Mam viac hnedych a sivych kariet ako oponent.")
                else:
                    parameter = oponent_param
                    logging.debug(f"Oponent ma viac sivych a hnedych kariet.")
            elif meno_karty == "Cech_obchodniku":
                hrac_param = self.zrataj_karty(hrac, "zlta")
                oponent_param = self.zrataj_karty(oponent, "zlta")
                if hrac_param >= oponent_param:
                    parameter = hrac_param
                    logging.debug(f"Mam viac zltych kariet ako oponent.")
                else:
                    parameter = oponent_param
                    logging.debug(f"Oponent ma viac zltych kariet.")
            elif meno_karty == "Cech_taktiku":
                hrac_param = self.zrataj_karty(hrac, "cervena")
                oponent_param = self.zrataj_karty(oponent, "cervena")
                if hrac_param >= oponent_param:
                    parameter = hrac_param
                    logging.debug(f"Mam viac cervenych kariet ako oponent.")
                else:
                    parameter = oponent_param
                    logging.debug(f"Oponent ma viac cervenych kariet.")
            elif meno_karty == "Cech_uredniku":
                hrac_param = self.zrataj_karty(hrac, "modra")
                oponent_param = self.zrataj_karty(oponent, "modra")
                if hrac_param >= oponent_param:
                    parameter = hrac_param
                    logging.debug(f"Mam viac modrych kariet ako oponent.")
                else:
                    parameter = oponent_param
                    logging.debug(f"Oponent ma viac modrych kariet.")
            elif meno_karty == "Cech_vedcu":
                hrac_param = self.zrataj_karty(hrac, "zelena")
                oponent_param = self.zrataj_karty(oponent, "zelena")
                if hrac_param >= oponent_param:
                    parameter = hrac_param
                    logging.debug(f"Mam viac zelenych kariet ako oponent.")
                else:
                    parameter = oponent_param
                    logging.debug(f"Oponent ma viac zelenych kariet.")
            peniaze_gain = eval(f"self.{meno_karty.lower()}.vyrataj_penaznu_odmenu({parameter})")

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
                    #   ak aktivny hrac vlastni urbanismus, dostava 4 peniaze
                    if "Urbanismus" in eval(f"self.hrac_{hrac}_tokeny"):
                        exec(f"self.hrac_{hrac}_peniaze += 4")
                        logging.debug(f"Hrac vlastni token Urbanismus, dostava 4 peniaze.")
                else:
                    cena_karty = cena_karty[0]

        if type(cena_karty) == int:
            cena = cena_karty
        else:
            #   ak mam token "Zednarstvi, ktory mi zlacnuje modre karty, pridam si 2 suroviny X do poolu"
            if eval(f"self.{meno_karty.lower()}.farba") == "modra" and "Zednarstvi" in eval(f"self.hrac_{hrac}_tokeny"):
                co_mam.append("X")
                co_mam.append("X")

            #   ak mam div Architektura, pridam si 2 suroviny YY do poolu"
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
            if cena != 0: logging.debug(f"Karta nie je zlacnena Divmi alebo Tokenmi. Jej cena je: {cena}")
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
        if karta_farba in ("hneda", "siva", "div", "zlta") :
            for sur in suroviny_gain:
                exec(f"self.hrac_{hrac}_suroviny.append('{sur}')")
        #   boje

        #   ak vlastnim token Strategie, zosilnim boje tym kartam, ktore davaju boje, vynimka su divy
        if boje_gain != 0:
            if eval("self." + meno_karty.lower() + ".farba") != "div":
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

            # zisti, ci nemam 2 rovnake symboly aby som vyhral
            symbol = eval("self." + meno_karty.lower() + ".symbol")
            eval(f"self.hrac_{hrac}_symboly.append('{symbol}')")
            logging.debug(f"Kvoli zelenej karte {meno_karty} ziskavam symbol {symbol}")

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
                #self.metadata_to_json(f"archiv_hier/input_metadata_{self.hra_id}.json")
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
        diskart_img = np.zeros((200, monitor_sirka, 3), np.uint8)
        y = 10
        validne_klavesy = []
        for idx, odhodena_karta in enumerate(self.odhodene_karty):
            odhodena_karta = najdi_kartu(odhodena_karta)
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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Diskart")
            cv2.destroyWindow("Vyber div")

    def odhod_hracovi_kartu(self, hrac, typ):
        cv2.namedWindow("Hracove karty")
        oponentove_karty_img = np.zeros((200, monitor_sirka, 3), np.uint8)
        y = 10
        validne_klavesy = []
        hracove_karty = []

        for karta in eval(f"self.hrac_{hrac}_karty"):
            if eval("self." + karta.lower() + ".farba") == typ:
                hracove_karty.append(karta)

        logging.debug(f"Hracove karty typu {typ} su: {hracove_karty}")
        for idx, karta in enumerate(hracove_karty):
            karta = najdi_kartu(karta)
            oponentove_karty_img[20:20 + karta_vyska, y:y + karta_sirka] = karta
            cv2.putText(oponentove_karty_img, str(idx), (y, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y += karta_sirka + 10
            validne_klavesy.append(str(idx))
        cv2.imshow("Hracove karty", oponentove_karty_img)
        key = cv2.waitKey()
        if chr(key) in validne_klavesy:
            logging.info(f"Oponentovi rusim: {hracove_karty[int(chr(key))]}")
            #   rusim kartu
            eval(f"self.hrac_{hrac}_karty.remove('{hracove_karty[int(chr(key))]}')")
            #   rusim suroviny
            suroviny = eval(f"self.{hracove_karty[int(chr(key))].lower()}.suroviny")
            eval(f"self.hrac_{hrac}_suroviny.remove('{suroviny}')")
            #   pridavam do diskartu
            eval(f"self.odhodene_karty.append('{hracove_karty[int(chr(key))]}')")
            cv2.destroyWindow("Hracove karty")
        else:
            logging.error(f"Volba {chr(key)} nie je povolena. Vyber z {validne_klavesy}. Znova.")
            ukaz_error("nespravna_volba")
            cv2.destroyWindow("Hracove karty")
            cv2.destroyWindow("Vyber div")

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
            cv2.destroyWindow("Neherne tokeny")
            cv2.destroyWindow("Vyber div")

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
            self.aktivny_hrac = self.naposledy_hral
            self.tah = self.tah - 1
            cv2.destroyWindow("Herne tokeny")
            cv2.destroyWindow("Vyber div")

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
                eval(f"self.hrac_{hrac}_symboly.append('zakon')")
                if len(set(eval(f"self.hrac_{hrac}_symboly"))) == 6:
                    logging.info(f"Hrac {hrac} vyhral na symboly ekonomie.")
                    sys.exit(0)

            if efekt_tokenu == "zlacni_modre":
                #   hotovo v mozem_kupit()
                pass

    def zrataj_karty(self, hrac, farba):
        count = 0
        if farba != "div":
            for meno_karty in eval("self.hrac_"+str(hrac)+"_karty"):
                if eval("self."+meno_karty.lower()+".farba") == farba:
                    count = count +1
        elif farba == "div":
            aktivne_divy = eval(f"self.hrac_{hrac}_divy_aktivne")
            #aktivne_divy = np.unique(aktivne_divy)
            #aktivne_divy = np.delete(aktivne_divy, 0)
            #aktivne_divy = aktivne_divy.tolist()
            for meno_karty in aktivne_divy:
                if meno_karty is not False:
                    if eval("self."+meno_karty.lower()+".farba") == farba:
                        count = count +1
            count = count / 2

        #logging.debug(f"{hrac} ma {count} kariet farby {farba}")
        return count

    def read_from_meta(self):
        data = self.net.get()

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
        self.vek = data["vek"]
        self.hraci_mena = data["hraci_mena"]
        self.naposledy_hral = data["naposledy_hral"]
        #self.aktivny_hrac = nasledujuci_hrac(self.naposledy_hral, self.hraci_mena)
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
        self.hrac_1_symboly = data["hrac_1_symboly"]
        self.hrac_2_tokeny = data["hrac_2_tokeny"]
        self.hrac_2_symboly = data["hrac_2_symboly"]

    def metadata_to_json(self):
        logging.debug(f"Obnovujem metadata...")
        vars_to_json = {"rozohrana_hra": "Ano",
                        "vek": 3,
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
                        "naposledy_hral": self.aktivny_hrac,
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
                        "hrac_1_symboly": self.hrac_1_symboly,
                        "hrac_2_tokeny": self.hrac_2_tokeny,
                        "hrac_2_symboly": self.hrac_2_symboly}

        self.net.send(json.dumps(vars_to_json))

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

def najdi_kartu(karta_meno, karta_sirka=karta_sirka, karta_vyska=karta_vyska):
    if os.path.exists(f"karty/vek_1/{karta_meno}.jpg"):
        karta_meno = cv2.imread(f"karty/vek_1/{karta_meno}.jpg")
        karta_meno = cv2.resize(karta_meno, (karta_sirka, karta_vyska))
    elif os.path.exists(f"karty/vek_2/{karta_meno}.jpeg"):
        karta_meno = cv2.imread(f"karty/vek_2/{karta_meno}.jpeg")
        karta_meno = cv2.resize(karta_meno, (karta_sirka, karta_vyska))
    elif os.path.exists(f"karty/vek_3/{karta_meno}.jpeg"):
        karta_meno = cv2.imread(f"karty/vek_3/{karta_meno}.jpeg")
        karta_meno = cv2.resize(karta_meno, (karta_sirka, karta_vyska))
    else:
        logging.error("Karta nie je ani vo veku 1 ani vo veku 2")
    return karta_meno

def nasledujuci_hrac(aktualny_hrac, hraci):
    id_hrac = hraci.index(aktualny_hrac)
    if id_hrac == 0:
        return hraci[1]
    else:
        return hraci[0]

def vyhra_na_boje(vitaz):
    vitazny_obrazok = cv2.imread("karty/ine/fight_winner.jpg")
    cv2.putText(vitazny_obrazok, f"Vitaz: {vitaz}", (10, 35), cv2.FONT_HERSHEY_DUPLEX, 1, (153, 204, 255), 1)
    cv2.imshow("Vitaz na boje", vitazny_obrazok)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    sys.exit(0)

def vyhra_na_symboly(vitaz):
    vitazny_obrazok = cv2.imread("karty/ine/economy_winner.png")
    cv2.putText(vitazny_obrazok, f"Vitaz: {vitaz}", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 153, 0), 1)
    cv2.imshow("Vitaz na symboly ekonomie", vitazny_obrazok)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    sys.exit(0)