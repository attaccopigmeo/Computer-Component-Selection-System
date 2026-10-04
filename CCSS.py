from dataclasses import dataclass
from typing import Callable


# Факты предметной области

@dataclass
class Fact:
    name: str
    value: object


# Шаблон проектирования (декоратор) продукционного правила

def Rule(rule_id: str, name: str):
    def decorator(func: Callable):
        func.rule_id = rule_id
        func.rule_name = name
        return func
    return decorator


# Ядро системы

class System:
    def __init__(self):
        self.facts = {}
        self.fired_rules = []
        self.rules = [
            self.determine_profile,
            self.select_build,
            self.check_socket,
            self.check_ram,
            self.check_power,
            self.check_budget,
            self.make_recommendation,
        ]

        # Демонстрационный каталог комплектующих (цены могут не соответствовать рыночным)
        self.builds = [
            {
                "name": "Офисная сборка",
                "profile": "office",
                "price": 45000,
                "cpu": "Intel Core i5-12400",
                "socket": "LGA 1700",
                "motherboard_socket": "LGA 1700",
                "ram_type": "DDR4",
                "motherboard_ram": "DDR4",
                "ram_gb": 16,
                "gpu": "Встроенная графика",
                "power": 550,
                "required_power": 450,
            },
            {
                "name": "Учебная сборка",
                "profile": "study",
                "price": 60000,
                "cpu": "Intel Core i5-12400F",
                "socket": "AM4",
                "motherboard_socket": "AM4",
                "ram_type": "DDR4",
                "motherboard_ram": "DDR4",
                "ram_gb": 16,
                "gpu": "GeForce RTX 3060",
                "power": 550,
                "required_power": 450,
            },
            {
                "name": "Игровая сборка",
                "profile": "gaming",
                "price": 400000,
                "cpu": "AMD Ryzen 7 9800X3D",
                "socket": "AM5",
                "motherboard_socket": "AM5",
                "ram_type": "DDR5",
                "motherboard_ram": "DDR5",
                "ram_gb": 64,
                "gpu": "GeForce RTX 5090",
                "power": 1500,
                "required_power": 1200,
            },
        ]

    def add_fact(self, name, value):
        self.facts[name] = Fact(name, value)

    def get(self, name, default=None):
        fact = self.facts.get(name)
        return fact.value if fact else default

    def run(self):
        """ Повторяем проходы, пока срабатывают новые правила. 
        Это позволяет использовать вывод одного правила как входные данные для следующего."""
        while True:
            changed = False

            for rule in self.rules:
                if rule.rule_id in self.fired_rules:
                    continue # Пропускаем сработавшие правила

                if rule():
                    self.fired_rules.append(rule.rule_id)
                    changed = True
            if not changed:
               break

        self.show_results()

    # Правило R01

    @Rule("R01", "Определение назначения компьютера")
    def determine_profile(self):
        purpose = self.get("purpose")

        if not purpose:
            return False

        if purpose == "игры":
            profile = "gaming"
        elif purpose == "учёба":
            profile = "study"
        else:
            profile = "office"

        self.add_fact("profile", profile)
        print(f"[R01] Определено назначение компьютера: {profile}")
        return True

    # Правило R02

    @Rule("R02", "Подбор конфигурации по назначению и бюджету")
    def select_build(self):
        profile = self.get("profile")
        budget = self.get("budget")

        if profile is None or budget is None:
            return False

        """"Исправление по результатам проверки:
        выбираем самую подходящую сборбку, которая укладывается в бюджет,
        а не просто перрвый вариант из каталога."""
        priority = {
            "office": ["office", "study", "gaming"],
            "study": ["study", "office", "gaming"],
            "gaming": ["gaming", "study", "office"],
        }

        candidates = [
            build for build in self.builds
            if build["price"] <= budget
        ]

        if not candidates:
            self.add_fact("selected_build", None)
            self.add_fact("budget_issue", True)
            print("[R02] Бюджета недостаточно для доступных сборок")
            return True

        candidates.sort(
                key=lambda build: priority[profile].index(build["profile"])
            )

        build = candidates[0]
        self.add_fact("selected_build", build)
        self.add_fact("budget_issue", build["profile"] != profile)

        print("[R02] Выбрана сборка:", build["name"])
        return True

    # Правило R03

    @Rule("R03", "Проверка сокета процессора")
    def check_socket(self):
        build = self.get("selected_build")

        if build is None:
            return False

        compatible = build["socket"] == build["motherboard_socket"]
        self.add_fact("socket_ok", compatible)

        if not compatible:
            print("[R03] Ошибка: сокеты процессора и платы различаются")
        else:
            print("[R03] Сокет процессора и платы совместим")

        return True

    # Правило R04

    @Rule("R04", "Проверка типа оперативной памяти")
    def check_ram(self):
        build = self.get("selected_build")

        if build is None:
            return False

        compatible = build["ram_type"] == build["motherboard_ram"]
        self.add_fact("ram_ok", compatible)

        if not compatible:
            print("[R04] Ошибка: тип RAM не поддерживается платой")
        else:
            print("[R04] Тип оперативной памяти совместим")

        return True

    # Правило R05

    @Rule("R05", "Проверка мощности блока питания")
    def check_power(self):
        build = self.get("selected_build")

        if build is None:
            return False

        compatible = build["power"] >= build["required_power"]
        self.add_fact("power_ok", compatible)

        if not compatible:
            print("[R05] Ошибка: недостаточная мощность БП")
        else:
            print("[R05] Мощности блока питания достаточно")

        return True

        # Правило R06

    @Rule("R06", "Проверка соответствия бюджету")
    def check_budget(self):
        build = self.get("selected_build")

        if build is None:
            self.add_fact("within_budget", False)
            return True

        within_budget = build["price"] <= self.get("budget")
        self.add_fact("within_budget", within_budget)

        print(
            "[R06] Сборка укладывается в бюджет"
            if within_budget
            else "[R06] Сборка превышает бюджет"
        )
        return True

    # Правило R07

    @Rule("R07", "Формирование итоговой рекомендации")
    def make_recommendation(self):
        # Ждём завершения проверок совместимости.
        if self.get("selected_build") is not None:
            if self.get("socket_ok") is None:
                return False
            if self.get("ram_ok") is None:
                return False
            if self.get("power_ok") is None:
                return False
            if self.get("within_budget") is None:
                return False

        build = self.get("selected_build")

        if build is None:
            recommendation = (
                "Увеличьте бюджет или пересмотрите требования."
            )
        elif not all([
            self.get("socket_ok"),
            self.get("ram_ok"),
            self.get("power_ok"),
            self.get("within_budget"),
        ]):
            recommendation = (
                "Сборка требует замены несовместимых комплектующих."
            )
        elif self.get("budget_issue"):
            recommendation = (
                "Сборка совместима, но для выбранного назначения "
                "может потребоваться более производительная конфигурация."
            )
        else:
            recommendation = "Конфигурация подходит под заданные условия."

        self.add_fact("recommendation", recommendation)
        print("[R07] Итоговая рекомендация сформирована")
        return True

    # Вывод результатов

    def show_results(self):
        print("\n" + "=" * 45)
        print("РЕЗУЛЬТАТ РАБОТЫ ЭКСПЕРТНОЙ СИСТЕМЫ")
        print("=" * 45)

        build = self.get("selected_build")

        if build:
            print("Сборка:", build["name"])
            print("Процессор:", build["cpu"])
            print("Видеокарта:", build["gpu"])
            print("Оперативная память:", build["ram_gb"], "ГБ")
            print("Блок питания:", build["power"], "Вт")
            print("Стоимость:", f'{build["price"]:,}'.replace(",", " "), "руб.")
        else:
            print("Подходящая сборка в заданном бюджете не найдена.")

        print("\nРекомендация:")
        print(self.get("recommendation", "Недостаточно данных."))

        print("\nСработавшие правила:")
        for rule_id in self.fired_rules:
            rule = next(
                rule for rule in self.rules
                if rule.rule_id == rule_id
            )
            print(f"- {rule_id}: {rule.rule_name}")


# Запуск программы

def main():
    print("СИСТЕМА ПОДБОРА КОМПЬЮТЕРНЫХ КОМПЛЕКТУЮЩИХ")
    print("Укажите бюджет и назначение компьютера.\n")

    while True:
        try:
            budget = int(input("Ваш бюджет в рублях: "))
            if budget <= 0:
                print("Бюджет должен быть положительным.")
                continue
            break
        except ValueError:
            print("Введите целое число.")

    print("\nНазначение:")
    print("1 — Офис")
    print("2 — Учёба")
    print("3 — Игры")

    choices = {
        "1": "офис",
        "2": "учёба",
        "3": "игры",
    }

    while True:
        choice = input("Выберите вариант (1–3): ").strip()
        if choice in choices:
            break
        print("Введите 1, 2 или 3.")

    system = System()
    system.add_fact("budget", budget)
    system.add_fact("purpose", choices[choice])
    system.run()


if __name__ == "__main__":
    main()