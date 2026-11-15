#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
import importlib.machinery;
import importlib.util;
import tempfile;
from pathlib import Path;

source = str(Path(__file__).resolve().parent / 'sumdisp');
loader = importlib.machinery.SourceFileLoader('sumdisp_test14', source);
spec = importlib.util.spec_from_loader(loader.name, loader);
m = importlib.util.module_from_spec(spec);
loader.exec_module(m);
with tempfile.TemporaryDirectory() as temporary:
    m.CONFIG_DIR = Path(temporary);
    m.CONFIG_FILE = Path(temporary) / 'config.json';
    m.PROFILES_DIR = Path(temporary) / 'profiles';
    output = {'name': 'eDP-1-1', 'mode': '1366x768', 'modes': ['1366x768'], 'primary': True};
    key = m.key_for(output['name']);
    settings = {'scale': '1600x800', 'brightness': 1.4, 'gamma': [0.8, 0.8, 0.9], 'mode': '1366x768'};
    m.config_write({'displays': {key: dict(settings)}, 'active_profiles': {}});
    m.profile_save('Defecto', output);
    assert m.matched_profile(output) == 'Defecto';
    commands = [];
    m.xrandr = lambda *args: commands.append(args);
    applied = m.update(output, {'brightness': 1.4, 'gamma': [0.8, 0.8, 0.9]});
    assert applied['scale'] == '1600x800';
    assert m.matched_profile(output) == 'Defecto', 'Reapply must not erase active profile';
    assert m.current_profile_name(output) == 'Defecto';
    assert m.config_read()['active_profiles'][key] == 'Defecto';
    assert m.matched_profile(output) == 'Defecto', 'Restart semantics';
    m.update(output, {'brightness': 1.45});
    assert m.matched_profile(output) is None, 'Change must disconnect previous profile';
    assert m.current_profile_name(output) == '';
    m.profile_load('Defecto', output);
    assert m.matched_profile(output) == 'Defecto', 'Load restores association';
    m.update(output, {'gamma': [0.8, 0.8, 0.9], 'brightness': 1.4});
    assert m.matched_profile(output) == 'Defecto';
    assert all('--mode' not in cmd for cmd in commands);
    print('PASS: reapply, restart, change, reload, no physical mode change');
