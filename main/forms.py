from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Product


class RegisterForm(UserCreationForm):
    # класс meta говорит с какой моделькой работать (User)
    class Meta:
        model = User
        # яне говорю что надо заполнить еще поле пароль тк это автоматически (типо из за UserCreation)
        fields = ["username"]

class ProfileForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        # брать список продуктов из всей таблицы.
        queryset =Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required =False,
        label="Продукты, которые у тебя есть постоянно",
    )

    class Meta:
        model = Profile
        fields = ["age", "gender", "weight", "goal", "products"]
        #подписи на рус
        labels = {
            "age": "Возраст",
            "gender": "Пол",
            "weight": "Вес, кг",
            "goal": "Цель",
        }


# форма ежемесячного взвешивания
class WeightForm(forms.Form):
    weight = forms.FloatField(label = "Новый вес, кг", min_value=30 , max_value=300)