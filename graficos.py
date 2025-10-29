from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from controllers import controller as ctl
from sqlalchemy import create_engine




def tela_graficos():
    app = ctk.CTk()
    app.title("Gráficos de Desempenho- Auto Escola")
    app.geometry("1100x800")
    app.resizable(False, False)

    frame_graficos = ctk.CTkFrame(app)
    frame_graficos.pack(fill="both", expand=True, padx=20, pady=20)
    # Limpa os gráficos anteriores
    """for widget in frame_graficos.winfo_children():
        widget.destroy()"""

    def atualizar_graficos():

        try:
            conn = ctl.conectar_banco()
            engine = create_engine("mysql+mysqlconnector://user:1234@localhost:3306/autoescola")

            # MÉTRICA 1 — Preferência por Turno
            query_turno = """
                SELECT
                    CASE
                        WHEN HOUR(a.datetime) BETWEEN 6 AND 11 THEN 'Manhã'
                        WHEN HOUR(a.datetime) BETWEEN 12 AND 17 THEN 'Tarde'
                        WHEN HOUR(a.datetime) BETWEEN 18 AND 23 THEN 'Noite'
                        ELSE 'Madrugada'
                    END AS turno,
                    COUNT(*) AS total
                FROM agendamento AS a
                GROUP BY turno
                ORDER BY total DESC;
            """
            df_turno = pd.read_sql(query_turno, engine)

            # MÉTRICA 2 — Preferência por Veículo
            query_veiculo = """
                SELECT v.nome AS veiculo, COUNT(*) AS total
                FROM agendamento AS a
                JOIN veiculo v ON a.id_veiculo = v.id
                GROUP BY v.nome
                ORDER BY total DESC;
            """
            df_veiculo = pd.read_sql(query_veiculo, engine)

            # MÉTRICA 3 — Preferência de Alunos por Instrutor
            query_instrutor = """
                SELECT i.nome AS instrutor, COUNT(*) AS total
                FROM agendamento AS a
                JOIN instrutor i ON a.id_instrutor = i.id
                GROUP BY i.nome
                ORDER BY total DESC;
            """
            df_instrutor = pd.read_sql(query_instrutor, engine)

            # MÉTRICA 4 — Preferência por Categoria
            query_categoria = """
                SELECT a.cat AS categoria, COUNT(*) AS total
                FROM agendamento AS a
                GROUP BY a.cat
                ORDER BY total DESC;
            """
            df_categoria = pd.read_sql(query_categoria, engine)

            conn.close()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados para os gráficos:\n{e}")
            return

        # Verifica se há dados
        if any(df.empty for df in [df_turno, df_veiculo, df_instrutor, df_categoria]):
            ctk.CTkLabel(frame_graficos, text="Sem dados suficientes para gerar gráficos.",
                         font=("Arial", 16, "bold")).pack(pady=20)
            return

        # Cria figura com 2 linhas e 2 colunas
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))

        # Gráfico 1 — Turnos
        df_turno.plot(kind="bar", x="turno", y="total", ax=axs[0, 0], color="skyblue", legend=False)
        axs[0, 0].set_title("Preferência por Turno")
        axs[0, 0].set_ylabel("Quantidade")

        # Gráfico 2 — Veículos
        df_veiculo.plot(kind="bar", x="veiculo", y="total", ax=axs[0, 1], color="orange", legend=False)
        axs[0, 1].set_title("Preferência por Veículo")

        # Gráfico 3 — Instrutores
        df_instrutor.plot(kind="bar", x="instrutor", y="total", ax=axs[1, 0], color="lightgreen", legend=False)
        axs[1, 0].set_title("Preferência de Alunos por Instrutor")

        # Gráfico 4 — Categorias
        df_categoria.plot(kind="pie", y="total", labels=df_categoria["categoria"], ax=axs[1, 1], autopct='%1.1f%%')
        axs[1, 1].set_title("Distribuição por Categoria")
        axs[1, 1].set_ylabel("")

        # Ajusta layout
        fig.tight_layout()

        # Mostra dentro do frame
        canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    btn_atualizar = ctk.CTkButton(frame_graficos, text="Atualizar Gráficos", command=atualizar_graficos)
    btn_atualizar.pack(pady=10)

    atualizar_graficos()

# ===== Executar a tela principal =====
if __name__ == "__main__":
    tela_graficos()
