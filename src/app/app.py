from dataclasses import dataclass, field
from typing import Callable, Protocol


@dataclass(eq=False)
class Usuário:
    ttask: int


class Servidor(Protocol):
    """ Interface para servidores. """
    umax: int
    custo_por_tick: int
    usuários: list[Usuário]
    _total_ticks: int

    def __gt__(self, other) -> bool:
        """ Deve ser implementado. """

    def disponível(self) -> bool:
        """ Deve ser implementado. """

    def adiciona_usuário(self, usuário) -> None:
        """ Deve ser implementado. """

    def custo(self) -> int:
        """ Deve ser implementado. """

    def tick(self) -> None:
        """ Deve ser implementado. """

    def a_finalizar(self) -> bool:
        """ Deve ser implementado. """


@dataclass
class ServidorTipoUm():
    """ Objeto para processar ticks de tarefas de usuário. """
    umax: int
    custo_por_tick: int = 1
    usuários: list[Usuário] = field(default_factory=list)
    _total_ticks: int = 0

    def __gt__(self, other) -> bool:
        """ Pra comparar tempo de vida maior. """
        return (
            sum(u.ttask for u in self.usuários) - self._total_ticks >
            sum(u.ttask for u in other.usuários) - other._total_ticks
        )

    def disponível(self) -> bool:
        """ Disponível para novos usuários. """
        return len(self.usuários) < self.umax

    def adiciona_usuário(self, usuário: Usuário) -> None:
        """ Adiciona usuário. """
        if self.disponível():
            self.usuários.append(usuário)

    def _desconecta_finalizado(self) -> None:
        """ Desconecta usuários com tarefas finalizadas. """
        self.usuários = [u for u in self.usuários if u.ttask > 0]

    def custo(self) -> int:
        """ Calcula custo total por utilização. """
        return self._total_ticks * self.custo_por_tick

    def tick(self) -> None:
        for u in self.usuários:
            u.ttask -= 1
        self._total_ticks += 1
        self._desconecta_finalizado()

    def a_finalizar(self) -> bool:
        return not any(u.ttask for u in self.usuários)


def cria_usuário(ttask: int):
    return Usuário(ttask)


def cria_servidor_tipo_um(umax: int) -> Servidor:
    return ServidorTipoUm(umax)


@dataclass
class Balanceador:
    """ Balanceador de cargas de tarefas de usuários em servidores. """
    path_entrada: str
    fábrica_usuário: Callable
    fábrica_servidor: Callable
    _ttask: int = field(init=False)
    _umax: int = field(init=False)
    _numero_novos_usuários: list = field(init=False)
    _servidores: list[Servidor] = field(init=False, default_factory=list)
    _custo_total: int = 0

    def _le_entradas(self) -> None:
        """ Obtem dados do arquido de entrada. """
        with open(self.path_entrada) as f:
            self._ttask = int(f.readline())
            self._umax = int(f.readline())
            self._numero_novos_usuários = [int(li) for li in f.readlines()]

    def __post_init__(self):
        self._le_entradas()

    def _associa_usuários_servidores(self, n_usuários) -> None:
        """ Cria usuários e os associam à servidores existentes ou criados. """
        for _ in range(n_usuários):
            usuário = self.fábrica_usuário(self._ttask)
            s = next(
                (s for s in sorted(self._servidores) if s.disponível()),
                None
            )
            if not s:
                s = self.fábrica_servidor(self._umax)
                s.adiciona_usuário(usuário)
                self._servidores.append(s)
            else:
                s.adiciona_usuário(usuário)

    def _remove_servidor_ocioso(self) -> None:
        """ remove o servidor a finalizar e acumula o custo. """
        a_remover = [s for s in self._servidores if s.a_finalizar()]
        for r in a_remover:
            self._custo_total += r.custo()
            self._servidores.remove(r)

    def _tick(self, n_u) -> str:
        """ Um manipulador para executar os ticks nos servidores e
        retorna usuários ativos.
        """
        self._remove_servidor_ocioso()
        self._associa_usuários_servidores(n_u)
        usuarios_ativos = []
        for s in self._servidores:
            usuarios_ativos.append(len(s.usuários))
            s.tick()
        return ','.join(str(u) for u in usuarios_ativos)

    def _obtém_numero_usuarios(self) -> int:
        """ Obtém o número de usuários da fila. """
        if len(self._numero_novos_usuários) > 0:
            return self._numero_novos_usuários.pop(0)
        else:
            return 0

    def processa_tarefas(self) -> str:
        """ Loop principal de processamento das tarefas. """
        saída = []
        while True:
            n_u = self._obtém_numero_usuarios()
            saída.append(self._tick(n_u))
            if len(self._servidores) == 0:
                break

        saída.append(str(self._custo_total))
        r = '\n'.join(s for s in saída if s)
        print(r)
        return r


def main(path_entrada):
    balanceador = Balanceador(
        path_entrada,
        cria_usuário,
        cria_servidor_tipo_um
    )
    return balanceador.processa_tarefas()
