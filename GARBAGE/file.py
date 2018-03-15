import csv

with open('names.csv', 'w') as csvfile:
    fieldnames = ['parcours'] + ['ue'+str(i) for i in range(1,4)]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writer
    D = {'parcours': ['androide'], 'ue1': 'lrc','ue2': 'mogpl'}
    writer.writerow(D)
    writer.writerow({'parcours': 'dac', 'ue2': 'mlbda'})
