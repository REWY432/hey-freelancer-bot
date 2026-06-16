"""
GitHub Actions content poster for @hey_freelancer
Uses pre-written content banks — no external API needed.
Rotates through tips, tools, stats, cases based on day of week.
"""
import urllib.request, json, os, sys, random
from datetime import datetime, timezone, timedelta

MOSCOW_TZ = timezone(timedelta(hours=3))
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not set"); sys.exit(1)
CHANNEL = "@hey_freelancer"

CONTENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_index.json")

# ===== CONTENT BANKS =====
TIPS = [
    ("Всегда бери предоплату 30-50%. Это фильтрует несерьёзных заказчиков и даёт тебе уверенность в проекте. Если клиент отказывается — скорее всего, он и не собирался платить.",
     "https://habr.com/ru/articles/"),
    ("Не работай без ТЗ. Даже для маленького заказа — задокументируй объём, сроки и цену. Это спасёт тебя от «а я думал…» и бесконечных правок.",
     "https://habr.com/ru/articles/"),
    ("Повышай цены раз в полгода. Серьёзно. Если ты растёшь как специалист — твой чек тоже должен расти. Клиенты, которые ценят качество, останутся.",
     "https://vc.ru/"),
    ("Один довольный клиент приводит двух новых. Сарафанное радио — лучший источник заказов для фрилансера. Делай чуть больше, чем обещал.",
     "https://vc.ru/"),
    ("Разделяй рабочее и личное время. Фриланс ≠ работа 24/7. Поставь границы: с 10 до 18 ты на связи, вечером — твоя жизнь. Выгорание реально.",
     "https://habr.com/ru/articles/"),
    ("Веди учёт финансов с первого дня. Таблица доходов/расходов, налоги, отчисления. Фрилансер без финансовой дисциплины — это кассир без кассы.",
     "https://habr.com/ru/articles/"),
    ("Не бери заказы «на подумать». Если клиент говорит «сделай демку, а там посмотрим» — вежливо откажись. Твоё время стоит денег.",
     "https://vc.ru/"),
    ("Создай портфолио из 3-5 лучших работ. Не количества — качества. Один сильный кейс продаёт лучше, чем 20 посредственных.",
     "https://habr.com/ru/articles/"),
    ("Учись говорить «нет». Самый недооценённый навык фрилансера. Плохой заказ отнимает время, которое ты мог бы потратить на хороший.",
     "https://vc.ru/"),
    ("Автоматизируй рутину. Шаблоны договоров, типовые ответы, автоинвойсы — всё что повторяется, должно делаться за минуту. Это освобождает часы.",
     "https://habr.com/ru/articles/"),
    ("Прокачивай личный бренд. Веди Telegram-канал или блог о своей нише. Когда заказчики приходят к тебе, а не ты к ним — ты диктуешь условия.",
     "https://vc.ru/"),
    ("Делай ревью своих проектов раз в квартал. Что получилось? Где просел по деньгам? Какие клиенты отняли больше всего нервов? Анализируй и корректируй.",
     "https://habr.com/ru/articles/"),
]

TOOLS = [
    ("<b>Tilda</b> — конструктор сайтов. Идеален для лендингов и портфолио. Без кода, быстро, красиво. Бесплатный тариф есть.",
     "https://tilda.cc/"),
    ("<b>Figma</b> — макеты, прототипы, дизайн-системы. Бесплатно для одного пользователя. Стандарт индустрии.",
     "https://www.figma.com/"),
    ("<b>Notion</b> — база знаний, трекер проектов, CRM для фрилансера. Один инструмент для всего.",
     "https://www.notion.so/"),
    ("<b>ClickUp</b> — управление проектами. Доски, списки, тайм-трекинг. Мощнее Trello, удобнее Asana.",
     "https://clickup.com/"),
    ("<b>Toggl Track</b> — трекер времени. Узнай куда уходит твой день и выставляй счета с точностью до минуты.",
     "https://toggl.com/"),
    ("<b>Grammarly</b> — проверка грамматики для англоязычных текстов. Must-have для копирайтеров и переводчиков.",
     "https://www.grammarly.com/"),
    ("<b>Remove.bg</b> — удаление фона за секунду. Экономит часы дизайнерам и контент-мейкерам.",
     "https://www.remove.bg/"),
    ("<b>Canva</b> — графика и дизайн без навыков. Шаблоны для соцсетей, презентации, визуал для клиентов.",
     "https://www.canva.com/"),
    ("<b>Miro</b> — онлайн-доска. Майнд-карты, брейнштормы, схемы проектов. Удобно для обсуждения с заказчиком.",
     "https://miro.com/"),
    ("<b>Obsidian</b> — заметки с графом связей. Локально, быстро, бесконечная канва для мыслей фрилансера.",
     "https://obsidian.md/"),
]

STATS = [
    ("По данным исследования FL.ru (2025), <b>62% фрилансеров</b> в России зарабатывают более 50 000 ₽ в месяц. При этом топ-10% — более 200 000 ₽.",
     "https://habr.com/ru/articles/"),
    ("Средний чек фрилансера в IT вырос на <b>18% за год</b>. Разработка, дизайн и маркетинг — топ-3 по доходности.",
     "https://vc.ru/"),
    ("<b>43% заказчиков</b> ищут фрилансеров через Telegram-каналы. Биржи отходят на второй план.",
     "https://habr.com/ru/articles/"),
    ("Самая высокооплачиваемая ниша на фрилансе в 2026 — <b>AI/ML интеграции</b>. Средний чек проекта: 150 000–500 000 ₽.",
     "https://vc.ru/"),
    ("<b>71% фрилансеров</b> начинали без портфолио. Главное — первые 3-5 проектов и отзывы.",
     "https://habr.com/ru/articles/"),
    ("Спрос на <b>Telegram-ботов</b> вырос на 340% с 2024 года. Нативная разработка, Mini Apps, крипто-боты — золотая жила.",
     "https://vc.ru/"),
]

CASES = [
    ("<b>От 0 до 200 000 ₽/мес за год:</b> Дизайнер из Новосибирска начал с заказов на 3000 ₽. Через год вышел на международных клиентов через Behance. Ключевой совет: «Первые 3 месяца работал за отзывы — это дало портфолио».",
     "https://habr.com/ru/articles/"),
    ("<b>Копирайтер на 150К:</b> Уволилась с работы в офисе (40К), завела Telegram-канал о копирайтинге. Через 8 месяцев — очередь из клиентов. «Канал заменил мне и резюме, и портфолио».",
     "https://vc.ru/"),
    ("<b>Разработчик Python — 500К/мес:</b> Специализировался только на парсинге и автоматизации. Узкая ниша → мало конкурентов → высокие чеки. «Не будь универсалом, будь лучшим в одном».",
     "https://habr.com/ru/articles/"),
    ("<b>SMM-менеджер — 120К на фрилансе:</b> Начала вести местный бизнес за 15К. Накопила кейсы, подняла чек до 40К, взяла двух ассистентов. «Не бойтесь делегировать — это масштабирует доход».",
     "https://vc.ru/"),
    ("<b>3D-дизайнер — 300К:</b> Выкладывал работы в Twitter и Discord-серверы. Через 6 месяцев — заказы от game-студий из США и Европы. «Соцсети + английский = мировой рынок».",
     "https://habr.com/ru/articles/"),
]


def load_index():
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tips": [], "tools": [], "stats": [], "cases": []}


def save_index(data):
    with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def pick_next(bank, used_indices):
    available = [i for i in range(len(bank)) if i not in used_indices]
    if not available:
        available = list(range(len(bank)))
        used_indices.clear()
    i = random.choice(available)
    used_indices.append(i)
    return bank[i], i


def tg_send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHANNEL, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def post_tips():
    idx = load_index()
    (text, link), _ = pick_next(TIPS, idx["tips"])
    msg = (
        f"<b>💡 Совет фрилансерам</b>\n\n{text}\n\n"
        f"<b>А ты так делаешь? Пиши в комментах 👇</b>\n\n"
        f"🔗 <a href=\"{link}\">Полезные статьи</a>\n\n"
        f"<i>🔄 Перешли другу — полезно же</i>\n\n"
        f"#советы #фриланс"
    )
    result = tg_send(msg)
    if result.get("ok"):
        save_index(idx)
        print(f"  ✅ Tips #{result['result']['message_id']}")
    else:
        print(f"  ❌ {result}")


def post_tools():
    idx = load_index()
    (text, link), _ = pick_next(TOOLS, idx["tools"])
    msg = (
        f"<b>🛠 Инструмент дня. Пользуешься таким?</b>\n\n{text}\n\n"
        f"<b>Кидай в сохранёнки, пригодится 📌</b>\n\n"
        f"🔗 <a href=\"{link}\">Подробнее</a>\n\n"
        f"<i>🔄 Скинь другу — пусть тоже знает полезный инструмент</i>\n\n"
        f"#инструменты #фриланс #полезное"
    )
    result = tg_send(msg)
    if result.get("ok"):
        save_index(idx)
        print(f"  ✅ Tools #{result['result']['message_id']}")
    else:
        print(f"  ❌ {result}")


def post_stats():
    idx = load_index()
    (text, link), _ = pick_next(STATS, idx["stats"])
    msg = (
        f"<b>📊 Фриланс в цифрах. Знал об этом?</b>\n\n{text}\n\n"
        f"<b>Какая цифра удивила? Ставь реакцию 👇</b>\n😱 — если в шоке\n🤔 — надо проверить\n\n"
        f"🔗 <a href=\"{link}\">Источник</a>\n\n"
        f"<i>🔄 Перешли другу-фрилансеру — удиви его цифрами</i>\n\n"
        f"#статистика #фриланс #цифры"
    )
    result = tg_send(msg)
    if result.get("ok"):
        save_index(idx)
        print(f"  ✅ Stats #{result['result']['message_id']}")
    else:
        print(f"  ❌ {result}")


def post_cases():
    idx = load_index()
    (text, link), _ = pick_next(CASES, idx["cases"])
    msg = (
        f"<b>📖 История успеха: как фрилансер сделал это</b>\n\n{text}\n\n"
        f"<b>А у тебя была похожая история? Расскажи 👇</b>\n\n"
        f"🔗 <a href=\"{link}\">Читать истории</a>\n\n"
        f"<i>🔄 Вдохнови друга — перешли ему эту историю</i>\n\n"
        f"#история #фриланс #успех"
    )
    result = tg_send(msg)
    if result.get("ok"):
        save_index(idx)
        print(f"  ✅ Cases #{result['result']['message_id']}")
    else:
        print(f"  ❌ {result}")


ROUTES = {
    "tips": post_tips,
    "tools": post_tools,
    "stats": post_stats,
    "cases": post_cases,
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tips"
    now = datetime.now(MOSCOW_TZ)
    print(f"📝 Content [{mode}]: {now.strftime('%H:%M MSK')}")
    if mode in ROUTES:
        ROUTES[mode]()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
