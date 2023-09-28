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
            'Data is loaded')
        )
