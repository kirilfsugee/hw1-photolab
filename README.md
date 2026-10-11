# ДЗ 1 «Фотолаборатория»

Курс «Введение в компьютерное зрение», Innopolis University, Fall 2026.

`photolab.py` — инструмент командной строки: цветокоррекция (гамма, баланс белого, CLAHE), хромакей,
геометрия (поворот, масштаб, выпрямление по четырём углам) и контактный лист. Отчёт с числами — `REPORT.md`.

## Установка и самопроверка

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest tests -q                                   # 11 тестов на синтетических данных
```

## Структура

```
photolab.py            инструмент
REPORT.md              отчёт: числа, три вопроса, отказы
requirements.txt       opencv-contrib-python==4.14.0.94 и остальное
data/                  исходные фотографии
out/                   результаты команд
tests/test_photolab.py самопроверка
.github/workflows/     CI: те же тесты на чистой машине
```

## Команды

Каждая команда пишет результат в `out/` и печатает одну JSON-строку с числами для отчёта.
Полный список, включая прогоны на кадрах курса (`out/course/`) и `report_checks.py`, — в `REPORT.md`, раздел 4.

```bash
# цветокоррекция
python photolab.py gamma data/dark.jpg --gamma 0.5 -o out/dark_g05.jpg --hist out/dark_g05_hist.png
python photolab.py gamma data/dark.jpg --gamma 2.0 -o out/dark_g20.jpg --hist out/dark_g20_hist.png
python photolab.py wb data/bright.jpg --method grey-world -o out/bright_gw.jpg
python photolab.py wb data/bright.jpg --method white-patch -o out/bright_wp.jpg
python photolab.py clahe data/dark.jpg --clip 2 --tiles 8 -o out/dark_clahe.jpg --compare out/dark_cmp.jpg --hist out/dark_clahe_hist.png

# хромакей: границы с прямоугольника на объекте или руками (красный — lo[0] > hi[0])
python photolab.py chromakey data/object.jpg --bg data/bg.jpg --sample 820,480,420,200 -o out/object_on_bg.jpg --mask out/object_mask.png
python photolab.py chromakey data/object.jpg --bg data/bg.jpg --lo H,S,V --hi H,S,V -o out/object_on_bg.jpg --mask out/object_mask.png

# геометрия
python photolab.py rotate data/poster.jpg --deg 30 -o out/poster_rot30.jpg
python photolab.py resize data/text.jpg --scale 0.25 --report -o out/text_x025.jpg
python photolab.py rectify data/poster.jpg --corners 1821,838,448,519,1032,1309,1056,272 --aspect 0.67 -o out/poster_front.jpg
python photolab.py rectify data/poster.jpg --clicks --aspect 0.67 -o out/poster_front.jpg

# контактный лист (маски *.jpg раскрываются и в cmd / PowerShell)
python photolab.py sheet "data/*.jpg" "out/*.jpg" --cols 4 -o out/sheet.jpg
```

Справка по аргументам: `python photolab.py <команда> -h`.
