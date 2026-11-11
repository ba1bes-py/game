"""
НОЧНОЙ ЭКСПРЕСС
Текстовая детективная игра-новелла.

Сюжет: в ночном поезде «Северный экспресс» отравлен богатый промышленник
Аркадий Громов. Под подозрением пятеро пассажиров. Вы детектив, который
случайно оказался в соседнем вагоне. Поезд прибывает на станцию утром,
и у вас ограниченное число ходов, чтобы найти убийцу.

Уровни:
    1. Купе жертвы: осмотр места преступления, сбор улик.
    2. Допросы: разговоры с подозреваемыми, поиск противоречий.
    3. Вагон-ресторан и багажный вагон: шифр, загадка, противники, тайник.
    4. Разоблачение: обвинение и доказательства.

Используемые коллекции:
    список    - инвентарь, блокнот, список противников, история команд
    кортеж    - параметры уровней, координаты вагонов, хронология, алфавит
    множество - найденные улики, осмотренные объекты, допрошенные,
                разоблачённые, побеждённые противники
    словарь   - предметы и их описания, подозреваемые, объекты комнат,
                противники и их слабости, ячейки багажа, рецепт доказательств
"""

# =====================================================================
#                      КОНСТАНТЫ (КОРТЕЖИ)
# =====================================================================

MAX_TURNS = 160          # сколько ходов до прибытия поезда
WARNING_TURNS = (80, 120, 145)   # кортеж: когда предупреждать о времени

# Кортеж кортежей: (номер, название, задача уровня)
LEVELS = (
    (1, "Купе жертвы", "Осмотрите место преступления и соберите главные улики."),
    (2, "Допросы", "Допросите всех пассажиров и поймайте хотя бы троих на лжи."),
    (3, "Ресторан и багажный вагон", "Расшифруйте записку и найдите тайник убийцы."),
    (4, "Разоблачение", "Назовите убийцу и предъявите доказательства."),
)

# Словарь кортежей: вагон -> (номер вагона, место в составе)
TRAIN_MAP = {
    "локомотив": (0, "голова поезда"),
    "багажный вагон": (1, "сразу за локомотивом"),
    "вагон-ресторан": (2, "между багажным и спальными"),
    "спальный вагон №3 (купе Громова)": (3, "середина поезда"),
    "спальный вагон №4 (ваше купе)": (4, "хвост поезда"),
}

# Кортеж кортежей: известная хронология вечера
TIMELINE = (
    ("21:00", "Поезд отходит от столицы."),
    ("22:00", "Громов ужинает в своём купе."),
    ("01:15", "Проводник находит Громова мёртвым."),
)

# Алфавит для шифра Цезаря (без буквы Ё)
ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
SECRET_SHIFT = 6
SECRET_TEXT = "ЯЧЕЙКА СЕМЬ ПОД ЧЕРНЫМ ЧЕМОДАНОМ"

# =====================================================================
#                      ДАННЫЕ ИГРЫ (СЛОВАРИ)
# =====================================================================

# Все предметы: название -> описание и тип доказательства
ITEMS = {
    "бокал": {
        "desc": "Хрустальный бокал с остатками вина. Пахнет горьким миндалём.",
        "proof": "орудие",
    },
    "запонка": {
        "desc": "Серебряная запонка с гравировкой «Л.С.». Валялась под столиком.",
        "proof": "возможность",
    },
    "обрывок": {
        "desc": "Обрывок записки с бессмысленными буквами. Похоже на шифр.",
        "proof": None,
    },
    "ключ": {
        "desc": "Маленький латунный ключ от чемодана.",
        "proof": None,
    },
    "письмо": {
        "desc": ("Неотправленное письмо Громова в полицию: «Мой секретарь "
                 "Л. Сомов украл у компании 200 000 рублей. Завтра я его разоблачу»."),
        "proof": "мотив",
    },
    "расписка": {
        "desc": "Расписка графа Орлова: должен Громову 10 000 рублей.",
        "proof": None,
    },
    "платок": {
        "desc": "Шёлковый платок со следами помады и вышитыми буквами «В.Г.».",
        "proof": None,
    },
    "фонарь": {
        "desc": "Тяжёлый железнодорожный фонарь. Светит ярко.",
        "proof": None,
    },
    "счет": {
        "desc": ("Счёт из ресторана на имя Л. Сомова. Оплачен в 22:40, "
                 "хотя Сомов говорит, что сидел там до полуночи."),
        "proof": "возможность",
    },
    "сыр": {
        "desc": "Кусок пахучего сыра с кухни.",
        "proof": None,
    },
    "огнетушитель": {
        "desc": "Красный огнетушитель. Тяжёлый и шумный.",
        "proof": None,
    },
    "пузырек": {
        "desc": ("Аптечный пузырёк с надписью «Цианид калия. Д-р Белова». "
                 "Пустой."),
        "proof": "орудие",
    },
    "перчатки": {
        "desc": "Серые замшевые перчатки. На подкладке вышито «Л.С.».",
        "proof": "орудие",
    },
}

# Уровень 1: объекты купе
ROOM_COMPARTMENT = {
    "тело": {
        "desc": ("Аркадий Громов сидит в кресле, голова запрокинута. Губы "
                 "синеватые, следов борьбы нет. Похоже на отравление."),
        "items": [],
        "note": "Громов отравлен, скорее всего цианидом.",
        "needs": None,
    },
    "стол": {
        "desc": "На столике остатки ужина и бокал вина.",
        "items": ["бокал"],
        "note": None,
        "needs": None,
    },
    "кресло": {
        "desc": "Второе кресло, напротив жертвы. Здесь кто-то сидел.",
        "items": ["платок"],
        "note": "Вечером у Громова была гостья.",
        "needs": None,
    },
    "ковер": {
        "desc": "Под столиком на ковре что-то блестит.",
        "items": ["запонка"],
        "note": None,
        "needs": None,
    },
    "подушка": {
        "desc": "Под подушкой на полке что-то спрятано.",
        "items": ["ключ"],
        "note": None,
        "needs": None,
    },
    "корзина": {
        "desc": "В мусорной корзине скомканные бумажки.",
        "items": ["обрывок"],
        "note": None,
        "needs": None,
    },
    "чемодан": {
        "desc": "Кожаный чемодан Громова. Внутри документы.",
        "items": ["письмо", "расписка"],
        "note": "У Громова были бумаги, опасные для кого-то из пассажиров.",
        "needs": "ключ",
    },
    "окно": {
        "desc": "Окно закрыто на защёлку изнутри. Убийца вошёл через дверь.",
        "items": [],
        "note": "Убийца вошёл через дверь, окно закрыто изнутри.",
        "needs": None,
    },
}

# Улики, без которых нельзя покинуть купе (множество)
REQUIRED_LEVEL_1 = {"бокал", "запонка", "обрывок"}

# Уровень 2: подозреваемые
SUSPECTS = {
    "громова": {
        "name": "Вера Громова",
        "role": "жена погибшего",
        "alibi": "Я весь вечер спала у себя. С мужем не виделась с обеда.",
        "weak": "платок",
        "confession": ("Ладно... Я была у него в 22:00, мы поругались из-за "
                       "денег. Но когда я уходила в 22:30, он был жив и "
                       "кричал мне вслед!"),
        "note": "В 22:30 Громов был ещё жив (слова жены).",
    },
    "сомов": {
        "name": "Лев Сомов",
        "role": "личный секретарь",
        "alibi": "С десяти до полуночи я сидел в ресторане и разбирал бумаги.",
        "weak": "запонка",
        "confession": ("Да, это моя запонка... Я заходил около 23:00 отнести "
                       "документы. Аркадий Петрович дремал, я его не будил."),
        "note": "Сомов был в купе около 23:00 и соврал про алиби.",
    },
    "белова": {
        "name": "Ирина Белова",
        "role": "врач",
        "alibi": "Я весь вечер читала в купе. Ничего не видела.",
        "weak": "бокал",
        "confession": ("Миндаль... это цианид! Боже, вчера из моего саквояжа "
                       "пропал пузырёк с ядом. Я боялась признаться."),
        "note": "У доктора Беловой вчера украли пузырёк с цианидом.",
    },
    "орлов": {
        "name": "Граф Орлов",
        "role": "пассажир, картёжник",
        "alibi": "Всю ночь я играл в карты с проводником.",
        "weak": "расписка",
        "confession": ("Да, я должен ему. В 21:30 просил отсрочку, он отказал. "
                       "Но убивать? Мертвец долг не простит, он перейдёт "
                       "наследникам."),
        "note": "Орлов должен Громову, но смерть долг не отменяет.",
    },
    "степан": {
        "name": "Степан",
        "role": "проводник",
        "alibi": ("Играл с графом в карты до полуночи, потом обходил вагоны. "
                  "Около половины первого видел человека в сером пиджаке, "
                  "шёл в сторону багажного вагона. Возьмите фонарь, там "
                  "темно."),
        "weak": None,
        "confession": "",
        "note": "В 00:30 человек в сером пиджаке шёл к багажному вагону.",
    },
}

NEED_EXPOSED = 3   # сколько лжецов нужно разоблачить на уровне 2

# Уровень 3: вагон-ресторан
ROOM_RESTAURANT = {
    "бармен": {
        "desc": ("Пожилой бармен протирает стаканы. «Люблю загадки. Отгадаете "
                 "мою, подскажу что-нибудь полезное». (команда: загадка)"),
        "items": [],
    },
    "кухня": {
        "desc": "На кухне пахнет едой. На доске лежит кусок сыра.",
        "items": ["сыр"],
    },
    "стена": {
        "desc": "На стене висит огнетушитель.",
        "items": ["огнетушитель"],
    },
    "столик": {
        "desc": "Столик, за которым, по словам Сомова, он работал. Под солонкой счёт.",
        "items": ["счет"],
    },
}

RIDDLE = ("Сколько концов у двух с половиной палок?",
          ("6", "шесть"))   # кортеж: вопрос и верные ответы

# Противники багажного вагона: имя -> описание и слабость
ENEMIES = {
    "крыса": {
        "desc": "Огромная крыса шипит и не даёт пройти к ячейкам.",
        "weak": "сыр",
        "win": "Крыса хватает сыр и убегает в щель.",
        "damage": 3,
    },
    "громила": {
        "desc": ("Громила в кепке перекрывает проход. «Сюда нельзя. Мне "
                 "заплатили, чтобы никто не трогал ячейки»."),
        "weak": "огнетушитель",
        "win": ("Струя пены бьёт громиле в лицо, он падает и кричит: «Не бейте! "
                "Это всё тип в сером пиджаке, он заплатил!»"),
        "damage": 5,
    },
}

# Ячейки багажного вагона: номер -> содержимое
CELLS = {
    1: [], 2: [], 3: [], 4: [], 5: [],
    6: [], 7: ["пузырек", "перчатки"], 8: [], 9: [], 10: [],
}
CELL_JUNK = ("старые газеты", "пыльные шляпные коробки", "мешок картошки",
             "ящик с вилками", "пустые бутылки")

KILLER = "сомов"
PROOF_TYPES = {"мотив", "возможность", "орудие"}

# Синонимы команд: слово игрока -> команда игры
VERB_ALIASES = {
    "осмотреть": "осмотреть", "осм": "осмотреть", "посмотреть": "осмотреть",
    "обыскать": "осмотреть",
    "взять": "взять", "подобрать": "взять", "забрать": "взять",
    "изучить": "изучить", "что": "изучить",
    "использовать": "использовать", "исп": "использовать",
    "применить": "использовать",
    "допросить": "допросить", "поговорить": "допросить", "говорить": "допросить",
    "предъявить": "предъявить", "показать": "предъявить",
    "инвентарь": "инвентарь", "инв": "инвентарь", "и": "инвентарь",
    "блокнот": "блокнот", "улики": "блокнот", "заметки": "блокнот",
    "помощь": "помощь", "help": "помощь", "?": "помощь",
    "осмотреться": "осмотреться", "оглядеться": "осмотреться",
    "карта": "карта", "время": "время", "хронология": "хронология",
    "открыть": "открыть", "идти": "идти", "перейти": "идти", "пойти": "идти",
    "дальше": "дальше", "выйти": "дальше",
    "расшифровать": "расшифровать", "загадка": "загадка",
    "убежать": "убежать", "бежать": "убежать",
    "выход": "выход", "quit": "выход",
}


class GameOver(Exception):
    """Исключение для завершения игры."""


# =====================================================================
#                      СОСТОЯНИЕ ИГРОКА
# =====================================================================

def new_state():
    """Создаёт словарь с состоянием новой игры."""
    return {
        "name": "детектив",
        "inventory": [],          # список предметов
        "notebook": [],           # список записей
        "clues": set(),           # множество найденных улик
        "examined": set(),        # множество осмотренных объектов
        "interrogated": set(),    # кого допросили
        "exposed": set(),         # кого поймали на лжи
        "defeated": set(),        # побеждённые противники
        "opened_cells": set(),    # открытые ячейки
        "history": [],            # история команд
        "turn": 0,
        "health": 10,
        "level": 1,
        "riddle_solved": False,
        "decoded": False,
        "location": "ресторан",
    }


# =====================================================================
#                      ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =====================================================================

def line(char="=", width=64):
    print(char * width)


def title(text):
    print()
    line()
    print(text.center(64))
    line()


def normalize(text):
    """Приводит ввод к удобному виду."""
    return text.strip().lower().replace("ё", "е")


def match(word, key):
    """Сравнивает слово игрока с ключом, допуская разные окончания."""
    key = key.lower()
    if word == key:
        return True
    stem = key[:max(3, len(key) - 2)]
    return word.startswith(stem)


def find_key(arg, keys):
    """Ищет в строке arg слово, подходящее к одному из ключей."""
    for word in arg.split():
        for key in keys:
            if match(word, str(key)):
                return key
    return None


def split_command(text):
    """Разбивает команду на глагол и аргумент."""
    parts = text.split(maxsplit=1)
    if not parts:
        return "", ""
    verb = VERB_ALIASES.get(parts[0], parts[0])
    arg = parts[1] if len(parts) > 1 else ""
    return verb, arg


def ask(state, prompt="> "):
    """Получает команду от игрока, считает ходы."""
    try:
        raw = input(prompt)
    except EOFError:
        raise GameOver("Ввод закончился.")
    text = normalize(raw)
    if text:
        state["history"].append(text)
    return text


def tick(state, cost=1):
    """Тратит ходы и проверяет, не прибыл ли поезд."""
    state["turn"] += cost
    left = MAX_TURNS - state["turn"]
    for mark in WARNING_TURNS:
        if state["turn"] - cost < mark <= state["turn"]:
            print(f"\n  [Гудок поезда... До станции осталось {left} ходов.]")
    if left <= 0:
        print("\nПоезд прибывает на станцию. Пассажиры расходятся по перрону...")
        print("Убийца растворился в толпе. Дело осталось нераскрытым.")
        raise GameOver("time")


def add_item(state, item):
    """Добавляет предмет в инвентарь и, если это улика, в множество улик."""
    if item in state["inventory"]:
        return
    state["inventory"].append(item)
    if ITEMS[item]["proof"] is not None:
        state["clues"].add(item)
    print(f"  + {item.capitalize()} добавлен(а) в инвентарь.")


def add_note(state, note):
    """Записывает факт в блокнот (без повторов)."""
    if note and note not in state["notebook"]:
        state["notebook"].append(note)
        print(f"  [В блокноте: {note}]")


def show_inventory(state):
    if not state["inventory"]:
        print("Инвентарь пуст.")
        return
    print("Инвентарь:")
    for number, item in enumerate(state["inventory"], start=1):
        mark = " (улика)" if item in state["clues"] else ""
        print(f"  {number}. {item}{mark}")


def show_notebook(state):
    print("Блокнот детектива:")
    if not state["notebook"]:
        print("  пока пусто")
    for note in state["notebook"]:
        print(f"  • {note}")
    if state["clues"]:
        print("Улики:", ", ".join(sorted(state["clues"])))


def show_map(state):
    print("Схема поезда (от головы к хвосту):")
    for car, (number, place) in sorted(TRAIN_MAP.items(), key=lambda x: x[1][0]):
        print(f"  [{number}] {car} — {place}")


def show_timeline(state):
    print("Хронология:")
    for time, event in TIMELINE:
        print(f"  {time}  {event}")


def show_help(state):
    print("Общие команды:")
    print("  осмотреться            — что есть вокруг")
    print("  осмотреть <объект>     — внимательно изучить объект")
    print("  взять <предмет>        — взять предмет")
    print("  изучить <предмет>      — описание предмета из инвентаря")
    print("  инвентарь / блокнот    — ваши вещи и записи")
    print("  карта / хронология / время")
    print("  выход                  — закончить игру")
    level = state["level"]
    if level == 1:
        print("На этом уровне: открыть <объект>, дальше (покинуть купе)")
    elif level == 2:
        print("На этом уровне: допросить <имя>, предъявить <предмет> <имя>, дальше")
    elif level == 3:
        print("На этом уровне: идти ресторан/багаж, загадка, расшифровать,")
        print("  использовать <предмет>, убежать, открыть <номер ячейки>, дальше")


def describe_item(state, arg):
    item = find_key(arg, state["inventory"])
    if item is None:
        print("У вас нет такого предмета.")
        return
    print(f"{item.capitalize()}: {ITEMS[item]['desc']}")
    if ITEMS[item]["proof"]:
        print(f"  Может доказать: {ITEMS[item]['proof']}.")


def handle_common(state, verb, arg):
    """Обрабатывает команды, доступные на любом уровне.
    Возвращает True, если команда обработана."""
    commands = {
        "инвентарь": show_inventory,
        "блокнот": show_notebook,
        "помощь": show_help,
        "карта": show_map,
        "хронология": show_timeline,
    }
    if verb in commands:
        commands[verb](state)
        return True
    if verb == "время":
        print(f"Прошло ходов: {state['turn']}. До станции: {MAX_TURNS - state['turn']}.")
        return True
    if verb == "изучить":
        describe_item(state, arg)
        return True
    if verb == "выход":
        raise GameOver("quit")
    if verb == "":
        return True
    return False


def examine_object(state, room, arg):
    """Осмотр объекта в комнате-словаре."""
    key = find_key(arg, room.keys())
    if key is None:
        print("Здесь нет ничего такого. Наберите «осмотреться».")
        return
    tick(state)
    obj = room[key]
    if obj.get("needs") and obj["needs"] not in state["examined_opened"]:
        print(f"{key.capitalize()} заперт(а). Нужен предмет: {obj['needs']}.")
        return
    print(obj["desc"])
    state["examined"].add(key)
    if obj.get("note"):
        add_note(state, obj["note"])
    if obj["items"]:
        print("Здесь можно взять:", ", ".join(obj["items"]))


def take_item(state, room, arg):
    """Взять предмет из осмотренного объекта."""
    for key in state["examined"]:
        obj = room.get(key)
        if not obj:
            continue
        item = find_key(arg, obj["items"])
        if item:
            tick(state)
            obj["items"].remove(item)
            add_item(state, item)
            return
    print("Такого предмета рядом нет. Сначала осмотрите объекты.")


# =====================================================================
#                      ШИФР ЦЕЗАРЯ
# =====================================================================

def caesar(text, shift):
    """Сдвигает каждую букву текста по алфавиту."""
    result = []
    for ch in text.upper():
        if ch in ALPHABET:
            index = (ALPHABET.index(ch) + shift) % len(ALPHABET)
            result.append(ALPHABET[index])
        else:
            result.append(ch)
    return "".join(result)


ENCRYPTED = caesar(SECRET_TEXT, SECRET_SHIFT)


# =====================================================================
#                      УРОВЕНЬ 1: КУПЕ ЖЕРТВЫ
# =====================================================================

def level_1(state):
    title("УРОВЕНЬ 1. КУПЕ ЖЕРТВЫ")
    print("Час ночи. Проводник стучит в ваше купе: «Скорее! Господин Громов...")
    print("он мёртв!» Вы идёте в соседний вагон. Купе тесное, пахнет вином")
    print("и чем-то горьким. Дверь никто не трогал до вашего прихода.")
    print(f"\nЗадача: {LEVELS[0][2]}")
    print("Подсказка: начните с команды «осмотреться». «помощь» — все команды.")
    state["examined_opened"] = set()

    while True:
        verb, arg = split_command(ask(state))
        if handle_common(state, verb, arg):
            continue

        if verb == "осмотреться":
            print("В купе:", ", ".join(ROOM_COMPARTMENT.keys()))
        elif verb == "осмотреть":
            examine_object(state, ROOM_COMPARTMENT, arg)
        elif verb == "взять":
            take_item(state, ROOM_COMPARTMENT, arg)
        elif verb in ("открыть", "использовать"):
            target = find_key(arg, ROOM_COMPARTMENT.keys())
            uses_key = "ключ" in state["inventory"] and (
                target == "чемодан" or find_key(arg, ["ключ"]))
            if uses_key:
                tick(state)
                state["examined_opened"].add("ключ")
                print("Ключ подходит! Замок чемодана щёлкает.")
                print("Теперь можно «осмотреть чемодан».")
            elif target == "чемодан":
                print("Чемодан заперт. Где-то должен быть ключ.")
            else:
                print("Это нельзя открыть.")
        elif verb == "дальше":
            have = set(state["inventory"])
            missing = REQUIRED_LEVEL_1 - have
            if missing:
                print(f"Рано уходить. Не хватает важных улик: {len(missing)} шт.")
                print("Осмотрите купе внимательнее.")
            else:
                print("Вы собрали главные улики. Пора поговорить с пассажирами.")
                if "письмо" not in have:
                    print("(Вы не открыли чемодан. Возможно, зря.)")
                return
        else:
            print("Непонятная команда. Наберите «помощь».")


# =====================================================================
#                      УРОВЕНЬ 2: ДОПРОСЫ
# =====================================================================

def interrogate(state, arg):
    key = find_key(arg, SUSPECTS.keys())
    if key is None:
        print("Кого допросить? Подозреваемые:", ", ".join(SUSPECTS.keys()))
        return
    tick(state, 2)
    person = SUSPECTS[key]
    print(f"{person['name']} ({person['role']}):")
    print(f"  «{person['alibi']}»")
    state["interrogated"].add(key)
    if key == "степан":
        add_note(state, person["note"])
        if "фонарь" not in state["inventory"]:
            add_item(state, "фонарь")


def present(state, arg):
    item = find_key(arg, state["inventory"])
    suspect = find_key(arg, SUSPECTS.keys())
    if item is None or suspect is None:
        print("Формат: предъявить <предмет> <фамилия>. Например: предъявить бокал белова")
        return
    if suspect not in state["interrogated"]:
        print("Сначала допросите этого человека.")
        return
    tick(state)
    person = SUSPECTS[suspect]
    if suspect in state["exposed"]:
        print(f"{person['name']}: «Я уже всё рассказал(а)!»")
    elif person["weak"] == item:
        print(f"{person['name']} бледнеет при виде предмета «{item}».")
        print(f"  «{person['confession']}»")
        state["exposed"].add(suspect)
        add_note(state, person["note"])
    else:
        print(f"{person['name']} пожимает плечами: «Впервые вижу. При чём тут я?»")


def level_2(state):
    title("УРОВЕНЬ 2. ДОПРОСЫ")
    print("Проводник собрал всех пассажиров вагона в коридоре. Каждый")
    print("уверяет, что ни при чём. Но кто-то из них лжёт...")
    print(f"\nЗадача: {LEVELS[1][2]}")
    print("Команды: допросить <фамилия>, предъявить <предмет> <фамилия>, дальше")

    while True:
        verb, arg = split_command(ask(state))
        if handle_common(state, verb, arg):
            continue

        if verb == "осмотреться":
            print("В коридоре стоят:")
            for key, person in SUSPECTS.items():
                marks = []
                if key in state["interrogated"]:
                    marks.append("допрошен(а)")
                if key in state["exposed"]:
                    marks.append("пойман(а) на лжи")
                extra = f" [{', '.join(marks)}]" if marks else ""
                print(f"  {key}: {person['name']}, {person['role']}{extra}")
        elif verb == "допросить":
            interrogate(state, arg)
        elif verb == "предъявить":
            present(state, arg)
        elif verb == "дальше":
            not_asked = set(SUSPECTS.keys()) - state["interrogated"]
            if not_asked:
                print("Вы допросили не всех. Осталось:", ", ".join(sorted(not_asked)))
            elif len(state["exposed"]) < NEED_EXPOSED:
                print(f"Поймано лжецов: {len(state['exposed'])} из {NEED_EXPOSED}.")
                print("Предъявляйте предметы из инвентаря тем, кто врёт.")
            else:
                print("Картина проясняется. Проводник говорил про человека в")
                print("сером пиджаке... Стоит проверить вагон-ресторан и багаж.")
                return
        else:
            print("Непонятная команда. Наберите «помощь».")


# =====================================================================
#                 УРОВЕНЬ 3: РЕСТОРАН И БАГАЖНЫЙ ВАГОН
# =====================================================================

def ask_riddle(state):
    if state["location"] != "ресторан":
        print("Бармен остался в ресторане.")
        return
    if state["riddle_solved"]:
        print(f"Бармен: «Помните моё число? {SECRET_SHIFT}. Попробуйте его на шифре».")
        return
    question, answers = RIDDLE
    print(f"Бармен: «{question}»")
    answer = ask(state, "Ваш ответ: ")
    tick(state)
    if answer in answers:
        state["riddle_solved"] = True
        print("Бармен: «Верно! У половинки палки тоже два конца. Знаете, детектив,")
        print(f"шифровальщики любят сдвигать буквы. Попробуйте сдвиг {SECRET_SHIFT}».")
        add_note(state, f"Бармен намекнул: сдвиг шифра — {SECRET_SHIFT}.")
    else:
        print("Бармен качает головой: «Подумайте ещё. Половинка палки — тоже палка».")


def decode(state):
    if "обрывок" not in state["inventory"]:
        print("Вам нечего расшифровывать.")
        return
    if state["decoded"]:
        print(f"Записка уже расшифрована: {SECRET_TEXT}")
        return
    print(f"На обрывке: {ENCRYPTED}")
    answer = ask(state, "На сколько букв сдвинуть назад? ")
    tick(state)
    if not answer.isdigit():
        print("Нужно ввести число.")
        return
    text = caesar(ENCRYPTED, -int(answer))
    print(f"Получилось: {text}")
    if int(answer) == SECRET_SHIFT:
        state["decoded"] = True
        print("Это осмысленный текст! Тайник в багажном вагоне, ячейка 7.")
        add_note(state, "Записка: тайник в багажном вагоне, ячейка 7.")
    else:
        print("Бессмыслица. Попробуйте другой сдвиг.")


def active_enemies(state):
    """Список противников, которые ещё не побеждены."""
    return [name for name in ENEMIES if name not in state["defeated"]]


def go(state, arg):
    places = {"ресторан": "ресторан", "багаж": "багаж"}
    key = find_key(arg, places.keys())
    if key is None:
        print("Куда идти? Варианты: ресторан, багаж.")
        return
    if key == "багаж" and "фонарь" not in state["inventory"]:
        print("В багажном вагоне кромешная тьма. Без фонаря туда лучше не соваться.")
        return
    tick(state)
    state["location"] = key
    if key == "ресторан":
        print("Вагон-ресторан. Тихо играет граммофон.")
        print("Здесь:", ", ".join(ROOM_RESTAURANT.keys()))
    else:
        print("Багажный вагон. Луч фонаря выхватывает ряды пронумерованных ячеек 1–10.")
        enemies = active_enemies(state)
        for name in enemies:
            print(f"  ! {ENEMIES[name]['desc']}")
        if not enemies:
            print("Путь к ячейкам свободен.")


def use_item(state, arg):
    item = find_key(arg, state["inventory"])
    if item is None:
        print("У вас нет такого предмета.")
        return
    if state["location"] != "багаж":
        print("Здесь это ни к чему.")
        return
    enemies = active_enemies(state)
    if not enemies:
        print("Противников рядом нет.")
        return
    tick(state)
    for name in enemies:
        if ENEMIES[name]["weak"] == item:
            print(ENEMIES[name]["win"])
            state["defeated"].add(name)
            state["inventory"].remove(item)
            if name == "громила":
                add_note(state, "Громиле заплатил человек в сером пиджаке.")
            if not active_enemies(state):
                print("Путь к ячейкам свободен!")
            return
    # предмет не подошёл — противник атакует
    enemy = enemies[0]
    state["health"] -= ENEMIES[enemy]["damage"]
    print(f"Не сработало! {enemy.capitalize()} атакует. Здоровье: {state['health']}/10")
    check_health(state)


def check_health(state):
    if state["health"] <= 0:
        print("Вы теряете сознание... Очнулись вы уже на станции.")
        print("Убийца успел скрыться.")
        raise GameOver("health")


def run_away(state):
    if state["location"] != "багаж":
        print("Бежать не от кого.")
        return
    tick(state, 3)
    print("Вы отступаете в ресторан, переводя дыхание.")
    state["location"] = "ресторан"


def open_cell(state, arg):
    if state["location"] != "багаж":
        print("Ячейки находятся в багажном вагоне.")
        return
    enemies = active_enemies(state)
    if enemies:
        enemy = enemies[0]
        state["health"] -= ENEMIES[enemy]["damage"]
        print(f"{enemy.capitalize()} не подпускает вас к ячейкам! Здоровье: {state['health']}/10")
        check_health(state)
        return
    digits = "".join(ch for ch in arg if ch.isdigit())
    if not digits or int(digits) not in CELLS:
        print("Укажите номер ячейки от 1 до 10.")
        return
    number = int(digits)
    tick(state, 2)
    state["opened_cells"].add(number)
    content = CELLS[number]
    if content:
        print(f"Ячейка {number} под чёрным чемоданом! Внутри:")
        for item in list(content):
            add_item(state, item)
            content.remove(item)
    else:
        junk = CELL_JUNK[number % len(CELL_JUNK)]
        print(f"В ячейке {number}: {junk}. Ничего интересного.")


def level_3(state):
    title("УРОВЕНЬ 3. РЕСТОРАН И БАГАЖНЫЙ ВАГОН")
    print("Вы проходите в вагон-ресторан. Здесь, по словам Сомова, он провёл")
    print("весь вечер. Дальше по составу тёмный багажный вагон.")
    print(f"\nЗадача: {LEVELS[2][2]}")
    print("Команды: идти ресторан/багаж, загадка, расшифровать, открыть <номер>,")
    print("использовать <предмет>, убежать, дальше")
    state["location"] = "ресторан"
    examined_here = set()

    while True:
        verb, arg = split_command(ask(state))
        if handle_common(state, verb, arg):
            continue

        if verb == "осмотреться":
            if state["location"] == "ресторан":
                print("В ресторане:", ", ".join(ROOM_RESTAURANT.keys()))
            else:
                print("Ячейки 1–10. Открыто:", sorted(state["opened_cells"]) or "ничего")
                for name in active_enemies(state):
                    print(f"  ! {ENEMIES[name]['desc']}")
        elif verb == "осмотреть":
            if state["location"] != "ресторан":
                print("В темноте видны только ячейки. Наберите «осмотреться».")
                continue
            key = find_key(arg, ROOM_RESTAURANT.keys())
            if key is None:
                print("Здесь нет такого. Наберите «осмотреться».")
                continue
            tick(state)
            examined_here.add(key)
            print(ROOM_RESTAURANT[key]["desc"])
            if ROOM_RESTAURANT[key]["items"]:
                print("Можно взять:", ", ".join(ROOM_RESTAURANT[key]["items"]))
        elif verb == "взять":
            if state["location"] != "ресторан":
                print("Здесь нечего брать.")
                continue
            taken = False
            for key in examined_here:
                item = find_key(arg, ROOM_RESTAURANT[key]["items"])
                if item:
                    tick(state)
                    ROOM_RESTAURANT[key]["items"].remove(item)
                    add_item(state, item)
                    if item == "счет":
                        add_note(state, "Сомов оплатил ужин в 22:40, а не сидел до полуночи.")
                    taken = True
                    break
            if not taken:
                print("Такого предмета рядом нет. Сначала осмотрите объекты.")
        elif verb == "идти":
            go(state, arg)
        elif verb == "загадка":
            ask_riddle(state)
        elif verb == "расшифровать":
            decode(state)
        elif verb == "использовать":
            use_item(state, arg)
        elif verb == "убежать":
            run_away(state)
        elif verb == "открыть":
            open_cell(state, arg)
        elif verb == "дальше":
            if "пузырек" in state["inventory"]:
                print("У вас есть орудие убийства. Пора собрать всех и назвать убийцу!")
                return
            print("Вы ещё не нашли тайник убийцы.")
        else:
            print("Непонятная команда. Наберите «помощь».")


# =====================================================================
#                      УРОВЕНЬ 4: РАЗОБЛАЧЕНИЕ
# =====================================================================

def level_4(state):
    title("УРОВЕНЬ 4. РАЗОБЛАЧЕНИЕ")
    print("Все пассажиры собрались в вагоне-ресторане. Поезд замедляет ход:")
    print("до станции считанные минуты. Все смотрят на вас.")
    print(f"\nЗадача: {LEVELS[3][2]}")
    print("\nПодозреваемые:")
    for key, person in SUSPECTS.items():
        print(f"  {key}: {person['name']}, {person['role']}")
    print("\nМожно посмотреть «блокнот» и «инвентарь» перед обвинением.")

    while True:
        text = ask(state, "Кто убийца? (фамилия) > ")
        verb, arg = split_command(text)
        if verb in ("инвентарь", "блокнот", "помощь", "хронология", "карта", "изучить"):
            handle_common(state, verb, arg)
            continue
        if verb == "выход":
            raise GameOver("quit")
        accused = find_key(text, SUSPECTS.keys())
        if accused:
            break
        print("Назовите фамилию одного из подозреваемых.")

    print(f"\nВы указываете на: {SUSPECTS[accused]['name']}.")
    print("Предъявите доказательства через запятую (например: бокал, письмо).")
    show_inventory(state)
    raw = ask(state, "Доказательства > ")
    chosen = set()
    for part in raw.split(","):
        item = find_key(part, state["inventory"])
        if item:
            chosen.add(item)

    # что доказывает каждая улика: мотив, возможность, орудие
    proven = {ITEMS[item]["proof"] for item in chosen if ITEMS[item]["proof"]}
    return accused, chosen, proven


def ending(state, accused, chosen, proven):
    title("ФИНАЛ")
    score = 0
    if accused == KILLER:
        score += 50
        score += 15 * len(proven & PROOF_TYPES)
        missing = PROOF_TYPES - proven
        if not missing:
            print("«Лев Сомов! Громов узнал о ваших махинациях и собирался")
            print("сдать вас полиции. Это ваш мотив, вот письмо. Вчера вы украли")
            print("цианид из саквояжа доктора Беловой. В 23:00 вы пришли в купе")
            print("под предлогом документов и подлили яд в бокал. Ваша запонка")
            print("осталась под столом, а счёт доказывает, что вы ушли из")
            print("ресторана в 22:40. Пузырёк и перчатки вы спрятали в ячейке 7")
            print("и заплатили громиле за охрану».")
            print("\nСомов опускает голову: «Он бы меня уничтожил...»")
            print("На станции его уже ждёт полиция. ДЕЛО РАСКРЫТО!")
        else:
            print("Вы правы, это Сомов, но доказательств мало.")
            print("Не доказано:", ", ".join(sorted(missing)))
            print("Адвокат Сомова разбивает обвинение в суде. Убийца на свободе,")
            print("хотя все знают правду...")
    else:
        person = SUSPECTS[accused]
        print(f"{person['name']} в ужасе: «Это не я!»")
        print("Полиция арестовывает невиновного. А Лев Сомов, поправив серый")
        print("пиджак, спокойно выходит на перрон и исчезает навсегда.")
        print("ДЕЛО ПРОВАЛЕНО.")

    # бонусы за внимательность
    score += 5 * len(state["exposed"])
    score += max(0, (MAX_TURNS - state["turn"]) // 4)
    if state["decoded"]:
        score += 10
    print()
    line("-")
    print(f"Ходов потрачено: {state['turn']} из {MAX_TURNS}")
    print(f"Поймано лжецов: {len(state['exposed'])}, улик найдено: {len(state['clues'])}")
    print(f"Итоговый счёт: {score}")
    line("-")
    return score


# =====================================================================
#                      ГЛАВНАЯ ФУНКЦИЯ
# =====================================================================

def intro(state):
    title("НОЧНОЙ ЭКСПРЕСС")
    print("Детективная текстовая игра\n")
    name = input("Как вас зовут, детектив? > ").strip()
    if name:
        state["name"] = name
    print(f"\nДобро пожаловать, детектив {state['name']}.")
    print("Вы едете в отпуск ночным поездом «Северный экспресс».")
    print("Но отдохнуть, кажется, не получится...")
    print(f"\nУ вас {MAX_TURNS} ходов до прибытия поезда на станцию.")
    print("Почти каждое действие тратит ход. Не теряйте времени!")


def main():
    state = new_state()
    try:
        intro(state)
        level_1(state)
        state["level"] = 2
        level_2(state)
        state["level"] = 3
        level_3(state)
        state["level"] = 4
        accused, chosen, proven = level_4(state)
        ending(state, accused, chosen, proven)
    except GameOver as reason:
        if str(reason) == "quit":
            print("Вы закрываете блокнот. Может, в другой раз...")
        print("\nИГРА ОКОНЧЕНА.")
    except KeyboardInterrupt:
        print("\nИгра прервана.")
    print("Спасибо за игру!")


if __name__ == "__main__":
    main()
