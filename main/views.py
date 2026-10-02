from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import RegisterForm, ProfileForm, WeightForm
from .models import Profile, Product
from .dop_things import build_diet, get_workout, BASE_PRODUCTS


def months_text(num):
    two = num % 100
    last = num % 10
    # числа от 11 до 14 удет "месяцев"
    if 11 <= two <= 14:
        return "месяцев"
    # 1 месяц
    if last == 1:
        return "месяц"
    # если последняя цифра 2, 3 или 4 будет "месяца"
    if last in (2, 3, 4):
        return "месяца"
    # все остальное "месяцев"
    return "месяцев"


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        # создаем форму и засовываем туда данные которые ввел пользователь
        form = RegisterForm(request.POST)
        # типо такой логин свободен и пароли совпадают
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect("survey")
    # если первый заход на страницу создаем пустую форму
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        # создаем форму и сохраняем в нее данные типо пароль и логин
        form = AuthenticationForm(request, data=request.POST)
        # чекаем что такой логин и пароль существуют и все норм
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
    else:
        # пустая форма входа
        form = AuthenticationForm()
    return render(request, "main/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("register")


@login_required
def survey_view(request):
    # загружаем продукты если надо
    if not Product.objects.exists():
        for name, category, protein, fat, carbs, max_grams in BASE_PRODUCTS:
            Product.objects.create(
                name=name,
                category=category,
                protein=protein,
                fat=fat,
                carbs=carbs,
                max_grams=max_grams,
            )

    profile = request.user.profile
    if request.method == "POST":
        # создаем форму с указанными даными пользователя
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # сохраняем но не записываем в бд тк надо еще дать значение другим полям
            profile = form.save(commit=False)
            profile.start_weight = profile.weight
            profile.start_date = timezone.now().date()
            profile.last_weigh_in = timezone.now().date()
            profile.is_filled = True
            profile.save()
            form.save_m2m()
            return redirect("home")
    else:
        # форма с текущими данными анкеты
        form = ProfileForm(instance=profile)
    return render(request, "main/survey.html", {"form": form})


@login_required
def home_view(request):
    profile = request.user.profile
    if not profile.is_filled:
        return redirect("survey")
    if request.method == "POST":
        # создаем форму веса
        weight_form = WeightForm(request.POST)
        if weight_form.is_valid():
            profile.weight = weight_form.cleaned_data["weight"]
            profile.last_weigh_in = timezone.now().date()
            profile.save()
            return redirect("home")
    else:
        # пустая форма для нового веса
        weight_form = WeightForm()
    diet = build_diet(profile)
    workout = get_workout(profile.goal)
    change = profile.weight_change()

    context = {
        "profile": profile,
        "change": change,
        "change_sign": "+" if change > 0 else "",
        "months": profile.months_passed(),
        # чтобы правильно писать месяц или месяцев и тд
        "months_word": months_text(profile.months_passed()),
        "targets": diet["targets"],
        "ration": diet["ration"],
        "total": diet["total"],
        "workout": workout,
        "weight_form": weight_form,
        # перезвесится надо раз в месяц
        "needs_weigh_in": profile.needs_weigh_in(),
    }
    return render(request, "main/home.html", context)


@login_required
def menu_view(request):
    # загружаем продукты если ее еще не пикали
    if not Product.objects.exists():
        for name, category, protein, fat, carbs, max_grams in BASE_PRODUCTS:
            Product.objects.create(
                name=name,
                category=category,
                protein=protein,
                fat=fat,
                carbs=carbs,
                max_grams=max_grams,
            )
    profile = request.user.profile
    # запоминаем старую цель на всякий если пользователь ее изменил)
    old_goal = profile.goal
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # сохраняем анкету но пока не записывая в базу
            profile = form.save(commit=False)
            if profile.goal != old_goal:
                # обнуляем прогресс
                profile.start_weight = profile.weight
                profile.start_date = timezone.now().date()
            profile.last_weigh_in = timezone.now().date()
            profile.save()
            # сохраняем выбранные продукты
            form.save_m2m()
            return redirect("home")
    # если не кликнул отправить то показываем форму с текущими данными
    else:
        form = ProfileForm(instance=profile)
    return render(request, "main/menu.html", {"form": form, "profile": profile})




