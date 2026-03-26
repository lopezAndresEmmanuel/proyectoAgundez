import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re

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

#op relaciones
relacionales = {
    ">=": 84, 
    "<=": 85, 
    ">": 81, 
    "<": 82, 
    "=": 83
}

#op aritmeticos
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


# analizador
def analizar():

    limpiar_tablas()

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

            # ignorar espacios
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

                messagebox.showerror(
                    "Error Léxico",
                    f"Carácter no reconocido '{token}' en línea {num_linea}"
                )

            tree_tokens.insert(
                "", "end",
                values=(token_number, num_linea, token, tipo, codigo)
            )

            token_number += 1

    # Cargar tabla identificadores
    for ident, datos in tabla_identificadores.items():
        tree_ident.insert(
            "", "end",
            values=(ident, datos[0], ",".join(map(str, datos[1])))
        )

    # Cargar tabla constantes
    for const, datos in tabla_constantes.items():
        tree_const.insert(
            "", "end",
            values=(const, datos[0], datos[1])
        )


#funcion para limpiar las tablas
def limpiar_tablas():
    for item in tree_tokens.get_children():
        tree_tokens.delete(item)
    for item in tree_ident.get_children():
        tree_ident.delete(item)
    for item in tree_const.get_children():
        tree_const.delete(item)


# interfaz
ventana = tk.Tk()
ventana.title("ESCÁNER DML SQL")
ventana.geometry("1200x700")

texto_sql = tk.Text(ventana, height=6, font=("Consolas", 12))
texto_sql.pack(fill="x", padx=10, pady=10)

frame_botones = tk.Frame(ventana)
frame_botones.pack()

tk.Button(frame_botones, text="Analizar",
          command=analizar,
          bg="green", fg="white",
          width=15).pack(side="left", padx=10)

tk.Button(frame_botones, text="Limpiar",
          command=limpiar_tablas,
          bg="red", fg="white",
          width=15).pack(side="left", padx=10)


#tabla de tokens
tk.Label(ventana, text="TABLA DE TOKENS",
         font=("Arial", 12, "bold")).pack()

tree_tokens = ttk.Treeview(
    ventana,
    columns=("No", "Linea", "Token", "Tipo", "Codigo"),
    show="headings"
)
tree_tokens.pack(fill="both", expand=True)

for col in ("No", "Linea", "Token", "Tipo", "Codigo"):
    tree_tokens.heading(col, text=col)


#tabla dinamica de identificadores
tk.Label(ventana, text="TABLA DE IDENTIFICADORES",
         font=("Arial", 12, "bold")).pack()

tree_ident = ttk.Treeview(
    ventana,
    columns=("Identificador", "Valor", "Lineas"),
    show="headings",
    height=5
)
tree_ident.pack(fill="x")

for col in ("Identificador", "Valor", "Lineas"):
    tree_ident.heading(col, text=col)


# tabla dinamica de constantes
tk.Label(ventana, text="TABLA DE CONSTANTES",
         font=("Arial", 12, "bold")).pack()

    tree_const = ttk.Treeview(
        ventana,
    columns=("Constante", "Tipo", "Codigo"),
    show="headings",
    height=5
)
tree_const.pack(fill="x")

for col in ("Constante", "Tipo", "Codigo"):
    tree_const.heading(col, text=col)


ventana.mainloop()