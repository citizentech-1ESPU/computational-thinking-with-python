import os

import config


def test_regras_iguais_as_da_caixa_e_do_site():
    assert config.LIMITE_FRIO_C == 5.0
    assert config.XEPA_APOS_MIN == 120
    assert config.DESCARTE_APOS_MIN == 240
    assert config.AVISO_GELO_MIN == 15
    assert (config.TEMP_MIN_VALIDA_C, config.TEMP_MAX_VALIDA_C) == (-30.0, 60.0)
    assert config.FIM_DA_FEIRA == "14:00"
    assert config.DESCONTO_XEPA == 0.25


def test_banca_e_gelo():
    assert config.DIAS_DE_FEIRA == (3, 6)
    assert config.HORA_DE_ENCHER_AS_CAIXAS == "05:30"
    assert config.CONSTANTE_GELO_PADRAO == 2500.0


def test_dados_ficam_ao_lado_do_programa():
    assert os.path.isabs(config.PASTA_DADOS)
    assert os.path.dirname(config.PASTA_DADOS) == config.PASTA_DO_PROGRAMA
    assert os.path.exists(os.path.join(config.PASTA_DO_PROGRAMA, "config.py"))
