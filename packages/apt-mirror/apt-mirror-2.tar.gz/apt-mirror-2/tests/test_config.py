from pathlib import Path

from apt_mirror.apt_mirror import PathCleaner
from apt_mirror.download import URL
from apt_mirror.repository import ByHash, Repository
from tests.base import BaseTest


class TestConfig(BaseTest):
    def test_multiple_codenames(self):
        config = self.get_config("MixedConfig")

        self.assertEqual(len(config.repositories), 3)

        debian_security = self.ensure_repository(
            config.repositories[
                URL.from_string("http://ftp.debian.org/debian-security")
            ]
        )

        self.assertCountEqual(
            debian_security.codenames,
            ("bookworm-security", "bullseye-security", "trixie-security"),
        )

        self.assertFalse(
            debian_security.mirror_source.is_enabled_for_codename("bookworm-security")
        )
        self.assertFalse(
            debian_security.mirror_source.is_enabled_for_codename("trixie-security")
        )
        self.assertTrue(
            debian_security.mirror_source.is_enabled_for_codename("bullseye-security")
        )

        self.assertCountEqual(
            debian_security.arches.get_for_component("trixie-security", "main"),
            {
                config.default_arch,
                "amd64",
                "arm64",
                "armel",
                "armhf",
                "i386",
                "mips64el",
                "ppc64el",
                "s390x",
            },
        )

        self.assertCountEqual(
            debian_security.arches.get_for_component("bullseye-security", "main"),
            {
                config.default_arch,
                "amd64",
                "arm64",
                "armel",
                "armhf",
                "i386",
                "mips64el",
                "ppc64el",
                "s390x",
            },
        )

        self.assertCountEqual(
            debian_security.arches.get_for_component("bookworm-security", "main"),
            {config.default_arch, "arm64"},
        )

        ubuntu_security = self.ensure_repository(
            config.repositories[URL.from_string("http://archive.ubuntu.com/ubuntu")]
        )

        self.assertCountEqual(
            ubuntu_security.codenames,
            (
                "mantic",
                "mantic-security",
                "mantic-updates",
                "mantic-backports",
                "noble",
                "noble-security",
                "noble-updates",
                "noble-backports",
            ),
        )

        flat_repository = self.ensure_flat_repository(
            config.repositories[
                URL.from_string("http://mirror.something.ru/repository")
            ]
        )

        self.assertTrue(flat_repository.is_binaries_enabled)
        self.assertCountEqual(flat_repository.arches, (config.default_arch,))

    def test_skip_clean(self):
        config = self.get_config("SkipCleanConfig")

        debian = config.repositories[URL.from_string("http://ftp.debian.org/debian")]

        if not isinstance(debian, Repository):
            raise RuntimeError("debian repository is not Repository instance")

        self.assertCountEqual(debian.skip_clean, (Path("abcd"), Path("def/def")))

        cleaner = PathCleaner(
            self.TEST_DATA / "SkipCleanConfig" / "dir1", debian.skip_clean
        )
        self.assertEqual(cleaner.files_count, 0)
        self.assertEqual(cleaner.folders_count, 0)

        cleaner = PathCleaner(
            self.TEST_DATA / "SkipCleanConfig" / "dir2", debian.skip_clean
        )
        self.assertEqual(cleaner.files_count, 1)
        self.assertEqual(cleaner.folders_count, 1)

    def test_by_hash(self):
        config = self.get_config("ByHashConfig")

        repository = self.ensure_repository(
            config.repositories[
                URL.from_string("http://ftp.debian.org/debian-security")
            ]
        )

        self.assertEqual(repository.get_by_hash_policy("trixie-security"), ByHash.FORCE)
        self.assertEqual(repository.get_by_hash_policy("bookworm-security"), ByHash.NO)
        self.assertEqual(repository.get_by_hash_policy("stretch-security"), ByHash.YES)

        repository = self.ensure_repository(
            config.repositories[URL.from_string("http://archive.ubuntu.com/ubuntu")]
        )

        self.assertEqual(repository.get_by_hash_policy("mantic"), ByHash.NO)

        repository = self.ensure_repository(
            config.repositories[
                URL.from_string("http://mirror.something.ru/repository")
            ]
        )

        self.assertEqual(repository.get_by_hash_policy("codename"), ByHash.NO)

    def test_src_arch(self):
        config = self.get_config("SrcOptionConfig")

        repository = self.ensure_repository(
            config.repositories[
                URL.from_string("http://ftp.debian.org/debian-security")
            ]
        )

        self.assertTrue(repository.arches.is_empty())
        self.assertTrue(repository.is_source_enabled)

        repository = self.ensure_repository(
            config.repositories[URL.from_string("http://archive.ubuntu.com/ubuntu")]
        )

        self.assertTrue(repository.arches.is_empty())
        self.assertTrue(repository.is_source_enabled)

    def test_ignore_errors(self):
        config = self.get_config("IgnoreErrorsConfig")

        repository = self.ensure_repository(
            config.repositories[
                URL.from_string(
                    "https://packages.gitlab.com/runner/gitlab-runner/debian"
                )
            ]
        )

        self.assertCountEqual(
            repository.ignore_errors,
            [
                "pool/bullseye/main/g/gitlab-runner/gitlab-runner_14.8.1_amd64.deb",
                "pool/bullseye/main/d",
            ],
        )
