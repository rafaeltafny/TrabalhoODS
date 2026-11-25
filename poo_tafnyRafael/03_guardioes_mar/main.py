from abc import ABC, abstractmethod
from enum import Enum


class NivelAlerta(Enum):
    MODERADO = 1
    ALTO = 2
    EMERGENCIA_AMBIENTAL = 3


class AgenteCosteiro(ABC):
    def __init__(self, aid: int, nome: str, organizacao: str):
        self._aid = aid
        self._nome = nome.strip()
        self._organizacao = organizacao.strip()

    @property
    def aid(self) -> int:
        return self._aid

    @property
    def nome(self) -> str:
        return self._nome

    @abstractmethod
    def credencial(self) -> str:
        pass

    @abstractmethod
    def resumo(self) -> str:
        pass


class VoluntarioPraia(AgenteCosteiro):
    def __init__(self, aid: int, nome: str, organizacao: str):
        super().__init__(aid, nome, organizacao)
        self._mutiroes = 0

    def registrar_mutirao(self) -> None:
        self._mutiroes += 1

    def credencial(self) -> str:
        return "Voluntário Costeiro"

    def resumo(self) -> str:
        return f"[{self.credencial()}] {self._nome} ({self._organizacao}) | Ações: {self._mutiroes}"


class BiologoMarinho(AgenteCosteiro):
    def __init__(self, aid: int, nome: str, organizacao: str, crbio: str):
        super().__init__(aid, nome, organizacao)
        self._crbio = crbio.strip()
        self._validacoes = 0

    def validar_alerta(self) -> None:
        self._validacoes += 1

    def credencial(self) -> str:
        return f"Biólogo Marinho (CRBio {self._crbio})"

    def resumo(self) -> str:
        return f"[{self.credencial()}] {self._nome} | Laudos validados: {self._validacoes}"


class ZonaCosteira:
    def __init__(self, zid: str, praia: str, area_protegida: bool):
        self._zid = zid.strip()
        self._praia = praia.strip()
        self._area_protegida = bool(area_protegida)

    @property
    def area_protegida(self) -> bool:
        return self._area_protegida

    def __str__(self) -> str:
        tag = "APA Marinha" if self._area_protegida else "Zona Costeira"
        return f"{self._praia} [{tag}]"


class RegistroMarinho(ABC):
    def __init__(self, rid: str, autor: AgenteCosteiro, zona: ZonaCosteira, nivel_alerta: NivelAlerta):
        self._rid = rid
        self._autor = autor
        self._zona = zona
        self._nivel_alerta = nivel_alerta
        self._escalado = False

    @property
    def rid(self) -> str:
        return self._rid

    @property
    def zona(self) -> ZonaCosteira:
        return self._zona

    def escalar_autoridade(self) -> None:
        self._escalado = True

    @abstractmethod
    def tipo_registro(self) -> str:
        pass

    @abstractmethod
    def indice_risco_ecologico(self) -> int:
        pass

    @abstractmethod
    def acao_recomendada(self) -> str:
        pass


class ColetaResiduoPraia(RegistroMarinho):
    def __init__(self, rid: str, autor: AgenteCosteiro, zona: ZonaCosteira, nivel_alerta: NivelAlerta,
                 peso_plastico_kg: float, redes_fantasma: int):
        super().__init__(rid, autor, zona, nivel_alerta)
        self._peso_plastico_kg = float(peso_plastico_kg)
        self._redes_fantasma = int(redes_fantasma)

    def tipo_registro(self) -> str:
        return "Mutirão de Limpeza / Redes Fantasma"

    def indice_risco_ecologico(self) -> int:
        base = int(self._peso_plastico_kg * 0.5) + (self._redes_fantasma * 25)
        return base + (20 if self._zona.area_protegida else 0)

    def acao_recomendada(self) -> str:
        return f"Destinar {self._peso_plastico_kg:.1f}kg à cooperativa de reciclagem e mergulho de remoção para {self._redes_fantasma} rede(s)."


class AlertaPescaIlegal(RegistroMarinho):
    def __init__(self, rid: str, autor: AgenteCosteiro, zona: ZonaCosteira, nivel_alerta: NivelAlerta,
                 embarcacoes_avistadas: int, petrecho_proibido: bool):
        super().__init__(rid, autor, zona, nivel_alerta)
        self._embarcacoes_avistadas = int(embarcacoes_avistadas)
        self._petrecho_proibido = bool(petrecho_proibido)

    def tipo_registro(self) -> str:
        return "Denúncia de Pesca Predatória/Ilegal"

    def indice_risco_ecologico(self) -> int:
        base = self._nivel_alerta.value * 30 + self._embarcacoes_avistadas * 15
        if self._petrecho_proibido:
            base += 35
        if self._zona.area_protegida:
            base += 25
        return base

    def acao_recomendada(self) -> str:
        return "Acionar patrulhamento naval imediato da Capitania dos Portos e fiscalização do IBAMA."


class OficioAmbiental:
    def __init__(self, numero_oficio: str, registro: RegistroMarinho, orgao_destino: str):
        self._numero_oficio = numero_oficio
        self._registro = registro
        self._orgao_destino = orgao_destino.strip()
        self._registro.escalar_autoridade()

    def resumo(self) -> str:
        return f"Ofício {self._numero_oficio} -> {self._orgao_destino} | Ref: {self._registro.rid} ({self._registro.zona}) | Risco: {self._registro.indice_risco_ecologico()}"


class CentralGuardioesMar:
    def __init__(self, litoral: str):
        self._litoral = litoral
        self._agentes: dict[int, AgenteCosteiro] = {}
        self._zonas: dict[str, ZonaCosteira] = {}
        self._registros: list[RegistroMarinho] = []
        self._oficios: list[OficioAmbiental] = []

    def cadastrar_agente(self, a: AgenteCosteiro) -> AgenteCosteiro:
        self._agentes[a.aid] = a
        return a

    def cadastrar_zona(self, z: ZonaCosteira) -> ZonaCosteira:
        self._zonas[z._zid] = z
        return z

    def registrar_ocorrencia(self, r: RegistroMarinho) -> RegistroMarinho:
        self._registros.append(r)
        if isinstance(r._autor, VoluntarioPraia):
            r._autor.registrar_mutirao()
        elif isinstance(r._autor, BiologoMarinho):
            r._autor.validar_alerta()
        return r

    def emitir_oficio(self, num: str, rid: str, orgao: str) -> OficioAmbiental:
        reg = next(r for r in self._registros if r.rid == rid)
        of = OficioAmbiental(num, reg, orgao)
        self._oficios.append(of)
        return of

    def gerar_boletim_marinho(self) -> str:
        ordenados = sorted(self._registros, key=lambda r: r.indice_risco_ecologico(), reverse=True)
        linhas = [
            f"=== BOLETIM AMBIENTAL - GUARDIÕES DO MAR ({self._litoral}) ===",
            f"Ocorrências costeiras: {len(self._registros)} | Ofícios enviados às autoridades: {len(self._oficios)}",
            "--- Prioridade Ecológica ---"
        ]
        for r in ordenados:
            linhas.append(f"  * [{r.rid}] {r.tipo_registro()} em {r.zona} | Risco: {r.indice_risco_ecologico()} | Ação: {r.acao_recomendada()}")
        return "\n".join(linhas)


def executar_demo():
    central = CentralGuardioesMar("Litoral Sul - Costa dos Corais")
    v1 = central.cadastrar_agente(VoluntarioPraia(1, "Tafny Rafael", "ONG Mar Limpo"))
    b1 = central.cadastrar_agente(BiologoMarinho(2, "Dr. Henrique Costa", "Instituto Recifes", "CRBio-05 8821"))

    z1 = central.cadastrar_zona(ZonaCosteira("Z1", "Praia de Tamandaré", True))
    z2 = central.cadastrar_zona(ZonaCosteira("Z2", "Praia do Paiva", False))

    r1 = central.registrar_ocorrencia(ColetaResiduoPraia("MAR-01", v1, z2, NivelAlerta.MODERADO, 142.5, 2))
    r2 = central.registrar_ocorrencia(AlertaPescaIlegal("MAR-02", b1, z1, NivelAlerta.EMERGENCIA_AMBIENTAL, 3, True))

    of1 = central.emitir_oficio("OF-2026/89", "MAR-02", "IBAMA / Marinha do Brasil")
    print("=== OFÍCIO DE FISCALIZAÇÃO GERADO ===")
    print(of1.resumo())
    print("\n" + central.gerar_boletim_marinho())


if __name__ == "__main__":
    executar_demo()
