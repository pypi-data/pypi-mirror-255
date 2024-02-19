#!../venv/bin/pytest -s

import enum

from confattr import Config

import udsync.main

# the setup of other tests clear this dict so I need to save the values before any tests run
config_instances = tuple(Config.instances.values())

def test_all_types_used_for_configs_have_names() -> None:
	for c in config_instances:
		for f in c.type.get_primitives():
			t = f.type
			if t in (int, str, bool, float):
				continue
			if isinstance(t, type) and issubclass(t, enum.Enum):
				continue
			if hasattr(t, 'get_instances'):
				continue
			assert hasattr(t, 'type_name'), c.key
