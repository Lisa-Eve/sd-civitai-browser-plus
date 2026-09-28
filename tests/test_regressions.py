import ast
import json
import os
from pathlib import Path
import tempfile
import types
import unittest

from scripts.civitai_storage import is_model_sidecar, read_json, write_json, enough_space


def load_version_match():
    # The full extension needs WebUI and Gradio. Isolate the pure matching logic.
    source = Path(__file__).resolve().parents[1] / 'scripts' / 'civitai_file_manage.py'
    node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == 'version_match')
    scope = {'os': os, 'read_json': read_json, 'gl': types.SimpleNamespace()}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    return scope['version_match'], scope['gl']


def load_settings_writer(config):
    source = Path(__file__).resolve().parents[1] / 'scripts' / 'civitai_gui.py'
    node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == 'saveSettings')
    scope = {'cmd_opts': types.SimpleNamespace(ui_config_file=str(config)),
             'read_json': read_json, 'write_json': write_json, 'print': lambda _: None}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    return scope['saveSettings']


def load_queue_all(items, receiver):
    source = Path(__file__).resolve().parents[1] / 'scripts' / 'civitai_download.py'
    node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == 'queue_all_updates')
    scope = {'gl': types.SimpleNamespace(update_items=items), 'json': json,
             'selected_to_queue': receiver}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    return scope['queue_all_updates']


class RegressionTests(unittest.TestCase):
    def test_invalid_other_extension_sidecar_is_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'model.safetensors').touch()
            Path(folder, 'model.cm-info.json').touch()
            self.assertFalse(is_model_sidecar(folder, 'model.cm-info.json'))
            self.assertTrue(is_model_sidecar(folder, 'model.json'))

    def test_atomic_write_preserves_existing_metadata_on_error(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder, 'model.json')
            write_json(target, {'setting': 'keep'})
            with self.assertRaises(TypeError):
                write_json(target, {'bad': object()})
            self.assertEqual(read_json(target), {'setting': 'keep'})

    def test_settings_writer_preserves_other_extension_and_unknown_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder, 'ui-config.json')
            write_json(config, {'other_extension/value': 'keep',
                                'civitai_interface/custom/value': 'also keep'})
            load_settings_writer(config)(*range(12))
            data = read_json(config)
            self.assertEqual(data['other_extension/value'], 'keep')
            self.assertEqual(data['civitai_interface/custom/value'], 'also keep')
            self.assertEqual(data['civitai_interface/Tile count:/value'], 11)

    def test_update_stays_with_installed_base_model(self):
        match, state = load_version_match()
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder, 'installed.safetensors')
            model.touch()
            write_json(model.with_suffix('.json'), {
                'modelId': 7, 'modelVersionId': 20, 'sha256': 'ABCD'
            })
            item = {'id': 7, 'name': 'Example', 'modelVersions': [
                {'id': 30, 'baseModel': 'Krea', 'files': []},
                {'id': 20, 'baseModel': 'Qwen', 'files': []},
            ]}
            self.assertEqual(match([str(model)], {'items': [item]})[1], [])
            self.assertEqual(match([str(model)], {'items': [item]}, True)[1], [('&ids=7', 'Example')])
            self.assertEqual(state.update_preferred_versions['7'], 30)
            item['modelVersions'].insert(0, {'id': 31, 'baseModel': 'Qwen', 'files': []})
            self.assertEqual(match([str(model)], {'items': [item]})[1], [('&ids=7', 'Example')])
            self.assertEqual(state.update_preferred_versions['7'], 31)

    def test_space_check_uses_destination_volume(self):
        with tempfile.TemporaryDirectory() as folder:
            free = enough_space(folder, 0, reserve=0)[1]
            self.assertTrue(enough_space(folder, 0, reserve=0)[0])
            self.assertFalse(enough_space(folder, free + 1, reserve=0)[0])

    def test_queue_all_uses_every_scan_result(self):
        items = [{'id': 1, 'name': 'First'}, {'id': 2, 'name': 'Last page'}]
        captured = []
        fn = load_queue_all(items, lambda *args: captured.append(args))
        fn('start', True, 'html')
        self.assertEqual(json.loads(captured[0][0]), ['First (1)', 'Last page (2)'])
        self.assertEqual(captured[0][-1]['items'], items)


if __name__ == '__main__':
    unittest.main()
