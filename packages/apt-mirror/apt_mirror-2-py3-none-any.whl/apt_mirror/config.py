# SPDX-License-Identifer: GPL-3.0-or-later

import subprocess
from dataclasses import dataclass
from pathlib import Path
from string import Template

from apt_mirror.download import URL, Proxy
from apt_mirror.repository import BaseRepository, ByHash, FlatRepository, Repository

from .logs import get_logger
from .version import __version__


@dataclass
class RepositoryConfig:
    url: URL
    arches: list[str]
    source: bool
    codename: str
    components: list[str]
    by_hash: ByHash

    @classmethod
    def from_line(cls, line: str, default_arch: str):
        log = get_logger(cls)

        repository_type, url = line.split(maxsplit=1)
        source = False

        arches: list[str] = []
        if "-" in repository_type:
            _, arch = repository_type.split("-", maxsplit=1)
            if arch != "src":
                arches.append(arch)
            else:
                source = True

        by_hash = ByHash.YES
        if url.startswith("["):
            options, url = url.split(sep="]", maxsplit=1)
            options = options.strip("[]").strip().split()
            for key, value in map(lambda x: x.split("=", maxsplit=1), options):
                match key:
                    case "arch":
                        for arch in value.split(","):
                            if arch == "src":
                                source = True
                                continue

                            if arch in arches:
                                continue

                            arches.append(arch)
                    case "by-hash":
                        try:
                            by_hash = ByHash(value)
                        except ValueError:
                            log.warning(
                                "Wrong `by-hash` value"
                                f" {value}. Affected config"
                                f" line: {line}"
                            )
                    case _:
                        continue

        url, codename = url.split(maxsplit=1)
        url = URL.from_string(url)

        if not arches and not source:
            arches.append(default_arch)

        if not codename.endswith("/"):
            codename, components = codename.split(maxsplit=1)
            components = components.split()
        else:
            components = []

        return cls(url, arches, source, codename, components, by_hash)

    def to_repository(self) -> BaseRepository:
        if self.is_flat():
            return FlatRepository(
                url=self.url,
                source=self.source,
                arches=self.arches,
                clean=False,
                skip_clean=set(),
                mirror_path=None,
                ignore_errors=set(),
                directory=self.codename,
                by_hash=self.by_hash,
            )
        else:
            repository_by_hash = Repository.ByHashPerCodename.for_codename(
                self.codename,
                self.by_hash,
            )
            return Repository(
                url=self.url,
                mirror_source=(
                    Repository.MirrorSource.for_components(
                        self.codename,
                        self.components,
                        self.source,
                    )
                ),
                arches=Repository.Arches.for_components(
                    self.codename,
                    self.components,
                    self.arches,
                ),
                clean=False,
                skip_clean=set(),
                mirror_path=None,
                ignore_errors=set(),
                codenames=[self.codename],
                components=(
                    Repository.Components.for_codename(
                        self.codename,
                        self.components,
                    )
                ),
                by_hash=repository_by_hash,
            )

    def update_repository(self, repository: BaseRepository):
        if isinstance(repository, Repository):
            if self.codename not in repository.codenames:
                repository.codenames.append(self.codename)

            repository.components[self.codename] = self.components
            repository.by_hash.set_if_default(
                self.codename,
                self.by_hash,
            )

            for component in self.components:
                repository.arches.extend_for_component(
                    self.codename,
                    component,
                    self.arches,
                )

                if self.source:
                    mirror_source = repository.mirror_source
                    mirror_source.set_for_component(
                        self.codename,
                        component,
                        self.source,
                    )

        elif isinstance(repository, FlatRepository):
            if repository.by_hash == ByHash.default():
                repository.by_hash = self.by_hash

            repository.arches.extend(
                arch for arch in self.arches if arch not in repository.arches
            )
            if self.source:
                repository.source = self.source

    def is_flat(self):
        return self.codename.endswith("/")


class Config:
    DEFAULT_CONFIGFILE = "/etc/apt/mirror.list"

    def __init__(self, config_file: Path) -> None:
        self._log = get_logger(self)
        self._repositories: dict[URL, BaseRepository] = {}

        self._files = [config_file]
        config_directory = config_file.with_name(f"{config_file.name}.d")
        if config_directory.is_dir():
            for file in config_directory.glob("*"):
                if not file.is_file() or not file.suffix == ".list":
                    continue

                self._files.append(file)

        try:
            default_arch = subprocess.check_output(
                ["dpkg", "--print-architecture"], encoding="utf-8"
            ).strip()
        except subprocess.CalledProcessError:
            default_arch = "amd64"

        self._variables: dict[str, str] = {
            "defaultarch": default_arch,
            "nthreads": "20",
            "uvloop": "1",
            "base_path": "/var/spool/apt-mirror",
            "mirror_path": "$base_path/mirror",
            "skel_path": "$base_path/skel",
            "var_path": "$base_path/var",
            "cleanscript": "$var_path/clean.sh",
            "run_postmirror": "0",
            "postmirror_script": "$var_path/postmirror.sh",
            "_contents": "1",
            "_autoclean": "0",
            "_tilde": "0",
            "limit_rate": "100m",
            "unlink": "0",
            "use_proxy": "off",
            "http_proxy": "",
            "https_proxy": "",
            "proxy_user": "",
            "proxy_password": "",
            "http_user_agent": f"apt-mirror2/{__version__}",
            "no_check_certificate": "0",
            "certificate": "",
            "private_key": "",
            "ca_certificate": "",
        }

        self._parse_config_file()
        self._substitute_variables()

    def _parse_config_file(self):
        clean: list[URL] = []
        skip_clean: list[URL] = []
        mirror_paths: dict[URL, Path] = {}
        ignore_errors: dict[URL, set[str]] = {}

        for file in self._files:
            with open(file, "rt", encoding="utf-8") as fp:
                for line in fp:
                    line = line.strip()

                    match line:
                        case line if line.startswith("set "):
                            _, key, value = line.split(maxsplit=2)
                            self._variables[key] = value
                        case line if line.startswith("deb"):
                            try:
                                repository_config = RepositoryConfig.from_line(
                                    line, self.default_arch
                                )
                            except ValueError:
                                self._log.warning(
                                    f"Unable to parse repository config line: {line}"
                                )
                                continue

                            repository = self._repositories.get(repository_config.url)
                            if repository:
                                repository_config.update_repository(repository)
                            else:
                                self._repositories[repository_config.url] = (
                                    repository_config.to_repository()
                                )
                        case line if line.startswith("clean "):
                            _, url = line.split()
                            clean.append(URL.from_string(url))
                        case line if line.startswith("skip-clean "):
                            _, url = line.split()
                            skip_clean.append(URL.from_string(url))
                        case line if line.startswith("mirror_path "):
                            _, url, path = line.split(maxsplit=2)
                            mirror_paths[URL.from_string(url)] = Path(path.strip("/"))
                        case line if line.startswith("ignore_errors "):
                            _, url, path = line.split(maxsplit=2)
                            ignore_errors.setdefault(URL.from_string(url), set()).add(
                                path
                            )
                        case line if not line or any(
                            line.startswith(prefix) for prefix in ("#", ";")
                        ):
                            pass
                        case _:
                            self._log.warning(f"Unknown line in config: {line}")

        self._update_clean(clean)
        self._update_skip_clean(skip_clean)
        self._update_mirror_paths(mirror_paths)
        self._update_ignore_errors(ignore_errors)

    def _update_clean(self, clean: list[URL]):
        for url in clean:
            if url not in self._repositories:
                self._log.warning(
                    f"Clean was specified for missing repository URL: {url}"
                )
                continue

            self._repositories[url].clean = True

    def _update_skip_clean(self, skip_clean: list[URL]):
        for url in skip_clean:
            repositories = [
                r for r in self._repositories.values() if r.url.is_part_of(url)
            ]

            for repository in repositories:
                repository.skip_clean.add(
                    Path(url.path).relative_to(Path(repository.url.path))
                )

    def _update_mirror_paths(self, mirror_paths: dict[URL, Path]):
        for url, path in mirror_paths.items():
            if url not in self._repositories:
                self._log.warning(
                    f"mirror_path was specified for missing repository URL: {url}"
                )
                continue

            self._repositories[url].mirror_path = path

    def _update_ignore_errors(self, ignore_errors: dict[URL, set[str]]):
        for url, paths in ignore_errors.items():
            if url not in self._repositories:
                self._log.warning(
                    f"ignore_errors was specified for missing repository URL: {url}"
                )
                continue

            self._repositories[url].ignore_errors.update(paths)

    def _substitute_variables(self):
        max_tries = 16
        template_found = False
        while max_tries == 16 or template_found:
            template_found = False
            for key, value in self._variables.items():
                if "$" not in value:
                    continue

                self._variables[key] = Template(value).substitute(self._variables)
                template_found = True

            max_tries -= 1
            if max_tries < 1:
                raise ValueError(
                    "apt-mirror: too many substitutions while evaluating variables"
                )

    def __getitem__(self, key: str) -> str:
        if key not in self._variables:
            raise KeyError(
                f"Variable {key} is not defined in the config file {self._files[0]}"
            )

        return self._variables[key]

    def get_bool(self, key: str) -> bool:
        return bool(self[key]) and self[key].lower() not in ("0", "off", "no")

    def get_path(self, key: str) -> Path:
        return Path(self[key])

    def as_environment(self) -> dict[str, str]:
        return {f"APT_MIRROR_{k.upper()}": v for k, v in self._variables.items()}

    @property
    def autoclean(self) -> bool:
        return self.get_bool("_autoclean")

    @property
    def base_path(self) -> Path:
        return self.get_path("base_path")

    @property
    def verify_ca_certificate(self) -> bool | str:
        if self.get_bool("no_check_certificate"):
            return False

        if self._variables.get("ca_certificate"):
            return self["ca_certificate"]

        return True

    @property
    def client_private_key(self) -> str:
        return self["private_key"]

    @property
    def client_certificate(self) -> str:
        return self["certificate"]

    @property
    def cleanscript(self) -> Path:
        return self.get_path("cleanscript")

    @property
    def default_arch(self):
        return self["defaultarch"]

    @property
    def encode_tilde(self):
        return self.get_bool("_tilde")

    @property
    def limit_rate(self) -> int | None:
        if "limit_rate" not in self._variables:
            return None

        suffix = self["limit_rate"][-1:]

        if not suffix.isnumeric():
            limit_rate = int(self["limit_rate"][:-1])
            match suffix.lower():
                case "k":
                    return limit_rate * 1024
                case "m":
                    return limit_rate * 1024 * 1024
                case _:
                    raise ValueError(
                        f"Wrong limit_rate configuration suffix: {self['limit_rate']}"
                    )

        return int(self["limit_rate"])

    @property
    def nthreads(self) -> int:
        return int(self._variables["nthreads"])

    @property
    def mirror_path(self) -> Path:
        return self.get_path("mirror_path")

    @property
    def postmirror_script(self) -> Path:
        return self.get_path("postmirror_script")

    @property
    def repositories(self):
        return self._repositories.copy()

    @property
    def run_postmirror(self):
        return self.get_bool("run_postmirror")

    @property
    def skel_path(self) -> Path:
        return self.get_path("skel_path")

    @property
    def use_uvloop(self) -> bool:
        return self.get_bool("uvloop")

    @property
    def var_path(self) -> Path:
        return self.get_path("var_path")

    @property
    def proxy(self) -> Proxy:
        return Proxy(
            use_proxy=self.get_bool("use_proxy"),
            http_proxy=self["http_proxy"],
            https_proxy=self["https_proxy"],
            username=self._variables.get("proxy_user"),
            password=self._variables.get("proxy_password"),
        )

    @property
    def user_agent(self) -> str:
        return self["http_user_agent"]
