import os
import csv

class CSVManager:
    @staticmethod
    def save_csv(csv_file):
        csv_folder = os.path.join(os.path.dirname(__file__), 'csv')
        if not os.path.exists(csv_folder):
            os.makedirs(csv_folder)
        save_path = os.path.join(csv_folder, 'upload.csv')
        if os.path.exists(save_path):
            os.remove(save_path)
        csv_file.save(save_path)
        return save_path

    @staticmethod
    def read_csv(file_path):
        csv_data = []
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                csv_data.append(row)
        return csv_data
