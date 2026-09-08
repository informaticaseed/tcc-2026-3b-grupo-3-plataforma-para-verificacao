async function analisarURL() {

    const url = document.getElementById("url").value;

    console.log("Enviando URL...");

    const resposta = await fetch("/check_url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: url
        })
    });

    console.log("Resposta recebida:", resposta.status);

    const resultado = await resposta.json();

    console.log("JSON recebido:", resultado);

    document.getElementById("resultado").innerText =
        JSON.stringify(resultado);
}