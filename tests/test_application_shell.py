from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService


class StubPage:
    def render(self) -> str:
        return "Dashboard Content"


def test_application_shell_renders_layout_sections():
    navigation = NavigationService()
    navigation.register("dashboard", StubPage())

    shell = ApplicationShell(navigation_service=navigation)
    rendered = shell.render()

    assert "Header" in rendered
    assert "Sidebar" in rendered
    assert "Main Content" in rendered
    assert "Status Bar" in rendered


def test_application_shell_renders_current_page_content():
    navigation = NavigationService()
    navigation.register("dashboard", StubPage())

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("dashboard")
    rendered = shell.render()

    assert "Dashboard Content" in rendered
