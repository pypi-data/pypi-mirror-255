import time
from pathlib import Path

from rich import print
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from corpus_content.utils import update_content

DECISIONS_DIR = Path().home().joinpath("code/corpus-decisions")


class Watcher:
    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except Exception:
            self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):
    file_cache: dict = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        # ensure existence
        p = Path(event.src_path)
        if not p.exists():
            print(f"{p.name=} missing, may have been renamed")
            return

        if not event.src_path.endswith(".md"):
            return

        for ignoreable in ("README.md", "HEADINGS.md", "NOTES.md"):
            if event.src_path.endswith(ignoreable):
                print(f"Ignoring {ignoreable=}")
                return

        # Deal with caching issues
        seconds = int(time.time())
        key = (seconds, event.src_path)
        if key in self.file_cache:
            return
        self.file_cache[key] = True

        # Update file based on new content
        print(f"\nUpdating: {p.name=}")
        to_check = update_content(file=p)
        for text in to_check:
            print(f"\nCheck {text=}\n")
        if not to_check:
            print(f"Cleared: {p.name=}\n\n")

    def on_any_event(self, event):
        print(event)  # Your code here


if __name__ == "__main__":
    w = Watcher(str(DECISIONS_DIR), MyHandler())
    w.run()
