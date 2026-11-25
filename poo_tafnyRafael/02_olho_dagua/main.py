from abc import ABC, abstractmethod
from enum import Enum


class NivelUrgencia(Enum):
    BAIXA = 1
    MEDIA = 2
    CRITICA = 3


class UsuarioHidrico(ABC):
    def __init__(self, uid: int, nome: str, comunidade: str):
        self._uid = uid
        self._nome = nome.strip()
        self._comunidade = comunidade.strip()

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def nome(self) -> str:
        return self._nome

    @abstractmethod
    def perfil(self) -> str:
        pass

    @abstractmethod
    def resumo(self) -> str:
        pass


class MonitorComunitario(UsuarioHidrico):
    def __init__(self, uid: int, nome: str, comunidade: str):
        super().__init__(uid, nome, comunidade)
        self._coletas_realizadas = 0

    def registrar_coleta(self) -> None:
        self._coletas_realizadas += 1

    def perfil(self) -> str:
        return "Monitor Comunitário"

    def resumo(self) -> str:
        return f"[{self.perfil()}] {self._nome} ({self._comunidade}) | Registros: {self._coletas_realizadas}"


class TecnicoSaneamento(UsuarioHidrico):
    def __init__(self, uid: int, nome: str, comunidade: str, crea: str):
        super().__init__(uid, nome, comunidade)
        self._crea = crea.strip()
        self._ordens_emitidas = 0

    def emitir_parecer(self) -> None:
        self._ordens_emitidas += 1

    def perfil(self) -> str:
        return f"Técnico em Saneamento (CREA {self._crea})"

    def resumo(self) -> str:
        return f"[{self.perfil()}] {self._nome} | Ordens emitidas: {self._ordens_emitidas}"


class PontoManancial:
    def __init__(self, mid: str, nome_fonte: str, familias_atendidas: int):
        self._mid = mid.strip()
        self._nome_fonte = nome_fonte.strip()
        self._familias_atendidas = int(familias_atendidas)

    @property
    def familias_atendidas(self) -> int:
        return self._familias_atendidas

    def __str__(self) -> str:
        return f"{self._nome_fonte} ({self._familias_atendidas} famílias)"


class RelatoHidrico(ABC):
    def __init__(self, rid: str, autor: UsuarioHidrico, manancial: PontoManancial, urgencia: NivelUrgencia):
        self._rid = rid
        self._autor = autor
        self._manancial = manancial
        self._urgencia = urgencia
        self._atendido = False

    @property
    def rid(self) -> str:
        return self._rid

    @property
    def manancial(self) -> PontoManancial:
        return self._manancial

    def marcar_atendido(self) -> None:
        self._atendido = True

    @abstractmethod
    def categoria(self) -> str:
        pass

    @abstractmethod
    def indice_risco_sanitario(self) -> int:
        pass

    @abstractmethod
    def protocolo_tratamento(self) -> str:
        pass


class AnaliseQualidadeAgua(RelatoHidrico):
    def __init__(self, rid: str, autor: UsuarioHidrico, manancial: PontoManancial, urgencia: NivelUrgencia,
                 turbidez_ntu: float, coliformes_presentes: bool):
        super().__init__(rid, autor, manancial, urgencia)
        self._turbidez_ntu = float(turbidez_ntu)
        self._coliformes_presentes = bool(coliformes_presentes)

    def categoria(self) -> str:
        return "Análise de Potabilidade"

    def indice_risco_sanitario(self) -> int:
        risco = int(self._turbidez_ntu * 4) + (45 if self._coliformes_presentes else 0)
        return min(100, risco + (10 if self._manancial.familias_atendidas > 100 else 0))

    def protocolo_tratamento(self) -> str:
        if self._coliformes_presentes:
            return "Suspender consumo direto, distribuir hipoclorito de sódio e desinfetar reservatório."
        return "Realizar filtração lenta em areia e monitorar turbidez em 48h."


class VazamentoEsgoto(RelatoHidrico):
    def __init__(self, rid: str, autor: UsuarioHidrico, manancial: PontoManancial, urgencia: NivelUrgencia,
                 vazao_estimada_ls: float, proximo_nascente: bool):
        super().__init__(rid, autor, manancial, urgencia)
        self._vazao_estimada_ls = float(vazao_estimada_ls)
        self._proximo_nascente = bool(proximo_nascente)

    def categoria(self) -> str:
        return "Contaminação / Vazamento de Esgoto"

    def indice_risco_sanitario(self) -> int:
        risco = self._urgencia.value * 25 + int(self._vazao_estimada_ls * 6)
        if self._proximo_nascente:
            risco += 30
        return min(100, risco)

    def protocolo_tratamento(self) -> str:
        return "Isolar área da nascente, acionar caminhão hidrojato da companhia de saneamento e conter efluente."


class OrdemSaneamento:
    def __init__(self, protocolo: str, relato: RelatoHidrico, equipe_destino: str):
        self._protocolo = protocolo
        self._relato = relato
        self._equipe_destino = equipe_destino.strip()
        self._relato.marcar_atendido()

    def resumo(self) -> str:
        return f"Ordem {self._protocolo} -> {self._equipe_destino} | Ref: {self._relato.rid} ({self._relato.manancial}) | Risco: {self._relato.indice_risco_sanitario()}/100"


class PlataformaOlhoDAgua:
    def __init__(self, bacia_hidrografica: str):
        self._bacia_hidrografica = bacia_hidrografica
        self._usuarios: dict[int, UsuarioHidrico] = {}
        self._mananciais: dict[str, PontoManancial] = {}
        self._relatos: list[RelatoHidrico] = []
        self._ordens: list[OrdemSaneamento] = []

    def cadastrar_usuario(self, u: UsuarioHidrico) -> UsuarioHidrico:
        self._usuarios[u.uid] = u
        return u

    def cadastrar_manancial(self, m: PontoManancial) -> PontoManancial:
        self._mananciais[m._mid] = m
        return m

    def registrar_relato(self, r: RelatoHidrico) -> RelatoHidrico:
        self._relatos.append(r)
        if isinstance(r._autor, MonitorComunitario):
            r._autor.registrar_coleta()
        elif isinstance(r._autor, TecnicoSaneamento):
            r._autor.emitir_parecer()
        return r

    def gerar_ordem_saneamento(self, protocolo: str, rid: str, equipe: str) -> OrdemSaneamento:
        rel = next(r for r in self._relatos if r.rid == rid)
        ordem = OrdemSaneamento(protocolo, rel, equipe)
        self._ordens.append(ordem)
        return ordem

    def boletim_hidrico(self) -> str:
        ordenados = sorted(self._relatos, key=lambda r: r.indice_risco_sanitario(), reverse=True)
        linhas = [
            f"=== BOLETIM HÍDRICO - OLHO D'ÁGUA ({self._bacia_hidrografica}) ===",
            f"Ocorrências hídricas: {len(self._relatos)} | Ordens de saneamento emitidas: {len(self._ordens)}",
            "--- Prioridade Sanitária (Polimorfismo) ---"
        ]
        for r in ordenados:
            linhas.append(f"  * [{r.rid}] {r.categoria()} em {r.manancial} | Risco: {r.indice_risco_sanitario()}/100 | Protocolo: {r.protocolo_tratamento()}")
        return "\n".join(linhas)


def executar_demo():
    plat = PlataformaOlhoDAgua("Bacia do Rio Capibaribe")
    m1 = plat.cadastrar_usuario(MonitorComunitario(1, "Tafny Rafael", "Comunidade Vila Verde"))
    t1 = plat.cadastrar_usuario(TecnicoSaneamento(2, "Eng. Camila Mendes", "Defesa Civil / COMPESA", "CREA-PE 44190"))

    f1 = plat.cadastrar_manancial(PontoManancial("M1", "Nascente Olho d'Água do Alto", 180))
    f2 = plat.cadastrar_manancial(PontoManancial("M2", "Poço Comunitário São José", 75))

    r1 = plat.registrar_relato(AnaliseQualidadeAgua("H2O-01", m1, f2, NivelUrgencia.MEDIA, 8.5, True))
    r2 = plat.registrar_relato(VazamentoEsgoto("H2O-02", t1, f1, NivelUrgencia.CRITICA, 4.0, True))

    ord1 = plat.gerar_ordem_saneamento("OS-2026/14", "H2O-02", "Equipe Emergencial de Saneamento")
    print("=== ORDEM DE SANEAMENTO GERADA ===")
    print(ord1.resumo())
    print("\n" + plat.boletim_hidrico())


if __name__ == "__main__":
    executar_demo()
