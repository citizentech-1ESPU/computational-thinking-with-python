from datetime import datetime

import config
import regras


def test_decide_o_estado_com_a_prioridade_da_caixa():
    assert regras.decidir_estado(3.0, 0, 0.0) == 0
    assert regras.decidir_estado(6.0, 30, 0.0) == 1
    assert regras.decidir_estado(4.6, 30, 2.0) == 1      # passa de 5 °C em 12 min
    assert regras.decidir_estado(4.6, 30, 1.0) == 0      # só daqui a 24 min
    assert regras.decidir_estado(5.0, 0, 0.0) == 0       # 5 °C ainda não conta
    assert regras.decidir_estado(3.0, 120, 0.0) == 2
    assert regras.decidir_estado(7.8, 239, 1.2) == 2
    assert regras.decidir_estado(3.9, 240, -1.5) == 3
    assert regras.decidir_estado(100.0, 250, 0.0) == 4   # sem leitura vence tudo
    assert regras.decidir_estado(None, 0, 0.0) == 4


def test_minutos_ate_5c_so_quando_esquenta_abaixo_de_5():
    assert regras.minutos_ate_5c(4.6, 2.0) == 12
    assert regras.minutos_ate_5c(4.0, 3.0) == 20
    assert regras.minutos_ate_5c(4.6, -1.0) is None
    assert regras.minutos_ate_5c(6.0, 2.0) is None
    assert regras.minutos_ate_5c(3.0, 0.0) is None


def test_info_do_estado_traz_textos_e_cores():
    assert regras.info_do_estado(0) == ("normal", "Venda normal", "Pode vender tranquilo.", "#15803D", "#DCFCE7")
    assert regras.info_do_estado(1)[1] == "Complete o gelo"
    assert regras.info_do_estado(2)[2] == "Venda ou doe hoje. Não volta para a geladeira."
    assert regras.info_do_estado(3)[1] == "Descarte"
    assert regras.info_do_estado(4)[1] == "Sem leitura"
    assert regras.info_do_estado(7)[1] == "Sem leitura"


def test_codigo_do_texto():
    assert regras.codigo_do_texto("Hora da xepa") == 2
    assert regras.codigo_do_texto("Qualquer coisa") is None


def test_estado_da_leitura_confia_na_caixa():
    leitura = {"valida": True, "estado": 0, "temperatura": 7.8, "acumulado": 140, "taxa": 1.2}
    assert regras.estado_da_leitura(leitura) == 0
    leitura["estado"] = None
    assert regras.estado_da_leitura(leitura) == 2
    leitura["valida"] = False
    assert regras.estado_da_leitura(leitura) == 4


def test_preco_da_xepa_igual_ao_do_site():
    assert regras.preco_xepa_sugerido(39.9) == 29.9
    assert regras.preco_xepa_sugerido(10) == 7.5
    assert regras.preco_xepa_sugerido(12.5) == 9.3
    assert regras.preco_xepa_sugerido(18) == 13.5
    assert regras.preco_xepa_sugerido(2.8) == 2.1
    assert regras.preco_xepa_sugerido(34) == 25.5
    assert regras.preco_xepa_sugerido(0) is None
    assert regras.preco_xepa_sugerido(-5) is None


def test_proxima_feira_em_quinta_ou_domingo():
    fuso = config.FUSO_SAO_PAULO
    assert regras.proxima_feira(datetime(2026, 11, 9, 10, 0, tzinfo=fuso)).isoformat() == "2026-11-12"
    assert regras.proxima_feira(datetime(2026, 11, 12, 8, 0, tzinfo=fuso)).isoformat() == "2026-11-12"
    assert regras.proxima_feira(datetime(2026, 11, 12, 15, 0, tzinfo=fuso)).isoformat() == "2026-11-15"
