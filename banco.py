import tkinter as tk
from tkinter import messagebox

# Variáveis globais
saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

# Funções
def depositar():
    global saldo, extrato
    valor = entrada_valor.get()
    try:
        valor = float(valor)
        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"
            messagebox.showinfo("Depósito", "Depósito realizado com sucesso!")
        else:
            messagebox.showwarning("Erro", "Operação falhou! O valor informado é inválido.")
    except ValueError:
        messagebox.showwarning("Erro", "Operação falhou! O valor informado é inválido.")
    entrada_valor.delete(0, tk.END)
    atualizar_saldo()

def sacar():
    global saldo, extrato, numero_saques
    valor = entrada_valor.get()
    try:
        valor = float(valor)
        excedeu_saldo = valor > saldo
        excedeu_limite = valor > limite
        excedeu_saques = numero_saques >= LIMITE_SAQUES

        if excedeu_saldo:
            messagebox.showwarning("Erro", "Operação falhou! Você não tem saldo suficiente.")
        elif excedeu_limite:
            messagebox.showwarning("Erro", "Operação falhou! O valor do saque excede o limite.")
        elif excedeu_saques:
            messagebox.showwarning("Erro", "Operação falhou! Número máximo de saques excedido.")
        elif valor > 0:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f}\n"
            numero_saques += 1
            messagebox.showinfo("Saque", "Saque realizado com sucesso!")
        else:
            messagebox.showwarning("Erro", "Operação falhou! O valor informado é inválido.")
    except ValueError:
        messagebox.showwarning("Erro", "Operação falhou! O valor informado é inválido.")
    entrada_valor.delete(0, tk.END)
    atualizar_saldo()

def mostrar_extrato():
    global extrato, saldo
    extrato_texto = "Não foram realizadas movimentações." if not extrato else extrato
    extrato_texto += f"\nSaldo: R$ {saldo:.2f}"
    messagebox.showinfo("Extrato", extrato_texto)

def sair():
    root.quit()

def atualizar_saldo():
    label_saldo.config(text=f"Saldo: R$ {saldo:.2f}")

# Interface do Banco
root = tk.Tk()
root.title("Banco")
root.config(bg="lightblue")

# Frame para os botões
frame = tk.Frame(root)
frame.pack(pady=20)

# Labels e entradas
label_instrucoes = tk.Label(frame, text="Informe o valor da operação:")
label_instrucoes.grid(row=0, column=0, padx=10, pady=10)

entrada_valor = tk.Entry(frame, width=20)
entrada_valor.grid(row=0, column=1, padx=10, pady=10)

# Botões
botao_depositar = tk.Button(frame, text="Depositar", command=depositar)
botao_depositar.grid(row=1, column=0, padx=10, pady=10)

botao_sacar = tk.Button(frame, text="Sacar", command=sacar)
botao_sacar.grid(row=1, column=1, padx=10, pady=10)

botao_extrato = tk.Button(frame, text="Extrato", command=mostrar_extrato)
botao_extrato.grid(row=2, column=0, padx=10, pady=10)

botao_sair = tk.Button(frame, text="Sair", command=sair)
botao_sair.grid(row=2, column=1, padx=10, pady=10)

# Label para exibir o saldo
label_saldo = tk.Label(root, text=f"Saldo: R$ {saldo:.2f}", font=("Helvetica", 14))
label_saldo.pack(pady=20)

root.mainloop()
