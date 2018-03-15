import csv
import math
with open('EDT_Bis.csv') as csvfile:
    with open('edt.csv', 'w') as csvfileW:
        fieldnames = [str(i) for i in range(1,19)]#["num"] + ["oblig"+str(i) for i in range(1,4)] + ["cons"+str(i) for i in range(1,6)]
        writer = csv.DictWriter(csvfileW, fieldnames=fieldnames)
        writer.writeheader()

        #OBLIGATOIRE = {"algav", "dlp"}
        reader = csv.DictReader(csvfile)
        #etu = 1
        for row in reader:
            D =dict()
            for ch in [str(i) for i in range(1,19)]:
                if row[ch] != '' and int(ch) >= 9:
                    D[ch] = ((int(row[ch])-1)//4)*5 + (int(row[ch])-1)%4 +1
                else:
                    D[ch] = row[ch]

            writer.writerow(D)


