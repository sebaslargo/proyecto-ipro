# NutriFit - Versión básica
# Instalar la librería:  pip install customtkinter
# Ejecutar:              python calorias_basico.py
#---------------------------------------------- sebas
import customtkinter as ctk
from tkinter import messagebox
objetivos = ["Bajar de peso", "Ganar masa", "Definir"]
ajustes = [-0.20, 0.12, -0.10]          
proteinas = [2.0, 1.8, 2.2]             
descripciones = [
    "Déficit del 20% para perder grasa.",
    "Superávit del 12% para ganar músculo.",
    "Déficit del 10% con mucha proteína.",
]
actividades = ["Sedentario", "Ligero (1-3 días)", "Moderado (3-5 días)", "Alto (6-7 días)"]
factores = [1.2, 1.375, 1.55, 1.725]
meta = 0            
nombres = []        
calorias = []       
# ------------------------------------------------------------ fredy
def cambiar_descripcion(objetivo):
    posicion = objetivos.index(objetivo)
    texto_desc.configure(text=descripciones[posicion])
def calcular():
    global meta
    try:
        peso = float(entrada_peso.get().replace(",", "."))
        altura = float(entrada_altura.get().replace(",", "."))
        edad = float(entrada_edad.get().replace(",", "."))
    except ValueError:
        messagebox.showerror("Error", "Escribe solo números en peso, altura y edad.")
        return
    sexo = boton_sexo.get()
    posicion_act = actividades.index(menu_actividad.get())
    posicion_obj = objetivos.index(boton_objetivo.get())

    # Metabolismo fórmula de Mifflin-St Jeor
    if sexo == "Hombre":
        tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * edad - 161
    # Gasto total del día y meta según el objetivo
    gasto = tmb * factores[posicion_act]
    meta = gasto + gasto * ajustes[posicion_obj]
    if sexo == "Hombre" and meta < 1500:
        meta = 1500
    if sexo == "Mujer" and meta < 1200:
        meta = 1200
    proteina = proteinas[posicion_obj] * peso
    grasa = meta * 0.25 / 9
    carbos = (meta - proteina * 4 - grasa * 9) / 4
#----------------------------------------------------------------------------------------------------------------- alejo
    # Mostrar resultados
    texto_meta.configure(text=str(round(meta)) + " kcal")
    texto_detalle.configure(
        text="Metabolismo basal: " + str(round(tmb)) + " kcal\n"
        + "Gasto diario: " + str(round(gasto)) + " kcal\n\n"
        + "Proteína: " + str(round(proteina)) + " g\n"
        + "Carbohidratos: " + str(round(carbos)) + " g\n"
        + "Grasas: " + str(round(grasa)) + " g"
    )
    actualizar_pantalla()
    pestanas.set("2. Mis comidas")


def agregar_comida():
    """Agrega una comida a las listas."""
    nombre = entrada_comida.get()
    try:
        kcal = float(entrada_kcal.get().replace(",", "."))
    except ValueError:
        messagebox.showerror("Error", "Escribe un número en las calorías.")
        return

    if nombre == "":
        nombre = "Comida"

    nombres.append(nombre)
    calorias.append(round(kcal))

    entrada_comida.delete(0, "end")
    entrada_kcal.delete(0, "end")
    actualizar_pantalla()


def borrar_ultima():
    """Borra la última comida agregada."""
    if len(nombres) > 0:
        nombres.pop()
        calorias.pop()
        actualizar_pantalla()


def reiniciar():
    """Borra todas las comidas."""
    nombres.clear()
    calorias.clear()
    actualizar_pantalla()
#---------------------------------------------------------------------------------------------

def actualizar_pantalla():
    """Dibuja la lista de comidas, el total y la barra de progreso."""
    # Lista de comidas
    lista_comidas.configure(state="normal")
    lista_comidas.delete("1.0", "end")
    for i in range(len(nombres)):
        lista_comidas.insert("end", str(i + 1) + ". " + nombres[i] + " - " + str(calorias[i]) + " kcal\n")
    lista_comidas.configure(state="disabled")

    # Total de calorías
    total = sum(calorias)
    texto_total.configure(text=str(total) + " / " + str(round(meta)) + " kcal")

    # Barra y mensaje (solo si ya se calculó la meta)
    if meta > 0:
        barra.set(min(total / meta, 1))
        restante = round(meta) - total
        if restante >= 0:
            texto_restante.configure(text="Te quedan " + str(restante) + " kcal", text_color="#2ECC71")
            barra.configure(progress_color="#2ECC71")
        else:
            texto_restante.configure(text="Te pasaste por " + str(-restante) + " kcal", text_color="#E74C3C")
            barra.configure(progress_color="#E74C3C")
# 4. INTERFAZ GRÁFICA (ventana, pestañas y botones)
ctk.set_appearance_mode("dark")
ventana = ctk.CTk()
ventana.title("NutriFit - Contador de calorías")
ventana.geometry("520x720")

# Encabezado verde
encabezado = ctk.CTkFrame(ventana, corner_radius=0, fg_color="#27AE60", height=70)
encabezado.pack(fill="x")
ctk.CTkLabel(encabezado, text="NutriFit", font=("Arial", 26, "bold"), text_color="white").pack(pady=(10, 0))
ctk.CTkLabel(encabezado, text="Calcula tus calorías y controla tu día", text_color="white").pack(pady=(0, 10))

# Pestañas
pestanas = ctk.CTkTabview(ventana, segmented_button_selected_color="#27AE60")
pestanas.pack(fill="both", expand=True, padx=15, pady=15)
pestana1 = pestanas.add("1. Mis datos")
pestana2 = pestanas.add("2. Mis comidas")

# ---------- PESTAÑA 1: DATOS DEL USUARIO ----------
zona = ctk.CTkScrollableFrame(pestana1, fg_color="transparent")
zona.pack(fill="both", expand=True)

ctk.CTkLabel(zona, text="Peso (kg)", anchor="w").pack(fill="x", padx=6)
entrada_peso = ctk.CTkEntry(zona, placeholder_text="Ej: 70")
entrada_peso.pack(fill="x", padx=6, pady=(0, 8))

ctk.CTkLabel(zona, text="Altura (cm)", anchor="w").pack(fill="x", padx=6)
entrada_altura = ctk.CTkEntry(zona, placeholder_text="Ej: 175")
entrada_altura.pack(fill="x", padx=6, pady=(0, 8))

ctk.CTkLabel(zona, text="Edad (años)", anchor="w").pack(fill="x", padx=6)
entrada_edad = ctk.CTkEntry(zona, placeholder_text="Ej: 25")
entrada_edad.pack(fill="x", padx=6, pady=(0, 8))

ctk.CTkLabel(zona, text="Sexo", anchor="w").pack(fill="x", padx=6)
boton_sexo = ctk.CTkSegmentedButton(zona, values=["Hombre", "Mujer"], selected_color="#27AE60")
boton_sexo.set("Hombre")
boton_sexo.pack(fill="x", padx=6, pady=(0, 8))

ctk.CTkLabel(zona, text="Nivel de actividad", anchor="w").pack(fill="x", padx=6)
menu_actividad = ctk.CTkOptionMenu(zona, values=actividades, fg_color="#27AE60", button_color="#27AE60")
menu_actividad.set(actividades[2])
menu_actividad.pack(fill="x", padx=6, pady=(0, 8))

ctk.CTkLabel(zona, text="¿Cuál es tu objetivo?", anchor="w", font=("Arial", 13, "bold")).pack(fill="x", padx=6)
boton_objetivo = ctk.CTkSegmentedButton(zona, values=objetivos, selected_color="#27AE60",
                                        command=cambiar_descripcion)
boton_objetivo.set(objetivos[0])
boton_objetivo.pack(fill="x", padx=6)
texto_desc = ctk.CTkLabel(zona, text=descripciones[0], text_color="gray70")
texto_desc.pack(pady=(4, 8))

ctk.CTkButton(zona, text="Calcular mis calorías", height=40, fg_color="#27AE60",
              font=("Arial", 15, "bold"), command=calcular).pack(fill="x", padx=6, pady=6)

# Tarjeta de resultados
tarjeta = ctk.CTkFrame(zona, corner_radius=14)
tarjeta.pack(fill="x", padx=6, pady=8)
texto_meta = ctk.CTkLabel(tarjeta, text="— kcal", font=("Arial", 34, "bold"), text_color="#2ECC71")
texto_meta.pack(pady=(10, 0))
ctk.CTkLabel(tarjeta, text="meta diaria", text_color="gray60").pack()
texto_detalle = ctk.CTkLabel(tarjeta, text="Completa tus datos y pulsa calcular.")
texto_detalle.pack(pady=(8, 12))

# ---------- PESTAÑA 2: COMIDAS ----------
texto_total = ctk.CTkLabel(pestana2, text="0 / — kcal", font=("Arial", 24, "bold"))
texto_total.pack(pady=(8, 4))
barra = ctk.CTkProgressBar(pestana2, height=14, progress_color="#2ECC71")
barra.set(0)
barra.pack(fill="x", padx=10)
texto_restante = ctk.CTkLabel(pestana2, text="Primero calcula tu meta en la pestaña 1.", text_color="gray60")
texto_restante.pack(pady=6)

entrada_comida = ctk.CTkEntry(pestana2, placeholder_text="Comida (ej: Arroz con pollo)")
entrada_comida.pack(fill="x", padx=10, pady=4)
entrada_kcal = ctk.CTkEntry(pestana2, placeholder_text="Calorías")
entrada_kcal.pack(fill="x", padx=10, pady=4)

ctk.CTkButton(pestana2, text="Agregar comida", fg_color="#27AE60",
              command=agregar_comida).pack(fill="x", padx=10, pady=6)

lista_comidas = ctk.CTkTextbox(pestana2, state="disabled")
lista_comidas.pack(fill="both", expand=True, padx=10, pady=4)

ctk.CTkButton(pestana2, text="Borrar última", fg_color="gray30", hover_color="#E74C3C",
              command=borrar_ultima).pack(fill="x", padx=10, pady=(4, 2))
ctk.CTkButton(pestana2, text="Reiniciar el día", fg_color="gray30", hover_color="#E74C3C",
              command=reiniciar).pack(fill="x", padx=10, pady=(2, 8))

# Mantiene la ventana abierta
ventana.mainloop()