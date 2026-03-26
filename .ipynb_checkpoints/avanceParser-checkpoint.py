#!/bin/python3

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re

tokens_parser = []
error_lexico = False

#keywords
reserved = {
    "SELECT": 10, 
    "FROM": 11, 
    "WHERE": 12, 
    "IN": 13,
    "AND": 14, 
    "OR": 15, 
    "CREATE": 16, 
    "TABLE": 17,
    "CHAR": 18, 
    "NUMERIC": 19, 
    "NOT": 20, 
    "NULL": 21,
    "CONSTRAINT": 22, 
    "KEY": 23, 
    "PRIMARY": 24,
    "FOREIGN": 25, 
    "REFERENCES": 26,
    "INSERT": 27, 
    "INTO": 28, 
    "VALUES": 29
}
# operadores relacionales
relacionales = {
    ">=": 84,
    "<=": 85,
    ">": 81,
    "<": 82,
    "=": 83
}

# operadores aritmeticos
operators = {
    "+": 70,
    "-": 71,
    "*": 72,
    "/": 73
}

# delimitadores
delimiters = {
    ",": 50,
    ".": 51,
    "(": 52,
    ")": 53
}

#lexer dml

def analizar():

    global error_lexico
    error_lexico = False

    limpiar_tablas()
    tokens_parser.clear()

    entrada = texto_sql.get("1.0", tk.END)

    id_counter = 401
    const_counter = 600
    token_number = 1

    tabla_identificadores = {}
    tabla_constantes = {}

    lineas = entrada.split("\n")

    for num_linea, linea in enumerate(lineas, start=1):

        tokens = re.findall(
            r">=|<=|>|<|=|\+|-|\*|/|,|\(|\)|'[^']*'|[A-Za-z_][A-Za-z0-9_#]*|\d+|.",
            linea
        )

        for token in tokens:

            if token.strip() == "":
                continue

            tipo = None
            codigo = None

            if token.upper() in reserved:
                tipo = 1
                codigo = reserved[token.upper()]

            elif token in relacionales:
                tipo = 8
                codigo = relacionales[token]

            elif token in operators:
                tipo = 7
                codigo = operators[token]

            elif token in delimiters:
                tipo = 5
                codigo = delimiters[token]

            elif re.match(r"'[^']*'$", token):
                tipo = 6
                valor = token.strip("'")

                if valor not in tabla_constantes:
                    tabla_constantes[valor] = (62, const_counter)
                    codigo = const_counter
                    const_counter += 1
                else:
                    codigo = tabla_constantes[valor][1]

            elif token.isdigit():
                tipo = 6
                if token not in tabla_constantes:
                    tabla_constantes[token] = (61, const_counter)
                    codigo = const_counter
                    const_counter += 1
                else:
                    codigo = tabla_constantes[token][1]

            elif re.match(r"[A-Za-z_][A-Za-z0-9_#]*$", token):
                tipo = 4
                if token not in tabla_identificadores:
                    tabla_identificadores[token] = (id_counter, [num_linea])
                    codigo = id_counter
                    id_counter += 1
                else:
                    codigo = tabla_identificadores[token][0]
                    tabla_identificadores[token][1].append(num_linea)

            else:
                tipo = "ERROR"
                codigo = "No reconocido"
                error_lexico = True

                messagebox.showerror(
                    "Error Léxico",
                    f"Error 1:101 Línea {num_linea}. Símbolo desconocido '{token}'"
                )

            tree_tokens.insert(
                "", "end",
                values=(token_number, num_linea, token, tipo, codigo)
            )

            tokens_parser.append((token, tipo, codigo, num_linea))

            token_number += 1

    for ident, datos in tabla_identificadores.items():
        tree_ident.insert(
            "", "end",
            values=(ident, datos[0], ",".join(map(str, datos[1])))
        )

    for const, datos in tabla_constantes.items():
        tree_const.insert(
            "", "end",
            values=(const, datos[0], datos[1])
        )

# parser DML

def parser():

    global error_lexico

    if error_lexico:
        messagebox.showerror(
            "Parser",
            "No se puede ejecutar el parser porque hay errores léxicos."
        )
        return

    if not tokens_parser:
        messagebox.showwarning("Parser", "Primero ejecuta el análisis léxico")
        return

    i = 0
    n = len(tokens_parser)

    def actual():
        if i < n:
            return tokens_parser[i]

    def consumir():
        nonlocal i
        i += 1

    def error(codigo, mensaje):
        linea = tokens_parser[i][3] if i < n else tokens_parser[-1][3]
        messagebox.showerror(
            "Error Sintáctico",
            f"Error 2:{codigo} Línea {linea}. {mensaje}"
        )
        return False

    def identificador():
        nonlocal i

        if actual() is None or actual()[1] != 4:
            return False

        consumir()

        if actual() and actual()[0] == ".":
            consumir()

            if actual() and actual()[1] == 4:
                consumir()
            else:
                return False

        return True

    # regla SELECT
    if actual() is None or actual()[0].upper() != "SELECT":
        return error(201, "Se esperaba SELECT")

    consumir()

    # columnas
    if actual() and actual()[0] == "*":
        consumir()
    else:
        if not identificador():
            return error(204, "Se esperaba Identificador")

        while actual() and actual()[0] == ",":
            consumir()
            if not identificador():
                return error(204, "Se esperaba Identificador")

    # regla FROM
    if actual() is None or actual()[0].upper() != "FROM":
        return error(201, "Se esperaba FROM")

    consumir()

    if not identificador():
        return error(204, "Se esperaba Identificador")

    while actual() and actual()[0] == ",":
        consumir()
        if not identificador():
            return error(204, "Se esperaba Identificador")

    # regla WHERE
    if actual() and actual()[0].upper() == "WHERE":

        consumir()

        if not identificador():
            return error(204, "Se esperaba Identificador") # A

        #if actual() and actual()[1] == 4:
        #    return error(210, "Falta '.' o identificadores consecutivos inválidos")

        if actual() is None or actual()[0] not in relacionales:
            return error(208, "Se esperaba Operador Relacional") # =

        consumir()

        if not identificador() and (actual() is None or actual()[1] != 6): # A o 1
            return error(206, "Se esperaba Constante o Identificador")
        
        consumir()        
        while True:
            if not actual():
                break
            if actual() is None or not actual()[0].upper() in ("AND", "OR"):
                return error(201, "Se esperaba una palabra reservada")
            consumir()
 
            if not identificador():
                return error(204, "Se esperaba un identificador") # =
            
            if actual() is None or actual()[0] not in relacionales:
                return error(208, "Se esperaba Operador Relacional")
            consumir()
            if actual() is None or not identificador() and actual()[1] != 6:
                return error(206, "Se esperaba Constante o Identificador")
            consumir()            
#select * from a
#where a=1 and b=2 and c=3
        
    messagebox.showinfo("Resultado", "Consulta libre de errores")

#LIMPIAR LAS TABLAS

def limpiar_tablas():
    for item in tree_tokens.get_children():
        tree_tokens.delete(item)
    for item in tree_ident.get_children():
        tree_ident.delete(item)
    for item in tree_const.get_children():
        tree_const.delete(item)

#INTERFAZ GRAFICA
ventana = tk.Tk()
ventana.title("ESCÁNER + PARSER DML SQL")
ventana.geometry("1200x700")

texto_sql = tk.Text(ventana, height=6, font=("Consolas", 12))
texto_sql.pack(fill="x", padx=10, pady=10)

frame_botones = tk.Frame(ventana)
frame_botones.pack()

tk.Button(frame_botones,text="Analizar",
command=analizar,bg="green",fg="white",
width=15).pack(side="left", padx=10)

tk.Button(frame_botones,text="Parser",
command=parser,bg="blue",fg="white",
width=15).pack(side="left", padx=10)

tk.Button(frame_botones,text="Limpiar",
command=limpiar_tablas,bg="red",fg="white",
width=15).pack(side="left", padx=10)

tk.Label(ventana,text="TABLA DE TOKENS",
font=("Arial",12,"bold")).pack()

tree_tokens = ttk.Treeview(
ventana,
columns=("No","Linea","Token","Tipo","Codigo"),
show="headings"
)
tree_tokens.pack(fill="both",expand=True)

for col in ("No","Linea","Token","Tipo","Codigo"):
    tree_tokens.heading(col,text=col)

tk.Label(ventana,text="TABLA DE IDENTIFICADORES",
font=("Arial",12,"bold")).pack()

tree_ident = ttk.Treeview(
ventana,
columns=("Identificador","Valor","Lineas"),
show="headings",
height=5
)
tree_ident.pack(fill="x")

for col in ("Identificador","Valor","Lineas"):
    tree_ident.heading(col,text=col)

tk.Label(ventana,text="TABLA DE CONSTANTES",
font=("Arial",12,"bold")).pack()

tree_const = ttk.Treeview(
ventana,
columns=("Constante","Tipo","Codigo"),
show="headings",
height=5
)
tree_const.pack(fill="x")

for col in ("Constante","Tipo","Codigo"):
    tree_const.heading(col,text=col)

ventana.mainloop()
