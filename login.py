import customtkinter as ctk
from tkinter import messagebox
from controllers import controller as ctl
from tela_principal import abrir_tela_principal  # Importa a tela principal

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')  # opcional: tema mais legal


def validar_login():
    usuario = entrada_usuario.get()
    senha = entrada_senha.get()

    try:
        conn = ctl.conectar_banco()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM gestor WHERE username=%s AND senha=%s", (usuario, senha))
        resultado = cursor.fetchone()

        if resultado:
            resultado_login.configure(text="Login feito com sucesso", text_color='green')
            app.destroy()
            abrir_tela_principal()
        else:
            resultado_login.configure(text="Login incorreto", text_color='red')

        cursor.close()
        conn.close()

    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro na conexão: {erro}")

# ===== Tela de Login =====

app = ctk.CTk()
app.title('Sistema de Login')
app.geometry('400x450')
app.resizable(False, False)

frame_login = ctk.CTkFrame(app, width=350, height=380)
frame_login.pack(pady=30, padx=25)
frame_login.pack_propagate(False)  # mantém o tamanho do frame

ctk.CTkLabel(frame_login, text='Login', font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 25))

ctk.CTkLabel(frame_login, text='Usuário', anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=20)
entrada_usuario = ctk.CTkEntry(frame_login, placeholder_text='Digite seu usuário', width=280)
entrada_usuario.pack(pady=(5,15), padx=20)

ctk.CTkLabel(frame_login, text='Senha', anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=20)
entrada_senha = ctk.CTkEntry(frame_login, placeholder_text='Digite sua senha', show='*', width=280)
entrada_senha.pack(pady=(5,20), padx=20)

botao_login = ctk.CTkButton(frame_login, text='Login', command=validar_login, width=280)
botao_login.pack(pady=(0,15))

resultado_login = ctk.CTkLabel(frame_login, text='', font=ctk.CTkFont(size=14))
resultado_login.pack(pady=(0,15))


app.mainloop()