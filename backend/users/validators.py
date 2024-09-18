from django.core.validators import RegexValidator


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z', message='Не корректное поле.',
    code='invalid_registration')
