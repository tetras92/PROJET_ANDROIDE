import csv
with open('EDT_Bis.csv') as csvfile:
    with open('voeux.stl', 'w') as csvfileW:
        fieldnames = ["num"] + ["oblig"+str(i) for i in range(1,4)] + ["cons"+str(i) for i in range(1,6)]
        writer = csv.DictWriter(csvfileW, fieldnames=fieldnames)
        writer.writeheader()

        OBLIGATOIRE = {"algav", "dlp"}
        reader = csv.DictReader(csvfile)
        etu = 1
        for row in reader:
            i_obl = 1
            i_cons = 1

            D = dict()
            D["num"] = etu
            etu += 1
            for ide in ["a", "b", "c", "d", "e"]:
                if row[ide][:-1] in OBLIGATOIRE:
                    D["oblig"+str(i_obl)] = row[ide][:-1]
                    i_obl += 1
                else:
                    if row[ide][:-1] != "":
                        D["cons"+str(i_cons)] = row[ide][:-1]
                        i_cons += 1
            writer.writerow(D)


