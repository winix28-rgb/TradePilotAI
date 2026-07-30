from tradepilotai_os.navigation import NavigationService


def test_navigation_service_registers_and_resolves_routes():
    service = NavigationService()
    service.register("dashboard", "Dashboard")
    service.register("portfolio", "Portfolio")

    assert service.navigate("dashboard") == "Dashboard"
    assert service.navigate("portfolio") == "Portfolio"


def test_navigation_service_generates_breadcrumbs():
    service = NavigationService()
    service.register("dashboard", "Dashboard")
    service.register("portfolio", "Portfolio")
    service.register("position_detail", "Position Detail")

    breadcrumbs = service.breadcrumbs("position_detail", parent="portfolio")

    assert breadcrumbs[0] == "Dashboard"
    assert breadcrumbs[-1] == "Position Detail"


def test_navigation_service_supports_dashboard_drilldown():
    service = NavigationService()
    service.register("dashboard", "Dashboard")
    service.register("portfolio", "Portfolio")
    service.register("risk", "Risk")

    target = service.resolve_dashboard_target("risk")

    assert target == "risk"


def test_navigation_service_resolves_position_detail():
    service = NavigationService()
    service.register("position_detail", "Position Detail")

    assert service.navigate("position_detail") == "Position Detail"
