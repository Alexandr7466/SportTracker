from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Product(models.Model):
    # слева это как записываетяс в базе а справа для пользователя
    CATEGORIES = [
        ("protein", "Белковые"),
        ("carb", "Углеводные"),
        ("fat", "Жировые"),
        ("veg", "Овощи и фрукты"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORIES)
    # если че все эти бжу измеряются именно в 100г
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    # максимум этого продукта в день (чтобы не получилось 500 г яиц)
    max_grams = models.PositiveIntegerField(default=300)

    # как отображать в админке и в шаблонах
    def __str__(self):
        # говорим что надо отображать тупо название продукта
        return self.name

    # Метод считает калорийность 100 граммов продукта
    def calories(self):
        return self.protein * 4 + self.carbs * 4 + self.fat * 9


class Profile(models.Model):
    GENDERS = [
        ("male", "Мужской"),
        ("female", "Женский"),
    ]

    GOALS = [
        ("mass", "Набор массы"),
        ("loss", "Похудение"),
    ]

    # связь один к одному с пользователем значит что у одного пользователя одна анкета
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=20)
    gender = models.CharField(max_length=6, choices=GENDERS, default="male")
    weight = models.FloatField(default=70)
    start_weight = models.FloatField(default=70)
    goal = models.CharField(max_length=4, choices=GOALS, default="mass")
    start_date = models.DateField(default=timezone.now)
    last_weigh_in = models.DateField(default=timezone.now)
    products = models.ManyToManyField(Product, blank=True)
    is_filled = models.BooleanField(default=False)

    def __str__(self):
        return f"Анкета {self.user.username}"

    def weight_change(self):
        return self.weight - self.start_weight

    def months_passed(self):
        today = timezone.now().date()
        return (today - self.start_date).days // 30

    # пора ли просить пользователя звеситься (если прошло 30)
    def needs_weigh_in(self):
        return (timezone.now().date() - self.last_weigh_in).days >= 30