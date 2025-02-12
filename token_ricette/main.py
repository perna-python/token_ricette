import flet as ft
import pyperclip
from ricercaToken import token_emergenze, token_ricetta_bianca_elettronica, richiesta_token_emergenza
import time

class Emergenza(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.token, self.valido = token_emergenze()
    
        # 1
        richiediTokenButton = ft.ElevatedButton(text="RICHIEDI NUOVO TOKEN", on_click=self.richiediToken)
        # 2
        self.tokenText = ft.Text(value=self.testo())
        # 3
        self.copiaButton = ft.IconButton(icon=ft.Icons.COPY, on_click=self.copia)
        # 4
        aggiornaButton = ft.IconButton(icon=ft.Icons.UPDATE, on_click=self.aggiorna)

        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        self.controls=[
            ft.Row(
                alignment = ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("TOKEN EMERGENZA"),
                    aggiornaButton,
                ]
            ),
            ft.Row(
                alignment = ft.MainAxisAlignment.CENTER,
                controls=[
                    richiediTokenButton,
                ]
            ),
            ft.Row(
                alignment = ft.MainAxisAlignment.CENTER,
                controls=[
                    self.tokenText,
                    self.copiaButton
                ]
            )
        ]
        

    # 1
    def richiediToken(self, e):
        richiesta_token_emergenza()
        time.sleep(3)
        self.token, self.valido = token_emergenze()
        if self.valido:
            self.tokenText.value = self.token
        
        self.update()
        self.snackBar("Richiesta token Emergenza effettuata")
    
    # 2
    def testo(self):
        if self.valido:
            return self.token
        else:
            return "Richiedi Token"
    
    # 3
    def copia(self, e):
        pyperclip.copy(self.tokenText.value)
        self.snackBar("Token Emergenza copiato negli appunti")
    
    # 4
    def aggiorna(self, e):
        self.token, self.valido = token_emergenze()
        if self.valido:
            self.tokenText.value = self.token
        else:
            self.tokenText.value = "Richiedi Token"
        
        self.update()
        self.snackBar("Ricerca token Emergenza eseguito")

    # altro
    def snackBar(self, text, bgcolor="green"):
        snack = ft.SnackBar(ft.Text(text), bgcolor=bgcolor)
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()


class RicettaBianca(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.token, self.valido = token_ricetta_bianca_elettronica()
        # 1
        self.tokenText = ft.Text(value=self.testo())
        # 2
        self.copiaButton = ft.IconButton(icon=ft.Icons.COPY, on_click=self.copia)
        # 3
        aggiornaButton = ft.IconButton(icon=ft.Icons.UPDATE, on_click=self.aggiorna)

        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        self.controls = [
            ft.Row(
                alignment = ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("TOKEN RICETTA BIANCA"),
                    aggiornaButton
                ]
            ),
            ft.Row(
                alignment = ft.MainAxisAlignment.CENTER,
                controls=[
                    self.tokenText,
                    self.copiaButton
                ]
            ),
        ]
    
    # 1
    def testo(self):
        if self.valido:
            return self.token
        else:
            return "Richiedere token su Wingesfar"
    
    # 2
    def copia(self, e):
        pyperclip.copy(self.tokenText.value)
        self.snackBar("Token Ricetta Bianca copiato negli appunti")
    
    # 3
    def aggiorna(self, e):
        self.token, self.valido = token_ricetta_bianca_elettronica()
        if self.valido:
            self.tokenText.value = self.token
        else:
            self.tokenText.value = "Richiedere token su Wingesfar"
        
        self.update()
        self.snackBar("Ricerca token Ricetta Bianca eseguito")

    # altro
    def snackBar(self, text, bgcolor="green"):
        snack = ft.SnackBar(ft.Text(text), bgcolor=bgcolor)
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()


def main(page:ft.Page):
    page.title = "TOKEN FARMACIA BARBACOVI"
    page.window.resizable = False
    page.window.height = 380
    page.window.width = 400
    page.update()
    
    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    width=400,
                    height=100,
                    padding=10,
                    content=RicettaBianca(page=page)
                ),
                ft.Divider(),
                ft.Container(
                    width=400,
                    height=140,
                    padding=10,
                    content=Emergenza(page=page)
                )
            ]
        )
    )

if __name__ == "__main__":
    ft.app(target=main)