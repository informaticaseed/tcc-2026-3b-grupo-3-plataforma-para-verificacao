"""
Testes automáticos — TCC em Grupo
LTP3 + QP3 · CEMIC 2026 · Prof. Rafael Martins Alves

4 testes × 25 pontos = 100 pontos
NÃO EDITE ESTE ARQUIVO.
"""
import os
import re
import glob
import subprocess
from datetime import datetime, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _commits_semana():
    """Retorna dict {autor: quantidade} dos últimos 7 dias."""
    desde = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        r = subprocess.run(
            ["git", "log", f"--after={desde}", "--pretty=format:%an"],
            capture_output=True, text=True, cwd=RAIZ, timeout=15
        )
        autores = [l.strip() for l in r.stdout.splitlines()
                   if l.strip() and "github-classroom" not in l.lower()]
        contagem = {}
        for a in autores:
            contagem[a] = contagem.get(a, 0) + 1
        return contagem
    except Exception:
        return {}


def _total_commits():
    """Retorna dict {autor: quantidade} de todos os commits."""
    try:
        r = subprocess.run(
            ["git", "log", "--pretty=format:%an"],
            capture_output=True, text=True, cwd=RAIZ, timeout=15
        )
        autores = [l.strip() for l in r.stdout.splitlines()
                   if l.strip() and "github-classroom" not in l.lower()]
        contagem = {}
        for a in autores:
            contagem[a] = contagem.get(a, 0) + 1
        return contagem
    except Exception:
        return {}


# ── TESTE 1 (25 pts) — Backlog preenchido ─────────────────────────────────────

def test_backlog_preenchido():
    """BACKLOG.md existe e tem funcionalidades reais definidas."""
    backlog = os.path.join(RAIZ, "BACKLOG.md")
    assert os.path.exists(backlog), \
        "BACKLOG.md não encontrado! Crie o arquivo na raiz do repositório."

    conteudo = open(backlog, encoding="utf-8").read()

    # Integrantes identificados
    assert "(nome completo)" not in conteudo, \
        "Preencha os nomes dos integrantes no BACKLOG.md!"
    assert "(escreva aqui)" not in conteudo or conteudo.count("(escreva aqui)") == 0, \
        "Preencha o tema do TCC no BACKLOG.md!"

    # Funcionalidades na tabela
    linhas = [
        l for l in conteudo.split("\n")
        if l.strip().startswith("|")
        and "---" not in l
        and "Funcionalidade" not in l
        and l.count("|") >= 3
        and "(escreva aqui)" not in l
        and not all(c.strip() in ("", "—", "⏳ A fazer") for c in l.split("|")[1:-1])
    ]
    assert len(linhas) >= 3, \
        f"BACKLOG.md tem {len(linhas)} funcionalidade(s) definida(s). Mínimo: 3."


# ── TESTE 2 (25 pts) — Issue aberta esta semana ───────────────────────────────

def test_issue_aberta_esta_semana():
    """Pelo menos 1 commit nos últimos 7 dias — prova que o grupo trabalhou."""
    semana = _commits_semana()

    # Filtra bots e commits automáticos
    commits_reais = {
        autor: qtd for autor, qtd in semana.items()
        if "bot" not in autor.lower()
        and "github-classroom" not in autor.lower()
    }

    total = sum(commits_reais.values())

    print(f"\n📊 Commits esta semana: {total}")
    for autor, qtd in sorted(commits_reais.items(), key=lambda x: -x[1]):
        print(f"   {autor}: {qtd} commit(s)")

    assert total >= 2, \
        f"Apenas {total} commit(s) esta semana. O grupo precisa fazer pelo menos 2 commits por semana."


# ── TESTE 3 (25 pts) — Participação individual ────────────────────────────────

def test_participacao_individual():
    """Todos os integrantes ativos contribuíram com commits."""
    total = _total_commits()
    semana = _commits_semana()

    # Filtra bots
    integrantes = {
        autor: qtd for autor, qtd in total.items()
        if "bot" not in autor.lower()
        and "github-classroom" not in autor.lower()
    }

    if len(integrantes) < 2:
        # Repositório novo ou só 1 pessoa — não penaliza
        print("\n⚠️ Menos de 2 integrantes com commits. Verifique se todos configuraram o Git.")
        return

    # Verifica quem não commitou esta semana
    sem_commit_semana = [
        autor for autor in integrantes
        if semana.get(autor, 0) == 0
    ]

    print(f"\n📈 Total geral de commits:")
    for autor, qtd in sorted(integrantes.items(), key=lambda x: -x[1]):
        status = "✅" if semana.get(autor, 0) > 0 else "⚠️ sem commit esta semana"
        print(f"   {autor}: {qtd} total — {status}")

    # Tolerância: permite 1 integrante sem commit (pode estar doente)
    if len(integrantes) >= 3:
        assert len(sem_commit_semana) <= 1, \
            f"Integrantes sem commit esta semana: {sem_commit_semana}. " \
            "Todos devem contribuir semanalmente."
    else:
        assert len(sem_commit_semana) == 0, \
            f"Integrante(s) sem commit esta semana: {sem_commit_semana}."


# ── TESTE 4 (25 pts) — PR semanal entregue ────────────────────────────────────

def test_pr_semanal():
    """Verifica evidências de entrega semanal via histórico de merges."""
    try:
        # Verifica se há merges nos últimos 7 dias
        desde = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        r = subprocess.run(
            ["git", "log", f"--after={desde}", "--oneline", "--merges"],
            capture_output=True, text=True, cwd=RAIZ, timeout=15
        )
        merges = [l.strip() for l in r.stdout.splitlines() if l.strip()]

        # Verifica total de commits da semana como alternativa
        semana = _commits_semana()
        commits_reais = sum(
            v for k, v in semana.items()
            if "bot" not in k.lower() and "github-classroom" not in k.lower()
        )

        print(f"\n📋 Merges esta semana: {len(merges)}")
        print(f"📝 Commits esta semana: {commits_reais}")

        # Passa se tiver merge OU pelo menos 3 commits diretos
        tem_entrega = len(merges) >= 1 or commits_reais >= 3

        assert tem_entrega, \
            "Nenhum PR mergeado e poucos commits esta semana. " \
            "Abra um PR com 'Closes #N' e faça o merge para registrar a entrega."

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass