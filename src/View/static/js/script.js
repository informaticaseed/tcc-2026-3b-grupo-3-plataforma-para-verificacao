async function analisarURL() {

    const urlInput = document.getElementById("url");
    const resultadoContainer = document.getElementById("resultado-container");
    const resultado = document.getElementById("resultado");
    const button = document.getElementById("analisar-button");

    const url = urlInput.value.trim();


    // Não faz nada se o campo estiver vazio
    if (!url) {

        resultadoContainer.classList.add("visible");

        resultado.innerHTML = `
            <div class="error-box">
                Insira uma URL para realizar a análise.
            </div>
        `;

        return;
    }


    // Mostra o resultado e o estado de carregamento
    resultadoContainer.classList.add("visible");

    resultado.innerHTML = `
        <div class="loading">
            Analisando URL...<br>
            O VirusTotal pode levar alguns segundos.
        </div>
    `;

    button.disabled = true;
    button.innerText = "Analisando...";


    try {

        const resposta = await fetch("/check_url", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url: url
            })
        });


        const dados = await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                dados.detail || "Erro ao analisar a URL."
            );
        }


        mostrarResultado(dados);
        window.registrarAnalise?.("URL", url, dados);


    } catch (erro) {

        console.error("Erro:", erro);

        resultado.innerHTML = `
            <div class="error-box">
                Erro ao realizar a análise:
                ${escapeHTML(erro.message)}
            </div>
        `;

    } finally {

        button.disabled = false;
        button.innerHTML = "<span>⛶</span> Verificar Link";
    }
}

async function analisarArquivo() {
    const fileInput = document.getElementById("file");
    const resultadoContainer = document.getElementById("resultado-container");
    const resultado = document.getElementById("resultado");
    const button = document.getElementById("analisar-arquivo-button");
    const file = fileInput.files[0];

    if (!file) {
        resultadoContainer.classList.add("visible");
        resultado.innerHTML = `
            <div class="error-box">
                Selecione um arquivo para realizar a análise.
            </div>
        `;
        return;
    }

    if (file.size > 32 * 1024 * 1024) {
        resultadoContainer.classList.add("visible");
        resultado.innerHTML = `
            <div class="error-box">
                O arquivo deve ter no máximo 32 MB.
            </div>
        `;
        return;
    }

    resultadoContainer.classList.add("visible");
    resultado.innerHTML = `
        <div class="loading">
            Analisando arquivo...<br>
            O VirusTotal pode levar alguns segundos.
        </div>
    `;

    button.disabled = true;
    button.innerText = "Analisando...";

    try {
        const formData = new FormData();
        formData.append("file", file);
        const resposta = await fetch("/check_file", {
            method: "POST",
            body: formData
        });
        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(dados.detail || "Erro ao analisar o arquivo.");
        }

        mostrarResultadoArquivo(dados);
        window.registrarAnalise?.("Arquivo", file.name, dados);
    } catch (erro) {
        console.error("Erro:", erro);
        resultado.innerHTML = `
            <div class="error-box">
                Erro ao realizar a análise:
                ${escapeHTML(erro.message)}
            </div>
        `;
    } finally {
        button.disabled = false;
        button.innerHTML = "<span>⛶</span> Verificar arquivo";
    }
}

function mostrarResultadoArquivo(dados) {
    const resultado = document.getElementById("resultado");
    const virustotal = dados.VirusTotal;

    if (!virustotal || typeof virustotal !== "object") {
        resultado.innerHTML = `
            <div class="error-box">
                Não foi possível obter um resultado válido do VirusTotal.
            </div>
        `;
        return;
    }

    if (virustotal?.erro) {
        resultado.innerHTML = `
            <div class="result-url">
                <span class="result-label">Arquivo analisado</span>
                <span class="result-url-value">${escapeHTML(dados.arquivo || "Não informado")}</span>
            </div>
            <div class="error-box">${escapeHTML(virustotal.erro)}</div>
        `;
        return;
    }

    const stats = virustotal;
    const counts = [
        ["Harmless", stats.harmless ?? 0],
        ["Malicious", stats.malicious ?? 0],
        ["Suspicious", stats.suspicious ?? 0],
        ["Undetected", stats.undetected ?? 0]
    ];

    resultado.innerHTML = `
        <div class="result-url">
            <span class="result-label">Arquivo analisado</span>
            <span class="result-url-value">${escapeHTML(dados.arquivo || "Não informado")}</span>
        </div>
        <div class="result-block">
            <h3>Detecções do VirusTotal</h3>
            <div class="vt-grid">
                ${counts.map(([name, value]) => `
                    <div class="vt-item">
                        <span class="vt-item-name">${name}</span>
                        <span class="vt-item-value">${value}</span>
                    </div>
                `).join("")}
            </div>
        </div>
    `;
}


/*
    Monta os resultados recebidos do FastAPI
*/
function mostrarResultado(dados) {

    const resultado = document.getElementById("resultado");
    const score = Math.max(0, Math.min(100, Number(dados["Nivel de perigo"]) || 0));
    const riskLevel = score >= 70
        ? "Perigoso"
        : score >= 50
            ? "Suspeito"
            : "Baixo risco";
    const riskClass = score >= 70
        ? "risk-danger"
        : score >= 50
            ? "risk-suspicious"
            : "risk-low";


    /*
        Motivos da análise própria
    */

    let motivosHTML = "";

    if (Array.isArray(dados["Motivo:"])) {

        motivosHTML = dados["Motivo:"]
            .map(motivo => `
                <li>${escapeHTML(motivo)}</li>
            `)
            .join("");

    } else {

        motivosHTML = `
            <li>Nenhum motivo informado.</li>
        `;
    }


    /*
        VirusTotal
    */

    let virusTotalHTML = "";


    if (dados.VirusTotal) {

        if (dados.VirusTotal.erro) {

            virusTotalHTML = `
                <div class="result-block">

                    <h3>VirusTotal</h3>

                    <div class="error-box">
                        ${escapeHTML(dados.VirusTotal.erro)}
                    </div>

                </div>
            `;

        } else {

            const vt = dados.VirusTotal;

            virusTotalHTML = `
                <div class="result-block">

                    <h3>VirusTotal</h3>

                    <div class="vt-grid">

                        <div class="vt-item">
                            <span class="vt-item-name">
                                Harmless
                            </span>

                            <span class="vt-item-value">
                                ${vt.harmless ?? 0}
                            </span>
                        </div>


                        <div class="vt-item">
                            <span class="vt-item-name">
                                Malicious
                            </span>

                            <span class="vt-item-value">
                                ${vt.malicious ?? 0}
                            </span>
                        </div>


                        <div class="vt-item">
                            <span class="vt-item-name">
                                Suspicious
                            </span>

                            <span class="vt-item-value">
                                ${vt.suspicious ?? 0}
                            </span>
                        </div>


                        <div class="vt-item">
                            <span class="vt-item-name">
                                Undetected
                            </span>

                            <span class="vt-item-value">
                                ${vt.undetected ?? 0}
                            </span>
                        </div>

                    </div>

                </div>
            `;
        }

    }


    /*
        Monta tudo na tela
    */

    resultado.innerHTML = `

        <div class="result-url">

            <span class="result-label">
                URL analisada
            </span>

            <span class="result-url-value">
                ${escapeHTML(dados.url || "Não informado")}
            </span>

        </div>


        <div class="danger-box ${riskClass}">

            <div class="risk-summary">
                <span class="danger-label">Risco estimado · ${riskLevel}</span>
                <div
                    class="risk-meter"
                    role="progressbar"
                    aria-label="Pontuação estimada de risco"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow="${score}"
                >
                    <span class="risk-meter-fill" style="width: ${score}%"></span>
                </div>
            </div>

            <span class="danger-value">${score}<small>/100</small></span>

        </div>

        <p class="risk-disclaimer">
            Pontuação heurística baseada nos sinais abaixo; não é uma probabilidade nem substitui o VirusTotal.
        </p>


        <div class="result-block">

            <h3>
                Motivos da análise
            </h3>

            <ul class="reason-list">

                ${motivosHTML}

            </ul>

        </div>


        ${virusTotalHTML}

    `;
}


/*
    Evita que uma URL ou mensagem recebida
    seja interpretada como HTML.
*/
function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/*
    Permite apertar ENTER no campo da URL
*/
const urlInput = document.getElementById("url");
if (urlInput) {
    urlInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            analisarURL();
        }
    });
}

const fileInput = document.getElementById("file");
if (fileInput) {
    fileInput.addEventListener("change", function() {
        document.getElementById("file-name").textContent =
            fileInput.files[0]?.name || "Nenhum arquivo selecionado";
    });
}

const dropZone = document.getElementById("drop-zone");
if (dropZone && fileInput) {
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, event => {
            event.preventDefault();
            dropZone.classList.add("is-dragging");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, event => {
            event.preventDefault();
            dropZone.classList.remove("is-dragging");
        });
    });

    dropZone.addEventListener("drop", event => {
        const droppedFile = event.dataTransfer.files[0];
        if (!droppedFile) {
            return;
        }

        const transfer = new DataTransfer();
        transfer.items.add(droppedFile);
        fileInput.files = transfer.files;
        document.getElementById("file-name").textContent = droppedFile.name;
    });
}