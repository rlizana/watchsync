import json
import os
import shutil
import subprocess
import threading
import time
import tracemalloc
import unittest

from cleo import exceptions
from cleo.testers.command_tester import CommandTester

from watchsync import APP_NAME, __version__, create_app, utils
from watchsync.config import Config
from watchsync.daemon.connector import Connector
from watchsync.daemon.watchsyncd import main as watchsyncd_main
from watchsync.logger import logger as base_logger

tracemalloc.start()


class TestTreytuxControl(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.app = create_app()
        self.workspace = os.path.join(os.path.dirname(__file__), "workspace")
        self.config = Config(os.path.join(self.workspace, "config.yml"))

    def path(self, *args):
        return os.path.join(self.workspace, *args)

    def path_file(self, *args):
        return self.path(*("file", *args))

    def path_storage(self, *args):
        relative = self.path_file(*args)
        return self.path("storage") + relative

    def create_file(self, name, content="test"):
        with open(self.path_file(name), "w", encoding="utf-8") as file:
            file.write(content)

    def reset_test_folder(self):
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace)
        sample_path = os.path.join(os.path.dirname(__file__), "sample")
        shutil.copytree(sample_path, self.workspace)

    def execute(self, txt):
        args = txt.split(" ")
        cmd_list = []
        cmd = None
        while args:
            cmd_list.append(args.pop(0))
            try:
                cmd = self.app.find(" ".join(cmd_list))
            except exceptions.CleoCommandNotFoundError:
                continue
            break
        cmd = CommandTester(cmd)
        args.append(f"--config-file={self.config.config_file}")
        result_code = cmd.execute(" ".join(args))
        return result_code, cmd._io.fetch_output()

    def test_utils_shell(self):
        result = utils.shell(
            "logger -p local0.info 'WatchSync Test Message'", show_stdout=False
        )
        self.assertEqual(result, None)
        user = utils.shell("whoami")
        self.assertTrue(user)
        id_str = utils.shell("id")
        self.assertIn(f"({user})", id_str)
        with self.assertRaises(subprocess.TimeoutExpired):
            utils.shell("sleep 1d", timeout=1)
        with self.assertRaises(subprocess.CalledProcessError):
            utils.shell("command-not-exists")
        result = utils.shell("command-not-exists", show_stdout=False)
        self.assertEqual(result, None)

    def test_config(self):
        self.reset_test_folder()
        os.remove(self.config.config_file)
        with self.assertRaises(FileNotFoundError):
            self.execute("version")
        self.assertFalse(os.path.exists(self.config.config_file))
        shutil.rmtree(self.config.config_path)
        self.config.write()
        self.assertTrue(os.path.exists(self.config.config_file))
        self.assertEqual(self.config.get("not-exist", "default"), "default")
        self.assertIn("'config_file':", str(self.config))
        self.assertEqual(self.config.__repr__(), str(self.config))
        with self.assertRaises(FileNotFoundError):
            Config.get_config(config_file="/not-exists", use_defaults=False)

    def test_help(self):
        cmd = CommandTester(self.app.find("help-list"))
        result_code = cmd.execute("")
        self.assertEqual(result_code, 0)
        self.assertIn("Available commands", cmd._io.fetch_output())
        result_code = cmd.execute("--simple")
        self.assertEqual(result_code, 0)
        output = cmd._io.fetch_output()
        self.assertNotIn("Available commands", output)
        self.assertIn("start", output)

    def test_version(self):
        self.reset_test_folder()
        result_code, output = self.execute("version")
        self.assertEqual(result_code, 0)
        self.assertIn(__version__, output)
        pyproject_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
        )
        with open(pyproject_file, "r", encoding="utf-8") as file:
            content = file.read()
        self.assertIn(
            f'version = "{__version__}"',
            content,
            "Not same version in pyproject.toml and __version__",
        )

    def test_logger(self):
        logger = base_logger.getChild("WatchSyncDaemon")
        with self.assertLogs(APP_NAME, level="ERROR") as cm:
            logger.error("Sample test error.")
        self.assertIn("Sample test error.", cm.output[0])

    def test_storage(self):
        self.reset_test_folder()
        result_code, output = self.execute("storage list")
        self.assertEqual(result_code, 0)
        self.assertIn("No storages found.", output)
        result_code, output = self.execute("storage add test1 rsync /tmp")
        self.assertEqual(result_code, 0)
        result_code, output = self.execute("storage list")
        self.assertEqual(result_code, 0)
        self.assertIn("test1", output)
        self.assertIn("rsync", output)
        self.assertIn("/tmp", output)
        self.assertIn("{}", output)
        result_code, output = self.execute("storage add test2 rsync /tmp")
        self.assertEqual(result_code, 0)
        result_code, output = self.execute("storage add test2 rsync /tmp")
        self.assertEqual(result_code, 1)
        self.assertIn("Storage already exists", output)
        result_code, output = self.execute(
            "storage add not-exist not-exist /tmp"
        )
        self.assertEqual(result_code, 2)
        self.assertIn("not found", output)
        result_code, output = self.execute("storage list")
        self.assertEqual(result_code, 0)
        self.assertIn("test2", output)
        self.assertIn("rsync", output)
        self.assertIn("/tmp", output)
        self.assertIn("{}", output)
        result_code, output = self.execute("storage del not-exist")
        self.assertEqual(result_code, 1)
        self.assertIn("Storage not exists", output)
        result_code, output = self.execute("storage del test1")
        self.assertEqual(result_code, 0)
        result_code, output = self.execute("storage list")
        self.assertEqual(result_code, 0)
        self.assertNotIn("test1", output)
        self.assertIn("test2", output)
        self.assertIn("rsync", output)
        self.assertIn("/tmp", output)
        self.assertIn("{}", output)

    def test_file_rsync(self):
        self.reset_test_folder()
        self.execute(f'storage add storage1 rsync {self.path("storage")}')
        self.execute(f'storage add storage2 rsync {self.path("storage")}')
        result_code, output = self.execute("file list")
        self.assertEqual(result_code, 0)
        self.assertIn("No files found.", output)
        result_code, output = self.execute(
            "file add /not-exists --storage=storage1"
        )
        self.assertEqual(result_code, 1)
        result_code, output = self.execute(
            f"file add {self.path_file()} --storage=storage-not-exists"
        )
        self.assertEqual(result_code, 2)
        result_code, output = self.execute(
            f"file add {self.path_file()} --storage=storage1"
        )
        self.assertEqual(result_code, 0)
        result_code, output = self.execute(
            f"file add {self.path_file()} --storage=storage2"
        )
        self.assertEqual(result_code, 0)
        result_code, output = self.execute("file list")
        self.assertEqual(result_code, 0)
        self.assertIn(self.workspace, output)
        self.assertIn("storage1", output)
        self.assertIn("storage2", output)
        self.execute(f'file add {self.path_file()} --exclude="*.txt"')
        _, output = self.execute("file list")
        self.assertIn("*.txt", output)
        self.execute(f"file add {self.path_file()} --del-storage=storage2")
        _, output = self.execute("file list")
        self.assertNotIn("storage2", output)
        self.execute(f'file add {self.path_file()} --del-exclude="*.txt"')
        _, output = self.execute("file list")
        self.assertNotIn("*.txt", output)
        result_code, output = self.execute("file del /not-exists")
        self.assertEqual(result_code, 1)
        result_code, output = self.execute(
            f"file del {self.path_file()} storate-not-exists"
        )
        self.assertEqual(result_code, 2)
        result_code, output = self.execute(
            f"file del {self.path_file()} storage1"
        )
        self.assertEqual(result_code, 0)
        _, output = self.execute("file list")
        self.assertNotIn("storage1", output)
        result_code, _ = self.execute(f"file del {self.path_file()}")
        self.assertEqual(result_code, 0)
        _, output = self.execute("file list")
        self.assertNotIn(self.path_file(), output)

    def test_daemon_background(self):
        try:
            self._test_daemon_background()
        finally:
            self.execute("stop")

    def _test_daemon_background(self):
        self.reset_test_folder()
        self.execute("stop")
        for _ in range(10):
            time.sleep(1)
            result_code, output = self.execute("status")
            if "stopped" in output:
                break
        _, output = self.execute("reload")
        self.assertIn("Daemon is not running", output)
        self.execute("start")
        for _ in range(10):
            time.sleep(1)
            result_code, output = self.execute("status")
            if "running" in output:
                break
        else:
            self.fail("Daemon not started.")
        _, output = self.execute("start")
        self.assertIn("Daemon is already running", output)
        self.assertTrue(os.path.exists(self.config.socket_file))
        daemon = Connector(self.config.socket_file)
        info = daemon.send("info")
        info = json.loads(info)
        self.assertEqual(
            info["config"]["config_file"], self.config.config_file
        )
        self.assertEqual(
            info["config"]["socket_file"], self.config.socket_file
        )
        self.assertEqual(
            os.path.dirname(info["config"]["socket_file"]),
            os.path.dirname(info["config"]["config_file"]),
        )
        self.execute(f'storage add storage1 rsync {self.path("storage")}')
        self.execute(f"file add {self.path_file()} --storage=storage1")
        self.assertEqual(result_code, 0)
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        self.create_file("test.txt")
        self.assertTrue(os.path.exists(self.path_file("test.txt")))
        time.sleep(1)
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        os.remove(self.path_file("test.txt"))
        result_code, output = self.execute("reload")
        self.assertEqual(result_code, 0)
        self.assertIn("Reloaded", output)
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        self.create_file("test.txt")
        self.assertTrue(os.path.exists(self.path_file("test.txt")))
        time.sleep(1)
        self.assertTrue(os.path.exists(self.path_storage("test.txt")))

    def test_daemon_foreground(self):
        try:
            thread = threading.Thread(
                target=watchsyncd_main, args=(self.config.config_file,)
            )
            self._test_daemon_foreground(thread)
        finally:
            self.execute("stop")
            thread.join(timeout=5)
            if thread.is_alive():
                raise RuntimeError("Daemon thread did not terminate in time")

    def _test_daemon_foreground(self, thread):
        self.reset_test_folder()
        daemon = Connector("")
        self.assertFalse(daemon.is_alive())
        daemon = Connector(self.config.socket_file)
        with open(self.config.socket_file, "w") as file:
            file.write("test")
        thread.start()
        for _ in range(10):
            time.sleep(1)
            result_code, output = self.execute("status")
            if "running" in output:
                break
        else:
            self.fail("Daemon not started.")
        with self.assertRaises(RuntimeError):
            watchsyncd_main(self.config.config_file)
        _, output = self.execute("start")
        self.assertIn("Daemon is already running", output)
        self.assertTrue(os.path.exists(self.config.socket_file))
        info = daemon.send("info")
        info = json.loads(info)
        self.assertEqual(
            info["config"]["config_file"], self.config.config_file
        )
        self.assertEqual(
            info["config"]["socket_file"], self.config.socket_file
        )
        self.assertEqual(
            os.path.dirname(info["config"]["socket_file"]),
            os.path.dirname(info["config"]["config_file"]),
        )
        response = daemon.send("not-exists")
        self.assertIn("Unknown command", response)
        self.execute(f'storage add storage1 rsync {self.path("storage")}')
        self.execute(f"file add {self.path_file()} --storage=storage1")
        self.assertEqual(result_code, 0)
        self.assertIn("storage1", self.config.storages)
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        self.create_file("test.txt")
        self.assertTrue(os.path.exists(self.path_file("test.txt")))
        time.sleep(1)
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        os.remove(self.path_file("test.txt"))
        result_code, output = self.execute("reload")
        self.assertEqual(result_code, 0)
        self.assertIn("storage1", self.config.storages)
        self.assertIn("Reloaded", output)
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        self.create_file("test.txt")
        self.assertTrue(os.path.exists(self.path_file("test.txt")))
        time.sleep(1)
        self.assertTrue(os.path.exists(self.path_storage("test.txt")))
        with self.assertLogs(APP_NAME, level="ERROR") as cm:
            self.config.storages["storage1"]["type"] = "not-exist"
            self.config.write()
            response = daemon.send("reload")
            self.assertIn("Reloaded", response)
            self.create_file("test2.txt")
            time.sleep(1)
        self.assertIn("Unknown storage type", cm.output[0])
        self.execute("stop")
        for _ in range(10):
            time.sleep(1)
            result_code, output = self.execute("status")
            if "stopped" in output:
                break
        _, output = self.execute("reload")
        self.assertIn("Daemon is not running", output)

    def test_sync(self):
        self.reset_test_folder()
        self.execute(f'storage add storage1 rsync {self.path("storage")}')
        self.execute(f"file add {self.path_file()} --storage=storage1")
        self.config.read()
        self.assertIn("storage1", self.config.storages)
        self.assertIn(
            "storage1", self.config.files[self.path_file()]["storages"]
        )
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        self.create_file("test.txt")
        self.assertFalse(os.path.exists(self.path_storage("test.txt")))
        result_code, _ = self.execute("file sync")
        self.assertEqual(result_code, 0)
        self.assertTrue(os.path.exists(self.path_storage("test.txt")))
        self.create_file("test2.txt")
        self.assertFalse(os.path.exists(self.path_storage("test2.txt")))
        result_code, _ = self.execute(f"file sync {self.path_file()}")
        self.assertEqual(result_code, 0)
        self.assertTrue(os.path.exists(self.path_storage("test2.txt")))
        result_code, _ = self.execute("file sync not-exists")
        self.assertEqual(result_code, 1)
        self.execute(
            f"file add {self.path_file()} --storage=storage1 --exclude *.not"
        )
        self.create_file("test.not")
        self.assertFalse(os.path.exists(self.path_storage("test.not")))
        result_code, _ = self.execute(f"file sync {self.path_file()}")
        self.assertEqual(result_code, 0)
        self.assertFalse(os.path.exists(self.path_storage("test.not")))
