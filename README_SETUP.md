# Predicting Urban Water Quality — Python 3.12 + restyled UI

Runs on **Python 3.12** with no WampServer, MySQL or phpMyAdmin.
Everything the app did on Python 3.6 it still does, unchanged.

---

## Run it

Open a terminal in the folder holding `requirements.txt`.

### Windows

```bat
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cd predicting_urban_water_quality
python manage.py migrate
python manage.py runserver
```

### macOS / Linux

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd predicting_urban_water_quality
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

> Start `runserver` from inside the inner `predicting_urban_water_quality`
> folder (the one with `manage.py`). The views open
> `Water_Quality_Datasets.csv` by relative path, so launching from anywhere
> else makes training fail with `FileNotFoundError`. This was true on 3.6 too.

An empty, already-migrated database is included, so the site starts even if you
skip `migrate`. Re-running `migrate` is harmless.

## Logins

| Role | URL | Username | Password |
|---|---|---|---|
| Service Provider | `/serviceproviderlogin/` | `Admin` | `Admin` |
| Remote User | `/` | register at `/Register1/` | |

Training reads ~190,000 rows and fits three models, so **Train and Test Data
Sets** takes about 25 seconds and a prediction about 45–60 seconds. That is the
original design — every request retrains from scratch — and it was left alone.

---

## Part 1 — What made it run on 3.12

Four things broke between 3.6 and 3.12. Only these were touched.

| File | Change | Why |
|---|---|---|
| `predicting_urban_water_quality/__init__.py` | Emptied | It ran `import pymysql; pymysql.install_as_MySQLdb()`, which raised `ModuleNotFoundError` before Django loaded. Unnecessary once MySQL is gone. |
| `predicting_urban_water_quality/urls.py` | One import line → `from django.urls import re_path as url` | `django.conf.urls.url` was removed in Django 4.0. Keeping the name `url` means every route line underneath is untouched. |
| `predicting_urban_water_quality/settings.py` | `DATABASES` → SQLite | Drops the WampServer dependency. SQLite is built into Python. |
| `predicting_urban_water_quality/settings.py` | Added `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` | Preserves the original integer primary keys. Django 3.2+ would otherwise switch to `BigAutoField` and warn on every model. |
| `Remote_User/migrations/0008_sync_models_with_schema.py` | New file | See below. |
| `venv/`, `.idea/`, `__pycache__/` | Deleted | The bundled `venv` was 39 MB of **Windows Python 3.7** binaries and `.idea` pinned PyCharm to a "Python 3.6 (venv)" interpreter. Both fight a 3.12 setup. PyCharm rebuilds `.idea` by itself. |

No view, model, form, template tag or ML code was modified.

### Why the extra migration was needed

The three models the app actually uses — `water_quality_type`,
`detection_accuracy` and `detection_ratio` — had **no migration at all**. Their
tables existed only inside the MySQL dump, created by hand outside Django.
Migrations `0002`–`0007`, meanwhile, are leftovers from an unrelated project and
describe models (`ClientPosts_Model`, `review_Model`) that `models.py` does not
define.

That held together only while you restored the `.sql` dump into MySQL. A fresh
`migrate` on any database would have produced a site with missing tables.

`0008_sync_models_with_schema.py` creates the three missing models, drops the two
dead ones, and reconciles `ClientRegister_Model` (`phoneno` → `CharField`, plus
the `address` and `gender` fields `models.py` declares but `0001_initial` never
created). `manage.py makemigrations --check` now reports *No changes detected*.

---

## Part 2 — The restyle (CSS only)

**Only CSS changed.** Each template's `<style>` block was rewritten. Outside
those blocks every template is byte-for-byte identical to the original — no
markup, attribute, Django tag or piece of text was altered. I verified this by
blanking the `<style>` blocks in both the original and the new files and
diffing: 16 of 16 templates identical.

### The design

Palette drawn from water treatment rather than a generic dashboard theme:

| Token | Hex | Used for |
|---|---|---|
| `--abyss` | `#06202c` | page base |
| `--depth` | `#0c3547` | table label bands |
| `--current` | `#0f7f8c` | primary teal, buttons, card top edge |
| `--foam` | `#5fd4c8` | accents, focus rings |
| `--paper` | `#f6fafb` | card surfaces |
| `--slate` | `#24424f` | body text on cards |
| `--mineral` | `#c9791d` | **only** measured numbers (accuracy %, ratio %) |

Type is Space Grotesk for headings and IBM Plex Sans for body — a technical,
lab-instrument pairing rather than the old Lobster / Fredoka One / Russo One
mix. IBM Plex Mono appears on numeric readouts only, where tabular figures
genuinely help. The fonts load through a CSS `@import`, so no `<link>` tag had
to be added.

### How the old look was removed without touching markup

The templates are full of presentational HTML — `bgcolor="#FF0000"`,
`border="5"`, `bordercolor="#FF00FF"`, `width="879"` — plus inline
`style="color:red; font-size:20px; font-family:fantasy"`.

Presentational attributes carry zero specificity, so ordinary CSS overrides
them. Inline styles need `!important`. Cells were then classified by the
attributes they already carry:

| Selector | Role | Treatment |
|---|---|---|
| `th`, `td[bgcolor="#FF0000"]:not([style])`, `td[bgcolor="#FFFF00"]`, `td[bgcolor="#0000FF"]` | label / header cell | deep marine band, light text |
| `td[bgcolor="#FFFFFF"]`, `td[style*="fantasy"]` | data cell | white, zebra striped |
| `td[style*="monospace"]` | measured value | mineral amber, tabular mono |
| `td[height="68"]` | the prediction result | teal gradient readout panel |

The `:not([style])` test is what separates a header cell from a data cell that
happens to share the same red `bgcolor`.

The chart pages also had `#chartContainer` pinned at
`position:fixed; width:1180px; margin-left:250px; margin-top:-354px`, which
overlapped the page at most window sizes. It is now a normal flex panel beside
the chart-type buttons. Those pages keep a light card because CanvasJS draws its
labels in dark grey.

### Verified

- **Selector binding** — every page was rendered and its cells parsed. All 8/9/16/32 legacy-styled cells per page are claimed by a rule; none were left with the original colours.
- **Stylesheet validity** — all 12 pages parse without a CSS error.
- **Function** — the full 17-page smoke test passes: registration, login, profile, training, prediction, all three charts, ratio report, `.xls` export, admin. Training produced real accuracies (Naive Bayes 76.8%, SVM 78.7%, Logistic Regression 75.0%).

### Changing the colours

Every colour is a CSS variable in the `:root` block. The two files that cover
the whole site are `Template/htmls/RUser/Header.html` and
`Template/htmls/SProvider/Header.html`; the login, register and service-provider
login pages carry their own copy since they do not extend a header. Edit
`--current` and `--abyss` and the rest follows.

---

## Notes

- `Database/predicting_urban_water_quality.sql` is the old MySQL dump, kept for reference. Nothing loads it.
- `settings_backup.py` is a dead copy of the original settings, not imported anywhere.
- `Template/htmls/RUser/login.css` is not linked by any template, and was not linked before either.
- `Template/images/bg.jpg` is now unused. The two `.swf` Flash files were already dead.
- `serviceproviderlogin.html` requests `login.jpg` but the file on disk is `Login.jpg`. Case-insensitive on Windows, so it works there; on Linux the image 404s. Fixing it would mean editing markup, so it was left alone.
- `wordcloud` is imported in `Service_Provider/views.py` for an unused `STOPWORDS` set and pulls in matplotlib and pillow. Left as-is; deleting that one import would cut the install noticeably.
- `DEBUG = True` and the secret key are unchanged — fine locally, not for public hosting.
