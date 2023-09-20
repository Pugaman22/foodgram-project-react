import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('../data/ingredients.json', 'rb') as f:
            data = json.load(f)
            print("loaded:", len(data))
            for index, item in enumerate(data):
                print(f'add {index}')
                Ingredient.objects.create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
