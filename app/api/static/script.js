let lastQuery = null;
let lastAnswer = null;
let lastContexts = [];

/* =========================
   QUERY
========================= */

async function sendQuery() {
    const query = document.getElementById("query_text").value.trim();
    const topK = parseInt(document.getElementById("top_k").value, 10);
    const llmOption = document.getElementById("llm_option").value;

    if (!query) {
        showError("Por favor, introduce una consulta antes de enviar.");
        return;
    }

    showLoading(true);
    hideError();
    clearVisibleResults();
    resetEvaluationState();

    let provider = "mock";
    let model = "mistral";

    if (llmOption !== "mock") {
        const parts = llmOption.split("-");
        provider = parts[0];
        model = parts[1] || "mistral";
    }

    const payload = {
        query,
        top_k: topK,
        provider,
        model
    };

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Guardar datos para evaluación
        lastQuery = query;
        lastAnswer = data.answer;
        lastContexts = [];

        data.tickets?.forEach(t => t.content && lastContexts.push(t.content));
        data.docs?.forEach(d => d.content && lastContexts.push(d.content));

        // ✅ HABILITAR BOTÓN CORRECTAMENTE
        const evalBtn = document.getElementById("eval-btn");
        evalBtn.disabled = false;
        evalBtn.classList.add("enabled");

        showResultSections();

        setText("answer", data.answer);
        setText("tickets", JSON.stringify(data.tickets, null, 2));
        setText("docs", JSON.stringify(data.docs, null, 2));
        setText("meta", JSON.stringify(data.metadata, null, 2));
        setText("metrics", JSON.stringify(data.metrics, null, 2));

        setText("tickets-count", data.tickets?.length || 0);
        setText("docs-count", data.docs?.length || 0);
        setText("sources-count", (data.tickets?.length || 0) + (data.docs?.length || 0));

    } catch (e) {
        console.error(e);
        showError("Error al procesar la consulta: " + e.message);
    } finally {
        showLoading(false);
    }
}

/* =========================
   EVALUATION
========================= */

async function evaluateResponse() {
    if (!lastQuery || !lastAnswer || lastContexts.length === 0) {
        showError("Primero debes ejecutar una consulta antes de evaluar.");
        return;
    }

    showLoading(true);
    hideError();

    try {
        const response = await fetch("/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: lastQuery,
                answer: lastAnswer,
                contexts: lastContexts
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        document.getElementById("evaluation-section")
            .classList.add("visible");

        updateMetric("faithfulness", "faithfulness-text", data.metrics.faithfulness);
        updateMetric("answer_relevancy", "relevancy-text", data.metrics.answer_relevancy);

    } catch (e) {
        console.error(e);
        showError("Error evaluando respuesta: " + e.message);
    } finally {
        showLoading(false);
    }
}

/* =========================
   HELPERS
========================= */

function resetEvaluationState() {
    lastQuery = null;
    lastAnswer = null;
    lastContexts = [];

    const btn = document.getElementById("eval-btn");
    btn.disabled = true;
    btn.classList.remove("enabled");

    document.getElementById("evaluation-section")
        .classList.remove("visible");
}

function updateMetric(valueId, textId, score) {
    document.getElementById(valueId).innerText = score.toFixed(2);
    document.getElementById(textId).innerText = interpretScore(score);
}

function interpretScore(score) {
    if (score < 0.2) return "Muy bajo";
    if (score < 0.4) return "Bajo";
    if (score < 0.6) return "Medio";
    if (score < 0.8) return "Alto";
    return "Muy alto";
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.innerText = value ?? "-";
}

function showResultSections() {
    [
        "stats-section",
        "answer-section",
        "tickets-section",
        "docs-section",
        "metadata-section",
        "basic-metrics-section"
    ].forEach(id =>
        document.getElementById(id)?.classList.add("visible")
    );
}

function clearVisibleResults() {
    [
        "stats-section",
        "answer-section",
        "tickets-section",
        "docs-section",
        "metadata-section",
        "basic-metrics-section",
        "evaluation-section"
    ].forEach(id =>
        document.getElementById(id)?.classList.remove("visible")
    );
}

function showLoading(show) {
    document.getElementById("loading")
        ?.classList.toggle("show", show);
}

function showError(msg) {
    const el = document.getElementById("error");
    el.innerText = msg;
    el.classList.add("show");
}

function hideError() {
    document.getElementById("error")
        ?.classList.remove("show");
}
