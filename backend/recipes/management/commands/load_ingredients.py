import csv
import os
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка CSV файлов.'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('data', 'ingredients.csv')
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for read in reader:
                Ingredient.objects.create(
                    name=read[0],
                    measurement_unit=read[1])
