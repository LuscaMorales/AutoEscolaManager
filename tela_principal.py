import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from controllers import controller as ctl
import mysql.connector
from tkinter import ttk
from graficos import tela_graficos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ===== Tela Principal =====
def abrir_tela_principal():
    app = ctk.CTk()
    app.title("Menu Principal - Auto Escola")
    app.geometry("900x650")
    app.resizable(False, False)

    abas = ctk.CTkTabview(app, width=800, height=600)
    abas.pack(padx=15, pady=15)

    # ======= Função para criar campos =======
    def criar_campo(frame, texto, largura=400):
        label = ctk.CTkLabel(frame, text=texto, anchor="w", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(fill="x", pady=(10, 5))
        entry = ctk.CTkEntry(frame, width=largura)
        entry.pack(pady=(0, 5))
        return entry

    def criar_campoV2(frame, texto, largura=300):
        label = ctk.CTkLabel(frame, text=texto, anchor="w", font=ctk.CTkFont(size=15, weight="bold"))
        label.pack(fill="x")
        entry = ctk.CTkEntry(frame, width=largura)
        entry.pack()
        return entry

    alunos_dict, inst_dict, veic_dict = ctl.atualizar_registros()
    def atualizar_comboboxes():
        global alunos_dict, inst_dict, veic_dict
        alunos_dict, inst_dict, veic_dict  = ctl.atualizar_registros()
        entry_ag_nome.configure(values=list(alunos_dict.keys()))
        entry_ag_inst.configure(values=list(inst_dict.keys()))
        entry_ag_veic.configure(values=list(veic_dict.keys()))
        entry_ag_nomeEv.configure(values=list(alunos_dict.keys()))

    # ======= ABA 1 - CADASTRAR GESTOR =======
    aba_cadastrar = abas.add("Cadastrar Gestor")
    frame_cadastrarG = ctk.CTkFrame(aba_cadastrar)
    frame_cadastrarG.pack(pady=15, padx=20, fill="both", expand=True)

    ctk.CTkLabel(frame_cadastrarG, text="Usuário", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(20, 10))
    novo_usuario = ctk.CTkEntry(frame_cadastrarG, placeholder_text="Digite o username do usuário", width=250)
    novo_usuario.pack(pady=10)
    ctk.CTkLabel(frame_cadastrarG, text="Senha", font=ctk.CTkFont(size=15, weight="normal")).pack(pady=(10, 10))
    nova_senha = ctk.CTkEntry(frame_cadastrarG, placeholder_text="Digite a senha", show="*", width=250)
    nova_senha.pack(pady=5)
    ctk.CTkLabel(frame_cadastrarG, text="Nome Completo", font=ctk.CTkFont(size=15, weight="normal")).pack(pady=(10, 10))
    novo_nome = ctk.CTkEntry(frame_cadastrarG, placeholder_text="Digite o nome completo", width=250)
    novo_nome.pack(pady=5)
    ctk.CTkLabel(frame_cadastrarG, text="CPF", font=ctk.CTkFont(size=15, weight="normal")).pack(pady=(10, 10))
    novo_cpf = ctk.CTkEntry(frame_cadastrarG, placeholder_text="Digite o cpf do usuário", width=250)
    novo_cpf.pack(pady=5)

    btn_cadastrarG = ctk.CTkButton(frame_cadastrarG, text="Cadastrar", width=200,
        command=lambda:
            ctl.cadastrar_gestor(novo_usuario.get(), nova_senha.get(), novo_cpf.get(), novo_nome.get()))
    btn_cadastrarG.pack(pady=20)


    # ======= ABA 2 - CADASTRAR ALUNO =======
    aba_cadastrar = abas.add("Cadastrar Aluno")
    frame_cadastrar = ctk.CTkFrame(aba_cadastrar)
    frame_cadastrar.pack(pady=5, padx=20, fill="both", expand=True)

    entry_nome = criar_campo(frame_cadastrar, "Nome do Aluno:")
    entry_cpf = criar_campo(frame_cadastrar, "CPF:")
    entry_categoria = criar_campo(frame_cadastrar, "Categoria da CNH:")
    entry_email = criar_campo(frame_cadastrar, "E-mail:")
    entry_renache = criar_campo(frame_cadastrar, "RENACH:")

    data_atual = datetime.now().strftime('%d/%m/%Y')
    data_entrada_label = ctk.CTkLabel(frame_cadastrar, text=f"Data de Entrada: {data_atual}", font=ctk.CTkFont(size=13))
    data_entrada_label.pack(pady=10)

    #===== Função cadastrar aluno =====
    def cadastrar_aluno():
        nome = entry_nome.get()
        categoria = entry_categoria.get()
        email = entry_email.get()
        cpf = entry_cpf.get()
        renache = entry_renache.get()
        valor = 1000
        if not all([nome, categoria, renache, valor]):
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return
        try:
            valor_float = float(valor)
        except ValueError:
            messagebox.showerror("Erro", "Valor deve ser numérico.")
            return
        data_entrada_db = datetime.now().strftime("%Y-%m-%d")
        try:
            conn = ctl.conectar_banco()
            cursor = conn.cursor()
            sql = "INSERT INTO aluno (nome, cpf, senha, email, cat, renach, valor, entrada) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (nome, cpf, cpf, email, categoria, renache, valor_float, data_entrada_db))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao salvar no banco: {erro}")
            return
        messagebox.showinfo("Cadastro", f"Aluno {nome} cadastrado com sucesso!")
        entry_nome.delete(0, ctk.END)
        entry_categoria.delete(0, ctk.END)
        entry_renache.delete(0, ctk.END)
        entry_email.delete(0, ctk.END)
        entry_cpf.delete(0, ctk.END)

    btn_cadastrar = ctk.CTkButton(frame_cadastrar, text="Cadastrar", width=200,
        command=lambda:
            (cadastrar_aluno(), atualizar_comboboxes()))
    btn_cadastrar.pack(pady=20)


    #ABA CADASTRO INST VEIC
    aba_cad_inst = abas.add("Cadastrar Inst./Veic.")
    frame_cad_inst = ctk.CTkFrame(aba_cad_inst)
    frame_cad_inst.pack(pady=1, padx=3, fill="both", expand=True)
    ctk.CTkLabel(frame_cad_inst, text="Cadastre o instrutor", font=ctk.CTkFont(size=15, weight="normal")).pack(pady=(10, 10))
    entry_nome_inst = criar_campoV2(frame_cad_inst, "Nome do Inst:")
    entry_cpf_inst = criar_campoV2(frame_cad_inst, "CPF:")
    entry_categoria_inst = criar_campoV2(frame_cad_inst, "Categoria da CNH:")
    btn_cadastrar_inst = ctk.CTkButton(frame_cad_inst, text="Cadastrar Instrutor", width=200,
        command=lambda:
            (ctl.cadastrar_inst(entry_nome_inst.get(), entry_cpf_inst.get(), entry_categoria_inst.get()),
             atualizar_comboboxes(),
             entry_nome_inst.delete(0, ctk.END), entry_cpf_inst.delete(0, ctk.END),
             entry_categoria_inst.delete(0, ctk.END) ))
    btn_cadastrar_inst.pack(pady=13)
    ctk.CTkLabel(frame_cad_inst, text="Cadastre o Veiculo", font=ctk.CTkFont(size=15, weight="normal")).pack(pady=(10, 10))
    entry_nome_veic = criar_campoV2(frame_cad_inst, "Nome do veículo:")
    entry_placa_veic = criar_campoV2(frame_cad_inst, "Placa do veículo:")
    btn_cadastrar_veic = ctk.CTkButton(frame_cad_inst, text="Cadastrar Veículo", width=200,
        command=lambda:
            (ctl.cadastrar_veic(entry_nome_veic.get(), entry_placa_veic.get()), atualizar_comboboxes(),
             entry_nome_veic.delete(0, ctk.END), entry_placa_veic.delete(0, ctk.END)))
    btn_cadastrar_veic.pack(pady=13)





    # ======= ABA 3 - AGENDAR AULAS =======
    aba_agendar = abas.add("Agendar Aulas")
    frame_agendar = ctk.CTkFrame(aba_agendar)
    frame_agendar.pack(padx=20, pady=20, fill="both", expand=True)

    # ComboBox com nomes do banco

    entry_ag_nome = ctk.CTkComboBox(frame_agendar, values=list(alunos_dict.keys()), width=400)
    ctk.CTkLabel(frame_agendar, text="Nome do Aluno:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(10,5))
    entry_ag_nome.pack(pady=(0,5))
    entry_ag_inst = ctk.CTkComboBox(frame_agendar, values=list(inst_dict.keys()), width=300)
    ctk.CTkLabel(frame_agendar, text="Nome do Instrutor:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=(10,5))
    entry_ag_inst.pack(pady=(0,5))
    entry_ag_veic = ctk.CTkComboBox(frame_agendar, values=list(veic_dict.keys()), width=300)
    ctk.CTkLabel(frame_agendar, text="Veículo:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(
        fill="x", pady=(10, 5))
    entry_ag_veic.pack(pady=(0,5))
    entry_ag_data = criar_campo(frame_agendar, "Data (DD/MM/AAAA):")
    entry_ag_hora = criar_campo(frame_agendar, "Hora (HH:MM):")
    categorias = ["A", "B", "AB"]
    entry_ag_cat = ctk.CTkComboBox(frame_agendar, values=categorias, width=300)
    ctk.CTkLabel(frame_agendar, text="Categoria:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(
        fill="x", pady=(10, 5))
    entry_ag_cat.pack(pady=(0, 5))


    def agendar_aula():
        alunos_dict, inst_dict, veic_dict = ctl.atualizar_registros()
        nome = entry_ag_nome.get()
        alunodados = alunos_dict[nome]
        idAluno = alunodados["id"]
        inst = entry_ag_inst.get()
        idInst = inst_dict[inst]
        veic = entry_ag_veic.get()
        idVeic = veic_dict[veic]
        cat = entry_ag_cat.get()
        data = entry_ag_data.get()
        hora = entry_ag_hora.get()
        newDatetime = ctl.datetime_converter(data, hora)
        if not all([nome, data, hora, inst, veic, cat]):
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return
        try:
            conn = ctl.conectar_banco()
            cursor = conn.cursor()
            sql = "INSERT INTO agendamento (id_instrutor, id_aluno, id_veiculo, datetime, cat) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (idInst, idAluno, idVeic, newDatetime, cat))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Agendamento", f"Aula agendada para {nome} em {data} às {hora}")
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao salvar no banco: {erro}")
        entry_ag_nome.set("")
        entry_ag_data.delete(0, ctk.END)
        entry_ag_hora.delete(0, ctk.END)



    # ======= ABA 4 - AULAS AGENDADAS =======
    aba_agendadas = abas.add("Aulas Agendadas")
    frame_agendamentos = ctk.CTkFrame(aba_agendadas)
    frame_agendamentos.pack(fill="both", expand=True, padx=10, pady=10)
    colunas = ("id", "aluno", "instrutor", "veiculo", "datetime", "cat")
    tree = ttk.Treeview(frame_agendamentos, columns=colunas, show="headings", height=10)

    tree.heading("id", text="ID")
    tree.heading("aluno", text="Aluno")
    tree.heading("instrutor", text="Instrutor")
    tree.heading("veiculo", text="Veículo")
    tree.heading("datetime", text="Data/Hora")
    tree.heading("cat", text="Categoria")
    tree.column("id", width=50, anchor="center")
    tree.column("aluno", width=120)
    tree.column("instrutor", width=120)
    tree.column("veiculo", width=100)
    tree.column("datetime", width=150)
    tree.column("cat", width=80, anchor="center")

    ctl.buscar_aulas(tree)

    # Frame dos botões
    frame_botoes = ctk.CTkFrame(frame_agendamentos)
    frame_botoes.pack(fill="x", pady=(5, 10))

    btn_editar = ctk.CTkButton(frame_botoes, text="Editar", width=100,
                                command=lambda: (ctl.editar_agendamento(tree), ctl.buscar_aulas(tree)))
    btn_editar.pack(side="left", padx=5)

    btn_excluir = ctk.CTkButton(frame_botoes, text="Excluir", width=100, fg_color="red",
                                command=lambda: (ctl.excluir_agendamento(tree), ctl.buscar_aulas(tree)))
    btn_excluir.pack(side="left", padx=5)

    btn_graficos = ctk.CTkButton(frame_agendamentos, text="Gráficos", width=200, command=tela_graficos)
    btn_graficos.pack(pady=20)

    btn_agendar = ctk.CTkButton(frame_agendar, text="Agendar Aula", width=200, command=lambda:
    (agendar_aula(), ctl.buscar_aulas(tree), atualizar_comboboxes()))
    btn_agendar.pack(pady=20)

    # ======= ABA 5 - ENVIAR AULAS =======
    aba_envio = abas.add("Envio Aulas")
    frame_envio = ctk.CTkFrame(aba_envio)
    frame_envio.pack(padx=10, pady=10, fill="x")
    ctk.CTkLabel(
        frame_envio, text="Nome do Aluno:",
        anchor="w", font=ctk.CTkFont(size=14, weight="bold")
    ).grid(row=0, column=0, padx=5, pady=(10, 5), sticky="w")
    entry_ag_nomeEv = ctk.CTkComboBox(frame_envio, values=list(alunos_dict.keys()), width=400)
    entry_ag_nomeEv.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")
    lbl_data_inicialEv = ctk.CTkLabel(frame_envio, text="Data Inicial (DD/MM/AAAA):", font=ctk.CTkFont(size=13))
    lbl_data_inicialEv.grid(row=2, column=0, padx=25, pady=5, sticky="w")
    entry_data_inicialEv = ctk.CTkEntry(frame_envio, width=130)
    entry_data_inicialEv.grid(row=3, column=0, padx=55, pady=5, sticky="w")
    lbl_data_finalEv = ctk.CTkLabel(frame_envio, text="Data Final (DD/MM/AAAA):", font=ctk.CTkFont(size=13))
    lbl_data_finalEv.grid(row=2, column=0, padx=250, pady=5, sticky="w")
    entry_data_finalEv = ctk.CTkEntry(frame_envio, width=130)
    entry_data_finalEv.grid(row=3, column=0, padx=270, pady=5, sticky="w")
    btn_enviar = ctk.CTkButton(frame_envio, text="Enviar", width=120)
    btn_enviar.grid(row=5, column=0, padx=10, pady=5)
    btn_enviar.configure(command=lambda:
    ctl.agendamentos_aluno(entry_ag_nomeEv.get(), entry_data_inicialEv.get(), entry_data_finalEv.get()))



    # ======= BOTÃO SAIR =======
    def sair_sistema():
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            app.destroy()

    botao_sair = ctk.CTkButton(app, text="Sair", command=sair_sistema, width=100, fg_color="#a51f1f", hover_color="#8b1515")
    botao_sair.pack(pady=10, side="bottom")

    app.mainloop()

# ===== Executar a tela principal =====
if __name__ == "__main__":
    abrir_tela_principal()
