(function () {
    const storageKey = "verificacao-analises-recentes";
    const maximumEntries = 30;

    function escapeHistoryHTML(value) {
        const element = document.createElement("div");
        element.textContent = String(value ?? "");
        return element.innerHTML;
    }

    function showHistoryFeedback(message) {
        const feedback = document.getElementById("history-feedback");
        if (feedback) {
            feedback.textContent = message;
        }
    }

    function readHistory() {
        try {
            const stored = localStorage.getItem(storageKey);
            if (!stored) {
                return [];
            }

            const entries = JSON.parse(stored);
            if (!Array.isArray(entries)) {
                console.error("O histórico salvo possui um formato inválido.");
                showHistoryFeedback("O histórico salvo não está em um formato válido.");
                return [];
            }

            const validEntries = entries.filter(entry =>
                entry &&
                typeof entry.id === "string" &&
                typeof entry.target === "string" &&
                typeof entry.type === "string" &&
                typeof entry.status === "string" &&
                typeof entry.date === "string"
            );
            if (validEntries.length !== entries.length) {
                console.error("O histórico contém registros inválidos.");
                showHistoryFeedback("Alguns registros inválidos foram ignorados.");
            }
            return validEntries;
        } catch (error) {
            console.error("Não foi possível carregar o histórico de análises.", error);
            showHistoryFeedback("Não foi possível carregar o histórico do navegador.");
            return [];
        }
    }

    function formatDate(value) {
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return "Data indisponível";
        }

        const time = date.toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit"
        });
        const today = new Date();
        const yesterday = new Date();
        yesterday.setDate(today.getDate() - 1);

        if (date.toDateString() === today.toDateString()) {
            return `Hoje, ${time}`;
        }
        if (date.toDateString() === yesterday.toDateString()) {
            return `Ontem, ${time}`;
        }
        return `${date.toLocaleDateString("pt-BR")} ${time}`;
    }

    function renderHistory() {
        const tableBody = document.getElementById("history-entries");
        if (!tableBody) {
            return;
        }

        const entries = readHistory();
        if (entries.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="history-empty">Nenhuma análise realizada ainda.</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = entries.map(entry => `
            <tr>
                <td class="history-date">${escapeHistoryHTML(formatDate(entry.date))}</td>
                <td class="history-target" title="${escapeHistoryHTML(entry.target)}">
                    ${escapeHistoryHTML(entry.target)}
                </td>
                <td>${escapeHistoryHTML(entry.type)}</td>
                <td>
                    <span class="status-badge ${statusClassFor(entry.status)}">
                        ${escapeHistoryHTML(entry.status)}
                    </span>
                </td>
                <td class="history-action-cell">
                    <button
                        class="remove-history-button"
                        type="button"
                        data-history-id="${escapeHistoryHTML(entry.id)}"
                        aria-label="Remover análise do histórico"
                        title="Remover do histórico"
                    >×</button>
                </td>
            </tr>
        `).join("");
    }

    function statusClassFor(status) {
        const classes = {
            "Seguro": "status-seguro",
            "Baixo risco": "status-baixo-risco",
            "Perigoso": "status-perigoso",
            "Suspeito": "status-suspeito",
            "Indisponível": "status-indisponível"
        };
        return classes[status] || "status-indisponível";
    }

    function statusFor(data) {
        const virusTotal = data && data.VirusTotal;
        if (virusTotal && !virusTotal.erro && Number(virusTotal.malicious) > 0) {
            return "Perigoso";
        }

        if (virusTotal && !virusTotal.erro && Number(virusTotal.suspicious) > 0) {
            return "Suspeito";
        }

        if (data && data.url) {
            const score = Number(data["Nivel de perigo"]) || 0;
            if (score >= 70) {
                return "Perigoso";
            }
            return score >= 50 ? "Suspeito" : "Baixo risco";
        }

        if (!virusTotal || virusTotal.erro) {
            return "Indisponível";
        }
        return "Seguro";
    }

    window.registrarAnalise = function (type, target, data) {
        const entries = readHistory();
        entries.unshift({
            id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
            date: new Date().toISOString(),
            target: String(target || "Não informado"),
            type,
            status: statusFor(data)
        });

        try {
            localStorage.setItem(storageKey, JSON.stringify(entries.slice(0, maximumEntries)));
            showHistoryFeedback("");
            renderHistory();
        } catch (error) {
            console.error("Não foi possível salvar a análise no histórico.", error);
            showHistoryFeedback("Não foi possível salvar esta análise no histórico do navegador.");
        }
    };

    document.addEventListener("click", event => {
        const target = event.target;
        if (!(target instanceof Element)) {
            return;
        }

        const removeButton = target.closest(".remove-history-button");
        if (removeButton) {
            const entryId = removeButton.getAttribute("data-history-id");
            const entries = readHistory().filter(entry => entry.id !== entryId);
            try {
                localStorage.setItem(storageKey, JSON.stringify(entries));
                showHistoryFeedback("");
                renderHistory();
            } catch (error) {
                console.error("Não foi possível remover a análise do histórico.", error);
                showHistoryFeedback("Não foi possível remover esta análise do histórico.");
            }
            return;
        }

        if (target.closest("#clear-history")) {
            try {
                localStorage.removeItem(storageKey);
                showHistoryFeedback("");
                renderHistory();
            } catch (error) {
                console.error("Não foi possível limpar o histórico de análises.", error);
                showHistoryFeedback("Não foi possível limpar o histórico.");
            }
        }
    });

    document.addEventListener("DOMContentLoaded", renderHistory);
})();
