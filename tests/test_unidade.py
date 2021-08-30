from functools import partial
from os import path

from src.app.app import (
    Balanceador, cria_servidor_tipo_um, cria_usuário, entrada_aleatória,
    entrada_txt, main, Servidor, ServidorTipoUm, Usuário
)

"""
    tick - unidade básica de tempo de simulação

    *<Usuários <conectam>> em <servidores <<disponíveis>> e executam uma
<tarefa>.

    *Cada <tarefa> leva um número de <ticks> para ser <finalizada> e após isso
o <usuário se desconecta automaticamente>.

    *O <número de ticks> é representado por <ttask>

    Servidores são máquinas virtuais que se <auto criam> para acomodar novos
usuários.

    *Um servidor tem o <custo de R$1,00 por tick>.
    *Um servidor <suporta no máximo <umax> usuários simultâneamente>.
    Um servidor <deve ser finalizado se ocioso>.

Entrada:
    linha 1 - ttask
    linha 2 - umax
    demais  - número de usuários para cada tick


Saída:
    Um arquivo que contenha uma lista de servidores no final de cada tick,
representado pelo número de usuários em cada servidor separados por vírgula
e ao final, o custo total por utilização dos servidores.

"""


class TesteServidor:
    def test_usuarios_conectam_em_servidores_disponíveis(self):
        usuário = Usuário(ttask=1)
        servidor = ServidorTipoUm(umax=1)
        servidor.adiciona_usuário(usuário)
        assert usuário in servidor.usuários

    def test_tarefa_6_ticks_decrementa_para_5_num_tick(self):
        usuário = Usuário(ttask=6)
        servidor = ServidorTipoUm(umax=1)
        servidor.adiciona_usuário(usuário)
        servidor.tick()
        assert usuário.ttask == 5

    def test_usuario_se_desconecta_automaticamente(self):
        usuário = Usuário(ttask=3)
        usuário2 = Usuário(ttask=4)
        servidor = ServidorTipoUm(umax=2)
        servidor.adiciona_usuário(usuário)
        servidor.adiciona_usuário(usuário2)
        for _ in range(3):
            servidor.tick()
        assert usuário not in servidor.usuários

    def test_verifica_se_pode_ser_finalizado(self):
        ticks = 2
        usuário = Usuário(ttask=ticks)
        servidor = ServidorTipoUm(umax=2)
        servidor.adiciona_usuário(usuário)
        for _ in range(ticks):
            servidor.tick()
        assert servidor.a_finalizar()

    def test_tarefa_5_ticks_a_1_real_custa_5_reais(self):
        ttask = 5
        usuário = Usuário(ttask=ttask)
        servidor = ServidorTipoUm(umax=1)
        servidor.adiciona_usuário(usuário)
        for _ in range(ttask):
            servidor.tick()
        assert servidor.custo() == 5

    def test_permite_no_maximo_umax_2_usuários(self):
        usuário1 = Usuário(ttask=2)
        usuário2 = Usuário(ttask=2)
        usuário3 = Usuário(ttask=2)
        servidor = ServidorTipoUm(umax=2)
        servidor.adiciona_usuário(usuário1)
        servidor.adiciona_usuário(usuário2)
        servidor.adiciona_usuário(usuário3)
        assert usuário1 in servidor.usuários
        assert usuário2 in servidor.usuários
        assert usuário3 not in servidor.usuários

    def test_na_comparação_o_maior_é_o_com_maior_ticks_a_processar(self):
        usuário1 = Usuário(1)
        usuário2 = Usuário(2)
        usuário3 = Usuário(3)
        usuário4 = Usuário(4)

        servidor1 = ServidorTipoUm(2)
        servidor1.adiciona_usuário(usuário1)
        servidor1.adiciona_usuário(usuário2)
        servidor2 = ServidorTipoUm(2)
        servidor2.adiciona_usuário(usuário3)
        servidor2.adiciona_usuário(usuário4)

        assert servidor2 > servidor1


def test_cria_usuário():
    assert isinstance(cria_usuário(1), Usuário)


def test_cria_servidor_tipo_um():
    assert isinstance(cria_servidor_tipo_um(1), Servidor)

def test_entrada_aleatória():
    assert isinstance(entrada_aleatória(), tuple)

class TestBalanceador:
    def test_carrega_entrada_válida(self):
        balanceador = Balanceador(
            partial(entrada_txt, path.join(
                path.dirname(__file__), 'input.txt')),
            cria_usuário,
            cria_servidor_tipo_um
        )
        assert balanceador._ttask == 4
        assert balanceador._umax == 2
        assert balanceador._numero_novos_usuários == [1, 3, 0, 1, 0, 1]

    def test_cria_usuario_servidor(self):
        balanceador = Balanceador(
            partial(entrada_txt, path.join(
                path.dirname(__file__), 'input_test.txt')),
            cria_usuário,
            cria_servidor_tipo_um
        )
        balanceador._associa_usuários_servidores(1)
        assert len(balanceador._servidores) == 1

    def test_cria_usuários_em_servidores(self):
        balanceador = Balanceador(
            partial(entrada_txt, path.join(
                path.dirname(__file__), 'input_test2.txt')),
            cria_usuário,
            cria_servidor_tipo_um
        )
        balanceador._associa_usuários_servidores(2)
        balanceador._associa_usuários_servidores(1)
        assert len(balanceador._servidores[0].usuários) == 2
        assert len(balanceador._servidores[1].usuários) == 1

    def test_servidor_removido_quando_finalizado(self):
        balanceador = Balanceador(
            partial(entrada_txt, path.join(
                path.dirname(__file__), 'input_test.txt')),
            cria_usuário,
            cria_servidor_tipo_um
        )
        balanceador.processa_tarefas()
        assert len(balanceador._servidores) == 0

    def test_processa_tarefas(self):
        balanceador = Balanceador(
            partial(entrada_txt, path.join(
                path.dirname(__file__), 'input.txt')),
            cria_usuário,
            cria_servidor_tipo_um
        )
        esperado = '1\n2,2\n2,2\n2,2,1\n1,2,1\n2\n2\n1\n1\n15'
        retorno = balanceador.processa_tarefas()
        assert retorno == esperado


def test_main():
    retorno = main(
        path.join(path.dirname(__file__), 'input.txt')
    )
    esperado = '1\n2,2\n2,2\n2,2,1\n1,2,1\n2\n2\n1\n1\n15'
    assert retorno == esperado
