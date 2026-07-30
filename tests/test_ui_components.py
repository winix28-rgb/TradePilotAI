from tradepilotai_os.ui_library import (
    Breadcrumb,
    Card,
    ChartCard,
    DataTable,
    KPIChartCard,
    NotificationPanel,
    SectionHeader,
    StatusBadge,
    Toolbar,
)


def test_component_library_renders_expected_output():
    card = Card(title="Test")
    assert "Test" in card.render()

    badge = StatusBadge(label="Live", status="success")
    assert "Live" in badge.render()

    breadcrumb = Breadcrumb(items=["Home", "Portfolio"])
    assert "Home" in breadcrumb.render()

    toolbar = Toolbar(title="Actions")
    assert "Actions" in toolbar.render()

    table = DataTable(headers=["Symbol"], rows=[["AAPL"]])
    assert "Symbol" in table.render()

    notification = NotificationPanel(items=["New signal"])
    assert "New signal" in notification.render()

    section = SectionHeader(title="Summary")
    assert "Summary" in section.render()

    chart = ChartCard(title="Growth")
    assert "Growth" in chart.render()

    kpi = KPIChartCard(title="Equity", value="100")
    assert "Equity" in kpi.render()
