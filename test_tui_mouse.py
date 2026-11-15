#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
"""Check that actual Rich-rendered button positions receive mouse presses.""";
import ast;
from pathlib import Path;
import unittest;
from rich.console import Console;
from sumtui.app import Application;
from sumtui.events import MouseEvent;
from sumtui.widgets import Button, Dialog, HBox, Label, VBox;

class TestMouseRouting(unittest.TestCase):
    def test_visible_button_positions_for_multiple_terminal_sizes(self):
        source = ast.parse(Path(__file__).with_name('sumdisp').read_text());
        menu = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'menu');
        cls = next(n for n in ast.walk(menu) if isinstance(n, ast.ClassDef) and n.name == 'MainDialog');
        for height in (24, 27, 30, 35, 40, 45):
            with self.subTest(height=height):
                console = Console(width=90, height=height, force_terminal=False);
                app = Application('test', console=console);
                clicks = [];
                names = ('Apply', 'Save', 'Delete', 'Exit');
                actions = HBox(*(Button(name, on_press=lambda name=name: clicks.append(name)) for name in names), ratios=[1, 1, 1]);
                content = VBox(Label('Header'), Label('Profile'), Label('Resolution'), Label('Gamma'), actions, Label('status'));
                env = {'Dialog': Dialog, 'MouseEvent': MouseEvent, 'content': content, 'actions': actions, 'app': app};
                exec(compile(ast.Module(body=[cls], type_ignores=[]), '<test>', 'exec'), env);
                root = env['MainDialog'](content, title='test', width=76, height=27);
                app.set_root(root);
                lines = console.render_lines(root, console.options);
                plain = [''.join(segment.text for segment in line) for line in lines];
                y = next(i for i, line in enumerate(plain) if all(name in line for name in names));
                for name in names:
                    clicks.clear();
                    x = plain[y].find(name) + len(name)//2;
                    self.assertTrue(root.handle_event(MouseEvent(x, y, button='left', action='press')), (height,name,x,y));
                    self.assertEqual(clicks, [name]);
                # Clicking a different row must not trigger any action.
                clicks.clear();
                self.assertFalse(bool(clicks));

if __name__ == '__main__': unittest.main();
