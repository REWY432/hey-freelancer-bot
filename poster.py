"""
GitHub Actions vacancy poster for @hey_freelancer
Scrapes FL.ru, Freelance.ru, Kwork → filters → posts top 3 to Telegram.
No external API dependencies. State tracked via posted_vacancies.json in repo.
"""
import urllib.request, urllib.parse, json, re, os, sys, io
from datetime import datetime, timezone, timedelta
from html import unescape

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === CONFIG ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(SCRIPT_DIR, "posted_vacancies.json")
MOSCOW_TZ = timezone(timedelta(hours=3))
MAX_PER_POST = 3

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not set"); sys.exit(1)
CHANNEL = "@hey_freelancer"

# === KEYWORDS ===
INCLUDE_KW = [
    "дизайн", "разработ", "программист", "копирайт", "текст", "seo", "smm",
    "веб", "сайт", "лендинг", "бот", "telegram", "приложен", "мобильн",
    "верстк", "wordpress", "tilda", "логотип", "иллюстра", "видео", "монтаж",
    "анимац", "фронтенд", "бэкенд", "python", "javascript", "react", "vue",
    "php", "laravel", "1с", "битрикс", "figma", "photoshop", "реклам",
    "таргет", "контекст", "маркетинг", "аналитик", "тестиров", "qa",
    "перевод", "аудио", "подкаст", "озвучк", "чат", "crm", "google",
    "яндекс", "парсинг", "скрап", "автоматизац", "unity", "unreal",
    "3d", "моделирован", "нейросет", "ai", "ml", "интеграц", "api",
    "devops", "linux", "администрирован", "контент", "рилс", "reels",
    "сторис", "блогер", "визуал", "брендинг", "фирменный стиль",
    "айдентика", "ui", "ux", "презентац", "инфографик", "ретуш",
    "полиграф", "верстальщик"
]

EXCLUDE_KW = [
    "заправщик", "кассир", "азс", "охран", "уборщ", "грузч", "водител",
    "курьер", "продавец", "официант", "барист", "повар", "сантехник",
    "электрик", "строител", "разнорабоч", "нян", "сиделк", "медсестр",
    "такси", "склад", "комплектовщик", "фасовщ", "колл-центр",
    "оператор call", "оператор колл", "промоутер", "мерчендайзер",
    "бесплатно", "за отзыв", "за отзывы", "написать отзыв", "отзыв",
    "даром", "тестовое задание бесплатно", "за еду", "недорого",
    "бюджет минимальный", "минимальный бюджет", "плачу копейки",
    "оплата символическая", "нет бюджета", "без оплаты",
    "кушами", "опытом", "реклама канала", "подпишись", "лайкни",
    "размещу", "репост", "взаимный пиар", "накрутк", "ботовод",
    "ставки", "казино", "букмекер", "гемблинг", "betting",
    "сетевой маркетинг", "mlm", "матрица", "партнёрская программа",
    "нужен студент", "сделать дёшево", "срочно горит", "доллар", "$",
]


def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', errors='ignore')


def parse_fl(html):
    projects = []
    for m in re.finditer(r'qa-project-name="project-item(\d+)"[^>]*>.*?<a[^>]*href="(/projects/\d+/[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        link = "https://www.fl.ru" + m.group(2) + "?ref=1692663"
        title = unescape(re.sub(r'<[^>]+>', '', m.group(3)).strip())
        block = html[max(0,m.start()-100):min(len(html),m.end()+2500)]
        budget = "договорная"
        pm = re.search(r'b-post__price[^>]*>.*?<span[^>]*>(.*?)</span>', block, re.DOTALL)
        if pm: budget = unescape(' '.join(re.sub(r'<[^>]+>','',pm.group(1)).split()))
        desc = ""
        dm = re.search(r'class="b-post__txt[^"]*">(.*?)</div>', block, re.DOTALL)
        if dm: desc = ' '.join(unescape(re.sub(r'<[^>]+>','',dm.group(1))).split())[:180]
        projects.append({"id": m.group(1), "title": title, "link": link, "budget": budget, "description": desc, "source": "FL.ru"})
    return projects


def parse_fr(html):
    projects = []
    for m in re.finditer(r'<a class="task-card__title-link"[^>]*href="(/task/view/\d+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        link = "https://freelance.ru" + m.group(1)
        title = unescape(re.sub(r'<[^>]+>', '', m.group(2)).strip())
        block = html[max(0,m.start()-300):min(len(html),m.end()+2000)]
        budget = "договорная"
        bm = re.search(r'class="task-card__budget">\s*<span[^>]*>(.*?)</span>\s*<span[^>]*>(.*?)</span>', block, re.DOTALL)
        if bm:
            amount = unescape(re.sub(r'<[^>]+>','',bm.group(1)).strip()).replace('&#8381;','₽')
            unit = unescape(re.sub(r'<[^>]+>','',bm.group(2)).strip()) if bm.group(2) else ""
            budget = f"{amount} {unit}".strip() if unit else amount
        desc = ""
        dm = re.search(r'<p class="task-card__desc">(.*?)</p>', block, re.DOTALL)
        if dm: desc = ' '.join(unescape(re.sub(r'<[^>]+>','',dm.group(1))).split())[:180]
        projects.append({"id": m.group(1).split('/')[-1], "title": title, "link": link, "budget": budget, "description": desc, "source": "Freelance.ru"})
    return projects


def parse_kw(html):
    projects = []
    idx = html.find('"wantsListData":')
    if idx < 0: return projects
    start = html.find('{', idx + 16)
    depth = 0
    for i in range(start, min(len(html), start+200000)):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0: end = i+1; break
    try:
        data = json.loads(html[start:end])
        for w in data.get('pagination',{}).get('data',[]):
            if w.get('status') != 'active': continue
            wid = w.get('id','')
            price = w.get('possiblePriceLimit',0)
            budget = f"{price:,} ₽".replace(',',' ') if price and price > 0 else "договорная"
            desc = ' '.join(unescape(re.sub(r'<[^>]+>','',w.get('description',''))).split())[:180]
            projects.append({"id": str(wid), "title": unescape(w.get('name','')), "link": f"https://kwork.ru/projects/{wid}/view?ref=4104471", "budget": budget, "description": desc, "source": "Kwork"})
    except: pass
    return projects


def parse_habr():
    """Search Habr Career API for remote IT vacancies."""
    projects = []
    seen_ids = set()
    headers = {"User-Agent": "HeyFreelancerBot/1.0 (hey_freelancer@telegram.org)"}
    
    skills_queries = [
        "",
        "&skills[]=python&skills[]=javascript&skills[]=php",
        "&skills[]=design&skills[]=seo&skills[]=marketing",
    ]
    
    for sq in skills_queries:
        try:
            url = f"https://career.habr.com/api/frontend/vacancies?page=0&per_page=15&sort=date&divisions[]=remote{sq}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            
            for item in data.get("list", []):
                vid = item.get("id", "")
                if vid in seen_ids:
                    continue
                seen_ids.add(vid)
                
                title = item.get("title", "") or ""
                company = (item.get("company") or {}).get("title", "") or ""
                href = item.get("href", "") or ""
                link = f"https://career.habr.com{href}"
                
                # Salary
                salary = item.get("salary") or {}
                predicted = item.get("predictedSalary") or {}
                budget = salary.get("formatted") or predicted.get("formatted") or ""
                if not budget:
                    sal_from = salary.get("from")
                    sal_to = salary.get("to")
                    if sal_from and sal_to:
                        budget = f"{sal_from:,} – {sal_to:,} ₽".replace(",", " ")
                    elif sal_from:
                        budget = f"от {sal_from:,} ₽".replace(",", " ")
                    elif sal_to:
                        budget = f"до {sal_to:,} ₽".replace(",", " ")
                    if not budget:
                        p_from = predicted.get("from")
                        p_to = predicted.get("to")
                        if p_from and p_to:
                            budget = f"~{p_from:,} – {p_to:,} ₽".replace(",", " ")
                
                if not budget:
                    budget = "договорная"
                
                # Description from skills and divisions
                skills = [s.get("title","") for s in (item.get("skills") or [])[:5] if s]
                divisions = [d.get("title","") for d in (item.get("divisions") or [])[:2] if d]
                locs = [l.get("title","") for l in (item.get("locations") or [])[:1] if l]
                
                desc_parts = []
                if divisions:
                    desc_parts.append(", ".join(divisions))
                if skills:
                    desc_parts.append(", ".join(skills))
                if locs:
                    desc_parts.append(f"📍 {', '.join(locs)}")
                desc = ". ".join(desc_parts)[:200]
                
                full_title = title
                if company:
                    full_title = f"{title} ({company})"
                
                projects.append({
                    "id": f"habr{vid}",
                    "title": full_title,
                    "link": link,
                    "budget": budget,
                    "description": desc,
                    "source": "Habr Career"
                })
        except Exception as e:
            print(f"  ⚠️ Habr Career: {e}")
            continue
    
    return projects


def is_relevant(p):
    text = (p["title"] + " " + p["description"]).lower()
    for kw in EXCLUDE_KW:
        if kw in text: return False
    for kw in INCLUDE_KW:
        if kw in text: return True
    return p["budget"] not in ("договорная", "", "N/A", "по договоренности", "по результатам собеседования")


def quality_score(p):
    score = 0
    budget = p.get("budget","")
    if budget and budget not in ("договорная","по договоренности","по результатам собеседования","","N/A"):
        nums = re.findall(r'[\d\s]+', budget.replace(' ',''))
        for n in nums:
            try:
                a = int(n)
                if a >= 100000: score += 50
                elif a >= 50000: score += 40
                elif a >= 20000: score += 30
                elif a >= 5000: score += 20
                elif a >= 1000: score += 10
                else: score -= 5
                break
            except: pass
    else: score -= 30
    dl = len(p.get("description",""))
    if dl > 150: score += 15
    elif dl > 80: score += 8
    elif dl < 20: score -= 10
    if p.get("responses",0) > 10: score += 5
    if len(p.get("title","")) > 30: score += 5
    if p.get("source") == "Kwork": score += 3
    if p.get("source") == "Habr Career": score += 2  # Direct employer listings
    return score


def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"urls": [], "last_post": ""}


def save_tracking(data):
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def tg_send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHANNEL, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


# --- Category detection ---
CATEGORY_RULES = [
    ("Дизайн", ["дизайн", "figma", "photoshop", "логотип", "иллюстрац", "баннер", "креатив", "фирменный стиль", "айдентика", "брендинг", "полиграф", "верстк", "ретуш", "визуал", "ui", "ux", "графическ", "отрисовк", "рендер", "мокап", "типографик"]),
    ("Разработка", ["разработ", "программист", "python", "javascript", "react", "vue", "php", "laravel", "бот", "telegram", "api", "фронтенд", "бэкенд", "fullstack", "devops", "сайт", "приложен", "crm", "битрикс", "1с", "wordpress", "tilda", "код", "скрипт", "баз данных", "sql", "парсинг", "автоматизац", "unity", "unreal"]),
    ("Контент", ["текст", "копирайт", "контент", "стат", "написа", "seo", "редактур", "корректур", "перевод", "расшифровк", "транскрибац", "сценари", "раскадровк"]),
    ("Маркетинг", ["smm", "реклам", "таргет", "маркетинг", "продвижен", "трафик", "лидогенерац", "воронк", "контекст", "яндекс директ", "google ads", "медиа", "пиар"]),
    ("Видео", ["видео", "монтаж", "анимац", "моушн", "рилс", "reels", "youtube", "клип", "озвучк", "аудио", "подкаст"]),
    ("Аудит", ["аудит", "тестирован", "qa", "аналитик", "оптимизац", "консалтинг", "анализ"]),
]

def detect_category(title, desc):
    text = (title + " " + desc).lower()
    best_cat = "Фриланс"
    best_score = 0
    for cat, keywords in CATEGORY_RULES:
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_cat = cat
    return best_cat


def clean_budget(budget_str):
    """Clean and normalize budget string."""
    if not budget_str or budget_str in ("договорная", "по договоренности", "", "N/A", "по результатам собеседования"):
        return None
    b = budget_str.replace("&nbsp;", " ").replace("&#8381;", "₽").replace("руб", "₽")
    b = re.sub(r'\s+', ' ', b).strip()
    return b


def clean_desc(desc, max_len=150):
    d = desc.strip()
    if len(d) > max_len:
        d = d[:max_len].rsplit(' ', 1)[0] + "..."
    return d


MONTHS_RU = ["", "ЯНВАРЯ", "ФЕВРАЛЯ", "МАРТА", "АПРЕЛЯ", "МАЯ", "ИЮНЯ",
             "ИЮЛЯ", "АВГУСТА", "СЕНТЯБРЯ", "ОКТЯБРЯ", "НОЯБРЯ", "ДЕКАБРЯ"]


def format_post(projects, now):
    date_str = f"{now.day} {MONTHS_RU[now.month]}"
    
    lines = [
        f"📆 {date_str}",
        "<b>🔥 Вакансии на фрилансе — только с оплатой</b>",
        ""
    ]
    
    for p in projects[:3]:
        cat = detect_category(p["title"], p.get("description", ""))
        cat_line = f"│  {cat}  │"
        box_top = "┌" + "─" * (len(cat_line) - 2) + "┐"
        box_bot = "└" + "─" * (len(cat_line) - 2) + "┘"
        
        lines.append(f"<code>{box_top}</code>")
        lines.append(f"<code>{cat_line}</code>")
        lines.append(f"<code>{box_bot}</code>")
        lines.append("")
        
        lines.append(f"<b>{p['title']}</b>")
        
        desc = clean_desc(p.get("description", ""))
        if desc:
            lines.append(desc)
        
        budget = clean_budget(p.get("budget", ""))
        if budget:
            lines.append(f"💰 {budget}")
        
        source = p.get("source", "")
        lines.append(f"🔗 {p['link']}  |  {source}")
        lines.append("")
        lines.append("─" * 30)
        lines.append("")
    
    lines.append("#вакансии #удаленка #фриланс")
    lines.append("⏩ Поделиться с другом — @hey_freelancer")
    
    return "\n".join(lines)


def main():
    now = datetime.now(MOSCOW_TZ)
    today_str = now.strftime("%d.%m")
    print(f"📅 Vacancy round: {now.strftime('%H:%M MSK')}")

    # Fetch all sources
    all_projects = []
    sources = [
        ("www.fl.ru", lambda: parse_fl(fetch_html("https://www.fl.ru/projects/"))),
        ("freelance.ru", lambda: parse_fr(fetch_html("https://freelance.ru/task"))),
        ("kwork.ru", lambda: parse_kw(fetch_html("https://kwork.ru/projects"))),
        ("habr.com/career", parse_habr),
    ]
    for name, fetcher in sources:
        try:
            projects = fetcher()
            all_projects.extend(projects)
            print(f"  {name}: {len(projects)}")
        except Exception as e:
            print(f"  ⚠️ {name}: {e}")

    relevant = [p for p in all_projects if is_relevant(p)]
    tracking = load_tracking()
    posted = set(tracking.get("urls", []))
    new_projects = [p for p in relevant if p["link"] not in posted]
    new_projects.sort(key=quality_score, reverse=True)
    print(f"  New quality: {len(new_projects)}")

    if not new_projects:
        print("  No new projects to post")
        return

    # Take top 3
    top = new_projects[:MAX_PER_POST]
    text = format_post(top, now)

    # Post to Telegram
    result = tg_send(text)
    if result.get("ok"):
        print(f"  ✅ Posted: message #{result['result']['message_id']}")
        # Update tracking
        tracking["urls"] = list(posted | {p["link"] for p in top})
        if len(tracking["urls"]) > 300:
            tracking["urls"] = tracking["urls"][-300:]
        tracking["last_post"] = now.isoformat()
        save_tracking(tracking)
    else:
        print(f"  ❌ Post failed: {result}")


if __name__ == "__main__":
    main()
