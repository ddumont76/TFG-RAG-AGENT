from app.ingest.load_corpus import load_tickets, load_confluence_docs


def search_corpus(tickets, docs, query):
    q = query.lower()
    hits = []

    for t in tickets:
        text = f"{t.get('id','')} {t.get('summary','')} {t.get('description','')} {' '.join(t.get('comments', []))}".lower()
        if q in text:
            hits.append({'type': 'ticket', 'id': t.get('id'), 'summary': t.get('summary')})

    for d in docs:
        text = f"{d.get('id','')} {d.get('title','')} {d.get('content','')}".lower()
        if q in text:
            hits.append({'type': 'doc', 'id': d.get('id'), 'title': d.get('title')})

    return hits


def main():
    print('=== Simple corpus check (sin deps extras) ===')

    tickets = load_tickets()
    docs = load_confluence_docs()

    print(f'Tickets JSON count: {len(tickets)}')
    print(f'Confluence JSON count: {len(docs)}')

    query = 'jenkins'
    print(f"\nBuscar query: '{query}'")

    hits = search_corpus(tickets, docs, query)
    print(f'Resultados encontrados: {len(hits)}')

    for i, h in enumerate(hits, start=1):
        if h['type'] == 'ticket':
            print(f" {i}. [ticket] {h['id']} - {h['summary']}")
        else:
            print(f" {i}. [doc] {h['id']} - {h['title']}")

    if not hits:
        print('  (no se hallaron coincidencias)')


if __name__ == '__main__':
    main()
