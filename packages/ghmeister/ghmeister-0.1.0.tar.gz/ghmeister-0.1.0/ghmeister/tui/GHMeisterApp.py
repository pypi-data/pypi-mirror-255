from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.worker import get_current_worker

from ghmeister.services.GitHubService import get_github


class RepoMeisterApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.list_view = ListView()

    def compose(self) -> ComposeResult:
        yield Header()

        yield self.list_view
        yield Footer()

    def on_mount(self) -> None:
        self.list_view.loading = True
        self.load_repos()

    @work(exclusive=True, thread=True)
    def load_repos(self):
        worker = get_current_worker()
        list_items = []
        for r in get_github().get_user().get_repos(affiliation='owner'):
            list_items.append(ListItem(Label(r.full_name), name=r.full_name))
        if not worker.is_cancelled:
            self.call_from_thread(self.list_view.extend, list_items)
        self.list_view.loading = False

    def action_quit(self) -> None:
        self.exit()
