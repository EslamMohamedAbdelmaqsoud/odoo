# odoo_inspector.py
# A free, offline Odoo module inspector (CLI) with selectable report output language (EN/AR/BOTH).
# Terminal UI is English-only (clean prompts). Results are written to README_INSPECTOR.md.
################## Open This File :
# cd /opt/odoo17/odoo17
# python3 odoo/custom_addons/odoo_inspector.py

import os
import re
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from datetime import datetime

# =========================================================
# Result Writer (append to README, no terminal output)
# =========================================================
RESULT_FILE = "README_INSPECTOR.md"


class ResultWriter:
    """
    Redirects all print() output to README_INSPECTOR.md
    while keeping the terminal clean (options only).
    Appends results on each run.
    """

    def __init__(self, path: str = RESULT_FILE):
        self.path = path
        self.file = None
        self._redirect = None

    def __enter__(self):
        self.file = open(self.path, "a", encoding="utf-8")
        self.file.write("\n\n")
        self.file.write(f"## 🕒 Run — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.file.write("---\n")
        self._redirect = redirect_stdout(self.file)
        self._redirect.__enter__()
        return self.file

    def __exit__(self, exc_type, exc, tb):
        self._redirect.__exit__(exc_type, exc, tb)
        self.file.flush()
        self.file.close()


# =========================================================
# i18n helpers
# =========================================================
LANG_EN = "en"
LANG_AR = "ar"
LANG_BOTH = "both"


def L(en: str, ar: str, lang: str) -> str:
    """Return text in requested report language."""
    if lang == LANG_AR:
        return ar
    if lang == LANG_BOTH:
        return f"{en} | {ar}"
    return en


# =========================================================
# CLI texts (English-only – terminal output)
# =========================================================
CLI_TR = {
    "enter_path": "Enter module path:",
    "invalid_path": "Invalid path. Please enter a valid folder path.",
    "choose_lang": "Choose report language:\n1) English\n2) Arabic\n3) Both\n> ",
    "menu_title": "Choose an action:",
    "press_enter": "Press Enter to return to menu...",
    "search_title": "Search inside module",
    "search_type": "Search for:\n1) Model\n2) View ID\n3) Button\n4) Field\n5) Any text\n> ",
    "search_query": "Enter search query:",
    "export_title": "Export report",
    "export_choose": "Choose export:\n1) README.md\n2) report.json\n3) Both\n> ",
    "export_done": "Export completed.",
    "compare_title": "Compare modules",
    "enter_path_2": "Enter second module path:",
}

MENU_ITEMS_EN = [
    "1) Full module overview",
    "2) Views analysis (UI)",
    "3) Models & relations",
    "4) Workflow & states",
    "5) Buttons & user actions",
    "6) Executive summary",
    "7) Search inside module",
    "8) Complexity & risk analysis",
    "9) Export report (MD/JSON)",
    "10) Compare with another module",
    "0) Exit",
]


# =========================================================
# Markdown styling helpers
# =========================================================
def md_title(title: str, icon: str = "📌"):
    print("\n")
    print("═" * 80)
    print(f"## {icon} {title}")
    print("─" * 80)
    print()


def md_note(text: str):
    print(f"> ℹ️ {text}\n")


def md_big_section(title: str, icon: str):
    print("\n" + "═" * 80)
    print(f"## {icon} {title}")
    print("═" * 80 + "\n")


def md_section(title: str, icon: str = "📌"):
    print("\n" + "-" * 80)
    print(f"### {icon} {title}")
    print("-" * 80 + "\n")


def md_kv(label: str, value: str, icon: str = "🔹"):
    print(f"{icon} **{label}:** `{value}`")


def md_block(text: str, icon: str = "ℹ️"):
    print(f"> {icon} {text}\n")


def md_list(items):
    for i in items:
        print(f"- `{i}`")


# =========================================================
# Titles & notes per menu option (report layer)
# =========================================================
RESULT_TITLES = {
    "1": {
        "icon": "📦",
        "title_en": "Full Module Overview",
        "title_ar": "نظرة شاملة على الموديول",
        "note_en": "High-level overview of the module structure and features.",
        "note_ar": "نظرة عالية المستوى على هيكل الموديول وميزاته.",
    },
    "2": {
        "icon": "🖼️",
        "title_en": "Views Analysis (UI)",
        "title_ar": "تحليل الواجهات (UI)",
        "note_en": "Detailed breakdown of UI views grouped by model.",
        "note_ar": "تفصيل الواجهات وتجميعها حسب الموديل.",
    },
    "3": {
        "icon": "🧩",
        "title_en": "Models & Relations",
        "title_ar": "الموديلات والعلاقات",
        "note_en": "Models used by the module and their relationships.",
        "note_ar": "الموديلات المستخدمة والعلاقات بينها.",
    },
    "4": {
        "icon": "🔄",
        "title_en": "Workflow & States",
        "title_ar": "سير العمل والحالات",
        "note_en": "Workflow-related fields and state transitions (heuristic).",
        "note_ar": "حقول سير العمل وانتقالات الحالة (تقديري).",
    },
    "5": {
        "icon": "🖱️",
        "title_en": "Buttons & User Actions",
        "title_ar": "الأزرار وإجراءات المستخدم",
        "note_en": "Detected buttons and user-triggered actions.",
        "note_ar": "الأزرار والإجراءات التي ينفذها المستخدم.",
    },
    "6": {
        "icon": "📝",
        "title_en": "Executive Summary",
        "title_ar": "ملخص تنفيذي سريع",
        "note_en": "Quick executive-level summary of the module.",
        "note_ar": "ملخص سريع للإدارة عن الموديول.",
    },
    "7": {
        "icon": "🔍",
        "title_en": "Search Results",
        "title_ar": "نتائج البحث",
        "note_en": "Search results inside the module files.",
        "note_ar": "نتائج البحث داخل ملفات الموديول.",
    },
    "8": {
        "icon": "⚠️",
        "title_en": "Complexity & Risk Analysis",
        "title_ar": "تحليل التعقيد والمخاطر",
        "note_en": "Estimated complexity and risk level (heuristic).",
        "note_ar": "تقدير مستوى التعقيد والمخاطر (تقديري).",
    },
    "9": {
        "icon": "📤",
        "title_en": "Export Report",
        "title_ar": "تصدير التقرير",
        "note_en": "Generated export files and paths.",
        "note_ar": "ملفات التصدير والمسارات.",
    },
    "10": {
        "icon": "🔀",
        "title_en": "Module Comparison",
        "title_ar": "مقارنة الموديولات",
        "note_en": "Differences between two analyzed modules.",
        "note_ar": "الفروقات بين موديولين.",
    },
}

# =========================================================
# Parsing utilities
# =========================================================
VIEW_TAGS = ("form", "tree", "kanban", "search", "calendar")


def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def strip_ns(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


# =========================================================
# Data model
# =========================================================
@dataclass
class ViewEntry:
    view_id: str
    model: str
    inherited: bool
    counts: dict


@dataclass
class RelationEntry:
    field_name: str
    rel_type: str  # Many2one/One2many/Many2many
    comodel: str


@dataclass
class ModuleReport:
    module_path: str
    module_name: str

    manifest_summary: str | None
    manifest_description: str | None

    models_new: list
    models_inherited: list
    models_used_all: list
    wizards: int
    portal_support: bool
    cron_jobs: bool
    selections_by_field: dict
    views: list
    buttons: list
    relations_by_model: dict
    structure_folders: list


# =========================================================
# Analyzer
# =========================================================
import ast


class OdooModuleAnalyzer:
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.module_name = os.path.basename(module_path.rstrip("\\/"))

        self.models_new = set()
        self.models_inherited = set()
        self.portal_support = False
        self.cron_jobs = False
        self.wizards = 0

        self.selections_by_field = defaultdict(set)
        self.views = []
        self.buttons = set()

        self.relations_by_model = defaultdict(list)
        self.structure_folders = set()
        self._text_index = []

        # 🆕 Manifest info
        self.manifest_summary = None
        self.manifest_description = None

    # -----------------------------------------------------
    # Read __manifest__.py safely
    # -----------------------------------------------------
    def _read_manifest(self):
        manifest_path = os.path.join(self.module_path, "__manifest__.py")
        if not os.path.isfile(manifest_path):
            return

        try:
            content = read_file(manifest_path)
            data = ast.literal_eval(content)
            if isinstance(data, dict):
                self.manifest_summary = data.get("summary")
                self.manifest_description = data.get("description")
        except Exception:
            pass

    # -----------------------------------------------------
    # Main analyzer
    # -----------------------------------------------------
    def analyze(self) -> ModuleReport:
        self._read_manifest()

        for root, dirs, files in os.walk(self.module_path):
            for d in dirs:
                self.structure_folders.add(d)

            for file in files:
                full_path = os.path.join(root, file)

                # Python files
                if file.endswith(".py"):
                    content = read_file(full_path)
                    if not content.strip():
                        continue

                    self._text_index.append((full_path, content))

                    self.models_new.update(re.findall(r"_name\s*=\s*['\"](.+?)['\"]", content))
                    self.models_inherited.update(re.findall(r"_inherit\s*=\s*['\"](.+?)['\"]", content))

                    if "portal" in content.lower():
                        self.portal_support = True

                    if "TransientModel" in content:
                        self.wizards += 1

                    for m in re.finditer(
                            r"(\w+)\s*=\s*fields\.Selection\s*\((\[.*?\])",
                            content,
                            re.S,
                    ):
                        field_name = m.group(1)
                        block = m.group(2)
                        for val in re.findall(r"\('([^']+)'", block):
                            self.selections_by_field[field_name].add(val)

                    file_models = set(re.findall(r"_name\s*=\s*['\"](.+?)['\"]", content))
                    file_models |= set(re.findall(r"_inherit\s*=\s*['\"](.+?)['\"]", content))
                    if file_models:
                        rels = self._extract_relations(content)
                        for mdl in file_models:
                            self.relations_by_model[mdl].extend(rels)

                # XML files
                elif file.endswith(".xml"):
                    xml = read_file(full_path)
                    if not xml.strip():
                        continue

                    self._text_index.append((full_path, xml))

                    if "ir.cron" in xml:
                        self.cron_jobs = True

                    try:
                        root_xml = ET.fromstring(xml)
                    except Exception:
                        continue

                    for rec in root_xml.iter("record"):
                        if rec.attrib.get("model") != "ir.ui.view":
                            continue

                        view_id = rec.attrib.get("id", "unknown_view")

                        model_field = rec.find("field[@name='model']")
                        view_model = (
                            model_field.text.strip()
                            if model_field is not None and model_field.text
                            else "unknown.model"
                        )

                        is_inherited = rec.find("field[@name='inherit_id']") is not None
                        arch_field = rec.find("field[@name='arch']")
                        if arch_field is None:
                            continue

                        arch_text = ET.tostring(arch_field, encoding="unicode")
                        counts = {k: 0 for k in VIEW_TAGS}

                        try:
                            arch_xml = ET.fromstring(f"<root>{arch_text}</root>")
                        except Exception:
                            for k in VIEW_TAGS:
                                counts[k] += len(re.findall(rf"<{k}\b", arch_text))
                            self.views.append(
                                ViewEntry(view_id=view_id, model=view_model, inherited=is_inherited, counts=counts)
                            )
                            continue

                        for el in arch_xml.iter():
                            tag = strip_ns(el.tag)
                            if tag in counts:
                                counts[tag] += 1
                            if tag == "button" and el.attrib.get("type") in ("object", "action"):
                                if el.attrib.get("name"):
                                    self.buttons.add(el.attrib["name"])

                        self.views.append(
                            ViewEntry(view_id=view_id, model=view_model, inherited=is_inherited, counts=counts)
                        )

        return ModuleReport(
            module_path=self.module_path,
            module_name=self.module_name,
            models_new=sorted(self.models_new),
            models_inherited=sorted(self.models_inherited),
            models_used_all=sorted(self.models_new | self.models_inherited),
            wizards=self.wizards,
            portal_support=self.portal_support,
            cron_jobs=self.cron_jobs,
            selections_by_field={k: sorted(v) for k, v in self.selections_by_field.items()},
            views=[asdict(v) for v in self.views],
            buttons=sorted(self.buttons),
            relations_by_model=self.relations_by_model,
            structure_folders=sorted(self.structure_folders),
            # 🆕 Manifest
            manifest_summary=self.manifest_summary,
            manifest_description=self.manifest_description,
        )

    def _extract_relations(self, content: str):
        rels = []
        for m in re.finditer(
                r"(\w+)\s*=\s*fields\.(Many2one|One2many|Many2many)\s*\(\s*['\"]([^'\"]+)['\"]",
                content,
        ):
            rels.append(
                RelationEntry(
                    field_name=m.group(1),
                    rel_type=m.group(2),
                    comodel=m.group(3),
                )
            )
        return rels


# =========================================================
# Views grouping helper
# =========================================================
def group_views_by_model(rep: ModuleReport):
    grouped = defaultdict(lambda: {"main": [], "inherited": []})
    for v in rep.views:
        model = v.get("model", "unknown.model")
        inherited = bool(v.get("inherited"))
        entry = {"view_id": v.get("view_id"), "counts": v.get("counts", {k: 0 for k in VIEW_TAGS})}
        (grouped[model]["inherited"] if inherited else grouped[model]["main"]).append(entry)
    return dict(sorted(grouped.items()))


# =========================================================
# Renderers (write to README via ResultWriter)
# =========================================================
def render_overview(rep: ModuleReport, lang: str):
    md_big_section(L("Module Overview", "نظرة عامة على الموديول", lang), "🧩")

    md_section(L("Module Name", "اسم الموديول", lang), "🏷️")
    md_kv(L("Module", "الموديول", lang), rep.module_name, "📦")

    md_section(L("Description", "الوصف", lang), "📝")
    md_block(
        L(
            "This module extends and customizes existing Odoo functionality.",
            "هذا الموديول يوسّع ويخصص وظائف أودو الحالية.",
            lang,
        ),
        "📖",
    )

    md_big_section(L("Models Used", "الموديلات المستخدمة", lang), "🏗️")

    md_section(L("Models Summary", "ملخص الموديلات", lang), "📊")
    print(f"- 🆕 **{L('New Models', 'موديلات جديدة', lang)}:** `{len(rep.models_new)}`")
    print(f"- ♻️ **{L('Inherited Models', 'موديلات موروثة', lang)}:** `{len(rep.models_inherited)}`\n")

    if rep.models_used_all:
        md_section(L("Models List", "قائمة الموديلات", lang), "📋")
        md_list(rep.models_used_all)
    else:
        md_block(L("No models detected", "لا يوجد موديلات", lang), "⚠️")

    md_big_section(L("Wizards", "الـ Wizards", lang), "🧙")
    print(f"- 🔢 **{L('Total Wizards', 'إجمالي الـ Wizards', lang)}:** `{rep.wizards}`")

    md_big_section(L("Selection Values (by field)", "قيم Selection حسب الحقل", lang), "🎛️")
    if rep.selections_by_field:
        for field, vals in rep.selections_by_field.items():
            print(f"\n### 🔄 `{field}`")
            print(" · ".join([f"`{v}`" for v in vals]))
    else:
        md_block(L("No selection fields found", "لا يوجد", lang), "⚠️")

    md_big_section(L("Buttons (User Actions)", "الأزرار (إجراءات المستخدم)", lang), "🖱️")
    if rep.buttons:
        md_list(rep.buttons)
    else:
        md_block(L("No buttons detected", "لا يوجد أزرار", lang), "⚠️")

    md_big_section(L("Views Breakdown (by model)", "تفصيل الواجهات حسب الموديل", lang), "🖼️")
    grouped = group_views_by_model(rep)
    if not grouped:
        md_block(L("No views found", "لا يوجد واجهات", lang), "⚠️")
    else:
        for model, groups in grouped.items():
            print(f"\n### 📦 `{model}`")

            if groups["main"]:
                print(f"🟢 **{L('Main Views', 'واجهات أساسية', lang)}**")
                for v in groups["main"]:
                    c = v["counts"]
                    print(
                        f"- `{v['view_id']}` → form:{c['form']} tree:{c['tree']} kanban:{c['kanban']} search:{c['search']} calendar:{c['calendar']}")

            if groups["inherited"]:
                print(f"\n🟡 **{L('Inherited Views', 'واجهات موروثة', lang)}**")
                for v in groups["inherited"]:
                    c = v["counts"]
                    print(
                        f"- `{v['view_id']}` → form:{c['form']} tree:{c['tree']} kanban:{c['kanban']} search:{c['search']} calendar:{c['calendar']}")

    md_big_section(L("System Capabilities", "خصائص النظام", lang), "⚙️")
    print(
        f"- 🌐 **{L('Portal Support', 'دعم البورتال', lang)}:** `{L('Yes', 'نعم', lang) if rep.portal_support else L('No', 'لا', lang)}`")
    print(
        f"- ⏱️ **{L('Cron Jobs', 'مهام Cron', lang)}:** `{L('Yes', 'نعم', lang) if rep.cron_jobs else L('No', 'لا', lang)}`")

    md_big_section(L("Module Structure", "هيكل الموديول", lang), "🗂️")
    if rep.structure_folders:
        for f in rep.structure_folders:
            print(f"- `{f}`")
    else:
        md_block(L("No folders detected", "لا يوجد", lang), "⚠️")


def render_views(rep: ModuleReport, lang: str):
    md_big_section(L("Views Analysis (UI)", "تحليل الواجهات (UI)", lang), "🖼️")

    grouped = group_views_by_model(rep)
    if not grouped:
        md_block(L("No views found", "لا يوجد واجهات", lang), "⚠️")
        return

    for model, groups in grouped.items():
        print(f"\n### 📦 `{model}`")

        if groups["main"]:
            print(f"🟢 **{L('Main Views', 'واجهات أساسية', lang)}**")
            for v in groups["main"]:
                c = v["counts"]
                print(
                    f"- `{v['view_id']}` → form:{c['form']} tree:{c['tree']} kanban:{c['kanban']} search:{c['search']} calendar:{c['calendar']}")

        if groups["inherited"]:
            print(f"\n🟡 **{L('Inherited Views', 'واجهات موروثة', lang)}**")
            for v in groups["inherited"]:
                c = v["counts"]
                print(
                    f"- `{v['view_id']}` → form:{c['form']} tree:{c['tree']} kanban:{c['kanban']} search:{c['search']} calendar:{c['calendar']}")


def render_models_relations(rep: ModuleReport, lang: str):
    md_big_section(L("Models & Relations", "الموديلات والعلاقات", lang), "🧩")

    md_section(L("Models Used", "الموديلات المستخدمة", lang), "📦")
    if rep.models_used_all:
        for m in rep.models_used_all:
            print(f"- `{m}`")
    else:
        md_block(L("None", "لا يوجد", lang), "⚠️")

    md_section(L("Relations", "العلاقات", lang), "🔗")
    any_rel = False

    for model in sorted(rep.relations_by_model.keys()):
        rels = rep.relations_by_model[model]
        if not rels:
            continue

        any_rel = True
        print(f"\n### 📦 `{model}`")

        for r in rels:
            # يدعم dataclass
            rel_type = r.rel_type
            field_name = r.field_name
            comodel = r.comodel

            print(f"- `{rel_type}` : `{field_name}` → `{comodel}`")

    if not any_rel:
        md_block(L("No relations detected", "لا توجد علاقات", lang), "⚠️")


def render_workflow(rep: ModuleReport, lang: str):
    md_big_section(L("Workflow & States", "سير العمل والحالات", lang), "🔄")

    wf_names = {"state", "status", "stage", "stage_id", "approval_state"}
    workflows = {k: v for k, v in rep.selections_by_field.items() if k in wf_names}

    if not workflows:
        md_block(L("No workflow fields detected.", "لم يتم اكتشاف حقول سير عمل.", lang), "⚠️")
        return

    for field, vals in workflows.items():
        print(f"- `{field}`: " + " → ".join(vals))


def render_buttons(rep: ModuleReport, lang: str):
    md_big_section(L("Buttons & User Actions", "الأزرار وإجراءات المستخدم", lang), "🖱️")
    if rep.buttons:
        md_list(rep.buttons)
    else:
        md_block(L("No buttons detected", "لا يوجد أزرار", lang), "⚠️")


def render_summary(rep: ModuleReport, lang: str):
    md_big_section(L("Executive Summary", "الملخص التنفيذي", lang), "📝")

    view_records = len(rep.views)
    buttons = len(rep.buttons)
    models_total = len(rep.models_used_all)

    wf_names = {"state", "status", "stage", "stage_id", "approval_state"}
    workflows = [k for k in rep.selections_by_field.keys() if k in wf_names]

    main_views = sum(1 for v in rep.views if not v.get("inherited"))
    inherited_views = sum(1 for v in rep.views if v.get("inherited"))

    rows = [
        (L("Models", "الموديلات", lang), models_total),
        (L("View records", "عدد الواجهات (Records)", lang), view_records),
        (L("Main Views", "واجهات أساسية", lang), main_views),
        (L("Inherited Views", "واجهات موروثة", lang), inherited_views),
        (L("Buttons", "الأزرار", lang), buttons),
        (L("Wizards", "عدد الـ Wizards", lang), rep.wizards),
        (L("Workflow fields", "حقول سير العمل", lang), len(workflows)),
        (L("Cron jobs", "مهام Cron", lang), L("Yes", "نعم", lang) if rep.cron_jobs else L("No", "لا", lang)),
        (L("Portal", "البورتال", lang), L("Yes", "نعم", lang) if rep.portal_support else L("No", "لا", lang)),
    ]

    for k, v in rows:
        print(f"- {k}: {v}")


def render_risk(rep: ModuleReport, lang: str):
    md_big_section(L("Complexity & Risk Analysis", "تحليل التعقيد والمخاطر", lang), "⚠️")

    models_total = len(rep.models_used_all)
    view_records = len(rep.views)
    buttons = len(rep.buttons)
    selection_fields = len(rep.selections_by_field)

    score = 0
    score += 2 if models_total >= 30 else 1 if models_total >= 15 else 0
    score += 2 if view_records >= 40 else 1 if view_records >= 20 else 0
    score += 1 if buttons >= 20 else 0
    score += 2 if selection_fields >= 10 else 1 if selection_fields >= 5 else 0
    score += 1 if rep.cron_jobs else 0

    if score >= 6:
        level_en, level_ar = "High complexity", "تعقيد عالي"
    elif score >= 3:
        level_en, level_ar = "Medium complexity", "تعقيد متوسط"
    else:
        level_en, level_ar = "Low complexity", "تعقيد منخفض"

    print(f"- {L('Level', 'المستوى', lang)}: {L(level_en, level_ar, lang)}")
    print(f"- {L('Models', 'الموديلات', lang)}: {models_total}")
    print(f"- {L('View records', 'الواجهات (Records)', lang)}: {view_records}")
    print(f"- {L('Buttons', 'الأزرار', lang)}: {buttons}")
    print(f"- {L('Selection fields', 'حقول Selection', lang)}: {selection_fields}")
    print(f"- {L('Cron jobs', 'مهام Cron', lang)}: {L('Yes', 'نعم', lang) if rep.cron_jobs else L('No', 'لا', lang)}")


# =========================================================
# Search / Export / Compare
# =========================================================
def do_search(rep: ModuleReport, analyzer: OdooModuleAnalyzer, lang: str, choice: str, q: str):
    if not q:
        md_block(L("None", "لا يوجد", lang), "⚠️")
        return

    if choice == "1":
        hits = [m for m in rep.models_used_all if q.lower() in m.lower()]
        for h in hits or [L("None", "لا يوجد", lang)]:
            print(f"- {h}")

    elif choice == "2":
        hits = [v for v in rep.views if q.lower() in (v.get("view_id") or "").lower()]
        for v in hits:
            print(f"- {v.get('view_id')} (model={v.get('model')}, inherited={v.get('inherited')})")
        if not hits:
            print(f"- {L('None', 'لا يوجد', lang)}")

    elif choice == "3":
        hits = [b for b in rep.buttons if q.lower() in b.lower()]
        for b in hits or [L("None", "لا يوجد", lang)]:
            print(f"- {b}")

    elif choice == "4":
        found = False
        for field in rep.selections_by_field:
            if q.lower() in field.lower():
                print(f"- Selection: {field}")
                found = True
        for mdl, rels in rep.relations_by_model.items():
            for r in rels:
                if q.lower() in r["field_name"].lower():
                    print(f"- {mdl}: {r['rel_type']} {r['field_name']} → {r['comodel']}")
                    found = True
        if not found:
            print(f"- {L('None', 'لا يوجد', lang)}")

    elif choice == "5":
        matches = [p for p, c in analyzer._text_index if q.lower() in c.lower()]
        for p in matches[:50]:
            print(f"- {p}")
        if not matches:
            print(f"- {L('None', 'لا يوجد', lang)}")


def asdict_from_report(rep: ModuleReport):
    return {
        "module_path": rep.module_path,
        "module_name": rep.module_name,
        "models_new": rep.models_new,
        "models_inherited": rep.models_inherited,
        "models_used_all": rep.models_used_all,
        "wizards": rep.wizards,
        "portal_support": rep.portal_support,
        "cron_jobs": rep.cron_jobs,
        "selections_by_field": rep.selections_by_field,
        "views": rep.views,
        "buttons": rep.buttons,
        "relations_by_model": {
            model: [
                {
                    "field_name": r.field_name,
                    "type": r.rel_type,
                    "comodel": r.comodel,
                }
                for r in rels
            ]
            for model, rels in rep.relations_by_model.items()
        },
        "structure_folders": rep.structure_folders,
    }


def build_markdown(rep: ModuleReport, lang: str) -> str:
    lines = []

    # -------------------------------------------------
    # Title
    # -------------------------------------------------
    title = L("Odoo Module Inspector Report", "تقرير فحص موديول أودو", lang)
    lines.append(f"# {title}")
    lines.append("")

    lines.append(f"**{L('Module', 'الموديول', lang)}:** `{rep.module_name}`")
    lines.append(f"**{L('Path', 'المسار', lang)}:** `{rep.module_path}`")
    lines.append("")

    # -------------------------------------------------
    # Manifest summary / description
    # -------------------------------------------------
    if rep.manifest_summary or rep.manifest_description:
        lines.append(f"## {L('Module Description', 'وصف الموديول', lang)}")

        if rep.manifest_summary:
            lines.append(
                f"- **{L('Summary', 'الملخص', lang)}:** {rep.manifest_summary}"
            )

        if rep.manifest_description:
            lines.append("")
            lines.append(rep.manifest_description.strip())

        lines.append("")

    # -------------------------------------------------
    # Executive Summary
    # -------------------------------------------------
    lines.append(f"## {L('Executive Summary', 'الملخص التنفيذي', lang)}")
    lines.append(f"- {L('Models', 'عدد الموديلات', lang)}: **{len(rep.models_used_all)}**")
    lines.append(f"- {L('View records', 'عدد الواجهات', lang)}: **{len(rep.views)}**")
    lines.append(f"- {L('Buttons', 'عدد الأزرار', lang)}: **{len(rep.buttons)}**")
    lines.append(f"- {L('Wizards', 'عدد الـ Wizards', lang)}: **{rep.wizards}**")
    lines.append(
        f"- {L('Cron jobs', 'مهام Cron', lang)}: "
        f"**{L('Yes', 'نعم', lang) if rep.cron_jobs else L('No', 'لا', lang)}**"
    )
    lines.append(
        f"- {L('Portal', 'البورتال', lang)}: "
        f"**{L('Yes', 'نعم', lang) if rep.portal_support else L('No', 'لا', lang)}**"
    )
    lines.append("")

    # -------------------------------------------------
    # Models
    # -------------------------------------------------
    lines.append(f"## {L('Models Used', 'الموديلات المستخدمة', lang)}")
    if rep.models_used_all:
        for m in rep.models_used_all:
            lines.append(f"- `{m}`")
    else:
        lines.append(f"- {L('None', 'لا يوجد', lang)}")
    lines.append("")

    # -------------------------------------------------
    # Selection fields
    # -------------------------------------------------
    lines.append(f"## {L('Selection Values (by field)', 'قيم Selection حسب الحقل', lang)}")
    if rep.selections_by_field:
        for field, vals in rep.selections_by_field.items():
            lines.append(
                f"- **{field}**: " + ", ".join([f"`{v}`" for v in vals])
            )
    else:
        lines.append(f"- {L('None', 'لا يوجد', lang)}")
    lines.append("")

    # -------------------------------------------------
    # Buttons
    # -------------------------------------------------
    lines.append(f"## {L('Buttons', 'الأزرار', lang)}")
    if rep.buttons:
        for b in rep.buttons:
            lines.append(f"- `{b}`")
    else:
        lines.append(f"- {L('None', 'لا يوجد', lang)}")
    lines.append("")

    # -------------------------------------------------
    # Views
    # -------------------------------------------------
    lines.append(f"## {L('Views Breakdown (by model)', 'تفصيل الواجهات حسب الموديل', lang)}")

    grouped = defaultdict(lambda: {"main": [], "inherited": []})
    for v in rep.views:
        model = v.get("model", "unknown.model")
        if v.get("inherited"):
            grouped[model]["inherited"].append(v)
        else:
            grouped[model]["main"].append(v)

    for model in sorted(grouped.keys()):
        lines.append(f"### `{model}`")

        if grouped[model]["main"]:
            lines.append(f"- **{L('Main Views', 'واجهات أساسية', lang)}**")
            for v in sorted(grouped[model]["main"], key=lambda x: x.get("view_id") or ""):
                c = v.get("counts", {})
                lines.append(
                    f"  - `{v.get('view_id')}`: "
                    f"form={c.get('form', 0)}, "
                    f"tree={c.get('tree', 0)}, "
                    f"kanban={c.get('kanban', 0)}, "
                    f"search={c.get('search', 0)}, "
                    f"calendar={c.get('calendar', 0)}"
                )

        if grouped[model]["inherited"]:
            lines.append(f"- **{L('Inherited Views', 'واجهات موروثة', lang)}**")
            for v in sorted(grouped[model]["inherited"], key=lambda x: x.get("view_id") or ""):
                c = v.get("counts", {})
                lines.append(
                    f"  - `{v.get('view_id')}`: "
                    f"form={c.get('form', 0)}, "
                    f"tree={c.get('tree', 0)}, "
                    f"kanban={c.get('kanban', 0)}, "
                    f"search={c.get('search', 0)}, "
                    f"calendar={c.get('calendar', 0)}"
                )

        lines.append("")

    return "\n".join(lines)


def export_report(rep: ModuleReport, lang: str):
    # Export prompts stay in terminal (English only).
    print(CLI_TR["export_title"])
    choice = input(CLI_TR["export_choose"]).strip()

    base_dir = rep.module_path
    md_path = os.path.join(base_dir, "README_INSPECTOR.md")
    json_path = os.path.join(base_dir, "report_inspector.json")

    if choice in ("1", "3"):
        md = build_markdown(rep, lang)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)

    if choice in ("2", "3"):
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(asdict_from_report(rep), f, ensure_ascii=False, indent=2)

    print(CLI_TR["export_done"])
    if choice in ("1", "3"):
        print(f"- {md_path}")
    if choice in ("2", "3"):
        print(f"- {json_path}")


def compare_reports(rep1: ModuleReport, rep2: ModuleReport, lang: str):
    md_big_section(L("Module Comparison", "مقارنة الموديولات", lang), "🔀")
    print(f"`{rep1.module_name}`  <->  `{rep2.module_name}`\n")

    def diff_set(label_en, label_ar, s1, s2):
        added = sorted(list(set(s2) - set(s1)))
        removed = sorted(list(set(s1) - set(s2)))

        print(f"### {L(label_en, label_ar, lang)}")
        print(f"- {L('Added', 'مضاف', lang)}: {len(added)}")
        for x in added[:30]:
            print(f"  + {x}")
        if len(added) > 30:
            print(f"  ... ({len(added) - 30} more)")

        print(f"- {L('Removed', 'محذوف', lang)}: {len(removed)}")
        for x in removed[:30]:
            print(f"  - {x}")
        if len(removed) > 30:
            print(f"  ... ({len(removed) - 30} more)")
        print("")

    diff_set("Models Used", "الموديلات المستخدمة", rep1.models_used_all, rep2.models_used_all)
    diff_set("Buttons", "الأزرار", rep1.buttons, rep2.buttons)

    v1 = sorted(list({v.get("view_id") for v in rep1.views if v.get("view_id")}))
    v2 = sorted(list({v.get("view_id") for v in rep2.views if v.get("view_id")}))
    diff_set("Views", "الواجهات", v1, v2)

    wf_names = {"state", "status", "stage", "stage_id", "approval_state"}
    w1 = sorted([k for k in rep1.selections_by_field.keys() if k in wf_names])
    w2 = sorted([k for k in rep2.selections_by_field.keys() if k in wf_names])
    diff_set("Workflow fields", "حقول سير العمل", w1, w2)


# =========================================================
# CLI
# =========================================================
def choose_language() -> str:
    raw = input(CLI_TR["choose_lang"]).strip()
    if raw == "2":
        return LANG_AR
    if raw == "3":
        return LANG_BOTH
    return LANG_EN


def prompt_existing_path(prompt_text: str) -> str:
    while True:
        print(prompt_text)
        path = input("> ").strip().strip('"')
        if os.path.isdir(path):
            return path
        print("❌ " + CLI_TR["invalid_path"])


def main():
    module_path = prompt_existing_path(CLI_TR["enter_path"])
    lang = choose_language()

    analyzer = OdooModuleAnalyzer(module_path)
    rep = analyzer.analyze()

    while True:
        print("\n" + "=" * 60)
        print(CLI_TR["menu_title"])
        for item in MENU_ITEMS_EN:
            print(item)
        print("=" * 60)
        choice = input("> ").strip()

        if choice == "0":
            break

        meta = RESULT_TITLES.get(choice)
        if not meta:
            continue

        title = L(meta["title_en"], meta["title_ar"], lang)
        note = L(meta["note_en"], meta["note_ar"], lang)
        icon = meta["icon"]

        if choice == "1":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_overview(rep, lang)

        elif choice == "2":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_views(rep, lang)

        elif choice == "3":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_models_relations(rep, lang)

        elif choice == "4":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_workflow(rep, lang)

        elif choice == "5":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_buttons(rep, lang)

        elif choice == "6":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_summary(rep, lang)

        elif choice == "7":
            # Terminal inputs (English only)
            print(CLI_TR["search_title"])
            search_type = input(CLI_TR["search_type"]).strip()
            search_query = input(CLI_TR["search_query"] + "\n> ").strip()

            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                do_search(rep, analyzer, lang, search_type, search_query)

        elif choice == "8":
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                render_risk(rep, lang)

        elif choice == "9":
            # export is written to module folder; keep prompts in terminal.
            export_report(rep, lang)

        elif choice == "10":
            p2 = prompt_existing_path(CLI_TR["enter_path_2"])
            analyzer2 = OdooModuleAnalyzer(p2)
            rep2 = analyzer2.analyze()
            with ResultWriter():
                md_title(title, icon)
                md_note(note)
                compare_reports(rep, rep2, lang)

        input("\n" + CLI_TR["press_enter"])


if __name__ == "__main__":
    main()
