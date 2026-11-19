# NutriFit - Contador de calorías con inicio de sesión (todo en un solo archivo)
# Instalar la librería:  pip install customtkinter
# Ejecutar:              python nutrifit_completo.py
import os
import re
import hashlib
import secrets
import customtkinter as ctk
from tkinter import messagebox

# =====================================================================
# 1. DATOS (vectores fijos)
# =====================================================================
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

VERDE = "#27AE60"
VERDE_CLARO = "#2ECC71"
ROJO = "#E74C3C"

# Lista de comidas del día (dos vectores paralelos)
nombres = []
calorias = []

# Usuarios registrados (vectores paralelos: la posición une los datos de cada usuario)
correos = []
sales = []      # texto aleatorio único de cada usuario
hashes = []     # contraseña ya protegida (nunca se guarda la contraseña real)
ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.txt")
DOMINIO = "@gmail.com"

# Reglas de la contraseña con regex (cada regla tiene su mensaje en la misma posición)
reglas_clave = [r"[A-Z]", r"[a-z]", r"[0-9]"]
mensajes_clave = ["una letra mayúscula", "una letra minúscula", "un número"]


# =====================================================================
# 2. CÁLCULOS
# =====================================================================
def buscar_posicion(lista, valor):
    """Recorre la lista con un for y devuelve la posición del valor (-1 si no está)."""
    for i in range(len(lista)):
        if lista[i] == valor:
            return i
    return -1


def calcular_tmb(sexo, peso, altura, edad):
    """Metabolismo basal con la fórmula de Mifflin-St Jeor."""
    if sexo == "Hombre":
        tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * edad - 161
    return tmb


def calcular_meta(sexo, tmb, pos_actividad, pos_objetivo):
    """Devuelve el gasto diario y la meta de calorías."""
    gasto = tmb * factores[pos_actividad]
    meta = gasto + gasto * ajustes[pos_objetivo]
    if sexo == "Hombre" and meta < 1500:
        meta = 1500
    if sexo == "Mujer" and meta < 1200:
        meta = 1200
    return gasto, meta


def calcular_macros(meta, peso, pos_objetivo):
    """Devuelve proteína, grasa y carbohidratos en gramos."""
    proteina = proteinas[pos_objetivo] * peso
    grasa = meta * 0.25 / 9
    carbos = (meta - proteina * 4 - grasa * 9) / 4
    return proteina, grasa, carbos


# =====================================================================
# 3. COMIDAS
# =====================================================================
def comida_agregar(nombre, kcal):
    if nombre == "":
        nombre = "Comida"
    nombres.append(nombre)
    calorias.append(round(kcal))


def comida_borrar_ultima():
    if len(nombres) > 0:
        nombres.pop()
        calorias.pop()


def comida_reiniciar():
    nombres.clear()
    calorias.clear()


def comida_total():
    """Suma las calorías con un ciclo for."""
    suma = 0
    for kcal in calorias:
        suma = suma + kcal
    return suma


def comida_texto_lista():
    """Arma el texto que se muestra en la lista de comidas."""
    texto = ""
    for i in range(len(nombres)):
        texto = texto + str(i + 1) + ". " + nombres[i] + " - " + str(calorias[i]) + " kcal\n"
    return texto


# =====================================================================
# 4. AUTENTICACIÓN (solo Gmail)
# =====================================================================
def encriptar(clave, sal):
    """Convierte la contraseña en un hash (no se puede revertir) con PBKDF2-SHA256."""
    return hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal.encode("utf-8"), 100000).hex()


def cargar_usuarios():
    """Lee usuarios.txt (una línea por usuario: correo,sal,hash)."""
    correos.clear()
    sales.clear()
    hashes.clear()
    try:
        archivo = open(ARCHIVO, "r", encoding="utf-8")
    except FileNotFoundError:
        return
    for linea in archivo:
        partes = linea.strip().split(",")
        if len(partes) == 3:
            correos.append(partes[0])
            sales.append(partes[1])
            hashes.append(partes[2])
    archivo.close()


def guardar_usuarios():
    archivo = open(ARCHIVO, "w", encoding="utf-8")
    for i in range(len(correos)):
        archivo.write(correos[i] + "," + sales[i] + "," + hashes[i] + "\n")
    archivo.close()


def validar_gmail(correo):
    """Devuelve (True/False, mensaje). Solo deja pasar correos de Gmail."""
    if correo == "":
        return False, "Escribe tu correo."
    if not correo.endswith(DOMINIO):
        return False, "Solo se permite iniciar sesión con Gmail (@gmail.com)."
    if re.fullmatch(r"[a-z0-9.]{6,30}@gmail\.com", correo) is None:
        return False, "Antes del @ usa de 6 a 30 caracteres: letras, números o puntos."
    return True, ""


def validar_clave(clave):
    """Revisa las reglas de la contraseña usando regex."""
    if re.search(r"\s", clave):
        return False, "La contraseña no puede tener espacios."
    if re.fullmatch(r".{8,}", clave) is None:
        return False, "La contraseña debe tener mínimo 8 caracteres."
    for i in range(len(reglas_clave)):
        if re.search(reglas_clave[i], clave) is None:
            return False, "La contraseña debe tener " + mensajes_clave[i] + "."
    return True, ""


def existe_correo(correo):
    for i in range(len(correos)):
        if correos[i] == correo:
            return True
    return False


def registrar(correo, clave):
    """Crea una cuenta nueva. Devuelve (True/False, mensaje)."""
    correo = correo.strip().lower()
    valido, mensaje = validar_gmail(correo)
    if not valido:
        return False, mensaje
    valida, mensaje = validar_clave(clave)
    if not valida:
        return False, mensaje
    if existe_correo(correo):
        return False, "Ese correo ya está registrado. Inicia sesión."

    sal = secrets.token_hex(8)
    correos.append(correo)
    sales.append(sal)
    hashes.append(encriptar(clave, sal))
    guardar_usuarios()
    return True, "Cuenta creada. Ya puedes iniciar sesión."


def iniciar_sesion(correo, clave):
    """Comprueba correo y contraseña. Devuelve (True/False, mensaje)."""
    correo = correo.strip().lower()
    valido, mensaje = validar_gmail(correo)
    if not valido:
        return False, mensaje

    for i in range(len(correos)):
        if correos[i] == correo:
            if hashes[i] == encriptar(clave, sales[i]):
                return True, "Bienvenido"
            return False, "Contraseña incorrecta."
    return False, "Ese correo no está registrado. Crea una cuenta primero."


# =====================================================================
# PANTALLA DE GUÍA (se muestra antes del login)
# =====================================================================
def crear_guia(ventana, al_continuar):
    marco = ctk.CTkFrame(ventana, fg_color="transparent")

    zona = ctk.CTkScrollableFrame(marco, fg_color="transparent")
    zona.pack(fill="both", expand=True, padx=15, pady=(15, 5))

    ctk.CTkLabel(zona, text="Antes de empezar", font=("Arial", 22, "bold")).pack(pady=(0, 2))
    ctk.CTkLabel(zona, text="Lee estas reglas para llenar tus datos sin errores.",
                 text_color="gray70").pack(pady=(0, 10))

    titulos = ["1. Tu cuenta", "2. Tus datos", "3. Tus comidas"]
    reglas = [
        [
            "Usa un correo Gmail que termine en @gmail.com (no se aceptan Hotmail, Outlook, etc.).",
            "Antes del @ van de 6 a 30 caracteres: letras, números o puntos.",
            "La contraseña debe tener mínimo 8 caracteres, con una mayúscula, una minúscula y un número.",
            "La contraseña no puede tener espacios.",
            "Al crear la cuenta, repite la misma contraseña en el segundo campo.",
        ],
        [
            "Peso en kilogramos (ej: 70 o 70,5).",
            "Altura en centímetros, no en metros (ej: 175, no 1.75).",
            "Edad en años (ej: 25).",
            "Escribe solo números; la coma o el punto sirven para decimales.",
            "Elige tu sexo, nivel de actividad y objetivo antes de pulsar «Calcular mis calorías».",
        ],
        [
            "El nombre de la comida es opcional; si lo dejas vacío se guarda como «Comida».",
            "Las calorías deben ser un número (ej: 350).",
            "Si te pasas de tu meta, la barra se pone en rojo.",
            "Tu meta nunca baja de 1500 kcal (hombres) ni de 1200 kcal (mujeres).",
        ],
    ]

    for i in range(len(titulos)):
        tarjeta = ctk.CTkFrame(zona, corner_radius=14)
        tarjeta.pack(fill="x", pady=6)
        ctk.CTkLabel(tarjeta, text=titulos[i], font=("Arial", 15, "bold"), text_color=VERDE_CLARO,
                     anchor="w").pack(fill="x", padx=12, pady=(10, 4))
        for regla in reglas[i]:
            ctk.CTkLabel(tarjeta, text="• " + regla, anchor="w", justify="left",
                         wraplength=400).pack(fill="x", padx=12, pady=1)
        ctk.CTkLabel(tarjeta, text="").pack(pady=2)

    ctk.CTkButton(marco, text="Entendido, continuar", height=40, fg_color=VERDE,
                  font=("Arial", 15, "bold"), command=al_continuar).pack(fill="x", padx=15, pady=(5, 15))
    return marco


# =====================================================================
# 5. PANTALLA DE LOGIN
# =====================================================================
def crear_login(ventana, al_entrar, al_ver_guia):
    """Dibuja el login. Cuando el usuario entra bien, llama al_entrar(correo)."""
    marco = ctk.CTkFrame(ventana, fg_color="transparent")

    # Botón para volver a ver la guía (se coloca abajo antes que las pestañas)
    ctk.CTkButton(marco, text="Ver guía de datos", fg_color="gray30",
                  command=al_ver_guia).pack(side="bottom", fill="x", padx=15, pady=(0, 15))

    pestanas = ctk.CTkTabview(marco, segmented_button_selected_color=VERDE)
    pestanas.pack(fill="both", expand=True, padx=15, pady=15)
    pestana_entrar = pestanas.add("Iniciar sesión")
    pestana_crear = pestanas.add("Crear cuenta")

    # ---------- Iniciar sesión ----------
    ctk.CTkLabel(pestana_entrar, text="Correo Gmail", anchor="w").pack(fill="x", padx=10, pady=(20, 0))
    entrada_correo = ctk.CTkEntry(pestana_entrar, placeholder_text="tucorreo@gmail.com")
    entrada_correo.pack(fill="x", padx=10, pady=(0, 8))

    ctk.CTkLabel(pestana_entrar, text="Contraseña", anchor="w").pack(fill="x", padx=10)
    entrada_clave = ctk.CTkEntry(pestana_entrar, show="*")
    entrada_clave.pack(fill="x", padx=10, pady=(0, 8))

    mensaje_entrar = ctk.CTkLabel(pestana_entrar, text="", wraplength=380)
    mensaje_entrar.pack(pady=6)

    def entrar():
        ok, mensaje = iniciar_sesion(entrada_correo.get(), entrada_clave.get())
        if ok:
            al_entrar(entrada_correo.get().strip().lower())
        else:
            mensaje_entrar.configure(text=mensaje, text_color=ROJO)

    ctk.CTkButton(pestana_entrar, text="Entrar", height=40, fg_color=VERDE,
                  font=("Arial", 15, "bold"), command=entrar).pack(fill="x", padx=10, pady=6)

    # ---------- Crear cuenta ----------
    ctk.CTkLabel(pestana_crear, text="Correo Gmail", anchor="w").pack(fill="x", padx=10, pady=(20, 0))
    nuevo_correo = ctk.CTkEntry(pestana_crear, placeholder_text="tucorreo@gmail.com")
    nuevo_correo.pack(fill="x", padx=10, pady=(0, 8))

    ctk.CTkLabel(pestana_crear, text="Contraseña (mín. 8: mayúscula, minúscula y número)", anchor="w").pack(fill="x", padx=10)
    nueva_clave = ctk.CTkEntry(pestana_crear, show="*")
    nueva_clave.pack(fill="x", padx=10, pady=(0, 8))

    ctk.CTkLabel(pestana_crear, text="Repite la contraseña", anchor="w").pack(fill="x", padx=10)
    repetir_clave = ctk.CTkEntry(pestana_crear, show="*")
    repetir_clave.pack(fill="x", padx=10, pady=(0, 8))

    mensaje_crear = ctk.CTkLabel(pestana_crear, text="", wraplength=380)
    mensaje_crear.pack(pady=6)

    def crear_cuenta():
        if nueva_clave.get() != repetir_clave.get():
            mensaje_crear.configure(text="Las contraseñas no coinciden.", text_color=ROJO)
            return
        ok, mensaje = registrar(nuevo_correo.get(), nueva_clave.get())
        if ok:
            mensaje_crear.configure(text=mensaje, text_color=VERDE_CLARO)
            entrada_correo.delete(0, "end")
            entrada_correo.insert(0, nuevo_correo.get().strip().lower())
            pestanas.set("Iniciar sesión")
        else:
            mensaje_crear.configure(text=mensaje, text_color=ROJO)

    ctk.CTkButton(pestana_crear, text="Crear cuenta", height=40, fg_color=VERDE,
                  font=("Arial", 15, "bold"), command=crear_cuenta).pack(fill="x", padx=10, pady=6)

    return marco


# =====================================================================
# 6. PANTALLA PRINCIPAL (solo existe si hubo inicio de sesión)
# =====================================================================
def crear_app(ventana, correo, al_cerrar_sesion):
    marco = ctk.CTkFrame(ventana, fg_color="transparent")

    meta = [0]   # vector de 1 posición para poder cambiar la meta desde las funciones

    # Barra con el usuario y el botón de cerrar sesión
    barra_usuario = ctk.CTkFrame(marco, fg_color="transparent")
    barra_usuario.pack(fill="x", padx=15, pady=(10, 0))
    ctk.CTkLabel(barra_usuario, text=correo, text_color="gray70").pack(side="left")
    ctk.CTkButton(barra_usuario, text="Cerrar sesión", width=110, fg_color="gray30",
                  hover_color=ROJO, command=al_cerrar_sesion).pack(side="right")

    pestanas = ctk.CTkTabview(marco, segmented_button_selected_color=VERDE)
    pestanas.pack(fill="both", expand=True, padx=15, pady=(5, 15))
    pestana1 = pestanas.add("1. Mis datos")
    pestana2 = pestanas.add("2. Mis comidas")

    # ---------- PESTAÑA 1: DATOS ----------
    zona = ctk.CTkScrollableFrame(pestana1, fg_color="transparent")
    zona.pack(fill="both", expand=True)

    # Los campos numéricos se crean con un for usando vectores
    titulos = ["Peso (kg)", "Altura (cm)", "Edad (años)"]
    ejemplos = ["Ej: 70", "Ej: 175", "Ej: 25"]
    campos = []
    for i in range(len(titulos)):
        ctk.CTkLabel(zona, text=titulos[i], anchor="w").pack(fill="x", padx=6)
        campo = ctk.CTkEntry(zona, placeholder_text=ejemplos[i])
        campo.pack(fill="x", padx=6, pady=(0, 8))
        campos.append(campo)
    entrada_peso = campos[0]
    entrada_altura = campos[1]
    entrada_edad = campos[2]

    ctk.CTkLabel(zona, text="Sexo", anchor="w").pack(fill="x", padx=6)
    boton_sexo = ctk.CTkSegmentedButton(zona, values=["Hombre", "Mujer"], selected_color=VERDE)
    boton_sexo.set("Hombre")
    boton_sexo.pack(fill="x", padx=6, pady=(0, 8))

    ctk.CTkLabel(zona, text="Nivel de actividad", anchor="w").pack(fill="x", padx=6)
    menu_actividad = ctk.CTkOptionMenu(zona, values=actividades, fg_color=VERDE, button_color=VERDE)
    menu_actividad.set(actividades[2])
    menu_actividad.pack(fill="x", padx=6, pady=(0, 8))

    def cambiar_descripcion(objetivo):
        posicion = buscar_posicion(objetivos, objetivo)
        texto_desc.configure(text=descripciones[posicion])

    ctk.CTkLabel(zona, text="¿Cuál es tu objetivo?", anchor="w", font=("Arial", 13, "bold")).pack(fill="x", padx=6)
    boton_objetivo = ctk.CTkSegmentedButton(zona, values=objetivos, selected_color=VERDE,
                                            command=cambiar_descripcion)
    boton_objetivo.set(objetivos[0])
    boton_objetivo.pack(fill="x", padx=6)
    texto_desc = ctk.CTkLabel(zona, text=descripciones[0], text_color="gray70")
    texto_desc.pack(pady=(4, 8))

    def calcular():
        try:
            peso = float(entrada_peso.get().replace(",", "."))
            altura = float(entrada_altura.get().replace(",", "."))
            edad = float(entrada_edad.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Escribe solo números en peso, altura y edad.")
            return

        sexo = boton_sexo.get()
        pos_act = buscar_posicion(actividades, menu_actividad.get())
        pos_obj = buscar_posicion(objetivos, boton_objetivo.get())

        tmb = calcular_tmb(sexo, peso, altura, edad)
        gasto, meta[0] = calcular_meta(sexo, tmb, pos_act, pos_obj)
        proteina, grasa, carbos = calcular_macros(meta[0], peso, pos_obj)

        texto_meta.configure(text=str(round(meta[0])) + " kcal")
        texto_detalle.configure(
            text="Metabolismo basal: " + str(round(tmb)) + " kcal\n"
            + "Gasto diario: " + str(round(gasto)) + " kcal\n\n"
            + "Proteína: " + str(round(proteina)) + " g\n"
            + "Carbohidratos: " + str(round(carbos)) + " g\n"
            + "Grasas: " + str(round(grasa)) + " g"
        )
        actualizar_pantalla()
        pestanas.set("2. Mis comidas")

    ctk.CTkButton(zona, text="Calcular mis calorías", height=40, fg_color=VERDE,
                  font=("Arial", 15, "bold"), command=calcular).pack(fill="x", padx=6, pady=6)

    tarjeta = ctk.CTkFrame(zona, corner_radius=14)
    tarjeta.pack(fill="x", padx=6, pady=8)
    texto_meta = ctk.CTkLabel(tarjeta, text="— kcal", font=("Arial", 34, "bold"), text_color=VERDE_CLARO)
    texto_meta.pack(pady=(10, 0))
    ctk.CTkLabel(tarjeta, text="meta diaria", text_color="gray60").pack()
    texto_detalle = ctk.CTkLabel(tarjeta, text="Completa tus datos y pulsa calcular.")
    texto_detalle.pack(pady=(8, 12))

    # ---------- PESTAÑA 2: COMIDAS ----------
    texto_total = ctk.CTkLabel(pestana2, text="0 / — kcal", font=("Arial", 24, "bold"))
    texto_total.pack(pady=(8, 4))
    barra = ctk.CTkProgressBar(pestana2, height=14, progress_color=VERDE_CLARO)
    barra.set(0)
    barra.pack(fill="x", padx=10)
    texto_restante = ctk.CTkLabel(pestana2, text="Primero calcula tu meta en la pestaña 1.", text_color="gray60")
    texto_restante.pack(pady=6)

    entrada_comida = ctk.CTkEntry(pestana2, placeholder_text="Comida (ej: Arroz con pollo)")
    entrada_comida.pack(fill="x", padx=10, pady=4)
    entrada_kcal = ctk.CTkEntry(pestana2, placeholder_text="Calorías")
    entrada_kcal.pack(fill="x", padx=10, pady=4)

    def actualizar_pantalla():
        lista_comidas.configure(state="normal")
        lista_comidas.delete("1.0", "end")
        lista_comidas.insert("end", comida_texto_lista())
        lista_comidas.configure(state="disabled")

        total = comida_total()
        texto_total.configure(text=str(total) + " / " + str(round(meta[0])) + " kcal")

        if meta[0] > 0:
            barra.set(min(total / meta[0], 1))
            restante = round(meta[0]) - total
            if restante >= 0:
                texto_restante.configure(text="Te quedan " + str(restante) + " kcal", text_color=VERDE_CLARO)
                barra.configure(progress_color=VERDE_CLARO)
            else:
                texto_restante.configure(text="Te pasaste por " + str(-restante) + " kcal", text_color=ROJO)
                barra.configure(progress_color=ROJO)

    def agregar_comida():
        try:
            kcal = float(entrada_kcal.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Escribe un número en las calorías.")
            return
        comida_agregar(entrada_comida.get(), kcal)
        entrada_comida.delete(0, "end")
        entrada_kcal.delete(0, "end")
        actualizar_pantalla()

    def borrar_ultima():
        comida_borrar_ultima()
        actualizar_pantalla()

    def reiniciar():
        comida_reiniciar()
        actualizar_pantalla()

    ctk.CTkButton(pestana2, text="Agregar comida", fg_color=VERDE,
                  command=agregar_comida).pack(fill="x", padx=10, pady=6)

    lista_comidas = ctk.CTkTextbox(pestana2, state="disabled")
    lista_comidas.pack(fill="both", expand=True, padx=10, pady=4)

    ctk.CTkButton(pestana2, text="Borrar última", fg_color="gray30", hover_color=ROJO,
                  command=borrar_ultima).pack(fill="x", padx=10, pady=(4, 2))
    ctk.CTkButton(pestana2, text="Reiniciar el día", fg_color="gray30", hover_color=ROJO,
                  command=reiniciar).pack(fill="x", padx=10, pady=(2, 8))

    actualizar_pantalla()
    return marco


# =====================================================================
# 7. PROGRAMA PRINCIPAL
# =====================================================================
def main():
    ctk.set_appearance_mode("dark")
    ventana = ctk.CTk()
    ventana.title("NutriFit - Contador de calorías")
    ventana.geometry("520x720")

    # Encabezado verde (siempre visible)
    encabezado = ctk.CTkFrame(ventana, corner_radius=0, fg_color=VERDE, height=70)
    encabezado.pack(fill="x")
    ctk.CTkLabel(encabezado, text="NutriFit", font=("Arial", 26, "bold"), text_color="white").pack(pady=(10, 0))
    ctk.CTkLabel(encabezado, text="Calcula tus calorías y controla tu día", text_color="white").pack(pady=(0, 10))

    pantalla = [None]   # vector de 1 posición: guarda la pantalla que se está mostrando

    def quitar_pantalla():
        if pantalla[0] is not None:
            pantalla[0].destroy()

    def mostrar_guia():
        quitar_pantalla()
        pantalla[0] = crear_guia(ventana, mostrar_login)
        pantalla[0].pack(fill="both", expand=True)

    def mostrar_login():
        quitar_pantalla()
        pantalla[0] = crear_login(ventana, mostrar_app, mostrar_guia)
        pantalla[0].pack(fill="both", expand=True)

    def mostrar_app(correo):
        """Solo se llega aquí si el login fue correcto."""
        quitar_pantalla()
        pantalla[0] = crear_app(ventana, correo, cerrar_sesion)
        pantalla[0].pack(fill="both", expand=True)

    def cerrar_sesion():
        comida_reiniciar()
        mostrar_login()

    cargar_usuarios()
    mostrar_guia()
    ventana.mainloop()


if __name__ == "__main__":
    main()