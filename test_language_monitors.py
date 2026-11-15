#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
import pathlib;
import runpy;
import unittest;
from unittest.mock import patch;

APP = pathlib.Path(__file__).with_name('sumdisplay.py');

class TestLanguageAndMonitors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = runpy.run_path(str(APP), run_name='sumdisplay_test');

    def test_languages(self):
        set_language = self.api['set_language'];
        scale_label = self.api['scale_label'];
        scale_from_label = self.api['scale_from_label'];
        tr = self.api['T'];
        for language, resolution in [('en', 'Resolution'), ('fr', 'Résolution'), ('es', 'Resolución')]:
            with self.subTest(language=language):
                set_language(language);
                self.assertEqual(tr('Resolution'), resolution);
                self.assertEqual(scale_from_label(scale_label('1x1')), '1x1');
                self.assertEqual(scale_from_label(scale_label('1600x800')), '1600x800');
        set_language('en');

    def test_multiple_active_outputs(self):
        reports = [
            'eDP-1 connected primary 1366x768+0+0 (normal left inverted right x axis y axis) 300mm x 200mm',
            '   1366x768   60.0*+',
            'HDMI-2 connected 1920x1080+1366+0 (normal left inverted right x axis y axis)',
            '   1920x1080  60.0*',
            'DP-3 connected (normal left inverted right x axis y axis)',
            '   1920x1080  60.0+',
        ];
        with patch.dict(self.api['detect'].__globals__, {'xrandr': lambda *args: '\n'.join(reports)}):
            outputs = self.api['detect']();
        self.assertEqual([v['name'] for v in outputs if v['active']], ['eDP-1', 'HDMI-2']);
        self.assertEqual(self.api['select_output'](outputs)['name'], 'eDP-1');
        self.assertEqual(self.api['select_output'](outputs, 'HDMI-2')['name'], 'HDMI-2');

if __name__ == '__main__':
    unittest.main();
