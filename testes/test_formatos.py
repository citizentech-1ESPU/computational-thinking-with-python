from datetime import date, datetime, timezone

import formatos


def test_le_numero_do_jeito_brasileiro():
    assert formatos.ler_numero("3,5", 0, 100) == (3.5, None)
    assert formatos.ler_numero(" 3.5 ", 0, 100) == (3.5, None)
    assert formatos.ler_numero("R$ 39,90", 0, 1000) == (39.9, None)
    assert formatos.ler_numero("1.234,56", 0, 5000) == (1234.56, None)
    assert formatos.ler_numero("", 0, 100, vazio=0.0) == (0.0, None)


def test_le_numero_com_mensagens_de_erro():
    assert formatos.ler_numero("", 0, 100) == (None, "Preencha este campo.")
    assert formatos.ler_numero("abc", 0, 100) == (None, "Digite um número, como 3,5.")
    assert formatos.ler_numero("50", 0.5, 30) == (None, "Use um número entre 0,5 e 30.")
    assert formatos.ler_numero("nan", 0, 100)[0] is None


def test_le_data():
    hoje = date(2026, 11, 15)
    assert formatos.ler_data("15/11/2026", hoje) == (date(2026, 11, 15), None)
    assert formatos.ler_data("", hoje) == (None, "Preencha este campo.")
    assert formatos.ler_data("2026-11-15", hoje) == (None, "Use o formato dd/mm/aaaa, como 15/11/2026.")
    assert formatos.ler_data("16/11/2026", hoje) == (None, "A data não pode ser no futuro.")


def test_le_hora():
    assert formatos.ler_hora("11h40") == ("11:40", None)
    assert formatos.ler_hora(" 9:05 ") == ("09:05", None)
    assert formatos.ler_hora("11h") == ("11:00", None)
    assert formatos.ler_hora("25:00") == (None, "Use o formato 11:40 ou 11h40.")
    assert formatos.ler_hora("") == (None, "Preencha este campo.")
    assert formatos.ler_hora("", obrigatoria=False) == (None, None)


def test_formata_como_o_site():
    assert formatos.formatar_reais(29.9) == "R$ 29,90"
    assert formatos.formatar_reais(1234.5) == "R$ 1.234,50"
    assert formatos.formatar_kg(3) == "3 kg"
    assert formatos.formatar_kg(2.5) == "2,5 kg"
    assert formatos.formatar_kg(3.456) == "3,5 kg"
    assert formatos.formatar_temperatura(4.6) == "4,6 °C"
    assert formatos.formatar_temperatura(None) == "--"
    assert formatos.formatar_numero(0.5) == "0,5"
    assert formatos.formatar_numero(30.0) == "30"
    assert formatos.formatar_numero(0.01) == "0,01"
    assert formatos.formatar_duracao(0) == "0 min"
    assert formatos.formatar_duracao(45) == "45 min"
    assert formatos.formatar_duracao(60) == "1h"
    assert formatos.formatar_duracao(140) == "2h20"
    assert formatos.formatar_duracao(245) == "4h05"


def test_horas_e_datas_em_sao_paulo():
    assert formatos.formatar_hora(datetime(2026, 11, 15, 16, 50, tzinfo=timezone.utc)) == "13h50"
    assert formatos.formatar_hora(datetime(2026, 11, 16, 3, 0, tzinfo=timezone.utc)) == "00h00"
    assert formatos.hora_curta("11:40") == "11h40"
    assert formatos.minutos_do_dia("05:30") == 330
    assert formatos.hora_do_dia(733) == "12:13"
    assert formatos.formatar_data(date(2026, 11, 8)) == "08/11/2026"
    assert formatos.formatar_dia(date(2026, 11, 8)) == "domingo, 08/11"


def test_saudacao():
    assert formatos.saudacao(6) == "Bom dia!"
    assert formatos.saudacao(13) == "Boa tarde!"
    assert formatos.saudacao(20) == "Boa noite!"
    assert formatos.saudacao(3) == "Boa noite!"
