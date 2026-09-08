async function analisarURL() {

    const url = document.getElementById("url").value;

    const resposta = await fetch("/check_url", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: url
        })
    });

    const resultado = await resposta.json();

    document.getElementById("resultado").innerText = JSON.stringify(resultado);
}
