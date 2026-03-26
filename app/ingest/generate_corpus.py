import json
from pathlib import Path
from datetime import datetime

from app.ingest.create_embeddings import ingest_tickets, ingest_docs

TICKETS_DIR = Path('data/tickets')
CONFLUENCE_DIR = Path('data/confluence')

TICKETS_DIR.mkdir(parents=True, exist_ok=True)
CONFLUENCE_DIR.mkdir(parents=True, exist_ok=True)

BASE_TICKETS = [
    {
        'id': 'TCK-001',
        'summary': 'Data lake ingestion falla en S3 con errores de permisos',
        'description': 'Los jobs de Glue no pueden escribir en el bucket s3://prod-datalake por error AccessDenied. Impacta dashboards de Power BI y pipelines de ML.',
        'steps': [
            'Revisar policy de S3 en prod-datalake',
            'Asegurar sts:AssumeRole para el role glue_execution',
            'Probar creación de objeto de prueba'
        ],
        'comments': ['Se sospecha cambio de RW en el bucket por equipo de seguridad.', 'Aplica hotfix con policy temporal.']
    },
    {
        'id': 'TCK-002',
        'summary': 'Fallo de linaje en Glue catalogo -> no se muestra en DataOps',
        'description': 'No se visualizan los activos en la herramienta de linaje. Registro de AWS Glue no incluye registros de eventos de ETL recientes.',
        'steps': [
            'Validar AWS Glue catalogo y endpoints Glue Data Catalog',
            'Revisar IAM role con permisos glue:BatchGetPartition, glue:GetTable',
            'Reconstruir metadatos en AWS Glue y refrescar DataOps'        ],
        'comments': ['Posible patch de versión de Glue corredor.']
    },
    {
        'id': 'TCK-003',
        'summary': 'Carga incremental en Redshift desde datalake se ralentiza por filas duplicadas',
        'description': 'ETL incremental diseñado con COPY en Redshift está tardando 6h en lugar de 30 min. Identificado scan masivo en tabla staging por duplicates de UUID.',
        'steps': [
            'Analizar estrategia de merge (upsert) y batch_size',
            'Crear CTE para dedupe antes de COPY',
            'Ajustar WLM en Redshift para pobres queries'        ],
        'comments': ['Por ahora se ejecuta workaround con pre-filtering de parquet.']
    }
]

BASE_DOCS = [
    {
        'id': 'DOC-001',
        'title': 'Guía de resolución de errores de acceso S3 en pipelines Glue',
        'content': 'Se describe: roles IAM, políticas S3, cifrado KMS, y auditoría CloudTrail. Incluye steps para: detectar AccessDenied, investigar principalId y rootCause. Ejecución de pruebas con AWS CLI. Recomendación: evitar uso de * en acciones y autorizaciones de bucket.'
    },
    {
        'id': 'DOC-002',
        'title': 'Procedimiento de linaje de datos con AWS Glue y OpenLineage',
        'content': 'Implementación de captura de linaje para jobs ETL: usar Glue Schema Registry y establecer metadata.properties. Configurar webhook hacia DataOps y visualización en Power BI Dataset lineage.'
    },
    {
        'id': 'DOC-003',
        'title': 'Prácticas recomendadas para carga incremental en Redshift desde S3',
        'content': 'Incluye metodología de staging + merge, control de versiones y validación de datos. Se cubre uso de COPY con manifest, sortkeys, distkeys, y vacuum/analyze. Diagnóstico de throttling y WLM.'
    },
    {
        'id': 'DOC-004',
        'title': 'Checklist de monitoreo de Data Lake AWS (S3 / Glue / Lake Formation)',
        'content': 'Métricas clave: licz buckets, request errors, glue job duration, y registros de auditoría. Establece alertas en CloudWatch para registros de ETL fallidos, y reporte semanal de integridad de linaje.'
    }
]


def write_ticket(ticket):
    path = TICKETS_DIR / f"{ticket['id']}.json"
    path.write_text(json.dumps(ticket, ensure_ascii=False, indent=2), encoding='utf-8')


def write_doc(doc):
    path = CONFLUENCE_DIR / f"{doc['id']}.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')


def generate_dataset(n_tickets=20, n_docs=20):
    # crear semilla expandida por iteraciones aleatorias
    for i in range(n_tickets):
        base = BASE_TICKETS[i % len(BASE_TICKETS)]
        ticket = base.copy()
        ticket['id'] = f"TCK-{i+1:03d}"
        ticket['summary'] = f"{base['summary']} (instancia {i+1})"
        ticket['created_at'] = datetime.utcnow().isoformat() + 'Z'
        ticket['status'] = 'open' if i % 3 != 0 else 'resolved'
        write_ticket(ticket)

    for i in range(n_docs):
        base = BASE_DOCS[i % len(BASE_DOCS)]
        doc = base.copy()
        doc['id'] = f"DOC-{i+1:03d}"
        doc['title'] = f"{base['title']} (edición {i+1})"
        doc['created_at'] = datetime.utcnow().isoformat() + 'Z'
        write_doc(doc)


if __name__ == '__main__':
    generate_dataset(n_tickets=30, n_docs=30)
    print('Corpus generado en data/tickets y data/confluence.')
    
    # Refrescar embeddings automáticamente
    print('🔄 Refrescando embeddings...')
    ingest_tickets()
    ingest_docs()
    print('✅ Embeddings actualizados en ChromaDB.')
