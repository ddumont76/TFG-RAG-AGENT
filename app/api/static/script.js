async function sendQuery() {
    const query = document.getElementById("query").value.trim();
    const top_k = document.getElementById("top_k").value;
    const llm_option = document.getElementById("llm_option").value;

    // Validación: no enviar consulta vacía
    if (!query) {
        alert("Por favor, introduce algún texto en el campo de consulta antes de enviar.");
        return;
    }

    // Parse provider and model from the combined option
    let provider, model;
    if (llm_option === "mock") {
        provider = "mock";
        model = "mistral"; // Default model (fallback)
    } else {
        const parts = llm_option.split("-");
        provider = parts[0]; // ollama

        if (provider === "ollama" && parts[1] === "mistral") {
            model = "mistral";
        } else if (provider === "ollama" && parts[1] === "phi4") {
            model = "phi4"; // será normalizado en backend a phi-4
        } else if (provider === "ollama" && parts[1] === "qwen2.5") {
            model = "qwen2.5"; // será normalizado en backend a qwen-2.5
        } else {
            model = "mistral";
        }
    }

    const body = {
        query: query,
        top_k: parseInt(top_k),
        provider: provider,
        model: model
    };

    const response = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    const data = await response.json();

    document.getElementById("answer").innerText = data.answer;
    document.getElementById("tickets").innerText = JSON.stringify(data.tickets, null, 2);
    document.getElementById("docs").innerText = JSON.stringify(data.docs, null, 2);
    document.getElementById("meta").innerText = JSON.stringify(data.metadata, null, 2);
    document.getElementById("metrics").innerText = JSON.stringify(data.metrics, null, 2);
}