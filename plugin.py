from LSP.plugin import AbstractPlugin, ClientConfig, register_plugin, unregister_plugin, WorkspaceFolder
from LSP.plugin.core.typing import Dict, Optional, List
from shutil import which
import os
import sublime
import urllib.request


MARKSMAN_TAG = '2022-08-28'
MARKSMAN_RELEASES_BASE = 'https://github.com/artempyanykh/marksman/releases/download/{tag}/{platform}'
USER_AGENT = 'Sublime Text LSP'


def marksman_binary() -> Optional[str]:
    platform = sublime.platform()
    if platform == 'osx':
        return 'marksman-macos'
    if platform == 'windows':
        return 'marksman.exe'
    if platform == 'linux':
        return 'marksman-linux'
    return None


class Marksman(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return 'marksman'

    @classmethod
    def basedir(cls) -> str:
        return os.path.join(cls.storage_path(), __package__)

    @classmethod
    def marksman_path(cls) -> str:
        return os.path.join(cls.basedir(), 'bin', marksman_binary() or 'unsupported_platform')

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        return {
            'marksman_bin': marksman_binary() or 'unsupported_platform'
        }

    @classmethod
    def server_version(cls) -> str:
        return MARKSMAN_TAG

    @classmethod
    def current_server_version(cls) -> Optional[str]:
        try:
            with open(os.path.join(cls.basedir(), 'VERSION'), 'r') as fp:
                return fp.read()
        except Exception:
            return None

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        if marksman_binary() is None:
            raise ValueError('Platform "{}" is not supported'.format(sublime.platform()))
        return which(cls.marksman_path()) is None or cls.current_server_version() != cls.server_version()

    @classmethod
    def install_or_update(cls) -> None:
        marksman_path = cls.marksman_path()
        os.makedirs(os.path.dirname(marksman_path), exist_ok=True)
        bin_url = MARKSMAN_RELEASES_BASE.format(tag=cls.server_version(), platform=marksman_binary())
        req = urllib.request.Request(
            bin_url,
            data=None,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        with urllib.request.urlopen(req) as fp:
            with open(marksman_path, 'wb') as f:
                f.write(fp.read())

        os.chmod(marksman_path, 0o700)
        with open(os.path.join(cls.basedir(), 'VERSION'), 'w') as fp:
            fp.write(cls.server_version())


def plugin_loaded() -> None:
    register_plugin(Marksman)


def plugin_unloaded() -> None:
    unregister_plugin(Marksman)
