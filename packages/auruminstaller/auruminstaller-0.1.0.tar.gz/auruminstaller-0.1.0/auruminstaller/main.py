from time import sleep
import flet as ft

import csv
import pathlib

import os
import re
from glob import glob

import gettext

def main(page: ft.Page):
    page.title = "Aurum Installer"
    page.window_full_screen = True
    page.theme_mode = ft.ThemeMode.DARK
    page.window_bgcolor = ft.colors.BLACK
    page.bgcolor = ft.colors.BLACK

    # Theme
    theme = ft.Theme()
    theme.page_transitions.android = ft.PageTransitionTheme.OPEN_UPWARDS
    theme.page_transitions.ios = ft.PageTransitionTheme.OPEN_UPWARDS
    theme.page_transitions.macos = ft.PageTransitionTheme.OPEN_UPWARDS
    theme.page_transitions.linux = ft.PageTransitionTheme.OPEN_UPWARDS
    theme.page_transitions.windows = ft.PageTransitionTheme.OPEN_UPWARDS
    page.theme = theme
    page.update()

    # Translate

    ft_eng_lang = gettext.translation('installer', localedir = './locales', languages=['en'])
    ft_ukr_lang = gettext.translation('installer', localedir = './locales', languages=['ua'])

    ft_eng_lang.install()

    def select_language(lang):
        if lang == "en":
            ft_eng_lang.install()
        elif lang == "ua":
            ft_ukr_lang.install()

    # Vars
    path = pathlib.Path("/etc/os-release")
    with open(path) as stream:
        reader = csv.reader(stream, delimiter="=")
        os_release = dict(reader)

    # Handlers
    def handle_menu_about_click(e):
        page.dialog = dlg_about
        dlg_about.open = True
        page.update()

    def close_about_dlg(e):
        dlg_about.open = False
        page.update()

    # Elements
    dlg_about = ft.CupertinoAlertDialog(
        modal=True,
        title=ft.Text(_("About")),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Image(
                        src=f"/usr/share/pixmaps/{os_release['LOGO']}.png",
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Text(f"{os_release['NAME']} Installer", weight=ft.FontWeight.BOLD),
                    ft.Text(f"OS: {os_release['NAME']}"),
                    ft.Text(f"BUILD ID: {os_release['BUILD_ID']}"),
                    ft.CupertinoDialogAction(_("HOME PAGE"), on_click=lambda _: os.system(f"/usr/bin/epiphany {os_release['HOME_URL']}")),
                    ft.CupertinoDialogAction(_("DOCUMENTATION"), on_click=lambda _: os.system(f"/usr/bin/epiphany {os_release['DOCUMENTATION_URL']}")),
                    ft.CupertinoDialogAction(_("SUPPORT"), on_click=lambda _: os.system(f"/usr/bin/epiphany {os_release['SUPPORT_URL']}")),
                    ft.CupertinoDialogAction(_("REPORT BUG"), on_click=lambda _: os.system(f"/usr/bin/epiphany {os_release['BUG_REPORT_URL']}")),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ),
        actions=[
            ft.CupertinoDialogAction("Close", on_click=close_about_dlg, is_default_action=True, is_destructive_action=True),
        ],
    )

    def language_changed(e):
        select_language(languages_radio.value)
        page.update()

    languages_radio = ft.Dropdown(
        options=[
            ft.dropdown.Option(text="English", key="en"),
            ft.dropdown.Option(text="Українська", key="ua")
        ],
        value="en",
        width=400,
        border_color=ft.colors.BLACK,
        icon=None,
        on_change=language_changed
    )

    # Route
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Image(
                        src=f"/usr/share/pixmaps/{os_release['LOGO']}.png",
                        width=300,
                        height=300,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Text(f"Welcome to {os_release['NAME']} Installer", size=50, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        languages_radio,
                        ft.TextButton("Begin", on_click=lambda _: page.go("/language")),
                    ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    # languages_radio,
                    # ft.CupertinoDialogAction("Begin", on_click=lambda _: page.go("/language")),
                ],
                appbar = ft.AppBar( 
                    leading=ft.IconButton(
                                icon=ft.icons.INFO,
                                on_click=handle_menu_about_click
                            ),
                ),
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        if page.route == "/language":
            page.views.append(
                ft.View(
                    "/language",
                    [
                        ft.Text(_("Select Language"), size=50, weight=ft.FontWeight.BOLD),
                        
                    ],
                    appbar = ft.AppBar(
                        title=ft.Text(_("Select Language")),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        leading=ft.IconButton(ft.icons.ARROW_BACK, 
                            on_click=lambda _: page.go("/")
                        )
                    )
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

def run_app():
    ft.app(target=main)