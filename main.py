import flet as ft
from datetime import date, timedelta
from zman import get_weekend_dates, compute_zmanim, generate_excel


def main(page: ft.Page) -> None:
    page.title = "Zmanim Generator"
    page.window.width = 420
    page.window.height = 380

    # Mutable state held in a dict to avoid closure rebinding issues
    state: dict[str, date | None] = {"start": None, "end": None, "picking": "start"}

    range_label = ft.Text("No range selected", size=14)
    generate_btn = ft.Button(content=ft.Text("Generate Excel"), disabled=True)

    def refresh_ui() -> None:
        s, en = state["start"], state["end"]
        if s and en:
            range_label.value = f"{s.strftime('%Y-%m-%d')}  →  {en.strftime('%Y-%m-%d')}"
            generate_btn.disabled = False
        elif s:
            range_label.value = f"Start: {s.strftime('%Y-%m-%d')} — pick end date"
        else:
            range_label.value = "No range selected"
            generate_btn.disabled = True
        page.update()

    start_date_text = ft.Text(value="Start Date: None", size=14)
    end_date_text = ft.Text(value="End Date: None", size=14)
    date_range_picker = ft.DateRangePicker(
        current_date=date.today(),
        first_date=date.today() - timedelta(days=365 * 5),
        last_date=date.today() + timedelta(days=365 * 5),
        start_value=date.today(),
        end_value=date.today() + timedelta(days=7),
        modal=True,
    )

    def on_date_change(e: ft.ControlEvent) -> None:
        if not e.control.start_value or not e.control.end_value:
            return
        state["start"] = e.control.start_value
        state["end"] = e.control.end_value
        start_date_text.value = f"Start Date: {e.control.start_value.strftime('%Y-%m-%d')}"
        end_date_text.value = f"End Date: {e.control.end_value.strftime('%Y-%m-%d')}"
        refresh_ui()

    date_range_picker.on_change = on_date_change
    page.overlay.append(date_range_picker)

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    snack_bar = ft.SnackBar(content=ft.Text(""))
    page.overlay.append(snack_bar)

    def show_snack(msg: str) -> None:
        snack_bar.content = ft.Text(msg)
        snack_bar.open = True
        page.update()

    def on_pick_range(_e: ft.ControlEvent) -> None:
        date_range_picker.open = True
        page.update()

    async def on_generate(_e: ft.ControlEvent) -> None:
        s, en = state["start"], state["end"]
        if s is None or en is None:
            return
        dates = get_weekend_dates(s, en)
        if not dates:
            show_snack("No Fri/Sat/Sun in selected range.")
            return
        default_name = f"zmanim_{s.strftime('%Y%m%d')}_{en.strftime('%Y%m%d')}.xlsx"
        path = await file_picker.save_file(
            dialog_title="Save Zmanim Excel",
            file_name=default_name,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
        if not path:
            return
        rows = [compute_zmanim(d) for d in dates]
        generate_excel(rows, path)
        show_snack(f"Saved to {path}")

    generate_btn.on_click = on_generate

    page.add(
        ft.SafeArea(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Zmanim Generator — Savannah, GA",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Divider(),
                    ft.Row(controls=[start_date_text, end_date_text], spacing=16),
                    ft.Row(
                        controls=[ft.Button(content=ft.Text("Pick Date Range"),
                        on_click=on_pick_range)]
                    ),
                    ft.Divider(),
                    ft.Row(controls=[generate_btn], spacing=16),
                ],
                spacing=16,
            ),
            padding=20,
        )
        )
    )


if __name__ == "__main__":
    ft.run(main)