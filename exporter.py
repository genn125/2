from docx import Document


class Exporter:
    @staticmethod
    def to_docx(data, output_path):
        """Экспорт в DOCX"""
        doc = Document()
        # ... логика формирования документа ...
        doc.save(output_path)

    @staticmethod
    def to_json(data, output_path):
        """Экспорт в JSON"""
        import json
        with open(output_path, 'w') as f:
            json.dump(data, f)