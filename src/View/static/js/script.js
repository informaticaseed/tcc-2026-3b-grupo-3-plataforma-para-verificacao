async function analisarURL() {

    const url = document.getElementById("url").value;

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

        console.log("Status:", resposta.status);

        const resultado = await resposta.json();

        console.log("JSON recebido:", resultado);

        document.getElementById("resultado").innerHTML = `
            <p><strong>URL:</strong> ${resultado.url}</p>

            <p><strong>Nível de perigo:</strong> ${resultado["Nivel de perigo"]}</p>

            <p><strong>Motivos:</strong></p>
            <ul>
                ${resultado["Motivo:"].map(motivo => `<li>${motivo}</li>`).join("")}
            </ul>

            <p><strong>VirusTotal:</strong></p>
            <ul>
                <li>Harmless: ${resultado.VirusTotal.harmless}</li>
                <li>Malicious: ${resultado.VirusTotal.malicious}</li>
                <li>Suspicious: ${resultado.VirusTotal.suspicious}</li>
                <li>Undetected: ${resultado.VirusTotal.undetected}</li>
                <li>Timeout: ${resultado.VirusTotal.timeout}</li>
                <li>Confirmed timeout: ${resultado.VirusTotal.confirmed_timeout}</li>
                <li>Failure: ${resultado.VirusTotal.failure}</li>
                <li>Type unsupported: ${resultado.VirusTotal.type_unsupported}</li>
            </ul>
        `;

    } catch (erro) {

        console.error("ERRO NO FETCH:", erro);

        document.getElementById("resultado").innerText =
            "Erro: " + erro;
    }
}