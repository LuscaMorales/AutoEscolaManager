import mysql.connector
from tkinter import messagebox
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import customtkinter as ctk
from dotenv import load_dotenv
import os

load_dotenv()

def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )

def cadastrar_gestor(usuario, senha, cpf, nome_completo):
    if not usuario or not senha or not cpf or not nome_completo:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO gestor (nome, cpf, username, senha) VALUES (%s, %s, %s, %s)", (nome_completo, cpf, usuario, senha))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Cadastro", f"Usuário '{usuario}' cadastrado com sucesso!")
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao cadastrar: {erro}")

def cadastrar_inst(nome, cpf, cat):
    if not nome or not cpf or not cat:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO instrutor (nome, cpf, categoria) VALUES (%s, %s, %s)", (nome, cpf, cat))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Cadastro", f"Instrutor '{nome}' cadastrado com sucesso!")
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao cadastrar: {erro}")

def cadastrar_veic(nome, placa):
    if not nome or not placa:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")
        return
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO veiculo (nome, placa) VALUES (%s, %s)", (nome, placa))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Cadastro", f"Veiculo '{nome}' cadastrado com sucesso!")
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao cadastrar: {erro}")


def datetime_converter(data_str, hora_str):
    """
    Converte uma data (DD/MM/AAAA) e hora (HH:MM) em um objeto datetime compatível com MySQL.
    """
    try:
        data_hora_str = f"{data_str} {hora_str}"
        data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M")
        return data_hora
    except ValueError:
        raise ValueError("Formato inválido. Use data DD/MM/AAAA e hora HH:MM.")


def agendamentos_aluno(nome_aluno, alunodados, data_inicial, data_final):

    data_ini_sql = datetime.strptime(data_inicial, "%d/%m/%Y").strftime("%Y-%m-%d")
    data_fim_sql = datetime.strptime(data_final, "%d/%m/%Y").strftime("%Y-%m-%d")

    query = """
        SELECT 
            a.id,
            al.nome AS aluno,
            i.nome AS instrutor,
            v.nome AS veiculo,
            DATE_FORMAT(a.datetime, '%d/%m/%Y') AS data,
            DATE_FORMAT(a.datetime, '%H:%i') AS hora,
            a.cat
        FROM agendamento AS a
        JOIN aluno al ON a.id_aluno = al.id
        JOIN instrutor i ON a.id_instrutor = i.id
        JOIN veiculo v ON a.id_veiculo = v.id
        WHERE a.id_aluno = %s
          AND DATE(a.datetime) BETWEEN %s AND %s
        ORDER BY a.datetime;
    """
    id_aluno = alunodados["id"]
    email_aluno = alunodados["email"]
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(query, (id_aluno, data_ini_sql, data_fim_sql))
    agendamentos = cursor.fetchall()
    #return cursor.fetchall()
    enviar_email(email_aluno, nome_aluno, agendamentos)


def enviar_email(email_aluno, nome_aluno, agendamentos, porta=587):

    remetente = os.getenv("EMAIL_USER")
    senha = os.getenv("EMAIL_PASS")
    servidor_smtp = "smtp.gmail.com"

    if not agendamentos:
        print(f"Nenhum agendamento para {nome_aluno}.")
        return

    # Criar corpo do e-mail em HTML para formatação
    corpo_html = f"<h2>Agendamentos de {nome_aluno}</h2>"
    corpo_html += "<table border='1' cellpadding='5' cellspacing='0'>"
    corpo_html += "<tr><th>Data</th><th>Hora</th><th>Instrutor</th><th>Veículo</th><th>Categoria</th></tr>"

    for aula in agendamentos:
        corpo_html += f"<tr><td>{aula[4]}</td><td>{aula[5]}</td><td>{aula[2]}</td><td>{aula[3]}</td><td>{aula[6]}</td></tr>"

    corpo_html += "</table>"

    # Criar mensagem MIME
    mensagem = MIMEMultipart()
    mensagem['From'] = remetente
    mensagem['To'] = email_aluno
    mensagem['Subject'] = f"Seus agendamentos de aula prática - {nome_aluno}"

    mensagem.attach(MIMEText(corpo_html, 'html'))

    # Conectar no servidor SMTP e enviar e-mail
    try:
        server = smtplib.SMTP(servidor_smtp, porta)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, email_aluno, mensagem.as_string())
        server.quit()
        print(f"E-mail enviado com sucesso para {email_aluno}!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


def buscar_aulas(tree):
    for item in tree.get_children():
        tree.delete(item)
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        query = """
                SELECT 
                    a.id,
                    al.nome AS aluno,
                    i.nome AS instrutor,
                    v.nome AS veiculo,
                    a.datetime,
                    a.cat
                FROM agendamento AS a
                JOIN aluno al ON a.id_aluno = al.id
                JOIN instrutor i ON a.id_instrutor = i.id
                JOIN veiculo v ON a.id_veiculo = v.id
                ORDER BY a.datetime;
                """
        cursor.execute(query)
        aulas = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao carregar aulas: {erro}")
        aulas = []


    # Inserir os dados
    for aula in aulas:
        tree.insert("", "end", values=(
            aula[0], aula[1], aula[2], aula[3], aula[4], aula[5]
        ))

    tree.pack(fill="both", expand=True, padx=10, pady=10)


def excluir_agendamento(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione uma aula para excluir.")
        return

    item = tree.item(selected[0])["values"]
    id_agendamento = item[0]
    aluno = item[1]
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        query = """DELETE FROM agendamento WHERE id = %s;"""

        confirmar = messagebox.askyesno("Confirmação", f"Deseja excluir a aula de {aluno}?")
        if confirmar:
            tree.delete(selected[0])
            cursor.execute(query, (id_agendamento,))
            conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao excluir aula: {erro}")

def editar_agendamento(tree):
    size = 15
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Selecione um agendamento para editar.")
        return
    item = tree.item(selected[0])["values"]
    id_agendamento = item[0]
    janela_edicao = ctk.CTkToplevel()
    janela_edicao.title(f"Editar Agendamento #{id_agendamento}")
    janela_edicao.geometry("500x550")

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email FROM aluno ORDER BY nome")
        alunos = cursor.fetchall()
        alunos_dict = {aluno["nome"]: {
            "id":aluno["id"],
            "email":aluno["email"]}
            for aluno in alunos}

        cursor.execute("SELECT id, nome FROM instrutor ORDER BY nome")
        instrutores = cursor.fetchall()
        inst_dict = {instrutor["nome"]: instrutor["id"] for instrutor in instrutores}

        cursor.execute("SELECT id, nome FROM veiculo ORDER BY nome")
        veiculos = cursor.fetchall()
        veic_dict = {veic["nome"]: veic["id"] for veic in veiculos}

        cursor.close()
        conn.close()
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao carregar nomes dos alunos: {erro}")

    entry_ag_nome = ctk.CTkComboBox(janela_edicao, values=list(alunos_dict.keys()), width=300)
    ctk.CTkLabel(janela_edicao, text="Nome do Aluno:", anchor="w", font=ctk.CTkFont(size=size, weight="bold")).pack(fill="x", pady=(10,5), padx=20)
    entry_ag_nome.set(item[1])
    entry_ag_nome.pack(pady=(0,5))
    entry_ag_inst = ctk.CTkComboBox(janela_edicao, values=list(inst_dict.keys()), width=200)
    ctk.CTkLabel(janela_edicao, text="Nome do Instrutor:", anchor="w", font=ctk.CTkFont(size=size, weight="bold")).pack(fill="x", pady=(10,5), padx=20)
    entry_ag_inst.set(item[2])
    entry_ag_inst.pack(pady=(0,5))
    entry_ag_veic = ctk.CTkComboBox(janela_edicao, values=list(veic_dict.keys()), width=200)
    ctk.CTkLabel(janela_edicao, text="Veículo:", anchor="w", font=ctk.CTkFont(size=size, weight="bold")).pack(
        fill="x", pady=(10, 5), padx=20)
    entry_ag_veic.set(item[3])
    entry_ag_veic.pack(pady=(0,5))

    ctk.CTkLabel(janela_edicao, text="Data (DD/MM/AAAA):", anchor="w", font=ctk.CTkFont(size=size, weight="bold")).pack(
        fill="x",pady=5, padx=20)
    entry_data = ctk.CTkEntry(janela_edicao)
    dataF = item[4].split(" ")[0].split("-")
    dataF.reverse()
    dataF = "/".join(dataF)
    entry_data.insert(0, dataF)
    entry_data.pack(anchor="w", pady=5, padx=100)

    ctk.CTkLabel(janela_edicao, text="Hora (HH:MM):", anchor="w", font=ctk.CTkFont(size=size, weight="bold")).pack(
        fill="x",pady=5, padx=20)
    entry_hora = ctk.CTkEntry(janela_edicao)
    entry_hora.pack(anchor="w",pady=5, padx=100)
    entry_hora.insert(0, item[4].split(" ")[1][:5])

    categorias = ["A", "B", "AB"]
    entry_ag_cat = ctk.CTkComboBox(janela_edicao, values=categorias, width=150)
    ctk.CTkLabel(janela_edicao, text="Categoria:", anchor="w", font=ctk.CTkFont(size=size, weight="bold")).pack(
        fill="x", pady=(10, 5), padx=20)
    entry_ag_cat.set(item[5])
    entry_ag_cat.pack(pady=(0, 5))

    def update_aula():
        nome = entry_ag_nome.get()
        alunodados = alunos_dict[nome]
        idAluno = alunodados["id"]
        inst = entry_ag_inst.get()
        idInst = inst_dict[inst]
        veic = entry_ag_veic.get()
        idVeic = veic_dict[veic]
        cat = entry_ag_cat.get()
        data = entry_data.get()
        hora = entry_hora.get()
        if not all([nome, data, hora, inst, veic, cat]):
            messagebox.showwarning("Atenção", "Preencha todos os campos.", parent=janela_edicao)
            return
        try:
            newDatetime = datetime_converter(data, hora)
            conn = conectar_banco()
            cursor = conn.cursor()
            sql = """UPDATE agendamento
                     SET id_aluno = %s, id_instrutor = %s, id_veiculo = %s, datetime = %s, cat = %s
                     WHERE id = %s"""
            cursor.execute(sql, (idAluno, idInst, idVeic, newDatetime, cat, item[0]))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Aula alterada", f"Aula Prática de {nome} alterada com sucesso")
        except mysql.connector.Error as erro:
            messagebox.showerror("Erro", f"Erro ao salvar no banco: {erro}")
        janela_edicao.destroy()
        buscar_aulas(tree)



    btn_alterar = ctk.CTkButton(janela_edicao, text="Fazer alterações", width=200,
                                command=lambda: update_aula())
    btn_alterar.pack(pady=20)

def atualizar_registros():
    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email FROM aluno ORDER BY nome")
        alunos = cursor.fetchall()
        alunos_dict = {aluno["nome"]: {
            "id":aluno["id"],
            "email":aluno["email"]}
            for aluno in alunos}

        cursor.execute("SELECT id, nome FROM instrutor ORDER BY nome")
        instrutores = cursor.fetchall()
        inst_dict = {instrutor["nome"]: instrutor["id"] for instrutor in instrutores}

        cursor.execute("SELECT id, nome FROM veiculo ORDER BY nome")
        veiculos = cursor.fetchall()
        veic_dict = {veic["nome"]: veic["id"] for veic in veiculos}

        cursor.close()
        conn.close()
        return alunos_dict, inst_dict, veic_dict
    except mysql.connector.Error as erro:
        messagebox.showerror("Erro", f"Erro ao carregar nomes dos alunos: {erro}")
        return null

