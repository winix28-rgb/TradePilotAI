from tradepilotai_os.sidebar import Sidebar
from tradepilotai_os.navigation import NavigationService


class StubPage:
    def render(self) -> str:
        return "Stub page"


def test_sidebar_renders_sections_and_items():
    navigation = NavigationService()
    navigation.register("dashboard", StubPage())
    navigation.register("live_trading", StubPage())
    navigation.register("scanner", StubPage())
    navigation.register("backtesting", StubPage())
    navigation.register("portfolio", StubPage())

    sidebar = Sidebar(navigation_service=navigation)
    rendered = sidebar.render()

    assert "Dashboard" in rendered
    assert "Live Trading" in rendered
    assert "Scanner" in rendered
    assert "Backtesting" in rendered
    assert "Portfolio" in rendered


def test_sidebar_highlights_active_page():
    navigation = NavigationService()
    navigation.register("dashboard", StubPage())
    navigation.register("scanner", StubPage())

    sidebar = Sidebar(navigation_service=navigation, active_route="scanner")
    rendered = sidebar.render()

    assert "Scanner[active]" in rendered
