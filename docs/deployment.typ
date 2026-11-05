#set text(lang: "ru", size: 11pt)
= Публикация brand.bybor.cc

Статический сайт: public/. Источники логотипа: public/assets/.
Документация бренда: docs/brand.typ. Для публикации правил:
#raw("typst compile docs/brand.typ public/brand.pdf\ncp docs/brand.typ public/brand.typ", block: true)

Репозиторий GitHub: https://github.com/bybor-cc/brand.bybor.cc.
Локальная папка: /home/ab/Projects/brand.bybor.cc.
VPS: arch@devices, каталог /home/arch/brand.bybor.cc.
DNS: A brand.bybor.cc → 83.228.240.86, DNS only.

Общий Caddy проекта Devices завершает TLS. В его Compose подключены только
для чтения public/ как /srv/brand/public и infrastructure/Caddyfile как
/etc/caddy/brand.Caddyfile. Основной Caddyfile импортирует конфигурацию бренда.
Остальные сервисы Devices не нужны для работы статического сайта.

Перед публикацией сохранить прежние compose.yaml и Caddyfile на VPS.
При добавлении mount требуется пересоздать только сервис caddy; PostgreSQL,
API и MQTT не перезапускаются. Последующие изменения файлов сайта не требуют
перезапуска. Изменение Caddyfile проверяется caddy validate и применяется
через caddy reload. DNS-запись не проксируется Cloudflare.

Ресурсы Devices — производные копии отдельной зависимости third_party/bor/.
Её manifest source.json фиксирует репозиторий, commit и SHA-256 двух SVG.
Обновление выполняется tools/import-branding.py в репозитории Devices
из локального checkout этого репозитория, после чего запускаются генераторы
панели, Android и OLED. Не требуется загружать файлы с сайта при сборке продукта.
