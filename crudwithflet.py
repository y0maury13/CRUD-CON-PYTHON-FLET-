import flet as ft
from flet import Page, TextField, Text, DataTable, DataColumn, DataRow, DataCell, ElevatedButton, Column, Row, SnackBar
import sqlite3

def init_db():
    with sqlite3.connect("students.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT,
                universidad TEXT,
                edad INTEGER,
                carrera TEXT
            )
        ''')

def fetch_all():
    with sqlite3.connect("students.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        return cursor.fetchall()

def main(page: Page):
    page.scroll = "always"
    
    init_db()
    
    nombre_completo_field = TextField(label="Nombre Completo")
    universidad_field = TextField(label="Universidad")
    edad_field = TextField(label="Edad", keyboard_type=ft.KeyboardType.NUMBER)
    carrera_field = TextField(label="Carrera")
    
    youid = Text(visible=False)
    
    mytable = DataTable(
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("Nombre Completo")),
            DataColumn(Text("Universidad")),
            DataColumn(Text("Edad")),
            DataColumn(Text("Carrera")),
        ],
        rows=[]
    )

    def load_data():
        mytable.rows.clear()
        for row in fetch_all():
            mytable.rows.append(
                DataRow(
                    cells=[DataCell(Text(str(cell))) for cell in row],
                    on_select_changed=lambda e, row=row: editindex(e, row)
                )
            )
        page.update()

    def editindex(e, row):
        youid.value = str(row[0])
        nombre_completo_field.value = row[1]
        universidad_field.value = row[2]
        edad_field.value = str(row[3])
        carrera_field.value = row[4]
        
        addButton.visible = False
        deleteButton.visible = True
        editbutton.visible = True
        page.update()

    def addnewdata(e):
        new_nombre_completo = nombre_completo_field.value
        new_universidad = universidad_field.value
        new_edad = int(edad_field.value) if edad_field.value.isdigit() else 0
        new_carrera = carrera_field.value

        with sqlite3.connect("students.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (nombre_completo, universidad, edad, carrera) VALUES (?, ?, ?, ?)",
                           (new_nombre_completo, new_universidad, new_edad, new_carrera))
            new_id = cursor.lastrowid

        load_data()
        clear_fields()
        show_snackbar(f"Record added successfully with ID: {new_id}", "green")

    def editandsave(e):
        if youid.value:
            with sqlite3.connect("students.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET nombre_completo = ?, universidad = ?, edad = ?, carrera = ? WHERE ID = ?",
                               (nombre_completo_field.value, universidad_field.value, int(edad_field.value or 0), carrera_field.value, youid.value))

            load_data()
            clear_fields()
            addButton.visible = True
            deleteButton.visible = False
            editbutton.visible = False
            page.update()
            show_snackbar(f"Record with ID {youid.value} updated successfully", "orange")

    def removeindex(e):
        if youid.value:
            with sqlite3.connect("students.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE ID = ?", (youid.value,))

            load_data()
            clear_fields()
            addButton.visible = True
            deleteButton.visible = False
            editbutton.visible = False
            show_snackbar(f"Successfully deleted record ID = {youid.value}", "red")

    def clear_fields():
        for field in [nombre_completo_field, universidad_field, edad_field, carrera_field, youid]:
            field.value = ""

    def show_snackbar(message, color):
        page.snack_bar = SnackBar(
            content=Text(message, color="white"),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    addButton = ElevatedButton("Add New", bgcolor="blue", color="white", on_click=addnewdata)
    deleteButton = ElevatedButton("Delete", bgcolor="red", color="white", on_click=removeindex, visible=False)
    editbutton = ElevatedButton("Update", bgcolor="orange", color="white", on_click=editandsave, visible=False)
    
    page.add(
        Column([
            Text("CRUD Application", size=30, weight="bold"),
            nombre_completo_field,
            universidad_field,
            edad_field,
            carrera_field,
            Row([addButton, editbutton, deleteButton]),
            mytable
        ])
    )

    load_data()

ft.app(target=main)