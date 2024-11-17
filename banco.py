import textwrap
import tkinter as tk
from tkinter import Button, messagebox
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from tkinter import simpledialog


class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index < len(self.contas):
            conta = self.contas[self._index]
            self._index += 1
            return conta
        else:
            raise StopIteration()


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.index_conta = 0

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
        if not transacao.aprovada:
            messagebox.showerror("Erro", "Operação falhou! Você não tem saldo suficiente.")
            return False

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            messagebox.showerror(
                "Erro", "Operação falhou! Você não tem saldo suficiente."
            )
            
        elif valor > 0:
            self._saldo -= valor
            messagebox.showinfo("Sucesso", "Saque realizado com sucesso!")
            return True
        else:
            messagebox.showerror(
                "Erro", "Operação falhou! O valor informado é inválido."
            )
        
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            messagebox.showinfo("Sucesso", "Depósito realizado com sucesso!")
            
        else:
            messagebox.showerror(
                "Erro", "Operação falhou! O valor informado é inválido."
            )
            return False

        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            messagebox.showerror(
                "Erro", "Operação falhou! O valor do saque excede o limite."
            )
        elif excedeu_saques:
            messagebox.showerror(
                "Erro", "Operação falhou! Número máximo de saques excedido."
            )
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now(datetime.timezone.utc).strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self.transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self, tipo):
        data_atual = datetime.now(datetime.timezone.utc).strftime("%d-%m-%Y")
        for transacao in self.transacoes:
            if transacao["data"].startswith(data_atual):
                yield transacao

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# Fix function
def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
        print(f"[{data_hora}] {args[0].__class__.__name__}: R$ {args[1]}")
        return resultado

    return envelope


class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank App")
        self.geometry("400x400")
        self.clientes = []
        self.contas = []
        self.create_widgets()

    def create_widgets(self):
        # Widgets para o menu principal
        tk.Label(self, text="Bem-vindo ao Banco", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Criar Cliente", command=self.criar_cliente).pack(pady=5)
        tk.Button(self, text="Criar Conta", command=self.criar_conta).pack(pady=5)
        tk.Button(self, text="Depositar", command=self.depositar).pack(pady=5)
        tk.Button(self, text="Sacar", command=self.sacar).pack(pady=5)
        tk.Button(self, text="Extrato", command=self.exibir_extrato).pack(pady=5)
        tk.Button(self, text="Listar Contas", command=self.listar_contas).pack(pady=5)


    def filtrar_cliente(self, cpf, clientes):
        clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
        return clientes_filtrados[0] if clientes_filtrados else None

    def recuperar_conta_cliente(cliente):
        if not cliente.contas:
            messagebox.showerror("Erro", "Cliente não possui conta!")
            return
        
        return cliente.contas[0]

    @log_transacao
    def depositar(self, clientes):
        cpf = simpledialog.askstring("Depositar", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf, clientes)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            return

        valor = simpledialog.askfloat("Depositar", "Informe o valor do depósito:")
        transacao = Deposito(valor)

        conta = self.recuperar_conta_cliente(cliente)
        if not conta:
            return

        cliente.realizar_transacao(conta, transacao)

    @log_transacao
    def sacar(self, clientes):
        cpf = simpledialog.askstring("Sacar", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf, clientes)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            return

        valor = simpledialog.askfloat("Sacar", "Informe o valor do saque:")
        transacao = Saque(valor)

        conta = self.recuperar_conta_cliente(cliente)
        if not conta:
            return

        cliente.realizar_transacao(conta, transacao)

    @log_transacao
    def exibir_extrato(self, clientes):
        cpf = simpledialog.askstring("Extrato", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf, clientes)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            return

        conta = self.recuperar_conta_cliente(cliente)
        if not conta:
            return

        messagebox.showinfo("", "========== EXTRATO ==========")
        extrato = ""
        tem_transacao = False

        for transacao in conta.historico.gerar_relatorio(tipo_transacao="saque"):
            tem_transacao = True
            extrato += (
                f"{transacao['tipo']}:\n"
                f"\tR$ {transacao['valor']:.2f} - {transacao['data']}\n"
            )

        if not tem_transacao:
            extrato = "Não foram realizadas movimentações."

        messagebox.showinfo("Extrato do Cliente", extrato)
        messagebox.showinfo("", "=============================")

    @log_transacao
    def criar_cliente(self):
        # Exemplo de janela para criar cliente
        cliente_window = tk.Toplevel(self)
        cliente_window.title("Criar Cliente")

        tk.Label(cliente_window, text="Nome:").pack()
        nome_entry = tk.Entry(cliente_window)
        nome_entry.pack()

        tk.Label(cliente_window, text="CPF:").pack()
        cpf_entry = tk.Entry(cliente_window)
        cpf_entry.pack()

        tk.Label(cliente_window, text="Data de Nascimento:").pack()
        data_entry = tk.Entry(cliente_window)
        data_entry.pack()

        tk.Label(cliente_window, text="Endereço:").pack()
        endereco_entry = tk.Entry(cliente_window)
        endereco_entry.pack()

        def confirmar():
            nome = nome_entry.get()
            cpf = cpf_entry.get()
            data_nascimento = data_entry.get()
            endereco = endereco_entry.get()

            if not nome or not cpf or not data_nascimento or not endereco:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios")
                return

            # Criação do cliente
            cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
            self.clientes.append(cliente)
            messagebox.showinfo("Sucesso", "Cliente criado com sucesso")
            cliente_window.destroy()

        tk.Button(cliente_window, text="Criar", command=confirmar).pack()

    @log_transacao
    def criar_conta(self):
        # Janela para criar uma nova conta
        conta_window = tk.Toplevel(self)
        conta_window.title("Criar Conta")

        tk.Label(conta_window, text="CPF do Cliente:").pack()
        cpf_entry = tk.Entry(conta_window)
        cpf_entry.pack()

        def confirmar():
            cpf = cpf_entry.get()
            cliente = self.filtrar_cliente(cpf, self.clientes)

            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado")
                return

            numero_conta = len(self.contas) + 1
            conta = ContaCorrente.nova_conta(cliente, numero_conta, limite=500, limite_saques=3)
            self.contas.append(conta)
            cliente.contas.append(conta)
            messagebox.showinfo("Sucesso", "Conta criada com sucesso")
            conta_window.destroy()

        tk.Button(conta_window, text="Criar", command=confirmar).pack()

    def listar_contas(contas):
        for conta in ContasIterador(contas):
            print("=" * 100)
            print(textwrap.dedent(str(conta)))

    def chamar_criar_cliente(self):
        # 'clientes' é a lista ou estrutura que você tem no seu aplicativo
        self.clientes = []  # Substitua isso pela sua lista real de clientes
        self.criar_cliente(self.clientes)


if __name__ == "__main__":
    app = BankApp()
    app.mainloop()