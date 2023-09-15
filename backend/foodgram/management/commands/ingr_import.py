import json
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('../data/ingredients.json', 'rb') as f:
            data = json.load(f)
            print("loaded:", len(data))
            i = 0
            for item in data:
                print(f"add {i}")
                i += 1
                Ingredient.objects.create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
