from abc import ABC, abstractmethod
from enum import Enum


class StatusMentoria(Enum):
    SOLICITADA = "SOLICITADA"
    CONCLUIDA = "CONCLUIDA"


class MembroHub(ABC):
    def __init__(self, mid: int, nome: str, cidade: str):
        self._mid = mid
        self._nome = nome.strip()
        self._cidade = cidade.strip()

    @property
    def mid(self) -> int:
        return self._mid

    @property
    def nome(self) -> str:
        return self._nome

    @abstractmethod
    def papel(self) -> str:
        pass

    @abstractmethod
    def resumo(self) -> str:
        pass


class Artesao(MembroHub):
    def __init__(self, mid: int, nome: str, cidade: str, cooperativa: str):
        super().__init__(mid, nome, cidade)
        self._cooperativa = cooperativa.strip()
        self._receita_acumulada = 0.0

    def creditar_venda(self, valor: float) -> None:
        if valor > 0:
            self._receita_acumulada += float(valor)

    def papel(self) -> str:
        return "Artesão Produtor"

    def resumo(self) -> str:
        return f"[{self.papel()}] {self._nome} ({self._cooperativa}) | Receita direta: R$ {self._receita_acumulada:,.2f}"


class DesignerVoluntario(MembroHub):
    def __init__(self, mid: int, nome: str, cidade: str, especialidade: str):
        super().__init__(mid, nome, cidade)
        self._especialidade = especialidade.strip()
        self._mentorias_concluidas = 0

    def concluir_mentoria(self) -> None:
        self._mentorias_concluidas += 1

    def papel(self) -> str:
        return "Designer Voluntário"

    def resumo(self) -> str:
        return f"[{self.papel()}] {self._nome} ({self._especialidade}) | Mentorias: {self._mentorias_concluidas}"


class ProdutoArtesanal(ABC):
    def __init__(self, sku: str, titulo: str, artesao: Artesao, custo_material: float, horas_trabalho: float):
        self._sku = sku
        self._titulo = titulo.strip()
        self._artesao = artesao
        self._custo_material = float(custo_material)
        self._horas_trabalho = float(horas_trabalho)
        self._fator_design = 1.0

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def artesao(self) -> Artesao:
        return self._artesao

    def aplicar_selo_design(self, multiplicador: float = 1.25) -> None:
        self._fator_design = max(1.0, float(multiplicador))

    @abstractmethod
    def categoria(self) -> str:
        pass

    @abstractmethod
    def calcular_preco_justo(self) -> float:
        pass

    @abstractmethod
    def impacto_cultural(self) -> str:
        pass


class PecaCeramica(ProdutoArtesanal):
    def __init__(self, sku: str, titulo: str, artesao: Artesao, custo_material: float, horas_trabalho: float, queima_forno_horas: float):
        super().__init__(sku, titulo, artesao, custo_material, horas_trabalho)
        self._queima_forno_horas = float(queima_forno_horas)

    def categoria(self) -> str:
        return "Cerâmica Tradicional"

    def calcular_preco_justo(self) -> float:
        base = self._custo_material + (self._horas_trabalho * 28.0) + (self._queima_forno_horas * 6.5)
        return round(base * self._fator_design, 2)

    def impacto_cultural(self) -> str:
        return "Preserva técnicas ancestrais de modelagem em barro e queima artesanal."


class TecelagemManual(ProdutoArtesanal):
    def __init__(self, sku: str, titulo: str, artesao: Artesao, custo_material: float, horas_trabalho: float, fibra_natural: str):
        super().__init__(sku, titulo, artesao, custo_material, horas_trabalho)
        self._fibra_natural = fibra_natural.strip()

    def categoria(self) -> str:
        return "Tecelagem em Fibra Natural"

    def calcular_preco_justo(self) -> float:
        base = self._custo_material + (self._horas_trabalho * 32.0) + 15.0
        return round(base * self._fator_design, 2)

    def impacto_cultural(self) -> str:
        return f"Manejo sustentável de {self._fibra_natural} com tear manual comunitário."


class ConsultoriaDesign:
    def __init__(self, cid: str, produto: ProdutoArtesanal, designer: DesignerVoluntario):
        self._cid = cid
        self._produto = produto
        self._designer = designer
        self._status = StatusMentoria.SOLICITADA

    def aplicar_melhoria(self, fator_valorizacao: float = 1.30) -> None:
        if self._status == StatusMentoria.CONCLUIDA:
            raise ValueError("Consultoria já concluída.")
        self._produto.aplicar_selo_design(fator_valorizacao)
        self._designer.concluir_mentoria()
        self._status = StatusMentoria.CONCLUIDA


class PedidoVenda:
    def __init__(self, numero_pedido: str, produto: ProdutoArtesanal, quantidade: int):
        self._numero_pedido = numero_pedido
        self._produto = produto
        self._quantidade = int(quantidade)
        self._valor_total = round(self._produto.calcular_preco_justo() * self._quantidade, 2)
        self._produto.artesao.creditar_venda(self._valor_total)

    def resumo(self) -> str:
        return f"Pedido {self._numero_pedido}: {self._quantidade}x '{self._produto.titulo}' -> Repasse integral: R$ {self._valor_total:,.2f}"


class HubArtesaoDigital:
    def __init__(self, comunidade: str):
        self._comunidade = comunidade
        self._membros: dict[int, MembroHub] = {}
        self._produtos: dict[str, ProdutoArtesanal] = {}
        self._pedidos: list[PedidoVenda] = []

    def cadastrar_membro(self, m: MembroHub) -> MembroHub:
        self._membros[m.mid] = m
        return m

    def publicar_produto(self, p: ProdutoArtesanal) -> ProdutoArtesanal:
        self._produtos[p.sku] = p
        return p

    def executar_consultoria(self, cid: str, sku: str, designer_id: int, fator: float = 1.30) -> ConsultoriaDesign:
        des = self._membros[designer_id]
        if not isinstance(des, DesignerVoluntario):
            raise TypeError("Membro não é designer voluntário.")
        cons = ConsultoriaDesign(cid, self._produtos[sku], des)
        cons.aplicar_melhoria(fator)
        return cons

    def registrar_venda(self, numero: str, sku: str, qtd: int) -> PedidoVenda:
        ped = PedidoVenda(numero, self._produtos[sku], qtd)
        self._pedidos.append(ped)
        return ped

    def relatorio_economia_criativa(self) -> str:
        total_vendas = sum(p._valor_total for p in self._pedidos)
        linhas = [
            f"=== RELATÓRIO ECONOMIA CRIATIVA - HUB ARTESÃO DIGITAL ({self._comunidade}) ===",
            f"Volume comercializado (100% repassado aos artesãos): R$ {total_vendas:,.2f}",
            "--- Catálogo ---"
        ]
        for prod in self._produtos.values():
            linhas.append(f"  * [{prod.sku}] {prod.titulo} ({prod.categoria()}) | Preço Justo: R$ {prod.calcular_preco_justo():,.2f} | {prod.impacto_cultural()}")
        linhas.append("--- Membros ---")
        for m in self._membros.values():
            linhas.append(f"  * {m.resumo()}")
        return "\n".join(linhas)


def executar_demo():
    hub = HubArtesaoDigital("Vale do Cariri & Agreste")
    a1 = hub.cadastrar_membro(Artesao(1, "Dona Maria do Barro", "Tracunhaém - PE", "Coop. Mulheres Ceramistas"))
    a2 = hub.cadastrar_membro(Artesao(2, "José de Assis", "Caruaru - PE", "Associação Tear Vivo"))
    d1 = hub.cadastrar_membro(DesignerVoluntario(3, "Tafny Rafael", "Recife - PE", "Branding e Embalagens Sustentáveis"))

    p1 = hub.publicar_produto(PecaCeramica("CER-01", "Moringa Esculpida", a1, 18.0, 4.5, 8.0))
    p2 = hub.publicar_produto(TecelagemManual("TEC-02", "Rede de Algodão Agroecológico", a2, 45.0, 10.0, "Algodão Orgânico"))

    print(f"Preço inicial '{p1.titulo}': R$ {p1.calcular_preco_justo():.2f}")
    hub.executar_consultoria("CONS-01", "CER-01", d1.mid, fator=1.30)
    print(f"Preço após Selo Design '{p1.titulo}': R$ {p1.calcular_preco_justo():.2f}")

    ped1 = hub.registrar_venda("PED-101", "CER-01", 3)
    ped2 = hub.registrar_venda("PED-102", "TEC-02", 2)
    print("\n" + ped1.resumo())
    print(ped2.resumo())
    print("\n" + hub.relatorio_economia_criativa())


if __name__ == "__main__":
    executar_demo()
