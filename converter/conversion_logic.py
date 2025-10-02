"""
JSON Converter Logic
Ported from the original GUI application to work with Django
"""
import json
from collections import OrderedDict
from pathlib import Path
import traceback

# --------------------------- helpers ---------------------------

def ensure_namespace(sound_id: str) -> str:
    """Ensure sound ID has proper namespace"""
    s = (sound_id or "").strip()
    return s if ":" in s else f"pixelmon:{s}"

def convert_sounds(old_sounds):
    """Convert old sounds format to new format"""
    if not old_sounds or not isinstance(old_sounds, list):
        return []
    out = []
    for s in old_sounds:
        s = str(s).strip()
        if not s:
            continue
        out.append({"sound_id": ensure_namespace(s), "range": 14})
    return out

def particle_from_string(pstr):
    """Convert particle string to particle object"""
    if not pstr or not str(pstr).strip():
        return None
    return {
        "probability": 0.1,
        "options": {
            "type": "pixelmon:shiny",
            "diameter": 2.5,
            "lifetime": 30,
            "tint": {"red": 255, "green": 215, "blue": 0, "alpha": 255}
        }
    }

def has_any(d: dict, keys: list) -> bool:
    """Check if dict has any of the specified keys"""
    return any((k in d) and (d[k] is not None) for k in keys)

def wants_flying(movement: dict) -> bool:
    """Check if movement indicates flying capability"""
    if not isinstance(movement, dict):
        return False
    if movement.get("canFly") is True:
        return True
    if has_any(movement, ["flyingParameters", "mountedFlyingParameters"]):
        return True
    return False

def wants_swimming(movement: dict) -> bool:
    """Check if movement indicates swimming capability"""
    if not isinstance(movement, dict):
        return False
    if movement.get("canSurf") is True:
        return True
    if "swimmingParameters" in movement and movement["swimmingParameters"] is not None:
        return True
    return False

def pqc_to_bmd_path(pqc_path: str) -> str:
    """Convert PQC path to BMD path"""
    return str(Path(pqc_path).with_suffix(".bmd")).replace("\\", "/")

def build_animation_list(model_path: str, add_fly: bool, add_swim: bool):
    """Build animation list based on model path and capabilities"""
    base_dir = str(Path(model_path).parent).replace("\\", "/")
    def ap(name): return f"{base_dir}/{name}.bmd"
    anims = [
        OrderedDict([("type","idle"), ("animation", ap("idle"))]),
        OrderedDict([("type","walk"), ("animation", ap("walk"))]),
    ]
    if add_fly:
        anims.append(OrderedDict([("type","fly"), ("animation", ap("fly"))]))
    if add_swim:
        anims.append(OrderedDict([("type","swim"), ("animation", ap("swim"))]))
    # de-dup
    seen = set()
    out = []
    for a in anims:
        key = (a["type"], a["animation"])
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out

def derive_model_from_palette_paths(old_palette: dict) -> str or None:
    """Derive model path from palette texture/sprite paths"""
    base_hint = old_palette.get("texture") or old_palette.get("sprite")
    if not base_hint:
        return None
    base_dir = str(Path(base_hint).parent).replace("\\", "/")
    return f"{base_dir}/model.bmd"

def normalize_form_name(name: str) -> str:
    """Normalize form name, defaulting to 'base'"""
    return "base" if (name is None or str(name).strip() == "") else name

# --------------------------- ORDERING ---------------------------

TOP_ORDER = ["name", "dex", "defaultForms", "forms", "generation"]

FORM_HEAD_ORDER = [
    "name",
    "experienceGroup",
    "dimensions",
    "moves",
    "abilities",
    "movement",
    "aggression",
    "battleStats",
    "tags",
    "spawn",
    "possibleGenders",
    "genderProperties"
]

FORM_TAIL_ORDER = [
    "eggGroups",
    "types",
    "preEvolutions",
    "defaultBaseForm",
    "megaItems",
    "megas",
    "gigantamax",
    "eggCycles",
    "weight",
    "catchRate",
    "malePercentage",
    "evolutions",
    "evYields",
    "growth_data"  # must be last
]

SPAWN_ORDER = ["baseExp", "baseFriendship", "spawnLevel", "spawnLevelRange", "spawnLocations"]

def ordered(obj: dict, key_order: list) -> OrderedDict:
    """Create ordered dict with specified key order"""
    out = OrderedDict()
    if not isinstance(obj, dict):
        return obj
    for k in key_order:
        if k in obj:
            out[k] = obj[k]
    for k in obj:
        if k not in out:
            out[k] = obj[k]
    return out

def order_spawn(spawn_obj: dict):
    """Order spawn object keys"""
    if not isinstance(spawn_obj, dict):
        return spawn_obj
    return ordered(spawn_obj, SPAWN_ORDER)

def order_top(doc: dict):
    """Order top-level document keys"""
    return ordered(doc, TOP_ORDER)

# --------------------------- growth_data defaults ---------------------------

def make_growth_data() -> OrderedDict:
    """Create default growth_data object"""
    gd = OrderedDict()
    gd["mean"] = 40.0
    gd["standard_deviation"] = 2.0
    gd["min_render_scale"] = 0.7
    gd["max_render_scale"] = 1.3
    return gd

# --------------------------- core: model entries & wrappers ---------------------------

def make_model_entry(model_path: str, texture: str, emissive: str, add_fly: bool, add_swim: bool) -> OrderedDict:
    """Create a model entry with specified parameters"""
    # Key order: texture, model, animations, scale, (emissive)
    entry = OrderedDict()
    if texture:
        entry["texture"] = texture
    entry["model"] = model_path
    entry["animations"] = build_animation_list(model_path, add_fly, add_swim)
    entry["scale"] = 1.0
    if emissive:
        entry["emissive"] = emissive
    return entry

def wrap_models_with_predicate(entries: list) -> list:
    """Wrap model entries with predicate"""
    wrapper = OrderedDict()
    wrapper["model_predicate"] = OrderedDict([("type","pixelmon:always")])
    wrapper["models"] = entries or []
    return [wrapper]

# --------------------------- core conversion ---------------------------

def convert_palette(old_palette: dict, movement_for_rules: dict) -> OrderedDict:
    """Convert old palette format to new format"""
    out_pal = OrderedDict()

    # Palette stable keys
    if "name" in old_palette:
        out_pal["name"] = old_palette["name"]
    if "sprite" in old_palette:
        out_pal["sprite"] = old_palette["sprite"]

    snd = convert_sounds(old_palette.get("sounds"))
    if snd:
        out_pal["sounds"] = snd

    add_fly = wants_flying(movement_for_rules or {})
    add_swim = wants_swimming(movement_for_rules or {})

    texture = old_palette.get("texture")
    emissive = old_palette.get("emissive")

    # Build model entries from PQC (or derive)
    entries = []
    ml = old_palette.get("modelLocator") or {}
    pqc_list = []
    if isinstance(ml, dict):
        pqc_list = ml.get("pqc", [])
    if isinstance(pqc_list, str):
        pqc_list = [pqc_list]
    if not isinstance(pqc_list, list):
        pqc_list = []

    if pqc_list:
        for pqc in pqc_list:
            model_path = pqc_to_bmd_path(pqc)
            entries.append(make_model_entry(model_path, texture, emissive, add_fly, add_swim))
    else:
        derived = derive_model_from_palette_paths(old_palette)
        if derived:
            entries.append(make_model_entry(derived, texture, emissive, add_fly, add_swim))

    # Always wrap with predicate
    out_pal["models"] = wrap_models_with_predicate(entries)

    particle_obj = particle_from_string(old_palette.get("particle"))
    if particle_obj:
        out_pal["particle"] = particle_obj

    # Ensure tags exists (even if empty)
    out_pal["tags"] = old_palette.get("tags", [])

    return out_pal

def clone_models_for_shiny_wrapped(base_models_wrapped, shiny_texture_path: str):
    """Clone models for shiny variant"""
    if not (base_models_wrapped and isinstance(base_models_wrapped, list)):
        return None
    if not shiny_texture_path:
        return None

    base_wrapper = base_models_wrapped[0]
    base_entries = base_wrapper.get("models", []) if isinstance(base_wrapper, dict) else []
    new_entries = []
    for m in base_entries:
        clone = OrderedDict(m)
        # swap or set texture to shiny
        clone["texture"] = shiny_texture_path
        new_entries.append(clone)
    return wrap_models_with_predicate(new_entries)

def convert_form(old_form: dict, movement_fallback: dict = None) -> OrderedDict:
    """Convert old form format to new format"""
    # HEAD block
    head = OrderedDict()
    fname = normalize_form_name(old_form.get("name"))
    head["name"] = fname

    for k in ["experienceGroup","dimensions","moves","abilities","movement","aggression","battleStats","tags"]:
        if k in old_form:
            head[k] = old_form[k]

    movement_for_rules = old_form.get("movement") or movement_fallback or {}

    if "spawn" in old_form:
        head["spawn"] = order_spawn(old_form["spawn"])

    if "possibleGenders" in old_form:
        head["possibleGenders"] = old_form["possibleGenders"]

    # genderProperties with palettes
    gp = old_form.get("genderProperties", [])
    if isinstance(gp, list):
        new_gp = []
        for gp_entry in gp:
            if not isinstance(gp_entry, dict):
                continue
            gp_out = OrderedDict()
            if "gender" in gp_entry:
                gp_out["gender"] = gp_entry["gender"]

            palettes = gp_entry.get("palettes", [])
            new_palettes = []
            for pal in palettes:
                new_palettes.append(convert_palette(pal, movement_for_rules))

            # Ensure shiny has models wrapper by mirroring 'none' if needed
            base_pal = next((p for p in new_palettes if p.get("name") == "none"), None)
            shiny_pal = next((p for p in new_palettes if p.get("name") == "shiny"), None)
            if shiny_pal is not None:
                shiny_has_models = False
                if isinstance(shiny_pal.get("models"), list) and shiny_pal["models"]:
                    inner = shiny_pal["models"][0] if shiny_pal["models"] else {}
                    shiny_has_models = isinstance(inner, dict) and isinstance(inner.get("models"), list) and inner["models"]

                if not shiny_has_models:
                    orig_shiny = next((p for p in palettes if isinstance(p, dict) and p.get("name") == "shiny"), None)
                    shiny_tex = None
                    if isinstance(orig_shiny, dict):
                        shiny_tex = orig_shiny.get("texture") or orig_shiny.get("sprite")
                    if base_pal and base_pal.get("models"):
                        mirrored = clone_models_for_shiny_wrapped(base_pal["models"], shiny_tex)
                        if mirrored:
                            shiny_pal["models"] = mirrored
                    elif shiny_tex:
                        derived = derive_model_from_palette_paths({"texture": shiny_tex})
                        if derived:
                            shiny_pal["models"] = wrap_models_with_predicate([
                                make_model_entry(derived, shiny_tex, None, wants_flying(movement_for_rules), wants_swimming(movement_for_rules))
                            ])

            # Final guard: synthesize wrapper/entry from each palette's own texture/sprite if missing
            for idx, pal in enumerate(new_palettes):
                ok = False
                if isinstance(pal.get("models"), list) and pal["models"]:
                    inner = pal["models"][0]
                    ok = isinstance(inner, dict) and isinstance(inner.get("models"), list) and inner["models"]
                if not ok:
                    orig = palettes[idx] if idx < len(palettes) else {}
                    hint_tex = None
                    if isinstance(orig, dict):
                        hint_tex = orig.get("texture") or orig.get("sprite")
                    if not hint_tex:
                        hint_tex = pal.get("sprite")
                    if hint_tex:
                        derived = derive_model_from_palette_paths({"texture": hint_tex})
                        if derived:
                            pal["models"] = wrap_models_with_predicate([
                                make_model_entry(derived, hint_tex, None, wants_flying(movement_for_rules), wants_swimming(movement_for_rules))
                            ])
                    else:
                        pal["models"] = wrap_models_with_predicate([])

            if new_palettes:
                gp_out["palettes"] = new_palettes
            if "tags" in gp_entry:
                gp_out["tags"] = gp_entry["tags"]
            if gp_out:
                new_gp.append(gp_out)

        if new_gp:
            head["genderProperties"] = new_gp

    # TAIL block (after palettes) — always include growth_data with defaults
    tail = OrderedDict()
    for k in ["eggGroups","types","preEvolutions","defaultBaseForm","megaItems","megas","gigantamax","eggCycles","weight","catchRate","malePercentage","evolutions","evYields"]:
        if k in old_form and k != "spawn":
            tail[k] = old_form[k]

    # ALWAYS add growth_data with requested defaults, as last field
    tail["growth_data"] = make_growth_data()

    # Merge HEAD then TAIL preserving blocks
    form = OrderedDict()
    for k in FORM_HEAD_ORDER:
        if k in head:
            form[k] = head[k]
    for k in tail:
        form[k] = tail[k]
    return form

def convert_document(old_doc: dict) -> OrderedDict:
    """Convert entire document from old format to new format"""
    new_doc = OrderedDict()

    # Top-level: name, dex, defaultForms, forms, generation (last)
    if "name" in old_doc: new_doc["name"] = old_doc["name"]
    if "dex" in old_doc: new_doc["dex"] = old_doc["dex"]

    # defaultForms BEFORE forms
    old_forms = old_doc.get("forms", [])
    norm_first_form = "base"
    if isinstance(old_forms, list) and old_forms:
        norm_first_form = normalize_form_name(old_forms[0].get("name"))
    odf = old_doc.get("defaultForms") or []
    desired_default = odf[0] if (odf and str(odf[0]).strip()) else norm_first_form
    new_doc["defaultForms"] = [desired_default]

    # forms
    new_forms = []
    movement_fallback = {}
    if isinstance(old_forms, list) and old_forms:
        mf = old_forms[0].get("movement", {})
        if isinstance(mf, dict):
            movement_fallback = mf
    for f in old_forms:
        new_forms.append(convert_form(f, movement_fallback))
    new_doc["forms"] = new_forms

    # generation LAST
    if "generation" in old_doc:
        new_doc["generation"] = old_doc["generation"]

    # enforce top order
    return order_top(new_doc)

# --------------------------- I/O functions ---------------------------

def convert_json_string(json_string: str) -> str:
    """Convert JSON string from old format to new format"""
    try:
        old_doc = json.loads(json_string)
        new_doc = convert_document(old_doc)
        return json.dumps(new_doc, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Error converting JSON: {str(e)}")

def convert_json_file_content(file_content: str, filename: str = "unknown") -> str:
    """Convert JSON file content from old format to new format"""
    try:
        old_doc = json.loads(file_content)
        new_doc = convert_document(old_doc)
        return json.dumps(new_doc, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Error converting JSON file '{filename}': {str(e)}")