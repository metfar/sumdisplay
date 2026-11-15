#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
#import warnings;
#warnings.filterwarnings("ignore", category=UserWarning);

"""sumdisp: visual comfort and XRandR display profiles (first usable edition)."""

import argparse;
import json;
import os;
import pathlib;
import re;
import shutil;
import socket;
import subprocess;
import sys;
import threading;
import time;

VERSION = "0.1a19";
APP = pathlib.Path(sys.argv[0]).name;
CONFIG_DIR = pathlib.Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "sumdisp";
CONFIG_FILE = CONFIG_DIR / "config.json";
PROFILES_DIR = CONFIG_DIR / "profiles";
HISTORY_LIMIT = 24;
DEFAULT_GAMMA = (1.0, 1.0, 1.0);
LEGACY_GAMMA = (0.7, 0.7, 0.65);


LANGUAGES = ("en", "fr", "es");
TRANSLATIONS = {
    "fr": {
        'Yes': 'Oui', 'No': 'Non', 'Confirm resolution': 'Confirmer la résolution',
        'Delete profile': 'Supprimer le profil', 'Options': 'Options', 'Search or select an option:': 'Rechercher ou choisir une option :', 'Type to search...': 'Saisir pour rechercher...', 'Select': 'Sélectionner', 'Save': 'Enregistrer', 'Delete': 'Supprimer', 'Cancel': 'Annuler',
        "Display": "Écran", "Default": "Par défaut", "Custom": "Personnalisée", "original (1:1)": "origine (1:1)", "Physical mode": "Mode physique", "read-only": "lecture seule",
        "Resolution": "Résolution", "Profile": "Profil", "Load": "Charger",
        "Show resolution catalog (by size)": "Afficher le catalogue des résolutions (par taille)",
        "Brightness": "Luminosité", "Apply": "Appliquer", "Save": "Enregistrer",
        "Exit": "Quitter", "Save profile": "Enregistrer le profil",
        "Load profile": "Charger le profil", "Saved profiles:": "Profils enregistrés :",
        "Profile name:": "Nom du profil :", "Delete": "Supprimer", "Cancel": "Annuler",
        "Choose a profile; you may edit its name when saving.": "Choisissez un profil ; vous pouvez modifier son nom avant l'enregistrement.",
        "Choose a profile from the dropdown list.": "Choisissez un profil dans la liste déroulante.",
        "Saved configurations:": "Configurations enregistrées :",
        "Confirm overwrite": "Confirmer le remplacement", "Confirm deletion": "Confirmer la suppression",
        "Overwrite this profile?": "Remplacer ce profil ?", "Delete this profile permanently?": "Supprimer définitivement ce profil ?",
        "Yes, overwrite": "Oui, remplacer", "Yes, delete": "Oui, supprimer",
        "Ready. Only Exit or Esc closes the TUI.": "Prêt. Seuls Quitter ou Échap ferment le TUI.",
        "Configuration applied.": "Configuration appliquée.", "Profile loaded:": "Profil chargé :",
        "Profile saved:": "Profil enregistré :", "Profile overwritten:": "Profil remplacé :",
        "Profile deleted:": "Profil supprimé :", "Current": "Actuel",
        "No profiles are available for this display.": "Aucun profil disponible pour cet écran.",
        "Select a saved profile to load.": "Sélectionnez un profil enregistré à charger.",
        "Select an existing profile.": "Sélectionnez un profil existant.",
        "Used custom": "Personnalisées utilisées", "Used predefined": "Prédéfinies utilisées", "Unused custom": "Personnalisées non utilisées",
        "Visual comfort": "Confort visuel", "Keep this resolution?": "Conserver cette résolution ?",
    },
    "es": {
        'Yes': 'Sí', 'No': 'No', 'Confirm resolution': 'Confirmar resolución',
        'Delete profile': 'Eliminar perfil', 'Options': 'Opciones', 'Search or select an option:': 'Buscar o seleccionar una opción:', 'Type to search...': 'Escribir para buscar...', 'Select': 'Seleccionar', 'Save': 'Guardar', 'Delete': 'Eliminar', 'Cancel': 'Cancelar',
        "Display": "Monitor", "Default": "Predeterminada", "Custom": "Personalizada", "original (1:1)": "original (1:1)", "Physical mode": "Modo físico", "read-only": "solo lectura",
        "Resolution": "Resolución", "Profile": "Perfil", "Load": "Cargar",
        "Show resolution catalog (by size)": "Mostrar catálogo de resoluciones (por tamaño)",
        "Brightness": "Brillo", "Apply": "Aplicar", "Save": "Guardar",
        "Exit": "Salir", "Save profile": "Guardar perfil", "Load profile": "Cargar perfil",
        "Saved profiles:": "Perfiles guardados:", "Profile name:": "Nombre del perfil:",
        "Delete": "Eliminar", "Cancel": "Cancelar",
        "Choose a profile; you may edit its name when saving.": "Elegí un perfil; para guardar podés editar el nombre.",
        "Choose a profile from the dropdown list.": "Elegí una configuración de la lista desplegable.",
        "Saved configurations:": "Configuraciones existentes:",
        "Confirm overwrite": "Confirmar sobrescritura", "Confirm deletion": "Confirmar eliminación",
        "Overwrite this profile?": "¿Sobrescribir este perfil?", "Delete this profile permanently?": "¿Eliminar definitivamente este perfil?",
        "Yes, overwrite": "Sí, sobrescribir", "Yes, delete": "Sí, eliminar",
        "Ready. Only Exit or Esc closes the TUI.": "Listo. Solo Salir o Esc cierran el TUI.",
        "Configuration applied.": "Configuración aplicada.", "Profile loaded:": "Perfil cargado:",
        "Profile saved:": "Perfil guardado:", "Profile overwritten:": "Perfil sobrescrito:",
        "Profile deleted:": "Perfil eliminado:", "Current": "Actual",
        "No profiles are available for this display.": "No hay perfiles disponibles para esta salida.",
        "Select a saved profile to load.": "Seleccioná un perfil guardado para cargar.",
        "Select an existing profile.": "Seleccioná un perfil existente.",
        "Used custom": "Personalizadas usadas", "Used predefined": "Predefinidas usadas", "Unused custom": "Personalizadas sin usar",
        "Visual comfort": "Comodidad visual", "Keep this resolution?": "¿Conservar esta resolución?",
    },
};
CURRENT_LANGUAGE = "en";

def T(label):
    return TRANSLATIONS.get(CURRENT_LANGUAGE, {}).get(label, label);

def combo_texts():
    """Backend-neutral language strings for the reusable SUM ComboBox.""";
    return {"title": T("Options"), "help": T("Search or select an option:"),
            "placeholder": T("Type to search..."), "accept": T("Select"),
            "cancel": T("Cancel")};

def set_language(language):
    global CURRENT_LANGUAGE;
    language = str(language or "en").lower();
    if language not in LANGUAGES:
        raise DisplayError("Unsupported language: {} (en, fr, es)".format(language));
    CURRENT_LANGUAGE = language;
    return language;


class DisplayError(Exception):
    """A recoverable display management error."""


def config_read():
    if not CONFIG_FILE.exists():
        return {"version": 1, "displays": {}};
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle);
        if not isinstance(data, dict) or not isinstance(data.get("displays", {}), dict):
            raise DisplayError("Configuración inválida");
        return data;
    except (OSError, ValueError) as exc:
        raise DisplayError(f"No se puede leer {CONFIG_FILE}: {exc}") from exc;


def json_write(path, data):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True);
    temporary = path.with_name(path.name + ".tmp");
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False, sort_keys=True);
        handle.write("\n");
    temporary.replace(path);


def config_write(data):
    json_write(CONFIG_FILE, data);


def xrandr(*arguments):
    if not shutil.which("xrandr"):
        raise DisplayError("No encuentro xrandr (instalá x11-xserver-utils).");
    if not os.environ.get("DISPLAY"):
        raise DisplayError("No hay DISPLAY: se necesita una sesión X11 con acceso a RandR.");
    command = ["xrandr", *[str(item) for item in arguments]];
    try:
        outcome = subprocess.run(command, text=True, capture_output=True, check=False, timeout=15);
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DisplayError(f"Error ejecutando xrandr: {exc}") from exc;
    if outcome.returncode:
        raise DisplayError(f"xrandr ({outcome.returncode}): {(outcome.stderr or outcome.stdout).strip()}");
    return outcome.stdout;


def detect():
    report = xrandr("--query");
    outputs = [];
    current = None;
    for line in report.splitlines():
        match = re.match(r"^(\S+)\s+(connected|disconnected)\b(.*)$", line);
        if match:
            name, connection, tail = match.groups();
            if connection != "connected":
                current = None;
                continue;
            geometry = re.search(r"\b(\d+x\d+)\+\d+\+\d+\b", tail);
            current = {"name": name, "primary": bool(re.search(r"\bprimary\b", tail)),
                       "mode": geometry.group(1) if geometry else None, "modes": [], "active": bool(geometry)};
            outputs.append(current);
            continue;
        if current is not None:
            mode = re.match(r"^\s+(\d+x\d+)\s+(.+)$", line);
            if mode:
                sizes = mode.group(1);
                rates = re.findall(r"\d+(?:\.\d+)?(?=[*+ ]|$)", mode.group(2));
                if sizes not in current["modes"]:
                    current["modes"].append(sizes);
                if "*" in mode.group(2):
                    current["mode"] = sizes;
                    current["active"] = True;
    return outputs;


def select_output(outputs, requested=None):
    if requested:
        selected = next((item for item in outputs if item["name"] == requested), None);
        if selected is None:
            raise DisplayError(f"Salida {requested!r} no conectada; disponibles: {', '.join(x['name'] for x in outputs)}");
        return selected;
    if not outputs:
        raise DisplayError("No se encontraron salidas conectadas.");
    return next((item for item in outputs if item["primary"] and item["active"]), None) or next((item for item in outputs if item["active"]), None) or outputs[0];


def key_for(output):
    return socket.gethostname() + "/" + output;


def saved_settings(config, output):
    return dict(config.get("displays", {}).get(key_for(output), {}));


def gamma_parse(value):
    try:
        fields = value.replace(",", ":").split(":");
        if len(fields) != 3:
            raise ValueError("tres componentes requeridos");
        gamma = tuple(float(item) for item in fields);
        if any(not 0.1 <= item <= 10.0 for item in gamma):
            raise ValueError("los componentes deben estar entre 0.1 y 10");
        return gamma;
    except ValueError as exc:
        raise DisplayError(f"Gamma inválida {value!r}: {exc}") from exc;


def brightness_parse(value):
    try:
        brightness = float(value);
        if not -5.0 <= brightness <= 5.0:
            raise ValueError("brillo permitido: -5.0 a 5.0");
        return brightness;
    except ValueError as exc:
        raise DisplayError(f"Brillo inválido {value!r}: {exc}") from exc;


def mode_parse(value):
    if not re.fullmatch(r"\d{3,5}x\d{3,5}", value):
        raise DisplayError(f"Dimensiones inválidas: {value!r}");
    return value;


def apply(output, changes, previous):
    """Make geometry changes first; reapply gamma and brightness LAST."""
    name = output["name"];
    mode = changes.get("mode");
    if mode and mode != output.get("mode"):
        mode_parse(mode);
        if mode not in output["modes"]:
            raise DisplayError(f"Modo {mode} no anunciado por {name}; consultá 'sumdisp list'.");
        xrandr("--output", name, "--mode", mode);
    scale = scale_normalize(changes["scale"]) if "scale" in changes else None;
    if scale and scale != previous.get("scale", "1x1"):
        if scale in ("normal", "reset", "1x1"):
            xrandr("--output", name, "--scale", "1x1");
        else:
            xrandr("--output", name, "--scale-from", mode_parse(scale));
        # Give the X server a brief opportunity to settle the transform.
        time.sleep(0.25);
    gamma = tuple(changes.get("gamma", previous.get("gamma", LEGACY_GAMMA)));
    gamma_parse(":".join(str(item) for item in gamma));
    bright = brightness_parse(changes.get("brightness", previous.get("brightness", 1.0)));
    color_args = ("--output", name, "--gamma", ":".join(str(item) for item in gamma), "--brightness", str(bright));
    xrandr(*color_args);
    if scale and scale != previous.get("scale", "1x1"):
        time.sleep(0.65);
        xrandr(*color_args);
    return {"mode": mode or output.get("mode"), "scale": scale or previous.get("scale", "1x1"),
            "gamma": list(gamma), "brightness": bright};


def update(output, changes, persist=True):
    config = config_read();
    old = saved_settings(config, output["name"]);
    new = apply(output, changes, old);
    if persist:
        config.setdefault("displays", {})[key_for(output["name"])] = new;
        if "scale" in changes and scale_normalize(new["scale"]) != scale_normalize(old.get("scale", "1x1")):
            history_update(config, output["name"], new["scale"]);
        # A profile identifies the applied configuration, not the last button
        # pressed. Reapplying identical values must preserve its identity.
        active = str(config.get("active_profiles", {}).get(key_for(output["name"]), "") or "");
        if active and not profile_matches_settings(active, output, new):
            config.setdefault("active_profiles", {}).pop(key_for(output["name"]), None);
        config_write(config);
    return new;


def current_profile_name(output):
    config = config_read();
    return str(config.get("active_profiles", {}).get(key_for(output["name"]), "") or "");


def set_current_profile(output, name=None):
    config = config_read();
    key = key_for(output["name"]);
    profiles = config.setdefault("active_profiles", {});
    if name:
        profiles[key] = str(name);
    else:
        profiles.pop(key, None);
    config_write(config);


def profile_caption(output):
    name = current_profile_name(output);
    if name and profile_path(name).exists():
        return name;
    return "Actual";


PROFILE_ACTUAL = "__sumdisp_actual__";


def profile_matches_settings(name, output, settings):
    """Compare effective visual settings, ignoring legacy physical mode fields.""";
    if not name:
        return False;
    record = next((item for item in available_profiles(output) if item["name"] == name), None);
    if record is None:
        return False;
    expected = record["settings"];
    try:
        if scale_normalize(expected.get("scale", "1x1")) != scale_normalize(settings.get("scale", "1x1")):
            return False;
        if abs(float(expected.get("brightness", 1.0)) - float(settings.get("brightness", 1.0))) > 1e-4:
            return False;
        wanted_gamma = expected.get("gamma", DEFAULT_GAMMA);
        actual_gamma = settings.get("gamma", DEFAULT_GAMMA);
        if len(wanted_gamma) != 3 or len(actual_gamma) != 3:
            return False;
        return all(abs(float(a) - float(b)) <= 1e-4 for a, b in zip(wanted_gamma, actual_gamma));
    except (TypeError, ValueError):
        return False;


def matched_profile(output):
    """Show the associated saved profile while its applied settings match.""";
    name = current_profile_name(output);
    if not name:
        return None;
    current = saved_settings(config_read(), output["name"]);
    return name if profile_matches_settings(name, output, current) else None;


def profile_entries(output):
    return [(T("Current"), PROFILE_ACTUAL, "option")] + [(name, name, "option") for name in profile_names(output)];


def profile_path(name):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name):
        raise DisplayError("Nombre de perfil inválido: usá letras, números, _ o -.");
    return PROFILES_DIR / (name + ".json");


def available_profiles(output=None):
    """Valid on-disk profiles, with output-specific entries first.""";
    results = [];
    if not PROFILES_DIR.exists():
        return results;
    for path in sorted(PROFILES_DIR.glob("*.json"), key=lambda x: x.stem.casefold()):
        try:
            profile_path(path.stem);
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle);
            settings = data.get("settings", {});
            if not isinstance(settings, dict):
                continue;
            if output and data.get("output") not in (None, output["name"]):
                continue;
            results.append({"name": path.stem, "settings": settings,
                            "output": data.get("output"), "host": data.get("host")});
        except (ValueError, OSError, TypeError, DisplayError):
            continue;
    return results;


def profile_names(output=None):
    return [record["name"] for record in available_profiles(output)];


def profile_save(name, output):
    config = config_read();
    stored = saved_settings(config, output["name"]);
    data = {"version": 1, "profile": name, "host": socket.gethostname(), "output": output["name"],
            "settings": {"mode": output["mode"], "scale": stored.get("scale", "1x1"),
                         "gamma": stored.get("gamma", list(DEFAULT_GAMMA)),
                         "brightness": stored.get("brightness", 1.0)}};
    json_write(profile_path(name), data);
    set_current_profile(output, name);
    return profile_path(name);


def profile_load(name, output):
    path = profile_path(name);
    if not path.exists():
        raise DisplayError(f"No existe el perfil {name!r}.");
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle);
        changes = dict(data["settings"]);
        if not isinstance(changes, dict):
            raise ValueError("settings inválido");
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise DisplayError(f"Perfil {name!r} inválido: {exc}") from exc;
    # Los perfiles anteriores pueden tener modo fisico: nunca aplicarlo aqui.
    changes.pop("mode", None);
    applied = update(output, changes);
    set_current_profile(output, name);
    return applied;



def profile_delete(name, output):
    """Delete a profile without changing currently applied visual settings.""";
    if name not in profile_names(output):
        raise DisplayError("Profile does not exist for this display: {!r}.".format(name));
    path = profile_path(name);
    try:
        path.unlink();
    except OSError as exc:
        raise DisplayError("No pude eliminar el perfil {!r}: {}".format(name, exc)) from exc;
    config = config_read();
    active = config.get("active_profiles", {});
    if isinstance(active, dict):
        for key, value in list(active.items()):
            if value == name:
                del active[key];
        config_write(config);
    return path;


def status(output):
    settings = saved_settings(config_read(), output["name"]);
    gamma = settings.get("gamma", "no registrada");
    print(f"sumdisp {VERSION} | host: {socket.gethostname()}");
    print(f"Salida: {output['name']} | principal: {'sí' if output['primary'] else 'no'}");
    print(f"Resolución física activa: {output['mode'] or 'desconocida'}");
    print(f"Escala guardada: {settings.get('scale', 'no registrada')}");
    print(f"Gamma guardada: {gamma}");
    print(f"Brillo guardado: {settings.get('brightness', 'no registrado')}");
    print("Nota: escala, gamma y brillo guardados son los últimos valores aplicados por sumdisp;");
    print("      xrandr u otras aplicaciones pueden haberlos cambiado posteriormente.");


def list_modes(output):
    print(f"{output['name']} | actual: {output['mode'] or '?'}");
    for mode in output["modes"]:
        print(f"  {'*' if mode == output['mode'] else ' '} {mode}");


# Catálogo de dimensiones lógicas conocidas. No son modos físicos ofrecidos por XRandR.
# nombre descriptivo no implica soporte específico de la pantalla.
RESOLUTION_CATALOG = (
    (640, 480, "VGA"), (720, 480, "NTSC / SD"), (720, 576, "PAL / SD"),
    (800, 600, "SVGA"), (1024, 600, "WSVGA"), (1024, 768, "XGA"),
    (1152, 864, "XGA+"), (1280, 720, "HD"), (1280, 768, "WXGA"),
    (1280, 800, "WXGA"), (1280, 960, "SXGA-"), (1280, 1024, "SXGA"),
    (1360, 768, "WXGA"), (1366, 768, "WXGA"), (1400, 900, "WXGA+"),
    (1400, 1050, "SXGA+"), (1440, 900, "WXGA+"), (1600, 768, "Personalizada"),
    (1600, 800, "Personalizada"), (1600, 900, "HD+"),
    (1600, 1200, "UXGA"), (1680, 1050, "WSXGA+"),
    (1800, 900, "Personalizada"), (1920, 1080, "Full HD"),
    (1920, 1200, "WUXGA"), (2048, 1152, "QWXGA"),
    (2048, 1536, "QXGA"), (2560, 1080, "UW-FHD"),
    (2560, 1440, "QHD / WQHD"), (2560, 1600, "WQXGA"),
    (2880, 1800, "Retina / WQXGA+"), (3200, 1800, "QHD+"),
    (3440, 1440, "UWQHD"), (3840, 1600, "UWQHD+"),
    (3840, 2160, "4K UHD"), (4096, 2160, "DCI 4K"),
    (5120, 1440, "DQHD"), (5120, 2880, "5K"),
    (6016, 3384, "6K"), (7680, 4320, "8K UHD"),
);
CATALOG_LABELS = {"{}x{}".format(w, h): label for w, h, label in RESOLUTION_CATALOG};


def scale_normalize(value):
    text = str(value or "").strip();
    if text.lower() in ("default", "predeterminada", "par défaut", "normal", "reset", "1x1"):
        return "1x1";
    return mode_parse(text);


def scale_display(value):
    return T("Default") if scale_normalize(value) == "1x1" else scale_normalize(value);


def scale_label(value, detailed=True):
    value = scale_normalize(value);
    if value == "1x1":
        return "{} — {}".format(T("Default"), T("original (1:1)")) if detailed else T("Default");
    return "{} — {}".format(value, T("Custom") if CATALOG_LABELS.get(value, "Personalizada") == "Personalizada" else CATALOG_LABELS[value]) if detailed else value;


def scale_from_label(label):
    return scale_normalize(str(label).split(" — ", 1)[0]);


def history_for(config, output_name):
    records = config.get("resolution_history", {});
    if not isinstance(records, dict):
        return [];
    values = records.get(key_for(output_name), []);
    if not isinstance(values, list):
        return [];
    result = [];
    for item in values:
        try:
            value = scale_normalize(item);
            if value not in result:
                result.append(value);
        except (DisplayError, ValueError):
            continue;
    return result[:HISTORY_LIMIT];


def history_update(config, output_name, scale):
    scale = scale_normalize(scale);
    values = [scale] + [x for x in history_for(config, output_name) if x != scale];
    config.setdefault("resolution_history", {})[key_for(output_name)] = values[:HISTORY_LIMIT];
    return values;


def catalog_options():
    values = sorted(RESOLUTION_CATALOG, key=lambda item: (item[0] * item[1], item[0], item[1]), reverse=True);
    return ["{}x{}".format(width, height) for width, height, unused in values];


def is_predefined_scale(value):
    value = scale_normalize(value);
    return value == "1x1" or (value in CATALOG_LABELS and CATALOG_LABELS[value] != "Personalizada");


def defined_custom_for(config, output):
    return config.get("custom_resolutions", {}).get(key_for(output["name"]), []);


def define_custom(config, output, scale):
    scale = scale_normalize(scale);
    if is_predefined_scale(scale):
        raise DisplayError("La resolución ya es predefinida: {}".format(scale));
    defined = [scale] + [v for v in defined_custom_for(config, output) if v != scale];
    config.setdefault("custom_resolutions", {})[key_for(output["name"])] = defined;
    return defined;


def custom_defined_for(config, output):
    """Custom scales explicitly saved in profiles or in current settings.""";
    defined = [];
    for item in defined_custom_for(config, output):
        try:
            value = scale_normalize(item);
            if not is_predefined_scale(value) and value not in defined:
                defined.append(value);
        except (DisplayError, TypeError, ValueError):
            pass;
    for record in available_profiles(output):
        try:
            value = scale_normalize(record["settings"].get("scale", "1x1"));
            if not is_predefined_scale(value) and value not in defined:
                defined.append(value);
        except (DisplayError, TypeError, ValueError):
            pass;
    try:
        current = scale_normalize(saved_settings(config, output["name"]).get("scale", "1x1"));
        if not is_predefined_scale(current) and current not in defined:
            defined.append(current);
    except (DisplayError, TypeError, ValueError):
        pass;
    return sorted(defined, key=lambda x: tuple(int(n) for n in x.split("x")), reverse=True);


def scale_sections(output, saved, config=None):
    """Three ordered sections: used custom, used standard, unused custom.""";
    config = config if config is not None else config_read();
    used = history_for(config, output["name"]);
    current = scale_normalize(saved.get("scale", "1x1"));
    if current not in used:
        used.insert(0, current);
    defined = custom_defined_for(config, output);
    custom_used = [v for v in used if not is_predefined_scale(v)];
    predefined_used = [v for v in used if is_predefined_scale(v)];
    custom_unused = [v for v in defined if v not in used];
    return custom_used, predefined_used, custom_unused;


def scale_options(output, saved, catalog=False, config=None):
    """Selectable values, never separators; retain backward-compatible API.""";
    config = config if config is not None else config_read();
    selected = scale_normalize(saved.get("scale", "1x1"));
    if catalog:
        values = catalog_options();
        return [selected] + values if selected not in values else values;
    return [value for section in scale_sections(output, saved, config) for value in section];


def scale_grouped_labels(output, saved, config=None):
    """Presentation rows (label, value or None); None marks a separator.""";
    sections = scale_sections(output, saved, config);
    names = (T("Used custom"), T("Used predefined"), T("Unused custom"));
    rows = [];
    for title, section in zip(names, sections):
        if not section:
            continue;
        if rows:
            rows.append(("──────────────", None));
        rows.append(("── {} ──".format(title), None));
        rows.extend((scale_label(value), value) for value in section);
    return rows;


def menu(output_name=None):
    """sumTUI persistent editor: actions do not terminate the application.""";
    try:
        from sumtui.app import Application;
        from sumtui.widgets import Button, CheckBox, ComboBox, Dialog, HBox, Label, Slider, TextInput, VBox;
        from sumtui.prompt import controlling_terminal;
        from sumtui.events import MouseEvent;
        from rich.console import Console;
    except ImportError as exc:
        raise DisplayError("sumdisp --tui necesita sumTUI y Rich instalados.") from exc;
    output = select_output(detect(), output_name);
    active_outputs = [entry for entry in detect() if entry.get("active")];
    old = saved_settings(config_read(), output["name"]);
    gamma = list(old.get("gamma", LEGACY_GAMMA));
    bright = old.get("brightness", 1.0);
    choices = scale_options(output, old);
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        app = Application("sumdisp", theme="ZX", console=Console(file=writer, force_terminal=True), mouse=True);
        def tui_scale_entries(active):
            if active:
                return [(scale_label(v), scale_label(v)) for v in scale_options(output, {"scale": active_scale()}, catalog=True)];
            return [(label, scale_label(value) if value is not None else None) for label, value in scale_grouped_labels(output, {"scale": active_scale()})];
        def active_scale():
            return scale_from_label(selection.value);
        selection = ComboBox([(label, scale_label(value), "option") if value is not None else (label, None, "heading") for label, value in scale_grouped_labels(output, old)], value=scale_label(old.get("scale", "1x1")), app=app, width=48, texts=combo_texts());
        def switch_catalog(enabled):
            selected_value = scale_from_label(selection.value);
            if enabled:
                updated = scale_options(output, {"scale": selected_value}, catalog=True);
                selection.set_entries([(scale_label(item), scale_label(item)) for item in updated]);
            else:
                selection.set_entries([(label, scale_label(value), "option") if value is not None else (label, None, "heading") for label, value in scale_grouped_labels(output, {"scale": selected_value})]);
            selection.set_value(scale_label(selected_value), notify=False);
        show_catalog = CheckBox(T("Show resolution catalog (by size)"), checked=False, on_change=switch_catalog);
        brightness = Slider(-5.0, 5.0, bright, step=0.05, label="", width=48, value_format="{:.2f}");
        red = Slider(0.1, 2.0, gamma[0], step=0.05, label="", width=48, value_format="{:.2f}");
        green = Slider(0.1, 2.0, gamma[1], step=0.05, label="", width=48, value_format="{:.2f}");
        blue = Slider(0.1, 2.0, gamma[2], step=0.05, label="", width=48, value_format="{:.2f}");
        selected_profile = matched_profile(output) or PROFILE_ACTUAL;
        profile_combo = ComboBox(profile_entries(output), value=selected_profile, app=app, width=42, texts=combo_texts());
        notice = Label(T("Ready. Only Exit or Esc closes the TUI."));

        def refresh_profiles(selected_name=None):
            profile_combo.set_entries(profile_entries(current_output()));
            wanted = matched_profile(current_output()) or PROFILE_ACTUAL;
            profile_combo.set_value(wanted, notify=False);

        def load_selected_profile():
            try:
                name = profile_combo.value;
                if name == PROFILE_ACTUAL:
                    notice.text = T("Select a saved profile to load.");
                    return True;
                loaded = profile_load(str(name), current_output());
                refresh(loaded);
                switch_catalog(show_catalog.checked);
                refresh_profiles(str(name));
                notice.text = "{} {}".format(T("Profile loaded:"), name);
            except (DisplayError, OSError, ValueError, TypeError) as exc:
                notice.text = "Error: {}".format(exc);
            return True;

        def current_output():
            return select_output(detect(), output["name"]);

        def refresh(settings):
            """Reflect a loaded/applied profile without triggering callbacks.""";
            target_scale = scale_normalize(settings.get("scale", "1x1"));
            available = [item[1] for item in selection.options];
            if scale_label(target_scale) not in available:
                selection.set_entries([(scale_label(target_scale), scale_label(target_scale))] + selection.options);
            selection.set_value(scale_label(target_scale), notify=False);
            brightness.set_value(settings.get("brightness", 1.0), notify=False);
            color = settings.get("gamma", LEGACY_GAMMA);
            for slider, value in zip((red, green, blue), color):
                slider.set_value(value, notify=False);

        def action(kind):
            try:
                actual = current_output();
                if kind == "apply":
                    stored = saved_settings(config_read(), actual["name"]);
                    changes = {"brightness": brightness.value, "gamma": [red.value, green.value, blue.value]};
                    if scale_from_label(selection.value) != stored.get("scale", "1x1"):
                        changes["scale"] = scale_from_label(selection.value);
                    applied = update(actual, changes);
                    refresh(applied);
                    switch_catalog(show_catalog.checked);
                    refresh_profiles();
                    notice.text = T("Configuration applied.");
                elif kind in ("save", "load", "delete"):
                    open_profile_dialog(kind);
            except (DisplayError, OSError, ValueError, TypeError) as exc:
                notice.text = "Error: {}".format(exc);
            return True;

        def open_profile_dialog(kind):
            actual = current_output();
            names = profile_names(actual);
            if kind in ("load", "delete") and not names:
                notice.text = T("No profiles are available for this display.");
                return True;
            current = current_profile_name(actual);
            proposed = current if current in names else (names[0] if names else "");
            items = names if names else ["(sin perfiles guardados)"];
            choice = ComboBox(items, value=current if current in names else items[0], width=46, app=app, texts=combo_texts());
            title_field = TextInput(value=proposed, width=44);
            description = Label(T("Choose a profile; you may edit its name when saving."));
            def name_selected(value):
                if kind == "save" and str(value) in names:
                    title_field.set(str(value));
            choice.on_change = name_selected;
            # La selección inicial también debe poblar el textbox, aunque
            # el usuario no cambie de entrada (no hay evento on_change).
            if kind == "save" and choice.value in names:
                title_field.set(str(choice.value));
            def close_popup():
                app.pop_modal();
                return True;
            def commit():
                try:
                    output_now = current_output();
                    if kind == "save":
                        name = title_field.value.strip();
                        profile_path(name);
                        if name in profile_names(output_now):
                            confirm_overwrite(name, output_now);
                            return True;
                        saved = profile_save(name, output_now);
                        refresh_profiles(name);
                        notice.text = "{} {}".format(T("Profile saved:"), saved.name);
                    else:
                        name = str(choice.value);
                        if name not in profile_names(output_now):
                            raise DisplayError(T("Select an existing profile."));
                        applied = profile_load(name, output_now);
                        refresh(applied);
                        refresh_profiles(name);
                        notice.text = "{} {}".format(T("Profile loaded:"), name);
                    close_popup();
                except (DisplayError, ValueError, OSError, TypeError) as exc:
                    notice.text = "Error: {}".format(exc);
                return True;
            def confirm_overwrite(name, output_now):
                def yes():
                    try:
                        profile_save(name, current_output());
                        refresh_profiles(name);
                        notice.text = "{} {}".format(T("Profile overwritten:"), name);
                        app.pop_modal();
                        app.pop_modal();
                    except (DisplayError, ValueError, OSError, TypeError) as exc:
                        notice.text = "Error: {}".format(exc);
                        app.pop_modal();
                    return True;
                def no():
                    app.pop_modal();
                    return True;
                popup = Dialog(VBox(Label("{}: {}".format(T("Overwrite this profile?"), name)),
                                     HBox(Button(T("Yes, overwrite"), on_press=yes), Button(T("Cancel"), on_press=no), ratios=[1,1])),
                               title=T("Confirm overwrite"), width=60, height=9, on_cancel=no, shadow=True);
                app.push_modal(popup);
            def delete_selected():
                name = str(choice.value);
                if name not in profile_names(current_output()):
                    notice.text = T("Select an existing profile.");
                    return True;
                def yes():
                    try:
                        profile_delete(name, current_output());
                        app.pop_modal();  # Confirmación.
                        app.pop_modal();  # Diálogo de perfiles.
                        refresh_profiles();
                        notice.text = "{} {}".format(T("Profile deleted:"), name);
                    except (DisplayError, ValueError, OSError) as exc:
                        app.pop_modal();
                        notice.text = "Error: {}".format(exc);
                    return True;
                def no():
                    app.pop_modal();
                    return True;
                popup_confirm = Dialog(
                    VBox(Label("{}: {}".format(T("Delete this profile permanently?"), name)),
                         HBox(Button(T("Yes, delete"), on_press=yes), Button(T("Cancel"), on_press=no), ratios=[1, 1])),
                    title=T("Confirm deletion"), width=63, height=9, on_cancel=no, shadow=True,
                );
                app.push_modal(popup_confirm);
                return True;
            primary_action = delete_selected if kind == "delete" else commit;
            primary_label = T("Delete") if kind == "delete" else (T("Save") if kind == "save" else T("Load"));
            buttons = HBox(Button(primary_label, on_press=primary_action, default=True),
                           Button(T("Cancel"), on_press=close_popup), ratios=[1, 1]);
            if kind == "save":
                fields = VBox(description, Label(T("Saved configurations:")), choice,
                              Label(T("Profile name:")), title_field, buttons);
            else:
                fields = VBox(Label(T("Saved configurations:")), choice, buttons);
            popup = Dialog(fields, title=T("Save profile") if kind == "save" else (T("Delete profile") if kind == "delete" else T("Load profile")),
                           width=63, height=16 if kind == "save" else 12, on_cancel=close_popup, shadow=True);
            app.push_modal(popup);
            app.focus.set(title_field if kind == "save" else choice);
            return True;

        def switch_monitor(name):
            nonlocal output;
            if str(name) == output["name"]:
                return True;
            try:
                output = select_output(detect(), str(name));
                settings = saved_settings(config_read(), output["name"]);
                refresh(settings);
                switch_catalog(show_catalog.checked);
                refresh_profiles();
                monitor_heading.text = "{} | {} {} ({})".format(output["name"], T("Physical mode"), output.get("mode") or "?", T("read-only"));
                notice.text = "{}: {}".format(T("Display"), output["name"]);
            except (DisplayError, OSError, ValueError) as exc:
                notice.text = "Error: {}".format(exc);
            return True;

        monitor_heading = Label("{} | {} {} ({})".format(output["name"], T("Physical mode"), output.get("mode") or "?", T("read-only")));
        if len(active_outputs) > 1:
            monitor_control = HBox(Label(T("Display")), ComboBox([(item["name"], item["name"]) for item in active_outputs], value=output["name"], on_change=switch_monitor, app=app, width=42, texts=combo_texts()), sizes=[14, None]);
        else:
            monitor_control = monitor_heading;

        class MainDialog(Dialog):
            """Route action-button mouse clicks by their *visible* positions.

            Rich centers and pads sub-layouts independently of the geometry
            cached by VBox/HBox.  Those cached rectangles may miss the actual
            screen row, particularly when the terminal height changes.  The
            action bar is short, so resolve its visual button spans against
            the current Rich rendering on a mouse press.  Everything else
            continues through the standard SUM dialog event dispatcher.
            """;
            def handle_event(self, event):
                if isinstance(event, MouseEvent) and event.button == "left" and event.action == "press":
                    widgets = [item.widget for item in actions.items];
                    labels = [widget._decorated_label() for widget in widgets];
                    lines = app.console.render_lines(self, app.console.options);
                    for y, rich_line in enumerate(lines):
                        row = "".join(segment.text for segment in rich_line);
                        # A unique action row contains every button label.
                        if not all(label in row for label in labels):
                            continue;
                        if event.y != y:
                            break;
                        for widget, label in zip(widgets, labels):
                            start = row.find(label);
                            if start <= event.x < start + len(label) and widget.enabled:
                                app.focus.set(widget);
                                return bool(widget.press());
                        break;
                return super().handle_event(event);

        profile_bar = HBox(Label(T("Profile")), profile_combo, Button(T("Load"), on_press=load_selected_profile), sizes=[9, None, 12]);
        actions = HBox(Button(T("Apply"), on_press=lambda: action("apply"), default=True),
                       Button(T("Save"), on_press=lambda: action("save")),
                       Button(T("Delete"), on_press=lambda: action("delete")),
                       Button(T("Exit"), on_press=lambda: app.stop()), ratios=[1, 1, 1]);
        content = VBox(monitor_control, *([monitor_heading] if len(active_outputs) > 1 else []), profile_bar, HBox(Label(T("Resolution")), selection, sizes=[14, None]), show_catalog, HBox(Label(T("Brightness")), brightness, sizes=[14,None]), HBox(Label("Gamma R"), red, sizes=[14,None]), HBox(Label("Gamma G"), green, sizes=[14,None]), HBox(Label("Gamma B"), blue, sizes=[14,None]), actions, notice);
        dialog = MainDialog(content, title="sumdisp - " + T("Visual comfort"), width=76, height=27, on_cancel=lambda: app.stop(), shadow=True);
        app.set_root(dialog);
        app.focus.set(selection);
        original_stdin = sys.stdin;
        try:
            sys.stdin = reader;
            app.run();
        finally:
            sys.stdin = original_stdin;


def graphical(output_name=None):
    """Native sumGUI choice editor and sliders, without Tkinter."""
    try:
        from sumgui import easy as ui;
        from sumgui.dialogs import question_box;
        from sumgui.combobox_ext import ComboBox;
        import pygame;
    except ImportError as exc:
        raise DisplayError("sumdisp --gui necesita sumGUI, sumUI y pygame.") from exc;
    output = select_output(detect(), output_name);
    active_outputs = [entry for entry in detect() if entry.get("active")];
    old = saved_settings(config_read(), output["name"]);
    gamma = list(old.get("gamma", LEGACY_GAMMA));
    def gui_recent(scale):
        return [(label, value, "option") if value is not None else (label, None, "heading") for label, value in scale_grouped_labels(output, {"scale": scale})];
    choices = gui_recent(old.get("scale", "1x1"));
    selected = {"scale": old.get("scale", "1x1")};
    controls = {};
    ui.window(title="sumdisp {} - {}".format(VERSION, output["name"]), width=720, height=690, font_size=19, theme="ZX");
    physical_label = ui.label("{} | {} {} ({})".format(output["name"], T("Physical mode"), output.get("mode") or "?", T("read-only")), 22, 14, 665, 38, font_size=17);
    if len(active_outputs) > 1:
        physical_label.text = "{}: {} ({})".format(T("Physical mode"), output.get("mode") or "?", T("read-only"));
        physical_label.rect.x = 330;
        physical_label.rect.width = 365;
        physical_label.font = ui.app().make_font(14);
        ui.label(T("Display"), 22, 14, 135, 38, font_size=17);
        def change_monitor(name):
            nonlocal output;
            try:
                output = select_output(detect(), str(name));
                settings = saved_settings(config_read(), output["name"]);
                physical_label.text = "{}: {} ({})".format(T("Physical mode"), output.get("mode") or "?", T("read-only"));
                selected["scale"] = scale_normalize(settings.get("scale", "1x1"));
                gui_switch_catalog(catalog_state["enabled"]);
                controls["brightness"].set_value(settings.get("brightness", 1.0), notify=False);
                for channel, value in zip(("R", "G", "B"), settings.get("gamma", LEGACY_GAMMA)):
                    controls[channel].set_value(value, notify=False);
                refresh_profiles();
            except (DisplayError, OSError, ValueError) as exc:
                ui.alert(str(exc), "sumdisp: error");
        monitor_combo = ComboBox(ui.app().rect(135, 14, 185, 40), ui.app(), entries=[(entry["name"], entry["name"]) for entry in active_outputs], value=output["name"], on_change=change_monitor, texts=combo_texts());
        ui.app().add(monitor_combo);
    ui.label(T("Profile"), 22, 78, 150, 42);
    profile_combo = ComboBox(ui.app().rect(182, 78, 375, 44), ui.app(), entries=profile_entries(output), value=matched_profile(output) or PROFILE_ACTUAL, texts=combo_texts());
    ui.app().add(profile_combo);
    def refresh_profiles(selected_name=None):
        profile_combo.set_entries(profile_entries(current_output()));
        wanted = matched_profile(current_output()) or PROFILE_ACTUAL;
        profile_combo.set_value(wanted, notify=False);
    ui.label(T("Resolution"), 22, 153, 185, 42);
    combo = ComboBox(ui.app().rect(210, 153, 484, 44), ui.app(), entries=choices, value=selected["scale"], on_change=lambda value: selected.__setitem__("scale", value), texts=combo_texts());
    ui.app().add(combo);
    def gui_switch_catalog(enabled):
        catalog_state["enabled"] = bool(enabled);
        current_scale = selected["scale"];
        combo.set_entries(scale_options(output, {"scale": current_scale}, catalog=True) if enabled else gui_recent(current_scale));
        combo.set_value(current_scale, notify=False);
    catalog_state = {"enabled": False};
    ui.checkbox(T("Show resolution catalog (by size)"), 210, 205, 480, 34, checked=False, do=gui_switch_catalog);
    ui.label(T("Brightness"), 22, 246, 150, 36);
    controls["brightness"] = ui.slider("", 184, 243, 510, 46, minimum=-5.0, maximum=5.0, value=old.get("brightness", 1.0), step=0.05, compact=True);
    for index, (channel, value) in enumerate(zip(("R", "G", "B"), gamma)):
        y = 315 + 72 * index;
        ui.label("Gamma " + channel, 22, y, 150, 36);
        controls[channel] = ui.slider("", 184, y - 3, 510, 46, minimum=0.1, maximum=2.0, value=value, step=0.05, compact=True);
    def current_output():
        return select_output(detect(), output["name"]);
    def apply_all():
        try:
            current = current_output();
            original = saved_settings(config_read(), current["name"]);
            changes = {"brightness": controls["brightness"].value, "gamma": [controls[x].value for x in ("R", "G", "B")]};
            if selected["scale"] != original.get("scale", "1x1"):
                changes["scale"] = selected["scale"];
                update(current, changes, persist=False);
                expired = threading.Event();
                def revert():
                    try:
                        previous = dict(original);
                        previous["scale"] = selected["scale"];
                        apply(current_output(), {"scale": original.get("scale", "1x1")}, previous);
                    except (DisplayError, OSError) as exc:
                        print("sumdisp: fallo de reversión: {}".format(exc), file=sys.stderr);
                timer = threading.Timer(15.0, revert);
                timer.daemon = True;
                timer.start();
                approved = question_box(ui.app().screen, ui.app().clock, T("Confirm resolution"), T("Keep this resolution?") + " (15 s)", theme=ui.app().theme);
                timed_out = not timer.is_alive();
                expired.set();
                timer.cancel();
                if not approved or timed_out:
                    if not timed_out:
                        revert();
                    return;
            update(current_output(), changes);
            refresh_profiles();
            ui.alert(T("Configuration applied."), "sumdisp");
        except (DisplayError, OSError, ValueError) as exc:
            ui.alert(str(exc), "sumdisp: error");
    def handle_profile(save, delete=False):
        """SUM graphical profile dialog, with a real dropdown and editable name.""";
        try:
            from sumgui.widgets import Widget, Panel, Button, TextInput, draw_clipped_text;
            from sumgui.combobox_ext import ComboBox as ProfileComboBox;
            actual = current_output();
            names = profile_names(actual);
            if not names and not save:
                ui.alert(T("No profiles are available for this display."), "sumdisp");
                return;
            current_name = matched_profile(actual);
            initial = current_name if current_name in names else (names[0] if names else "");
            app = ui.app();

            class ProfileDialog(Widget):
                """Modal SUM widget; its selector uses the shared sumGUI ComboBox.""";
                def __init__(self):
                    super().__init__(pygame.Rect(0, 0, app.width, app.height), focusable=True);
                    self.theme = app.theme;
                    self.font = app.font;
                    self.big_font = app.big_font;
                    self.box = pygame.Rect(36, 75, app.width - 72, 455 if save else 330);
                    self.panel = Panel(self.box, self.theme);
                    self.name_field = None;
                    self.combo = None;
                    if names:
                        self.combo = self.panel.add(ProfileComboBox(
                            pygame.Rect(self.box.x + 34, self.box.y + 145, self.box.width - 68, 45),
                            app, entries=[(name, name) for name in names], value=initial,
                            on_change=self.name_selected, rows=6, texts=combo_texts(),
                        ));
                        # The shared ComboBox uses app.show_modal for its popup.
                        # Restore THIS dialog instead of dismissing both modals.
                        original_open = self.combo.open_popup;
                        def open_nested():
                            original_open();
                            popup = app.modal;
                            if popup is not self:
                                popup.close = lambda: app.show_modal(self);
                        self.combo.open_popup = open_nested;
                    if save:
                        self.name_field = self.panel.add(TextInput(
                            pygame.Rect(self.box.x + 34, self.box.y + 254, self.box.width - 68, 45),
                            self.font, text=initial, theme=self.theme,
                        ));
                    buttons_y = self.box.bottom - 75;
                    inner_w = self.box.width - 68;
                    gap = 12;
                    button_w = (inner_w - gap) // 2;
                    for index, (caption, handler) in enumerate((
                        (T("Delete") if delete else (T("Save") if save else T("Load")),
                         self.delete_selected if delete else self.commit),
                        (T("Cancel"), self.cancel),
                    )):
                        self.panel.add(Button(
                            pygame.Rect(self.box.x + 34 + index * (button_w + gap), buttons_y, button_w, 44),
                            caption, self.font, handler, theme=self.theme,
                        ));
                    self.panel.set_focus_widget(self.combo or self.name_field);

                def name_selected(self, name):
                    if save and self.name_field is not None:
                        self.name_field.set_value(str(name));

                def cancel(self, unused=None):
                    app.close_modal();
                    return True;

                def delete_selected(self, unused=None):
                    try:
                        if self.combo is None or self.combo.value not in profile_names(current_output()):
                            ui.alert(T("Select an existing profile."), "sumdisp");
                            return True;
                        name = str(self.combo.value);
                        approved = question_box(
                            app.screen, app.clock,
                            T("Confirm deletion"), "{}: {}".format(T("Delete this profile permanently?"),name),
                            theme=app.theme, yes_label=T("Yes"), no_label=T("No"),
                        );
                        if not approved:
                            return True;
                        profile_delete(name, current_output());
                        refresh_profiles();
                        self.cancel();
                        ui.alert("{} {}".format(T("Profile deleted:"),name), "sumdisp");
                    except (DisplayError, OSError, ValueError, TypeError) as exc:
                        ui.alert(str(exc), "sumdisp: error");
                    return True;

                def commit(self, unused=None):
                    try:
                        if save:
                            name = str(self.name_field.value()).strip();
                            profile_path(name);
                            if name in profile_names(current_output()):
                                approved = question_box(
                                    app.screen, app.clock,
                                    T("Confirm overwrite"), "{}: {}".format(T("Overwrite this profile?"),name),
                                    theme=app.theme, yes_label=T("Yes"), no_label=T("No"),
                                );
                                if not approved:
                                    return True;
                            profile_save(name, current_output());
                            refresh_profiles(name);
                            self.cancel();
                            ui.alert("{} {}".format(T("Profile saved:"),name), "sumdisp");
                        else:
                            name = str(self.combo.value);
                            if name not in profile_names(current_output()):
                                raise DisplayError(T("Select an existing profile."));
                            settings = profile_load(name, current_output());
                            selected["scale"] = scale_normalize(settings.get("scale", "1x1"));
                            if selected["scale"] not in [e.value for e in combo.model.entries if e.selectable]:
                                combo.set_entries([(scale_label(selected["scale"]), selected["scale"])] + combo.model.entries);
                            combo.set_value(selected["scale"], notify=False);
                            controls["brightness"].set_value(settings.get("brightness", 1.0), notify=False);
                            for channel, value in zip(("R", "G", "B"), settings.get("gamma", LEGACY_GAMMA)):
                                controls[channel].set_value(value, notify=False);
                            refresh_profiles(name);
                            self.cancel();
                            ui.alert("{} {}".format(T("Profile loaded:"),name), "sumdisp");
                    except (DisplayError, OSError, ValueError, TypeError, KeyError) as exc:
                        ui.alert(str(exc), "sumdisp: error");
                    return True;

                def handle_event(self, event):
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return self.cancel();
                    return self.panel.handle_event(event);

                def update(self, dt):
                    self.panel.update(dt);

                def draw(self, screen):
                    overlay = pygame.Surface((app.width, app.height), pygame.SRCALPHA);
                    overlay.fill((0, 0, 0, 160));
                    screen.blit(overlay, (0, 0));
                    pygame.draw.rect(screen, self.theme.panel, self.box, border_radius=9);
                    pygame.draw.rect(screen, self.theme.line, self.box, 3, border_radius=9);
                    title = T("Delete profile") if delete else (T("Save profile") if save else T("Load profile"));
                    # Panel.draw() paints its own background; labels must be drawn AFTER it.
                    self.panel.draw(screen);
                    draw_clipped_text(screen, self.big_font, title, self.theme.text,
                                      pygame.Rect(self.box.x + 25, self.box.y + 18, self.box.width - 50, 40));
                    draw_clipped_text(screen, self.font,
                                      T("Choose a profile from the dropdown list."),
                                      self.theme.text,
                                      pygame.Rect(self.box.x + 34, self.box.y + 70, self.box.width - 68, 40));
                    if names:
                        draw_clipped_text(screen, self.font, T("Saved configurations:"), self.theme.text,
                                          pygame.Rect(self.box.x + 34, self.box.y + 112, self.box.width - 68, 30));
                    if save:
                        draw_clipped_text(screen, self.font, T("Profile name:"), self.theme.text,
                                          pygame.Rect(self.box.x + 34, self.box.y + 214, self.box.width - 68, 34));

            app.show_modal(ProfileDialog());
        except (ImportError, DisplayError, OSError, ValueError, TypeError) as exc:
            ui.alert(str(exc), "sumdisp: error");
    def load_selected_profile():
        try:
            name = profile_combo.value;
            if name == PROFILE_ACTUAL:
                ui.alert(T("Select a saved profile to load."), "sumdisp");
                return;
            settings = profile_load(str(name), current_output());
            selected["scale"] = scale_normalize(settings.get("scale", "1x1"));
            if selected["scale"] not in [entry.value for entry in combo.model.entries if entry.selectable]:
                combo.set_entries([(scale_label(selected["scale"]), selected["scale"])] + combo.model.entries);
            combo.set_value(selected["scale"], notify=False);
            controls["brightness"].set_value(settings.get("brightness", 1.0), notify=False);
            for channel, value in zip(("R", "G", "B"), settings.get("gamma", LEGACY_GAMMA)):
                controls[channel].set_value(value, notify=False);
            refresh_profiles(str(name));
            ui.alert("{} {}".format(T("Profile loaded:"),name), "sumdisp");
        except (DisplayError, OSError, ValueError, TypeError) as exc:
            ui.alert(str(exc), "sumdisp: error");
    ui.button(T("Load"), 572, 78, 122, 44, do=load_selected_profile);
    ui.button(T("Apply"), 22, 555, 155, 52, do=apply_all);
    ui.button(T("Save"), 196, 555, 155, 52, do=lambda: handle_profile(True));
    ui.button(T("Delete"), 370, 555, 155, 52, do=lambda: handle_profile(False, delete=True));
    ui.button(T("Exit"), 544, 555, 155, 52, do=lambda: setattr(ui.app(), "running", False));
    ui.start();


def main():
    parser = argparse.ArgumentParser(prog=APP, description="sumdisp: X11 logical resolution, gamma, brightness and profiles");
    parser.add_argument("--language", "--lang", choices=LANGUAGES, default="en", dest="language", help="UI language: en (default), fr, es");
    parser.add_argument("--output", help="display output, e.g. HDMI-2");
    interface = parser.add_mutually_exclusive_group();
    interface.add_argument("--cli", action="store_true", help="show status when no command is supplied");
    interface.add_argument("--tui", action="store_true", help="native sumTUI interface");
    interface.add_argument("--gui", action="store_true", help="native sumGUI interface");
    parser.add_argument("command", nargs="?", help="status, list, grande, delgada, normal, setbright, gamma, mode, scale, define-scale, save, load, delete-profile, restore, reset");
    parser.add_argument("value", nargs="?", help="command value");
    parser.add_argument("--version", action="version", version=f"sumdisp {VERSION}");
    options = parser.parse_args();
    set_language(options.language);
    if options.gui:
        graphical(options.output);
        return 0;
    if options.tui:
        menu(options.output);
        return 0;
    command = (options.command or "").lower();
    value = options.value;
    if APP.lower() in ("ajustabrillo", "setbright") and command:
        value = command;
        command = "setbright";
    if not command and not options.cli and APP.lower() not in ("disp", "ajustabrillo", "setbright") and sys.stdin.isatty():
        menu(options.output);
        return 0;
    output = select_output(detect(), options.output);
    if command in ("", "status", "estado"):
        status(output);
    elif command in ("list", "lista", "modes", "resolutions"):
        list_modes(output);
    elif command in ("grande", "big"):
        update(output, {"scale": "1920x1080"});
    elif command in ("delgada", "light"):
        update(output, {"scale": "1800x900"});
    elif command in ("normal", "restaura", "restore", "reset", "restablecer"):
        if command in ("reset", "restablecer"):
            update(output, {"scale": "1x1", "gamma": DEFAULT_GAMMA, "brightness": 1.0});
        else:
            update(output, {"scale": "1x1"});
    elif command in ("setbright", "brightness", "brillo"):
        if value is None:
            raise DisplayError("Falta valor: sumdisp setbright .8");
        stored = saved_settings(config_read(), output["name"]);
        gamma = stored.get("gamma", LEGACY_GAMMA);
        update(output, {"brightness": brightness_parse(value), "gamma": gamma});
    elif command == "gamma":
        if value is None:
            raise DisplayError("Falta gamma: sumdisp gamma .8:.85:.95");
        update(output, {"gamma": gamma_parse(value)});
    elif command in ("mode", "resolucion", "resolution"):
        if value is None:
            raise DisplayError("Falta resolución: sumdisp mode 1920x1080");
        update(output, {"mode": mode_parse(value)});
    elif command in ("define-scale", "definir-escala"):
        if value is None:
            raise DisplayError("Falta escala: sumdisp define-scale 1500x850");
        config = config_read();
        define_custom(config, output, value);
        config_write(config);
        print("Resolución personalizada registrada:", value);
    elif command in ("scale", "escala"):
        if value is None:
            raise DisplayError("Falta escala: sumdisp scale 1800x900");
        update(output, {"scale": value});
    elif command in ("save", "guardar"):
        if not value:
            raise DisplayError("Falta nombre: sumdisp save lectura");
        print("Perfil guardado:", profile_save(value, output));
    elif command in ("load", "cargar"):
        if not value:
            raise DisplayError("Falta nombre: sumdisp load lectura");
        profile_load(value, output);
    elif command in ("delete-profile", "eliminar-perfil"):
        if not value:
            raise DisplayError("Falta nombre: sumdisp delete-profile lectura");
        print("Perfil eliminado:", profile_delete(value, output));
    else:
        parser.error(f"Comando desconocido: {command}");
    return 0;


if __name__ == "__main__":
    try:
        sys.exit(main());
    except (DisplayError, KeyboardInterrupt) as error:
        print(f"sumdisp: {error}", file=sys.stderr);
        sys.exit(1);
