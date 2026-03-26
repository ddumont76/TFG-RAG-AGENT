async function sendQuery() {
    const query = document.getElementById("query").value;
    const top_k = document.getElementById("top_k").value;

    const body = {
        query: query,
        top_k: parseInt(top_k)
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
}