# Хабр — шпаргалка для публикации

## Песочница
- URL редактора: `https://habr.com/ru/sandbox/new/`
- Статья в песочнице ждёт приглашения от полноправного пользователя, чтобы попасть в основной поток
- Пока нет приглашения — висит в песочнице

## Поля статьи (React-контролы, CDP требует setter + dispatchEvent)

### Редактор
- **Заголовок:** `textarea.editor-title` (в Markdown-режиме), либо contenteditable div с placeholder "Заголовок" (в WYSIWYG)
- **Текст:** `textarea.editor-body` (Markdown) или `.ProseMirror` (WYSIWYG)
- Переключатель WYSIWYG/Markdown: кнопка `.switcher-control`

### Настройки публикации
- **Заголовок:** `textarea[placeholder="Заголовок"]`
- **Текст публикации:** `textarea[placeholder="Текст публикации"]`
- **Текст в ленте:** `textarea[placeholder="Текст в ленте"]`
- **Целевая аудитория:** `input[placeholder="Выберите целевую аудиторию"]` — autocomplete, значение: "Промышленная инженерия"
- **Хабы:** `input[placeholder="Выберите хабы"]` — autocomplete, добавляются как `input[name="hubs[]"]` со значениями
- **Ключевые слова (теги):** `input[placeholder="Ключевые слова"]` — ввод по одному через Enter, хранятся как `input[name="tags[]"]`
- **Формат:** radio `input[name="format"]` — review=Обзор, case=Кейс, tutorial=Туториал...
- **Читать далее:** `input[placeholder="Читать далее"]` / `input[name="leadButtonText"]`
- **Сложность:** radio `input[name="complexity"]` — low/medium/high

## Как заполнять React-поля через CDP
```javascript
var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
setter.call(element, 'текст');
element.dispatchEvent(new Event('input', {bubbles: true}));
element.dispatchEvent(new Event('change', {bubbles: true}));
```

Для textarea — `window.HTMLTextAreaElement.prototype`.

## Процесс публикации
1. Открыть `/ru/sandbox/new/`
2. Переключить в Markdown-режим (switcher)
3. Заполнить title + body textarea
4. Переключить обратно в WYSIWYG
5. Нажать «Далее к настройкам»
6. Заполнить: аудитория, хабы, теги, формат, текст в ленте, читать далее
7. «Отправить на модерацию»

## Chrome для CDP
```bash
google-chrome-stable --no-sandbox --disable-gpu \
  --remote-debugging-port=9223 --remote-allow-origins=* \
  --user-data-dir=... --window-size=1280,900
```

Сессия сохраняется в user-data-dir — повторный вход не нужен при перезапуске с тем же профилем.
