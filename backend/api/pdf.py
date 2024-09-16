from dataclasses import dataclass
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from recipes.models import RecipeIngredient


@dataclass
class IngredientInfo:
    name: str
    measurement_unit: str
    total_amount: int


def create_ingredients_list(request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_carts__user=request.user).select_related(
        'ingredient'
    )
    ingredient_info_list = []
    print(ingredients)
    for recipe_ingredient in ingredients:
        name = recipe_ingredient.ingredient.name
        measurement_unit = recipe_ingredient.ingredient.measurement_unit
        amount = recipe_ingredient.amount
        if name not in [i.name for i in ingredient_info_list]:
            ingredient_info = IngredientInfo(
                name=name, measurement_unit=measurement_unit,
                total_amount=amount)
            ingredient_info_list.append(ingredient_info)
            continue
        for ingredient_info in ingredient_info_list:
            if ingredient_info.name == name:
                ingredient_info.total_amount += amount
    ingredient_info_list.sort(key=lambda x: x.name)
    return ingredient_info_list


def create_pdf(final_list, filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{
        filename}"'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont('Arial', 15)
    width, height = letter
    y = height - 40
    p.drawString(30, y, 'Ingredients List')
    y -= 20
    for ingredient_info in final_list:
        name = ingredient_info.name.capitalize()
        measurement_unit = ingredient_info.measurement_unit
        total_amount = ingredient_info.total_amount
        p.drawString(30, y, f'{name} ({measurement_unit}): {
            total_amount}')
        y -= 20
    p.showPage()
    p.save()
    return response
