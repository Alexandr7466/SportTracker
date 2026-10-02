from .models import Product

# название, категория, белки, жиры, углеводы на 100 г, максимум граммов в день
BASE_PRODUCTS = [
    ("Куриная грудка", "protein", 23.0, 1.9, 0.0, 400),
    ("Говядина", "protein", 20.0, 12.0, 0.0, 300),
    ("Свинина", "protein", 19.0, 21.0, 0.0, 250),
    ("Индейка", "protein", 21.0, 8.0, 0.0, 400),
    ("Яйца куриные", "protein", 12.7, 10.9, 0.7, 200),
    ("Творог 5%", "protein", 17.0, 5.0, 3.0, 400),
    ("Молоко 2.5%", "protein", 2.9, 2.5, 4.7, 500),
    ("Кефир 1%", "protein", 3.0, 1.0, 4.0, 500),
    ("Сыр твёрдый", "protein", 25.0, 30.0, 0.0, 80),
    ("Треска", "protein", 17.0, 0.7, 0.0, 400),
    ("Лосось", "protein", 20.0, 13.0, 0.0, 250),
    ("Креветки", "protein", 22.0, 1.0, 0.0, 300),
    ("Тунец консервированный", "protein", 23.0, 1.0, 0.0, 200),
    ("Протеин сывороточный", "protein", 75.0, 5.0, 8.0, 60),
    ("Соевое мясо", "protein", 52.0, 1.0, 20.0, 150),

    ("Рис белый", "carb", 7.0, 0.7, 77.0, 250),
    ("Гречка", "carb", 12.6, 3.3, 62.0, 250),
    ("Овсянка", "carb", 12.0, 6.0, 60.0, 150),
    ("Макароны", "carb", 11.0, 1.3, 71.0, 250),
    ("Картофель", "carb", 2.0, 0.4, 17.0, 600),
    ("Хлеб цельнозерновой", "carb", 9.0, 3.0, 45.0, 200),
    ("Фасоль варёная", "carb", 8.0, 0.5, 21.0, 400),
    ("Чечевица", "carb", 24.0, 1.5, 46.0, 200),
    ("Булгур", "carb", 12.0, 1.3, 63.0, 250),
    ("Кускус", "carb", 13.0, 0.6, 72.0, 250),

    ("Оливковое масло", "fat", 0.0, 100.0, 0.0, 40),
    ("Подсолнечное масло", "fat", 0.0, 100.0, 0.0, 40),
    ("Сливочное масло", "fat", 0.5, 82.0, 0.8, 30),
    ("Грецкие орехи", "fat", 15.0, 65.0, 7.0, 60),
    ("Миндаль", "fat", 21.0, 50.0, 22.0, 60),
    ("Арахисовая паста", "fat", 25.0, 50.0, 20.0, 60),
    ("Авокадо", "fat", 2.0, 15.0, 9.0, 200),
    ("Семена льна", "fat", 18.0, 42.0, 29.0, 40),

    ("Огурцы", "veg", 0.8, 0.1, 2.5, 300),
    ("Помидоры", "veg", 1.1, 0.2, 3.7, 300),
    ("Капуста", "veg", 1.8, 0.1, 4.7, 300),
    ("Брокколи", "veg", 3.0, 0.4, 5.0, 300),
    ("Морковь", "veg", 1.3, 0.1, 7.0, 300),
    ("Яблоки", "veg", 0.4, 0.4, 10.0, 300),
    ("Бананы", "veg", 1.5, 0.2, 21.0, 300),
    ("Апельсины", "veg", 0.9, 0.2, 8.1, 300),
    ("Салат листовой", "veg", 1.4, 0.2, 2.0, 300),
]

# это про кбжу
def calc_targets(profile):
    weight = profile.weight
    if profile.gender == "male":
        coef = 31
    else:
        coef = 28
    maint = weight * coef
    # После 30 лет обмен веществ немного замедляется, поэтому вычитаем по 5 ккал за каждый год свыше 30
    if profile.age > 30:
        maintenance = maint - (profile.age - 30) * 5
    if profile.goal == "mass":
        calories = maint + 350
        protein = weight * 2.0
        fat = weight
    else:
        calories = maint - 400
        protein = weight * 2.2
        fat = weight * 0.9
    carbs = (calories - protein * 4 - fat * 9) / 4

    if carbs < 50:
        carbs = 50
    # Возвращаем словарь со всеми посчитанными значениями, округлёнными до целых
    return {
        "calories": round(calories),
        "protein": round(protein),
        "fat": round(fat),
        "carbs": round(carbs),
    }

# products - список продуктов, need - сколько граммов нутриента надо набрать
# nutrient - название нутриента
def spread(products, need, nutrient):
    rows = []
    for index, product in enumerate(products):
        if need <= 0:
            break
        products_left = len(products)-index
        part = need / products_left
        # сколько этого нутриента в 100 граммах продукта который щас в цикле
        per_100 = getattr(product, nutrient)
        if per_100 <= 0:
            continue
        # считаем сколько грам этого продукта надо кушать
        grams = part / per_100 * 100
        if grams > product.max_grams:
            grams = product.max_grams
        if grams == 0:
            continue

        row = make_row(product, int(grams))
        rows.append(row)
        need = need - row[nutrient]
    return rows, need


# строит дневной рацион тоесть какие продукты и в каком количестве есть
def build_diet(profile):
    targets = calc_targets(profile)
    # продукты которые пикнули в анкете
    chosen = list(profile.products.all())
    protein_products = [p for p in chosen if p.category == "protein"]
    fat_products = [p for p in chosen if p.category == "fat"]
    carb_products = [p for p in chosen if p.category == "carb"]
    veg_products = [p for p in chosen if p.category == "veg"]

    # овощи и фрукты всегда 400 граммов в день
    veg_rows = []
    # если вообще пикали
    if veg_products:
        part = 400 / len(veg_products)
        for p in veg_products:
            # Если часть больше максимума продукта, ограничиваем максимумом
            g = part
            if part > p.max_grams:
                g = p.max_grams
            g = int(g)
            veg_rows.append(make_row(p, g))

    protein_rows, _ = spread(protein_products, targets["protein"] - sum(row["protein"] for row in veg_rows), "protein")

    fat_rows, _ = spread(fat_products, targets["fat"] - sum(row["fat"] for row in veg_rows) - sum(row["fat"] for row in protein_rows), "fat")

    carb_rows, _ = spread(carb_products, targets["carbs"] - sum(row["carbs"] for row in veg_rows) + sum(row["carbs"] for row in protein_rows) + sum(row["carbs"] for row in fat_rows), "carbs")

    # весь рацион
    ration = protein_rows + carb_rows + fat_rows + veg_rows

    total = {
        "protein": round(sum(row["protein"] for row in ration)),
        "fat": round(sum(row["fat"] for row in ration)),
        "carbs": round(sum(row["carbs"] for row in ration)),
        "calories": round(sum(row["calories"] for row in ration)),
    }
    return {"targets": targets, "ration": ration, "total": total}


def make_row(product, grams):
    # ретурним словарь с граммами и посчитанным бжу на эти граммы
    return {
        "name": product.name,
        "grams": grams,
        "protein": round(product.protein * grams / 100, 1),
        "fat": round(product.fat * grams / 100, 1),
        "carbs": round(product.carbs * grams / 100, 1),
        "calories": round(product.calories() * grams / 100),
    }


#програма для набора массы фул боди
WORKOUT_MASS = [
    ("Приседания со штангой", "4 подхода по 8 повторений", "Отдых 2 минуты между подходами"),
    ("Жим штанги лёжа", "4 подхода по 8 повторений", "Локти под углом 45 градусов"),
    ("Тяга штанги в наклоне", "4 подхода по 8 повторений", "Спина прямая"),
    ("Жим гантелей стоя", "3 подхода по 10 повторений", "Не прогибай поясницу"),
    ("Румынская тяга", "3 подхода по 10 повторений", "Работают задняя поверхность бедра и ягодицы"),
    ("Подтягивания или тяга верхнего блока", "3 подхода по 8 повторений", "Можно с резинкой"),
    ("Планка", "3 подхода по 45 секунд", "Держи корпус в одну линию"),
]

# Программа для похудения
WORKOUT_LOSS = [
    ("Приседания с гантелями", "4 подхода по 15 повторений", "Отдых 60 секунд между подходами"),
    ("Отжимания от пола", "4 подхода по 15 повторений", "Можно с колен, если тяжело"),
    ("Тяга гантели в наклоне", "4 подхода по 15 повторений", "По 15 раз на каждую руку"),
    ("Выпады на месте", "3 подхода по 12 повторений", "По 12 раз на каждую ногу"),
    ("Жим гантелей стоя", "3 подхода по 15 повторений", "Вес небольшой, темп ровный"),
    ("Планка", "3 подхода по 60 секунд", "Держи корпус в одну линию"),
    ("Кардио: быстрая ходьба или велосипед", "20-30 минут", "Сразу после силовой части"),
]


def get_workout(goal):
    if goal == "mass":
        return WORKOUT_MASS
    return WORKOUT_LOSS