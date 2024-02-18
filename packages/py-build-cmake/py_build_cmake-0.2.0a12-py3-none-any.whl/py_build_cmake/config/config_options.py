"""
Classes to define hierarchical configuration options which support inheriting
from other options, default values, overriding options, etc.
"""

from __future__ import annotations

import logging
import os
import os.path as osp
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from ..common import ConfigError

logger = logging.getLogger(__name__)

ConfPath = Tuple[str, ...]
ConfValue = Optional[Union[bool, int, str, List[str], Dict[str, Any]]]
Conf = Dict[str, Any]


def pth(s: str) -> ConfPath:
    if not s:
        return ()
    return tuple(s.split("/"))


def pth2str(p: ConfPath) -> str:
    return "/".join(p)


def joinpth(p1: ConfPath, p2: ConfPath) -> ConfPath:
    while p1 and p2 and p2[0] == "^":
        p1 = p1[:-1]
        p2 = p2[1:]
    return p1 + p2


def hasparent(path: ConfPath) -> bool:
    return len(path) >= 1


def parent(path: ConfPath) -> ConfPath:
    if not hasparent(path):
        msg = f"Path {pth2str(path)} does not have a parent"
        raise RuntimeError(msg)
    return path[:-1]


def basename(path: ConfPath) -> str:
    return path[-1]


class ConfigNode:
    def __init__(
        self, value: ConfValue = None, sub: dict[str, ConfigNode] | None = None
    ) -> None:
        self.value: ConfValue = value
        self.sub: dict[str, ConfigNode] | None = sub
        self.inherited = False

    @classmethod
    def from_dict(cls, d: dict):
        node = cls()
        node.sub = {}
        for k, v in d.items():
            if isinstance(v, dict):
                node.sub[k] = cls.from_dict(v)
            else:
                node.sub[k] = cls(value=v)
        return node

    def to_dict(self):
        if self.sub is None:
            return self.value
        return {k: v.to_dict() for k, v in self.sub.items()}

    def iter_dfs(self, path: ConfPath = ()):
        yield path, self
        if self.sub is not None:
            for name, sub in self.sub.items():
                yield from sub.iter_dfs((*path, name))

    def __getitem__(self, key):
        if isinstance(key, str):
            if self.sub is None:
                raise KeyError()
            return self.sub[key]
        elif isinstance(key, tuple):
            if len(key) == 0:
                return self
            elif self.sub is None:
                raise KeyError()
            else:
                return self.sub[key[0]][key[1:]]
        else:
            raise TypeError(key)

    def get(self, key: ConfPath, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, path: str | ConfPath, default: Any):
        if isinstance(path, str):
            path = (path,)
        tgt = self[parent(path)]
        if tgt.sub is None:
            tgt.sub = {}
        return tgt.sub.setdefault(basename(path), default)

    def contains(self, path: str | ConfPath):
        try:
            self[path]
            return True
        except KeyError:
            return False


@dataclass
class DefaultValueWrapper:
    value: ConfValue


class DefaultValue(ABC):
    @abstractmethod
    def get_default(
        self,
        rootopts: ConfigOption,
        opt: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        optpath: ConfPath,
    ) -> DefaultValueWrapper | None: ...

    @abstractmethod
    def get_name(self) -> str: ...


class DefaultValueValue(DefaultValue):
    def __init__(self, value: ConfValue) -> None:
        self.value: ConfValue = value

    def get_default(
        self,
        rootopts: ConfigOption,
        opt: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        optpath: ConfPath,
    ) -> DefaultValueWrapper | None:
        return DefaultValueWrapper(self.value)

    def get_name(self) -> str:
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return repr(self.value)


class NoDefaultValue(DefaultValue):
    def __init__(self, name: str = "none"):
        self.name = name

    def get_default(
        self,
        rootopts: ConfigOption,
        opt: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        optpath: ConfPath,
    ) -> DefaultValueWrapper | None:
        return None

    def get_name(self) -> str:
        return self.name


class MissingDefaultError(ConfigError):
    """The user did not provide a required value."""


class RequiredValue(DefaultValue):
    def get_default(
        self,
        rootopts: ConfigOption,
        opt: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        optpath: ConfPath,
    ) -> DefaultValueWrapper | None:
        msg = f"{pth2str(cfgpath)} requires a value"
        raise MissingDefaultError(msg)

    def get_name(self) -> str:
        return "required"


class RefDefaultValue(DefaultValue):
    def __init__(self, path: ConfPath, relative: bool = False) -> None:
        super().__init__()
        self.path: ConfPath = path
        self.relative = relative

    def get_default(
        self,
        rootopts: ConfigOption,
        opt: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        optpath: ConfPath,
    ) -> DefaultValueWrapper | None:
        abscfgpath = absoptpath = self.path
        if self.relative:
            absoptpath = joinpth(optpath, ("^", *absoptpath))
            abscfgpath = joinpth(cfgpath, ("^", *abscfgpath))
        ref_opt = rootopts.get(absoptpath)
        if ref_opt is None:
            msg = f"DefaultValue: reference to nonexisting option {pth2str(absoptpath)}"
            raise ValueError(msg)
        return ref_opt.update_default(rootopts, cfg, abscfgpath, absoptpath)

    def get_name(self) -> str:
        r = pth2str(self.path).replace("^", "..")
        if not self.relative:
            r = "/" + r
        return r


class ConfigOption:
    allow_unknown_keys = False

    def __init__(
        self,
        name: str,
        description: str = "",
        example: str = "",
        default: DefaultValue | None = None,
        inherit_from: ConfPath | None = None,
        create_if_inheritance_target_exists: bool = False,
    ) -> None:
        if default is None:
            default = NoDefaultValue()
        self.name = name
        self.description = description
        self.example = example
        self.sub: dict[str, ConfigOption] = {}
        self.default: DefaultValue = default
        self.inherit_from: ConfPath | None = inherit_from
        self.create_if_inheritance_target_exists = create_if_inheritance_target_exists

    def get_typename(self, md: bool = False):
        return None

    def insert(self, opt: ConfigOption):
        assert opt.name not in self.sub
        self.sub[opt.name] = opt
        return self.sub[opt.name]

    def insert_multiple(self, opts: Iterable[ConfigOption]):
        for opt in opts:
            self.insert(opt)

    def iter_opt_paths(self) -> Iterator[ConfPath]:
        """DFS of the option tree."""
        for name, subopt in self.sub.items():
            yield (name,)
            for p in subopt.iter_opt_paths():
                yield (name, *p)

    def iter_leaf_opt_paths(self) -> Iterator[ConfPath]:
        """DFS of the option tree."""
        if not self.sub:
            yield ()
        else:
            for name, subopt in self.sub.items():
                for p in subopt.iter_leaf_opt_paths():
                    yield (name, *p)

    def iter_dfs(self, path: ConfPath = ()):
        yield path, self
        for name, sub in self.sub.items():
            yield from sub.iter_dfs((*path, name))

    def __getitem__(self, key) -> ConfigOption:
        if isinstance(key, str):
            return self.sub[key]
        elif isinstance(key, tuple):
            if len(key) == 0:
                return self
            else:
                return self.sub[key[0]][key[1:]]
        else:
            raise TypeError(key)

    def get(self, key: ConfPath, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, path: ConfPath, default: Any):
        tgt = self[parent(path)]
        return tgt.sub.setdefault(basename(path), default)

    def contains(self, path: ConfPath):
        try:
            self[path]
            return True
        except KeyError:
            return False

    def inherit(self, rootopts: ConfigOption, cfg: ConfigNode, selfpth: ConfPath):
        superpth = self.inherit_from
        if superpth is not None:
            # If the super option is not set, there's nothing to inherit
            supercfg = cfg.get(superpth)
            if supercfg is None:
                return

            # If this option is not set, but the super option is,
            # create our own config as well, including all of its parents,
            # but only if create_if_inheritance_target_exists is set on those
            # options
            selfcfg = self.create_parent_config_for_inheritance(rootopts, cfg, selfpth)
            # If this option still does not exist, our work is done.
            if selfcfg is None:
                return
            # If we already inherited, don't do it again
            if selfcfg.inherited:
                return

            # Find the option we inherit from and make sure it exists
            superopt = rootopts.get(superpth)
            if superopt is None:
                msg = f"{pth2str(superpth)} is not a valid option"
                raise ValueError(msg)

            # If our super option inherits from other options, carry out that
            # inheritance first
            # TODO: this doesn't work if we inherit from a subtree whose
            # parent inherits from something else, we might need to traverse
            # up the tree until we find a parent of our superopt that also
            # inherits. This is stretching it for the current implementation,
            # though, so I'll keep this for the future rewrite.
            superopt.inherit(rootopts, cfg, superpth)

            # Create a copy of the config of our super-option and override it
            # with our own config
            supercfg = deepcopy(supercfg)
            # Clear the inherited flags from the copied tree
            for _, s in supercfg.iter_dfs():
                if s is not None:
                    s.inherited = False
            superopt.explicit_override(rootopts, supercfg, superpth, selfcfg, selfpth)
            selfcfg.sub = supercfg.sub
            selfcfg.inherited = True
        if self.sub:
            for name, sub in self.sub.items():
                sub.inherit(rootopts, cfg, (*selfpth, name))

    @staticmethod
    def create_parent_config_for_inheritance(
        rootopts: ConfigOption, cfg: ConfigNode, selfpth: ConfPath
    ):
        """
        Loop over all parent options of selfpth in rootopts and default-
        initialize their configuration in cfg to empty ConfigNodes if the
        option's create_if_inheritance_target_exists is set to True.
        Returns cfg[selfpth] or None if parents were not created because of
        create_if_inheritance_target_exists.
        """
        selfcfg = None
        p: ConfPath = ()
        opt = rootopts
        create_paths: list[ConfPath] = []
        for s in selfpth:
            p += (s,)
            opt = opt[s]
            selfcfg = cfg.get(p)
            if selfcfg is None:
                if not opt.create_if_inheritance_target_exists:
                    return None
                create_paths.append(p)
        for p in create_paths:
            selfcfg = cfg.setdefault(p, ConfigNode(sub={}))
        return selfcfg

    def explicit_override(
        self,
        rootopts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        # The default ConfigOption simply overrides all of its sub-options, but
        # this function is overridden by specific subclasses.

        # If this option inherits from another, we have to use that other
        # option's option tree, because this one is empty
        if self.inherit_from is not None:
            assert not self.sub, "Inheriting options should not have sub-options"
            actual_opts = rootopts[self.inherit_from]
            return actual_opts.explicit_override(
                rootopts, selfcfg, selfpth, overridecfg, overridepath
            )
        # If no sub-options are set in the config, there is nothing to override
        if not overridecfg.sub:
            return None
        # Actually override all sub-options
        for name, subopt in self.sub.items():
            assert isinstance(selfcfg, ConfigNode)
            assert isinstance(overridecfg, ConfigNode)
            # Only override sub-options that are present in the overrider's config
            if name not in overridecfg.sub:
                continue
            # Add the overrider's option to our own config
            subselfcfg = selfcfg.setdefault((name,), ConfigNode())
            subpath = (*selfpth, name)
            suboverridepath = (*overridepath, name)
            suboverridecfg = overridecfg.sub[name]
            # Override our subconfig by the overrider's subconfig
            subopt.explicit_override(
                rootopts, subselfcfg, subpath, suboverridecfg, suboverridepath
            )
        return None

    def override(self, rootopts: ConfigOption, cfg: ConfigNode, selfpath: ConfPath):
        """Override other options with this option if appropriate. This is a
        no-op in most cases and only does something in OverrideConfigOption."""
        assert cfg.contains(selfpath)

    def verify_impl(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        assert cfg.contains(cfgpath)
        selfcfg = cfg[cfgpath]
        # Check if there are any unknown options in the config
        if not self.allow_unknown_keys:
            unknwn = set(selfcfg.sub or ()) - set(self.sub or ())
            if unknwn:
                raise ConfigError(
                    f"Unknown options in {pth2str(cfgpath)}: " + ", ".join(unknwn)
                )
        # Recursively verify the sub-options
        if selfcfg.sub:
            for name, _sub in selfcfg.sub.items():
                if name in self.sub:
                    self.sub[name].verify(rootopts, cfg, (*cfgpath, name))

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if self.inherit_from is None:
            return self.verify_impl(rootopts, cfg, cfgpath)
        else:
            return rootopts[self.inherit_from].verify_impl(rootopts, cfg, cfgpath)

    def override_all(self, cfg: ConfigNode):
        # This is just me being lazy, we probably don't need to iterate over
        # all nodes ...
        for p, opt in self.iter_dfs():
            if cfg.contains(p):
                opt.override(self, cfg, p)

    def verify_all(self, cfg: ConfigNode):
        self.verify(self, cfg, ())

    def inherit_all(self, cfg: ConfigNode):
        self.inherit(self, cfg, ())

    def update_default(
        self,
        rootopts: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        selfpath: ConfPath | None = None,
        max_depth: int = 5,
    ) -> DefaultValueWrapper | None:
        if selfpath is None:
            selfpath = cfgpath

        result = None
        # If the entire path exists in cfg, simply return that value
        cfgval = cfg.get(cfgpath)
        if cfgval is not None:
            result = cfgval
        # If the path is not yet in cfg
        else:
            assert self is rootopts[selfpath]
            # Find the default value for this option
            default = self.default.get_default(rootopts, self, cfg, cfgpath, selfpath)
            # Only set our value if our parent exists
            if default is not None and cfg.contains(parent(cfgpath)):
                cfgval = cfg.setdefault(cfgpath, ConfigNode())
                cfgval.value = default.value
                if cfgval.value is not None:
                    self.verify(rootopts, cfg, cfgpath)
            result = default

        # If we inherited from another option, apply the defaults of our
        # target to our own config
        if self.inherit_from is not None:
            targetopt = rootopts.get(self.inherit_from)
            if targetopt is None:
                msg = f"Inheritance {pth2str(selfpath)} targets nonexisting option {pth2str(self.inherit_from)}"
                raise ValueError(msg)
            for p, opt in targetopt.iter_dfs():
                inherits = opt.inherit_from is None
                max_depth_left = max_depth if inherits else max_depth - 1
                if max_depth_left == 0:
                    logger.warning("Maximum inheritance reached")
                    continue
                optpth = joinpth(self.inherit_from, p)
                newcfgpth = joinpth(cfgpath, p)
                opt.update_default(
                    rootopts, cfg, newcfgpth, optpth, max_depth=max_depth_left
                )

        return result

    def update_default_all(self, cfg: ConfigNode):
        for p, opt in self.iter_dfs():
            if hasparent(p) and cfg.contains(parent(p)):
                opt.update_default(self, cfg, p)


class UncheckedConfigOption(ConfigOption):
    allow_unknown_keys = True


class StrConfigOption(ConfigOption):
    def get_typename(self, md: bool = False):
        return "string"

    def explicit_override(
        self,
        opts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        assert not self.sub
        assert not selfcfg.sub
        assert not overridecfg.sub
        selfcfg.value = deepcopy(overridecfg.value)

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if cfg[cfgpath].sub:
            msg = f"Type of {pth2str(cfgpath)} should be {str}, not {dict}"
            raise ConfigError(msg)
        elif not isinstance(cfg[cfgpath].value, str):
            msg = f"Type of {pth2str(cfgpath)} should be {str}, not {type(cfg[cfgpath].value)}"
            raise ConfigError(msg)


class IntConfigOption(ConfigOption):
    def get_typename(self, md: bool = False):
        return "int"

    def explicit_override(
        self,
        opts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        assert not self.sub
        assert not selfcfg.sub
        assert not overridecfg.sub
        selfcfg.value = deepcopy(overridecfg.value)

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if cfg[cfgpath].sub:
            msg = f"Type of {pth2str(cfgpath)} should be {int}, not {dict}"
            raise ConfigError(msg)
        elif not isinstance(cfg[cfgpath].value, int):
            msg = f"Type of {pth2str(cfgpath)} should be {int}, not {type(cfg[cfgpath].value)}"
            raise ConfigError(msg)


class EnumConfigOption(ConfigOption):
    def __init__(
        self,
        name: str,
        description: str = "",
        example: str = "",
        default: DefaultValue | None = None,
        inherit_from: ConfPath | None = None,
        create_if_inheritance_target_exists: bool = False,
        options: list[str] | None = None,
    ) -> None:
        if default is None:
            default = NoDefaultValue()
        if options is None:
            options = []
        super().__init__(
            name,
            description,
            example,
            default,
            inherit_from,
            create_if_inheritance_target_exists,
        )
        self.options = options

    def get_typename(self, md: bool = False):
        if md:
            return "`'" + "'` \\| `'".join(self.options) + "'`"
        else:
            return "'" + "' | '".join(self.options) + "'"

    def explicit_override(
        self,
        opts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        assert not self.sub
        assert not selfcfg.sub
        assert not overridecfg.sub
        selfcfg.value = deepcopy(overridecfg.value)

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if cfg[cfgpath].sub:
            msg = f"Type of {pth2str(cfgpath)} should be {str}, not {dict}"
            raise ConfigError(msg)
        elif not isinstance(cfg[cfgpath].value, str):
            msg = f"Type of {pth2str(cfgpath)} should be {str}, not {type(cfg[cfgpath].value)}"
            raise ConfigError(msg)
        if cfg[cfgpath].value not in self.options:
            raise ConfigError(
                f"Value of {pth2str(cfgpath)} should be "
                "one of '" + "', '".join(self.options) + "'"
            )


class BoolConfigOption(ConfigOption):
    def get_typename(self, md: bool = False):
        return "bool"

    def explicit_override(
        self,
        opts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        assert not self.sub
        assert not selfcfg.sub
        assert not overridecfg.sub
        selfcfg.value = deepcopy(overridecfg.value)

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if cfg[cfgpath].sub:
            msg = f"Type of {pth2str(cfgpath)} should be {bool}, not {dict}"
            raise ConfigError(msg)
        elif not isinstance(cfg[cfgpath].value, bool):
            msg = f"Type of {pth2str(cfgpath)} should be {bool}, not {type(cfg[cfgpath].value)}"
            raise ConfigError(msg)


@dataclass
class RelativeToCurrentConfig:
    project_path: Path
    description: str = "current configuration file"


@dataclass
class RelativeToProject:
    project_path: Path
    description: str = "project directory"


class PathConfigOption(StrConfigOption):
    def __init__(
        self,
        name: str,
        description: str = "",
        example: str = "",
        default: DefaultValue | None = None,
        must_exist: bool = True,
        expected_contents: list[str] | None = None,
        base_path: RelativeToProject | RelativeToCurrentConfig | None = None,
        allow_abs: bool = False,
        is_folder: bool = True,
    ):
        if default is None:
            default = NoDefaultValue()
        if expected_contents is None:
            expected_contents = []
        super().__init__(name, description, example, default)
        self.must_exist = must_exist or bool(expected_contents)
        self.expected_contents = expected_contents
        self.base_path = base_path
        self.allow_abs = allow_abs
        self.is_folder = is_folder
        if self.base_path:
            assert self.base_path.project_path.is_absolute()

    def get_typename(self, md: bool = False):
        return "path" if self.is_folder else "filepath"

    def check_path(self, cfg: ConfigNode, cfgpath):
        osp = os.path
        path = osp.normpath(cfg[cfgpath].value)
        # Absolute or relative path?
        if osp.isabs(path):
            # Absolute path
            if not self.allow_abs:
                msg = f'{pth2str(cfgpath)}: "{path!s}" must be a relative path'
                raise ConfigError(msg)
        # Relative path
        elif isinstance(self.base_path, RelativeToCurrentConfig):
            # cfgpath[0] is relative for files inside of the project,
            # otherwise it is absolute
            path = osp.join(osp.dirname(cfgpath[0]), path)
            if not osp.isabs(path):
                path = osp.join(self.base_path.project_path, path)
        elif isinstance(self.base_path, RelativeToProject):
            path = osp.join(self.base_path.project_path, path)
        else:
            msg = "Invalid relative path type"
            raise AssertionError(msg)
        assert osp.isabs(path), "Failed to make path absolute"
        # Does the path exist?
        if self.must_exist:
            if not osp.exists(path):
                msg = f'{pth2str(cfgpath)}: "{path!s}" does not exist'
                raise ConfigError(msg)
            if self.is_folder != osp.isdir(path):
                type_ = "directory" if self.is_folder else "file"
                msg = f'{pth2str(cfgpath)}: "{path!s}" should be a {type_}'
                raise ConfigError(msg)
            # Are any of the required contents missing?
            missing = [
                sub
                for sub in self.expected_contents
                if not osp.exists(osp.join(path, sub))
            ]
            if missing:
                missingstr = '", "'.join(missing)
                msg = f'{pth2str(cfgpath)}: "{path!s}" does not contain the following required files or folders: "{missingstr}"'
                raise ConfigError(msg)
        cfg[cfgpath].value = osp.normpath(path)

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        super().verify(rootopts, cfg, cfgpath)
        self.check_path(cfg, cfgpath)


class ListOfStrConfigOption(ConfigOption):
    def __init__(
        self,
        name: str,
        description: str = "",
        example: str = "",
        default: DefaultValue | None = None,
        inherit_from: ConfPath | None = None,
        create_if_inheritance_target_exists: bool = False,
        convert_str_to_singleton=False,
        append_by_default=False,
    ) -> None:
        super().__init__(
            name,
            description,
            example,
            default,
            inherit_from,
            create_if_inheritance_target_exists,
        )
        self.convert_str_to_singleton = convert_str_to_singleton
        self.append_by_default = append_by_default

    list_op_keys = frozenset(("+", "-", "=", "append", "prepend"))

    def get_typename(self, md: bool = False):
        return "list+" if self.append_by_default else "list"

    def _override_list(self, selfcfg, overridecfg):
        assert isinstance(overridecfg.value, list)
        if self.append_by_default:
            selfcfg.value += deepcopy(overridecfg.value)
        else:
            selfcfg.value = deepcopy(overridecfg.value)

    def _override_dict(self, selfcfg, overridecfg):
        if "=" in overridecfg.sub:
            selfcfg.value = deepcopy(overridecfg.sub["="].value)
            return
        if "-" in overridecfg.sub:
            remove = set(overridecfg.sub["-"].value)
            selfcfg.value = [v for v in selfcfg.value if v not in remove]
        if "+" in overridecfg.sub:
            selfcfg.value += deepcopy(overridecfg.sub["+"].value)
        if "append" in overridecfg.sub:
            selfcfg.value += deepcopy(overridecfg.sub["append"].value)
        if "prepend" in overridecfg.sub:
            selfcfg.value = deepcopy(overridecfg.sub["prepend"].value) + selfcfg.value

    def explicit_override(
        self,
        opts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        assert not self.sub
        assert not selfcfg.sub
        if overridecfg.sub is not None:
            if selfcfg.sub is not None:
                msg = f"Type of {pth2str(selfpth)} should be {list}, not {dict}"
                raise ConfigError(msg)
            if selfcfg.value is None:
                selfcfg.value = []
            assert isinstance(selfcfg.value, list)
            self._override_dict(selfcfg, overridecfg)
        if overridecfg.value is not None:
            if selfcfg.value is None:
                selfcfg.value = []
            assert isinstance(selfcfg.value, list)
            self._override_list(selfcfg, overridecfg)

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if cfg[cfgpath].sub is not None:
            value = cfg[cfgpath].sub
            invalid_keys = set(value.keys()) - self.list_op_keys
            if invalid_keys:
                inv_str = ", ".join(map(str, invalid_keys))
                val_str = ", ".join(map(str, self.list_op_keys))
                msg = f"Invalid keys in {pth2str(cfgpath)}: {inv_str} (valid keys are: {val_str})"
            for k, v in value.items():
                pthname = f"{pth2str(cfgpath)}[{k}]"
                if v.sub is not None:
                    msg = f"Type of {pthname} should be {list}, not {dict}"
                    raise ConfigError(msg)
                if not isinstance(v.value, list):
                    msg = f"Type of {pthname} should be {list}, not {type(v.value)}"
                    raise ConfigError(msg)
                if not all(isinstance(el, str) for el in v.value):
                    msg = f"Type of elements in {pthname} should be {str}"
                    raise ConfigError(msg)
        elif not isinstance(cfg[cfgpath].value, list):
            if self.convert_str_to_singleton and isinstance(cfg[cfgpath].value, str):
                cfg[cfgpath].value = [cfg[cfgpath].value]
            else:
                msg = f"Type of {pth2str(cfgpath)} should be {list}, not {type(cfg[cfgpath].value)}"
                raise ConfigError(msg)
        elif not all(isinstance(el, str) for el in cfg[cfgpath].value):
            msg = f"Type of elements in {pth2str(cfgpath)} should be {str}"
            raise ConfigError(msg)

    def _dict_to_list(self, d: dict) -> list[str]:
        if not d:
            return []
        if "=" in d:
            return d["="].value
        r = []
        if "prepend" in d:
            r = d["prepend"].value
        if "append" in d:
            r += d["append"].value
        if "+" in d:
            r += d["+"].value
        return r

    def update_default(
        self,
        rootopts: ConfigOption,
        cfg: ConfigNode,
        cfgpath: ConfPath,
        selfpath: ConfPath | None = None,
        max_depth: int = 5,
    ) -> DefaultValueWrapper | None:
        # This is a bit of a hack, but the user might have specified a dict
        # (the override syntax) for the base option. This is not allowed, but
        # we cannot really detect it any earlier, because we have to know
        # whether it's going to be overriding anything first (for which we
        # would have to traverse the entire option tree up to the root, because
        # our parents might be overriding something).
        cfgnode = cfg.get(cfgpath)
        if cfgnode is not None and cfgnode.sub is not None:
            cfgnode.value = self._dict_to_list(cfgnode.sub)
            cfgnode.sub = None
            msg = f"Type of {pth2str(cfgpath)} should be {list}, not {dict}"
            raise ConfigError(msg)
        return super().update_default(rootopts, cfg, cfgpath, selfpath, max_depth)


class DirPatternsConfigOption(ListOfStrConfigOption):
    def __init__(
        self,
        name: str,
        description: str = "",
        example: str = "",
        default: DefaultValue | None = None,
        inherit_from: ConfPath | None = None,
        create_if_inheritance_target_exists: bool = False,
        convert_str_to_singleton=False,
    ) -> None:
        super().__init__(
            name,
            description,
            example,
            default,
            inherit_from,
            create_if_inheritance_target_exists,
            convert_str_to_singleton,
        )

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        # Based on https://github.com/pypa/flit/blob/f7496a50debdfa393e39f8e51d328deabcd7ae7e/flit_core/flit_core/config.py#L215
        super().verify(rootopts, cfg, cfgpath)
        # Windows filenames can't contain these (nor * or ?, but they are part of
        # glob patterns) - https://stackoverflow.com/a/31976060/434217
        bad_chars = re.compile(r'[\000-\037<>:"\\]')
        pattern_list = cfg[cfgpath].value
        for i, pattern in enumerate(pattern_list):
            if bad_chars.search(pattern):
                msg = f"Pattern '{pattern}' in {pth2str(cfgpath)} contains bad characters (<>:\"\\ or control characters)"
                raise ConfigError(msg)
            # Normalize the path
            normp = PurePath(osp.normpath(pattern))
            # Make sure that the path is relative and inside of the project
            if normp.is_absolute():
                msg = f"Pattern '{pattern}' in {pth2str(cfgpath)} should be relative"
                raise ConfigError(msg)
            if normp.parts[0] == "..":
                msg = f"Pattern '{pattern}' in {pth2str(cfgpath)} cannot refer to the parent directory (..)"
                raise ConfigError(msg)
            pattern_list[i] = str(normp)


class DictOfStrConfigOption(ConfigOption):
    def get_typename(self, md: bool = False):
        return "dict"

    def explicit_override(
        self,
        opts: ConfigOption,
        selfcfg: ConfigNode,
        selfpth: ConfPath,
        overridecfg: ConfigNode,
        overridepath: ConfPath,
    ):
        assert not self.sub
        assert not selfcfg.value
        assert not overridecfg.value
        if overridecfg.sub is not None:
            if selfcfg.sub is None:
                selfcfg.sub = {}
            assert isinstance(selfcfg.sub, dict)
            assert isinstance(overridecfg.sub, dict)
            selfcfg.sub.update(deepcopy(overridecfg.sub))

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        if cfg[cfgpath].value is not None:
            if isinstance(cfg[cfgpath].value, dict):
                newcfg = ConfigNode.from_dict(cfg[cfgpath].value)
                cfg[cfgpath].value = newcfg.value
                cfg[cfgpath].sub = newcfg.sub
            else:
                msg = f"Type of {pth2str(cfgpath)} should be {dict}, not {type(cfg[cfgpath].value)}"
                raise ConfigError(msg)
        valdict = cfg[cfgpath].sub
        if not isinstance(valdict, dict):
            msg = f"Type of {pth2str(cfgpath)} should be {dict}, not {type(valdict)}"
            raise ConfigError(msg)
        elif not all(isinstance(el, str) for el in valdict):
            msg = f"Type of keys in {pth2str(cfgpath)} should be {str}"
            raise ConfigError(msg)
        elif not all(isinstance(el.value, str) for el in valdict.values()):
            msg = f"Type of values in {pth2str(cfgpath)} should be {str}"
            raise ConfigError(msg)


class OverrideConfigOption(ConfigOption):
    def __init__(
        self,
        name: str,
        description: str,
        targetpath: ConfPath,
        default: DefaultValue | None = None,
    ) -> None:
        super().__init__(name, description, "", default)
        self.targetpath = targetpath

    def verify(self, rootopts: ConfigOption, cfg: ConfigNode, cfgpath: ConfPath):
        rootopts[self.targetpath].verify(rootopts, cfg, cfgpath)

    def inherit(self, rootopts: ConfigOption, cfg: ConfigNode, selfpth: ConfPath):
        pass

    def override(self, rootopts: ConfigOption, cfg: ConfigNode, selfpth: ConfPath):
        selfcfg = cfg.get(selfpth, None)
        if selfcfg is None or (selfcfg.value is None and selfcfg.sub is None):
            return
        super().override(rootopts, cfg, selfpth)
        curropt = rootopts[self.targetpath]
        self.create_parent_config(cfg, self.targetpath)
        currcfg = cfg[self.targetpath]
        overridecfg = cfg[selfpth]
        # Override the config at those paths by our own config
        curropt.explicit_override(
            rootopts, currcfg, self.targetpath, overridecfg, selfpth
        )

    @staticmethod
    def create_parent_config(cfg: ConfigNode, path: ConfPath):
        parentcfg = cfg
        for s in path:
            assert parentcfg.sub is not None
            parentcfg = parentcfg.sub.setdefault(s, ConfigNode(sub={}))
