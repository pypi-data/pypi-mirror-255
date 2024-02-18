from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import isort
import yaml

if TYPE_CHECKING:
    from typing import ModuleType


def import_module(module_path: Path) -> ModuleType:
    package = _load_package(module_path.parent)
    module_name = module_path.stem
    if package:
        module_name = f"{package}.{module_name}"

    return _load_module(module_name, module_path)


def _check_clone_present(lines: list[str]) -> None:
    if not any(("cfg = cfg.clone()" in line) for line in lines):
        warnings.warn(
            "Extending config file without clone() is discouraged, as it frequently leads to bugs",
            stacklevel=4,
        )


def merge_cfg_module(module: ModuleType, imported_modules: set[str] = None) -> list[str]:
    lines = []
    if imported_modules is None:
        imported_modules = set()
    module_name = module.__spec__.name
    if module_name in imported_modules:
        return []

    module_path = Path(module.__file__)

    with module_path.open() as module_file_fobj:
        module_file = list(module_file_fobj)
    lines.append(f"# START --- {module_path} ---\n")
    for line in module_file:
        if line.startswith("from "):
            _, import_path, __, *imports = line.strip().split(" ")
            imported_module = importlib.import_module(import_path, package=module.__package__)
            if imported_module.__spec__.name in imported_modules:
                continue
            valid_cfg_names = {"cfg", "cfg,"}
            for pattern in valid_cfg_names:
                if pattern in imports:
                    lines.extend(merge_cfg_module(imported_module, imported_modules=imported_modules))
                    if "as" in imports:
                        as_idxs = [idx for idx, elem in enumerate(imports) if elem == "as"]
                        for as_index in as_idxs:
                            if imports[as_index + 1] in pattern:
                                imports = imports[: as_index - 1] + imports[as_index + 2 :]
                    imports.remove(pattern)
                    _check_clone_present(module_file)

                    line = f"from {import_path} import " + ", ".join(imports) if imports else None
                    if line:
                        line += "\n"
        if line:
            lines.append(line)

    lines.append(f"# END --- {module_path} ---\n")

    imported_modules.add(module_name)
    return isort.code("".join(lines)).splitlines(keepends=True)


def add_yaml_str_representer():
    def obj_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))

    yaml.add_multi_representer(object, obj_representer)


def _load_module(module_name: str, module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Could not find an importable module at {module_name=!r}, {module_path=!r}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def _load_package(package_path: Path) -> str:
    init_path = package_path / "__init__.py"
    if not init_path.exists():
        return ""
    package_name = package_path.stem
    parent_package_name = _load_package(package_path.parent)
    if parent_package_name:
        package_name = f"{parent_package_name}.{package_name}"
    _load_module(package_name, init_path)

    return package_name


def full_type_name(_type) -> str:
    module = _type.__module__
    class_name = getattr(_type, "__name__", None) or str(_type)
    if module is None or module == str.__class__.__module__:
        return class_name  # Avoid reporting __builtin__
    return f"{module}.{class_name}"


def full_class_name(obj) -> str:
    return full_type_name(obj.__class__)
