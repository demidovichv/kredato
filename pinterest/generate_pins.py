#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / 'pinterest' / 'content-hub.json'
TEMPLATE = ROOT / 'pinterest' / 'templates' / 'pin-card.md'

hub = json.loads(HUB.read_text(encoding='utf-8'))

TEMPLATES_BY_VERTICAL = {
    'fin': [
        {
            'headline': '{{benefit}} за {{timeframe}} без {{pain}}',
            'desc': 'Крючок: {{pain}} в {{topic}}. Польза: {{benefit}} за {{timeframe}}. CTA: {{cta}}.',
            'visual': 'Обычная жизнь + 1 сбой: стол с ноутбуком, а на экране вместо отчёта — пульс от ставок.'
        },
        {
            'headline': '{{number}} ошибок в {{topic}}, которые стоят вам {{loss}}',
            'desc': 'Контраст: {{common_action}} vs {{better_action}}. Польза: {{number}} ошибок = {{loss}}. CTA: {{cta}}.',
            'visual': 'Обычная жизнь + 1 сбой: человек в магазине держит ценник, а цифры над ним буквально горят.'
        }
    ],
    'strah': [
        {
            'headline': '{{benefit}} при {{event}} за {{timeframe}}',
            'desc': 'Крючок: {{event}} и страх {{pain}}. Польза: {{benefit}} без лишней переплаты. CTA: {{cta}}.',
            'visual': 'Обычная жизнь + 1 сбой: автосервис, а механик протягивает не ключ, а таблицу из 3 СК.'
        }
    ],
    'earning': [
        {
            'headline': '{{specific_result}} за {{duration}} без {{pain}}',
            'desc': 'Крючок: {{pain}} при {{topic}}. Польза: {{specific_result}} за {{duration}}. CTA: {{cta}}.',
            'visual': 'Обычная жизнь + 1 сбой: кухня утром, а вместо кофе — список заданий на первый заказ.'
        }
    ]
}


def fill_template(text, ctx):
    for k, v in ctx.items():
        text = text.replace('{{' + k + '}}', str(v))
    return text


def build_context(vertical, rubric):
    sections = {
        'fin': {
            'benefit': 'сравните вклады без скрытых условий',
            'timeframe': '2 минуты',
            'pain': 'скрытых условий',
            'topic': 'вкладах',
            'number': '3',
            'loss': 'тысячи рублей',
            'common_action': 'выбирать первый попавшийся банк',
            'better_action': 'сравнить ставки и требования',
            'cta': 'Сравните 3 варианта за 2 минуты'
        },
        'strah': {
            'benefit': 'сравните 3 СК без лишней переплаты',
            'event': 'оформлении полиса',
            'pain': 'переплаты',
            'topic': 'страхование',
            'number': '3',
            'loss': ' лишняя переплата',
            'common_action': 'покупать первый попавшийся полис',
            'better_action': 'сравнить покрытие и цену за 2 минуты',
            'cta': 'Скачайте чек-лист: что проверить перед покупкой'
        },
        'earning': {
            'benefit': 'получите первый заказ без вложений',
            'duration': 'неделю',
            'pain': 'вложений',
            'topic': 'фрилансе',
            'number': '5',
            'loss': 'дополнительные траты',
            'common_action': 'ждать идеальных условий',
            'better_action': 'сделать 1 маленькое задание сегодня',
            'cta': 'Скачайте чек-лист: первый заказ за неделю'
        }
    }
    base = sections.get(vertical, {})
    base.update({'audience': 'новичок', 'specific_result': 'первый заказ'})
    return base


def main():
    pins = []
    for vertical, rubrics in hub['verticals'].items():
        for rubric in rubrics['rubrics']:
            templates = TEMPLATES_BY_VERTICAL.get(vertical, [])
            for i, tpl in enumerate(templates, start=1):
                ctx = build_context(vertical, rubric)
                headline = fill_template(tpl['headline'], ctx)
                desc = fill_template(tpl['desc'], ctx)
                visual = tpl['visual']
                pins.append({
                    'vertical': vertical,
                    'rubric': rubric,
                    'headline'
