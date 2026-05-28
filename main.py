import flet as ft
from datetime import date, timedelta
from zman import get_weekend_dates, compute_zmanim, generate_excel, compute_dataframe


def main(page: ft.Page) -> None:
    page.title = 'Zmanim Generator'
    page.window.width = 520
    page.window.height = 620

    state: dict[str, date | None] = {'start': None, 'end': None}

    generate_btn = ft.Button(content=ft.Text('Generate Excel'), disabled=True)
    clear_btn = ft.Button(content=ft.Text('Clear'), disabled=True)

    date_range_picker = ft.DateRangePicker(
        current_date=date.today(),
        first_date=date.today() - timedelta(days=365 * 5),
        last_date=date.today() + timedelta(days=365 * 5),
        start_value=date.today(),
        end_value=date.today() + timedelta(days=7),
        confirm_text='Accept',
    )

    def on_pick_range(_e: ft.ControlEvent) -> None:
        if not date_range_picker.open:
            page.show_dialog(date_range_picker)

    date_range_field = ft.TextField(
        label='Date Range',
        hint_text='Click to pick a date range',
        read_only=True,
        on_focus=on_pick_range,
        expand=True,
    )

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text('Date')),
            ft.DataColumn(ft.Text('Zman')),
            ft.DataColumn(ft.Text('Time')),
        ],
        rows=[],
        column_spacing=16,
    )

    def on_date_change(e: ft.ControlEvent) -> None:
        if not e.control.start_value or not e.control.end_value:
            return
        state['start'] = e.control.start_value
        state['end'] = e.control.end_value
        s, en = state['start'], state['end']
        date_range_field.value = f"{s.strftime('%Y-%m-%d')}  →  {en.strftime('%Y-%m-%d')}"
        generate_btn.disabled = False
        clear_btn.disabled = False
        dates = get_weekend_dates(s, en)
        rows = [compute_zmanim(d) for d in dates]
        df = compute_dataframe(rows)
        seen: set[str] = set()
        rows_out: list[ft.DataRow] = []
        for _, row in df.iterrows():
            date_label = row['Date'] if row['Date'] not in seen else ''
            seen.add(row['Date'])
            rows_out.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(date_label)),
                ft.DataCell(ft.Text(row['Zman'])),
                ft.DataCell(ft.Text(row['Time'])),
            ]))
        data_table.rows = rows_out
        page.update()

    date_range_picker.on_change = on_date_change

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    snack_bar = ft.SnackBar(content=ft.Text(''))
    page.overlay.append(snack_bar)

    def show_snack(msg: str) -> None:
        snack_bar.content = ft.Text(msg)
        snack_bar.open = True
        page.update()

    async def on_generate(_e: ft.ControlEvent) -> None:
        s, en = state['start'], state['end']
        if s is None or en is None:
            return
        dates = get_weekend_dates(s, en)
        if not dates:
            show_snack('No Fri/Sat/Sun in selected range.')
            return
        default_name = f"zmanim_{s.strftime('%Y%m%d')}_{en.strftime('%Y%m%d')}.xlsx"
        path = await file_picker.save_file(
            dialog_title='Save Zmanim Excel',
            file_name=default_name,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['xlsx'],
        )
        if not path:
            return
        rows = [compute_zmanim(d) for d in dates]
        generate_excel(rows, path)
        show_snack(f'Saved to {path}')

    def on_clear(_e: ft.ControlEvent) -> None:
        state['start'] = None
        state['end'] = None
        date_range_field.value = ''
        date_range_picker.start_value = date.today()
        date_range_picker.end_value = date.today() + timedelta(days=7)
        data_table.rows = []
        generate_btn.disabled = True
        clear_btn.disabled = True
        page.update()

    generate_btn.on_click = lambda e: page.run_task(on_generate, e)
    clear_btn.on_click = on_clear

    page.add(
        ft.SafeArea(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            'Zmanim Generator — Savannah, GA',
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        ft.Row(controls=[date_range_field]),
                        ft.Divider(),
                        ft.Row(controls=[generate_btn, clear_btn], spacing=16),
                        ft.Container(
                            content=ft.ListView(
                                controls=[data_table],
                                expand=True,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=16,
                    expand=True,
                ),
                padding=20,
                expand=True,
            ),
            expand=True,
        )
    )


def run() -> None:
    ft.run(main)


if __name__ == '__main__':
    run()
