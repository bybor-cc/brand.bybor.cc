# brand.bybor.cc

Материалы бренда Bor: единственный знак **b∅r**, правила использования и сайт.

- Сайт: https://brand.bybor.cc
- Исходные SVG: `public/assets/bybor-mark-light.svg` и `bybor-mark-dark.svg`.
- Правила: `docs/brand.typ`; опубликованы также как `public/brand.pdf`.
- Статический сайт: `public/`, без сборки и сторонних сервисов.
- Размещение: `docs/deployment.typ`.

`light` — тёмный знак для светлого фона, `dark` — светлый для тёмного.
Это два цвета одной геометрии, без `by`. Шрифт Geist используется только
для текста сайта; логотип от шрифта не зависит. Лицензия Geist — рядом с шрифтом.

Локальный просмотр: `python -m http.server 8080 --directory public`.
PDF: `typst compile docs/brand.typ public/brand.pdf`.

Производные ресурсы Devices хранятся в репозитории Devices. Его инструменты
импортируют SVG из этого репозитория и фиксируют контрольные суммы.
