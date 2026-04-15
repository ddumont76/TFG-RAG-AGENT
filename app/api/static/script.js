async function sendQuery() {
    const query = document.getElementById("query_text").value.trim();
    const topK = parseInt(document.getElementById("top_k").value, 10);
    const llmOption = document.getElementById("llm_option").value;

    // Validación básica
    if (!query) {
        showError("Por favor, introduce una consulta antes de enviar.");
        return;
    }

    showLoading(true);
    hideError();
    clearVisibleResults();

    // Resolver provider + model desde el selector
    let provider = "mock";
    let model = "mistral";

    if (llmOption !== "mock") {
        const parts = llmOption.split("-");
        provider = parts[0]; // ollama
        model = parts[1] || "mistral";
    }

    const payload = {
        query: query,
        top_k: topK,
        provider: provider,
        model: model
    };

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}`);
        }

        const data = await response.json();

        // Mostrar secciones
        showResultSections();

        // Respuesta del agente
        setText("answer", data.answer);

        // Fuentes
        setText("tickets", JSON.stringify(data.tickets, null, 2));
        setText("docs", JSON.stringify(data.docs, null, 2));

        // Metadata
        setText("meta", JSON.stringify(data.metadata, null, 2));

        // Métricas básicas
        setText("metrics", JSON.stringify(data.metrics, null, 2));

        // Estadísticas
        const ticketCount = Array.isArray(data.tickets) ? data.tickets.length : 0;
        const docCount = Array.isArray(data.docs) ? data.docs.length : 0;

        setText("tickets-count", ticketCount);
        setText("docs-count", docCount);
        setText("sources-count", ticketCount + docCount);

    } catch (error) {
        console.error("Error en la consulta:", error);
        showError("Error al procesar la consulta: " + error.message);
    } finally {
        showLoading(false);
    }
}

/* =========================
   Helpers seguros
========================= */

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = value ?? "-";
    }
}

function showResultSections() {
    const sectionIds = [
        "stats-section",
        "answer-section",
        "tickets-section",
        "docs-section",
        "metadata-section",
        "basic-metrics-section"
    ];

    sectionIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add("visible");
    });
}

function clearVisibleResults() {
    const sectionIds = [
        "stats-section",
        "answer-section",
        "tickets-section",
        "docs-section",
        "metadata-section",
        "basic-metrics-section"
    ];

    sectionIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove("visible");
    });
}

function clearResults() {
    document.getElementById("query_text").value = "";
    clearVisibleResults();
    hideError();
}

function showLoading(show) {
    const el = document.getElementById("loading");
    if (!el) return;
    el.classList.toggle("show", show);
}

function showError(message) {
    const el = document.getElementById("error");
    if (!el) return;
    el.innerText = message;
    el.classList.add("show");
}

function hideError() {
    const el = document.getElementById("error");
    if (el) el.classList.remove("show");
}