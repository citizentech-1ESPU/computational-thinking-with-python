from datetime import datetime, timezone

import config
import internet
import thingspeak

FEED = {"created_at": "2026-11-15T15:10:00Z", "entry_id": 42, "field1": "7.8", "field2": "140",
        "field3": "2", "field4": "1.2", "field5": "100"}
CAIXA_COM_SENSOR = {"id": "caixa-1", "nome": "Tilápia", "gelo_padrao_kg": 5.0, "canal": "123"}
CAIXA_SEM_SENSOR = {"id": "caixa-2", "nome": "Queijo", "gelo_padrao_kg": 4.0, "canal": ""}
AGORA = datetime(2026, 11, 15, 12, 30, tzinfo=config.FUSO_SAO_PAULO)


def test_interpreta_o_feed_como_o_site():
    assert thingspeak.interpretar_feed(FEED) == {
        "quando": datetime(2026, 11, 15, 15, 10, tzinfo=timezone.utc),
        "temperatura": 7.8, "acumulado": 140, "estado": 2, "taxa": 1.2, "restantes": 100, "valida": True,
    }
    assert thingspeak.interpretar_feed(-1) is None
    assert thingspeak.interpretar_feed("-1") is None
    assert thingspeak.interpretar_feed({}) is None


def test_marca_leitura_invalida():
    trocas = (("field1", "999"), ("field1", "abc"), ("field1", None), ("field3", "7"),
              ("field2", "-5"), ("field4", "nan"))
    for campo, valor in trocas:
        feed = dict(FEED)
        feed[campo] = valor
        assert thingspeak.interpretar_feed(feed)["valida"] is False


def test_leitura_antiga_depois_de_2_minutos():
    agora = datetime(2026, 11, 15, 15, 10, tzinfo=timezone.utc)
    assert thingspeak.leitura_antiga(datetime(2026, 11, 15, 15, 8, tzinfo=timezone.utc), agora) is False
    assert thingspeak.leitura_antiga(datetime(2026, 11, 15, 15, 7, 59, tzinfo=timezone.utc), agora) is True
    assert thingspeak.leitura_antiga(None, agora) is True


def test_busca_os_feeds_do_canal(monkeypatch):
    pedidos = []
    def baixar_falso(url, parametros):
        pedidos.append((url, parametros))
        return {"channel": {"id": 123}, "feeds": [FEED, FEED]}, None
    monkeypatch.setattr(internet, "baixar_json", baixar_falso)
    feeds, erro = thingspeak.buscar_feeds("123")
    assert erro is None and len(feeds) == 2
    assert pedidos == [("https://api.thingspeak.com/channels/123/feeds.json", {"results": 2000})]


def test_canal_errado_ou_fechado(monkeypatch):
    def baixar_404(url, parametros):
        return None, internet.NAO_ENCONTRADO
    monkeypatch.setattr(internet, "baixar_json", baixar_404)
    assert thingspeak.buscar_feeds("999") == ([], "Canal do ThingSpeak não encontrado. Confira o número em Caixas e produtos.")

    def baixar_menos_um(url, parametros):
        return -1, None
    monkeypatch.setattr(internet, "baixar_json", baixar_menos_um)
    assert thingspeak.buscar_feeds("123") == ([], "O canal do ThingSpeak não está aberto para leitura. Confira se ele é público.")


def test_sem_internet_usa_as_leituras_salvas(monkeypatch):
    cache = {}
    def baixar_ok(url, parametros):
        return {"channel": {}, "feeds": [FEED]}, None
    monkeypatch.setattr(internet, "baixar_json", baixar_ok)
    leituras, aviso = thingspeak.leituras_da_caixa(CAIXA_COM_SENSOR, cache, AGORA)
    assert len(leituras) == 1 and aviso is None
    assert cache["123"]["salvo_em"] == AGORA.isoformat()

    def baixar_sem_conexao(url, parametros):
        return None, "Sem conexão com o servidor. Tente de novo."
    monkeypatch.setattr(internet, "baixar_json", baixar_sem_conexao)
    leituras, aviso = thingspeak.leituras_da_caixa(CAIXA_COM_SENSOR, cache, AGORA)
    assert len(leituras) == 1
    assert aviso == "Sem conexão com o servidor. Tente de novo. Mostrando as leituras salvas de domingo, 15/11 às 12h30."
    assert thingspeak.leituras_da_caixa(CAIXA_COM_SENSOR, {}, AGORA) == ([], "Sem conexão com o servidor. Tente de novo.")


def test_caixa_sem_canal_nem_tenta():
    assert thingspeak.leituras_da_caixa(CAIXA_SEM_SENSOR, {}, AGORA) == (
        [], "Sem sensor ligado. Coloque o número do canal em Caixas e produtos.")


def test_situacao_para_o_cartao():
    leitura = thingspeak.interpretar_feed(FEED)
    agora_ao_vivo = datetime(2026, 11, 15, 15, 11, tzinfo=timezone.utc)
    cartao = thingspeak.situacao_da_caixa(CAIXA_COM_SENSOR, [leitura], None, agora_ao_vivo)
    assert (cartao["texto"], cartao["temperatura"]) == ("Hora da xepa", "7,8 °C")
    assert cartao["detalhe"] == "Fora do frio: 2h20 · Restam 1h40"
    assert cartao["mensagem"] == ""
    cartao = thingspeak.situacao_da_caixa(CAIXA_COM_SENSOR, [leitura], None, AGORA.replace(hour=13))
    assert cartao["mensagem"] == "Sem leitura recente da caixa (última às 12h10). Confira a conexão."
    cartao = thingspeak.situacao_da_caixa(CAIXA_COM_SENSOR, [], None, AGORA)
    assert (cartao["texto"], cartao["mensagem"]) == ("Sem leitura", "Ainda não chegou nenhuma leitura desta caixa.")
    cartao = thingspeak.situacao_da_caixa(CAIXA_SEM_SENSOR, [], "Sem sensor ligado.", AGORA)
    assert (cartao["tem_sensor"], cartao["texto"], cartao["temperatura"]) == (False, "Sem sensor", "--")
