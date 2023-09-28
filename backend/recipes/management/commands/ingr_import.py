# import json

# from django.core.management.base import BaseCommand
# from recipes.models import Ingredient


# class Command(BaseCommand):

#     def handle(self, *args, **options):
#         with open('../data/ingredients.json', 'rb') as f:
#             data = json.load(f)
#             print("loaded:", len(data))
#             for index, item in enumerate(data):
#                 print(f'add {index}')
#                 Ingredient.objects.create(
#                     name=item['name'],
#                     measurement_unit=item['measurement_unit']
#                 )

import csv

from django.core.management import BaseCommand

from django.conf import settings
from recipes.models import Ingredient, Tag

DATA = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    """Add data from csv. """

    def handle(self, *args, **kwargs):
        for model, file in DATA.items():
            with open(
                    f'{settings.BASE_DIR}/data/{file}',
                    'r', encoding='utf-8',
            ) as table:
                reader = csv.DictReader(table)
                model.objects.bulk_create(model(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS(
            'Data id loaded')
        )
