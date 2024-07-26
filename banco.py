import tkinter as tk
from tkinter import messagebox
from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import simpledialog


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

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
            messagebox.showerror("Erro", "Operação falhou! Você não tem saldo suficiente.")
        elif valor > 0:
            self._saldo -= valor
            messagebox.showinfo("Sucesso", "Saque realizado com sucesso!")
            return True
        else:
            messagebox.showerror("Erro", "Operação falhou! O valor informado é inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            messagebox.showinfo("Sucesso", "Depósito realizado com sucesso!")
        else:
            messagebox.showerror("Erro", "Operação falhou! O valor informado é inválido.")
            return False
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            messagebox.showerror("Erro", "Operação falhou! O valor do saque excede o limite.")
        elif excedeu_saques:
            messagebox.showerror("Erro", "Operação falhou! Número máximo de saques excedido.")
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
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


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


class BancoApp:
    def __init__(self, root):
        self.clientes = []
        self.contas = []

        self.root = root
        self.root.title("Banco")

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=10)

        self.depositar_button = tk.Button(self.menu_frame, text="Depositar", command=self.depositar)
        self.depositar_button.grid(row=0, column=0, padx=10)

        self.sacar_button = tk.Button(self.menu_frame, text="Sacar", command=self.sacar)
        self.sacar_button.grid(row=0, column=1, padx=10)

        self.extrato_button = tk.Button(self.menu_frame, text="Extrato", command=self.exibir_extrato)
        self.extrato_button.grid(row=0, column=2, padx=10)

        self.nova_conta_button = tk.Button(self.menu_frame, text="Nova Conta", command=self.criar_conta)
        self.nova_conta_button.grid(row=1, column=0, padx=10)

        self.listar_contas_button = tk.Button(self.menu_frame, text="Listar Contas", command=self.listar_contas)
        self.listar_contas_button.grid(row=1, column=1, padx=10)

        self.novo_usuario_button = tk.Button(self.menu_frame, text="Novo Usuário", command=self.criar_cliente)
        self.novo_usuario_button.grid(row=1, column=2, padx=10)

    def filtrar_cliente(self, cpf):
        clientes_filtrados = [cliente for cliente in self.clientes if cliente.cpf == cpf]
        return clientes_filtrados[0] if clientes_filtrados else None

    def recuperar_conta_cliente(self, cliente):
        if not cliente.contas:
            messagebox.showerror("Erro", "Cliente não possui conta!")
            return None

        if len(cliente.contas) == 1:
            return cliente.contas[0]

        contas_str = "\n".join([f"{i + 1} - Conta: {conta.numero}" for i, conta in enumerate(cliente.contas)])
        conta_idx = simpledialog.askinteger("Escolha a Conta", f"Escolha a conta:\n{contas_str}") - 1
        return cliente.contas[conta_idx]

    def depositar(self):
        cpf = simpledialog.askstring("Depositar", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            return

        valor = simpledialog.askfloat("Depositar", "Informe o valor do depósito:")
        transacao = Deposito(valor)

        conta = self.recuperar_conta_cliente(cliente)
        if not conta:
            return

        cliente.realizar_transacao(conta, transacao)

    def sacar(self):
        cpf = simpledialog.askstring("Sacar", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            return

        valor = simpledialog.askfloat("Sacar", "Informe o valor do saque:")
        transacao = Saque(valor)

        conta = self.recuperar_conta_cliente(cliente)
        if not conta:
            return

        cliente.realizar_transacao(conta, transacao)

    def exibir_extrato(self):
        cpf = simpledialog.askstring("Extrato", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado!")
            return

        conta = self.recuperar_conta_cliente(cliente)
        if not conta:
            return

        transacoes = conta.historico.transacoes

        extrato = "\n".join([f"{transacao['tipo']}: R$ {transacao['valor']:.2f}" for transacao in transacoes])
        if not extrato:
            extrato = "Não foram realizadas movimentações."
        saldo = f"\nSaldo: R$ {conta.saldo:.2f}"

        messagebox.showinfo("Extrato", extrato + saldo)

    def criar_cliente(self):
        cpf = simpledialog.askstring("Novo Usuário", "Informe o CPF (somente números):")
        cliente = self.filtrar_cliente(cpf)

        if cliente:
            messagebox.showerror("Erro", "Já existe cliente com esse CPF!")
            return

        nome = simpledialog.askstring("Novo Usuário", "Informe o nome completo:")
        data_nascimento = simpledialog.askstring("Novo Usuário", "Informe a data de nascimento (dd-mm-aaaa):")
        endereco = simpledialog.askstring("Novo Usuário", "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado):")

        cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
        self.clientes.append(cliente)

        messagebox.showinfo("Sucesso", "Cliente criado com sucesso!")

    def criar_conta(self):
        cpf = simpledialog.askstring("Nova Conta", "Informe o CPF do cliente:")
        cliente = self.filtrar_cliente(cpf)

        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado, fluxo de criação de conta encerrado!")
            return

        numero_conta = len(self.contas) + 1
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
        self.contas.append(conta)
        cliente.adicionar_conta(conta)

        messagebox.showinfo("Sucesso", "Conta criada com sucesso!")

    def listar_contas(self):
        contas_str = "\n\n".join([str(conta) for conta in self.contas])
        if not contas_str:
            contas_str = "Nenhuma conta encontrada."
        messagebox.showinfo("Listar Contas", contas_str)


if __name__ == "__main__":
    root = tk.Tk()
    app = BancoApp(root)
    root.mainloop()