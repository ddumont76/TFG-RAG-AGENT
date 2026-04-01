async function sendQuery() {
    const query = document.getElementById("query").value;
    const top_k = document.getElementById("top_k").value;
    const llm_option = document.getElementById("llm_option").value;

    // Parse provider and model from the combined option
    let provider, model;
    if (llm_option === "mock") {
        provider = "mock";
        model = "mistral"; // Default model for mock
    } else {
        const parts = llm_option.split("-");
        provider = parts[0]; // ollama or openai
        if (parts[1] === "gpt4omini") {
            model = "openai"; // Special case for gpt-4o-mini
        } else {
            model = parts[1]; // mistral or phi4
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