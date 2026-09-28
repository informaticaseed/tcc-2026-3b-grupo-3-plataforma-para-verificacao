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


/*
    Monta os resultados recebidos do FastAPI
*/
function mostrarResultado(dados) {

    const resultado = document.getElementById("resultado");


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


        <div class="danger-box">

            <span class="danger-label">
                Nível de perigo
            </span>

            <span class="danger-value">
                ${dados["Nivel de perigo"] ?? 0}
            </span>

        </div>


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
document.getElementById("url").addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        analisarURL();

    }

});