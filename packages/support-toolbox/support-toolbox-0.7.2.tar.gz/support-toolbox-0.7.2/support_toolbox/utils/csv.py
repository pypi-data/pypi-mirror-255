import csv


def process_csv_file(file_path):
    iris = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            iris.extend(row)
    return iris
