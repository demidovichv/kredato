#!/usr/bin/env python3
"""
LeadMagnet.ru Monitor Script
Monitors blog.leadmagnet.ru for new lessons and content updates.
"""

import json
import re
from datetime import datetime
import urllib.request
import urllib.error

def monitor_leadmagnet_blog():
    """Monitor blog.leadmagnet.ru for new content and lessons"""
    
    print("🔍 Мониторинг LeadMagnet.ru...")
    
    # Load previous state
    try:
        with open('state.json', 'r', encoding='utf-8') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"last_check": datetime.now().isoformat(), "lessons": []}
    
    # Fetch main page
    try:
        req = urllib.request.Request("https://blog.leadmagnet.ru", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return False
    
    # Extract educational content
    lessons = []
    
    # Pattern 1: Look for links with educational text
    link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*новость[^<]*|[^<]*статья[^<]*|[^<]*кейс[^<]*|[^<]*гайд[^<]*|[^<]*урок[^<]*)</a>'
    matches = re.findall(link_pattern, content, re.IGNORECASE)
    for href, title in matches:
        full_url = f"https://blog.leadmagnet.ru/{href}" if href.startswith('/') else href
        lessons.append({
            'title': title.strip(),
            'url': full_url,
            'type': 'link',
            'found': datetime.now().isoformat()
        })
    
    # Pattern 2: Look for specific sections
    sections = {
        'news': 'Новости',
        'articles': 'Статьи',
        'cases': 'Кейсы',
        'knowledge': 'База знаний',
        'blog': 'Блог'
    }
    
    for section_name, section_title in sections.items():
        if section_name in content.lower():
            lessons.append({
                'title': f'{section_title} · образовательный раздел',
                'url': f'https://blog.leadmagnet.ru/{section_name}',
                'type': 'section',
                'found': datetime.now().isoformat()
            })
    
    # Pattern 3: Look for educational keywords
    keyword_patterns = [
        r'гайд[^<]*',
        r'статья[^<]*',
        r'кейс[^<]*',
        r'урок[^<]*',
        r'инструкция[^<]*',
        r'обучение[^<]*',
        r'анализ[^<]*',
        r'стратегия[^<]*',
        r'метод[^<]*',
        r'тренд[^<]*',
        r'исследование[^<]*'
    ]
    
    for pattern in keyword_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match) > 5:
                lessons.append({
                    'title': f'Keyword: {match[:50]}...',
                    'url': 'https://blog.leadmagnet.ru',
                    'type': 'keyword',
                    'found': datetime.now().isoformat()
                })
    
    # Pattern 4: Look for marketing-related content
    marketing_patterns = [
        r'email[^<]*',
        r'рассылка[^<]*',
        r'marketing[^<]*',
        r'продажа[^<]*',
        r'клиент[^<]*',
        r'конверсия[^<]*'
    ]
    
    for pattern in marketing_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match) > 5:
                lessons.append({
                    'title': f'Marketing: {match[:50]}...',
                    'url': 'https://blog.leadmagnet.ru',
                    'type': 'marketing',
                    'found': datetime.now().isoformat()
                })
    
    # Remove duplicates
    unique_lessons = []
    seen_urls = set()
    for lesson in lessons:
        if lesson['url'] not in seen_urls:
            unique_lessons.append(lesson)
            seen_urls.add(lesson['url'])
    
    # Check for new lessons
    new_lessons = []
    for lesson in unique_lessons:
        is_new = True
        for old_lesson in state['lessons']:
            if lesson['url'] == old_lesson['url'] and lesson['title'] == old_lesson['title']:
                is_new = False
                break
        if is_new:
            new_lessons.append(lesson)
    
    # Update state
    state['last_check'] = datetime.now().isoformat()
    state['lessons'] = unique_lessons
    
    # Save state
    with open('state.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # Report results
    print(f"📊 Найдено уроков: {len(unique_lessons)}")
    print(f"🆕 Новых уроков: {len(new_lessons)}")
    
    if new_lessons:
        print("\n🎉 Новые уроки:")
        for lesson in new_lessons:
            print(f"  • {lesson['title']} ({lesson['type']})")
            print(f"    URL: {lesson['url']}")
    else:
        print("\n✅ Новых уроков нет")
    
    print(f"\n⏰ Последняя проверка: {state['last_check']}")
    
    return True

if __name__ == "__main__":
    monitor_leadmagnet_blog()