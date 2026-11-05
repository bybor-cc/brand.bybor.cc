# brand.bybor.cc

Подключаемый набор бренда **Bor** и skill **bor-brand**: https://brand.bybor.cc.

В новом проекте можно написать: **«Следуй бренду Bor»** или вызвать `$bor-brand`.
Навык прочитает инструкции проекта, выберет профиль и использует готовые ресурсы.

## Подключение

Скачать `https://brand.bybor.cc/bor-brand.zip` и распаковать. Из каталога с
распакованной папкой выполнить:

```sh
python bor-brand/scripts/brand.py install-skill
```

Навык устанавливается для пользователя Codex и доступен со следующего сообщения.
Установка отказывается заменять существующий skill. ZIP автономный: Python 3.9+
и стандартная библиотека; checkout этого репозитория и сеть для экспорта не нужны.

Без установки skill можно выполнить CLI из архива или checkout:

```sh
python skills/bor-brand/scripts/brand.py export --platform web --profile identity --output /path/to/project/public/bor
python skills/bor-brand/scripts/brand.py export --platform android --profile devices --output /path/to/project/vendor/bor --package cc.example.app.branding
python skills/bor-brand/scripts/brand.py check --output /path/to/project/public/bor
```

Сайт также раздаёт готовые `bor-web.zip` и `bor-android.zip` с отдельными папками
identity/devices, `brand.json` с токенами и `kit.json` с версией и SHA-256 архивов.
Проверка `check` обнаруживает изменённые/недостающие файлы экспорта; это не подпись.

## Два уровня правил

- **identity** — подтверждённый знак b∅r и правила Bor. Универсальные обязательные
  UI-палитра, шрифт и отступы пока не выбраны.
- **devices** — опциональное оформление существующего Devices: Geist,
  монохромные светлая/тёмная палитры, радиусы и интервалы. Это профиль продукта,
  а не обязательный стиль каждого проекта Bor.

Веб-экспорт: два SVG, CSS, пример HTML и manifest. Devices добавляет Geist с
лицензией, CSS-переменные и поверхность карточки. Селекторы темы ограничены
контейнером; глобальных сбросов нет. Android: векторы и adaptive foreground;
Devices добавляет шрифт и Kotlin-токены для подключения к существующей Compose-теме.
Экспорт сам не меняет приложение, его идентификаторы или сборочную конфигурацию.

## Источники и публикация

`skills/bor-brand/` — автономный исходный набор, включая CLI, SVG, шрифт,
`assets/brand.json` и Typst-правила в `references/`. Имена SVG `light`/`dark`
обозначают фон применения. Это два цвета одного знака без `by`.
`public/` — сайт и опубликованные экспорты; `tools/package.py` обновляет их.
`docs/deployment.typ` описывает размещение на существующем VPS с Caddy.

```sh
python tools/package.py
python -m unittest discover -s tests
python -m http.server 8080 --directory public
```

Для пересборки сайта нужен Typst; для использования готового набора — нет.
На iOS, OLED и в других средах доступны SVG и правила; специальных экспортёров
пока нет. OLED Devices остаётся ответственностью прошивки в репозитории Devices.
