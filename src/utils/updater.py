import requests
import flet as ft
import webbrowser

from utils.logger_config import log_exception


class Updater:
    def __init__(self, repo: str, current_version: str):
        """
        :param repo: "owner/repo" (например "myorg/geooffice")
        :param current_version: текущая версия программы (строка)
        """
        self.repo = repo
        self.current_version = current_version

    @log_exception
    def check_update(self):
        """Проверка обновлений через GitHub API"""
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        response = requests.get(url, timeout=5)
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        assets = data.get("assets", [])
        download_url = assets[0]["browser_download_url"] if assets else None

        if latest_version != self.current_version:
            return {
                "update_available": True,
                "latest_version": latest_version,
                "download_url": download_url,
            }
        return {"update_available": False}

    @log_exception
    def show_update_dialog(self, page: ft.Page):
        """Показ диалога в Flet при наличии новой версии"""
        info = self.check_update()

        if not info.get("update_available"):
            return  # обновлений нет

        def download(e):
            if info["download_url"]:
                webbrowser.open(info["download_url"])
            close_dialog(e)

        def close_dialog(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Доступна новая версия {info['latest_version']}"),
            content=ft.Text("Хотите скачать обновление?"),
            actions=[
                ft.TextButton("Да", on_click=download),
                ft.TextButton("Позже", on_click=close_dialog),
            ],
        )
        page.open(dlg)
        page.update()
