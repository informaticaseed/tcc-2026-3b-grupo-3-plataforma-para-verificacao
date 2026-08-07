# Documentação do Sistema

## Arquitetura

O sistema foi desenvolvido utilizando uma arquitetura em camadas.

### Interface

A interface é feita em HTML e permite que o usuário envie arquivos ou links para análise.

### Backend

O backend foi desenvolvido em Python utilizando FastAPI, responsável pelo processamento das requisições.

### Banco de Dados

As informações são armazenadas em um banco de dados SQL para registrar análises e facilitar futuras consultas.

## Fluxo do Sistema

Usuário
↓
HTML
↓
FastAPI
↓
Repositório
↓
Banco de Dados SQL
