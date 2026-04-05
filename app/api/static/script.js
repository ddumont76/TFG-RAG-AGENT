async function sendQuery() {
    const query = document.getElementById("query_text").value.trim();
    const top_k = document.getElementById("top_k").value;
    const llm_option = document.getElementById("llm_option").value;
    const chunking_strategy = document.getElementById("chunking_strategy").value;

    // Validación: no enviar consulta vacía
    if (!query) {
        showError("Por favor, introduce algún texto en el campo de consulta antes de enviar.");
        return;
    }

    showLoading(true);
    hideError();

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
        model: model,
        chunking_strategy: chunking_strategy
    };

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Mostrar todas las secciones de resultados
        showResultSections();

        // Mostrar datos básicos
        document.getElementById("answer").innerText = data.answer || "-";
        document.getElementById("tickets").innerText = JSON.stringify(data.tickets, null, 2);
        document.getElementById("docs").innerText = JSON.stringify(data.docs, null, 2);
        document.getElementById("meta").innerText = JSON.stringify(data.metadata, null, 2);
        document.getElementById("metrics").innerText = JSON.stringify(data.metrics, null, 2);

        // Calcular y mostrar estadísticas
        const ticketCount = data.tickets ? Object.keys(data.tickets).length : 0;
        const docCount = data.docs ? Object.keys(data.docs).length : 0;
        const totalSources = ticketCount + docCount;

        document.getElementById("tickets-count").innerText = ticketCount;
        document.getElementById("docs-count").innerText = docCount;
        document.getElementById("sources-count").innerText = totalSources;

        // Mostrar y colorear métricas RAGAS
        if (data.metrics) {
            updateMetricCard("faithfulness: ¿Qué tan fiel es la respuesta al contexto recuperado?", data.metrics.faithfulness);
            updateMetricCard("answer_relevancy: ¿Qué tan relevante es la respuesta respecto a la pregunta?", data.metrics.answer_relevancy);
            updateMetricCard("context_utilization: ¿Qué tan bien se utiliza el contexto en la respuesta?", data.metrics.context_utilization);
            //updateMetricCard("context_recall", data.metrics.context_recall);
        }

    } catch (error) {
        showError("Error al procesar la consulta: " + error.message);
        console.error("Error:", error);
    } finally {
        showLoading(false);
    }
}

function updateMetricCard(metricName, value) {
    const metric = parseFloat(value);
    const valueStr = !isNaN(metric) ? metric.toFixed(2) : "-";
    const interpretation = !isNaN(metric) ? interpretMetric(metricName, value) : "No disponible";
    
    document.getElementById(metricName).innerText = valueStr;
    
    // Interpretar y cambiar color
    const interpId = metricName === "faithfulness" ? "faith-interp" : 
                     metricName === "answer_relevancy" ? "rel-interp" :
                      metricName === "context_utilization" ? "context-interp" :
                     //metricName === "context_precision" ? "prec-interp" : "recall-interp";
    
    document.getElementById(interpId).innerText = interpretation;
    
    // Cambiar clase del color
    const card = document.getElementById(metricName).closest('.metric-card');
    card.classList.remove('low', 'medium', 'high');
    
    if (isNaN(metric)) {
        // Sin color específico
    } else if (metric < 0.4) {
        card.classList.add('low');
    } else if (metric < 0.7) {
        card.classList.add('medium');
    } else {
        card.classList.add('high');
    }
}

function interpretMetric(metric_name, value) {
    const numeric_value = parseFloat(value);
    
    if (isNaN(numeric_value) || value === "-") {
        return "No disponible";
    }
    
    if (numeric_value < 0.2) return "Muy bajo";
    if (numeric_value < 0.4) return "Bajo";
    if (numeric_value < 0.6) return "Medio";
    if (numeric_value < 0.8) return "Alto";
    return "Muy alto";
}

function showResultSections() {
    // Mostrar todas las secciones de resultados
    document.getElementById("stats-section").classList.add("visible");
    document.getElementById("answer-section").classList.add("visible");
    document.getElementById("tickets-section").classList.add("visible");
    document.getElementById("docs-section").classList.add("visible");
    document.getElementById("metrics-section").classList.add("visible");
    document.getElementById("metadata-section").classList.add("visible");
    document.getElementById("basic-metrics-section").classList.add("visible");
}

function clearResults() {
    document.getElementById("query_text").value = "";
    
    // Ocultar todas las secciones de resultados
    document.getElementById("stats-section").classList.remove("visible");
    document.getElementById("answer-section").classList.remove("visible");
    document.getElementById("tickets-section").classList.remove("visible");
    document.getElementById("docs-section").classList.remove("visible");
    document.getElementById("metrics-section").classList.remove("visible");
    document.getElementById("metadata-section").classList.remove("visible");
    document.getElementById("basic-metrics-section").classList.remove("visible");
    
    hideError();
}

function showLoading(show) {
    const element = document.getElementById("loading");
    if (show) {
        element.classList.add("show");
    } else {
        element.classList.remove("show");
    }
}

function showError(message) {
    const element = document.getElementById("error");
    element.innerText = message;
    element.classList.add("show");
}

function hideError() {
    const element = document.getElementById("error");
    element.classList.remove("show");
}