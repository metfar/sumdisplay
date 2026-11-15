#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
import importlib.machinery;
import importlib.util;
import tempfile;
from pathlib import Path;

source = str(Path(__file__).resolve().parent / 'sumdisp');
loader = importlib.machinery.SourceFileLoader('sumdisp_test16', source);
spec = importlib.util.spec_from_loader(loader.name, loader);
m = importlib.util.module_from_spec(spec);
loader.exec_module(m);
with tempfile.TemporaryDirectory() as temp:
    m.CONFIG_DIR = Path(temp);
    m.CONFIG_FILE = Path(temp) / 'config.json';
    m.PROFILES_DIR = Path(temp) / 'profiles';
    output = {'name': 'eDP-1-1', 'mode': '1366x768', 'modes': ['1366x768'], 'primary': True};
    key = m.key_for(output['name']);
    values = {'scale': '1600x800', 'brightness': 1.4, 'gamma': [0.8, 0.8, 0.9], 'mode': '1366x768'};
    m.config_write({'displays': {key: values.copy()}, 'active_profiles': {}});
    m.profile_save('Defecto', output);
    m.profile_save('Lectura', output);
    assert sorted(m.profile_names(output)) == ['Defecto', 'Lectura'];
    assert m.current_profile_name(output) == 'Lectura';
    original = m.saved_settings(m.config_read(), output['name']);
    m.profile_delete('Lectura', output);
    assert m.profile_names(output) == ['Defecto'];
    assert m.current_profile_name(output) == '';
    assert m.saved_settings(m.config_read(), output['name']) == original;
    assert m.profile_path('Defecto').exists();
    m.profile_delete('Defecto', output);
    assert m.profile_names(output) == [];
    try:
        m.profile_delete('Defecto', output);
        raise AssertionError('Deleting a nonexistent profile must fail');
    except m.DisplayError:
        pass;
    assert m.saved_settings(m.config_read(), output['name']) == original;
    print('PASS: profile delete, active association cleared, other profiles intact, no display changes');
