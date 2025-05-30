

""" Рабочий код сохранения в файл, но в развернутом виде"""


# def save_to_docx(self, output_path=None):
#     if not output_path:
#         output_path = filedialog.asksaveasfilename(
#             defaultextension=".docx",
#             filetypes=[("Word Documents", "*.docx")],
#             title="Сохранить коллекцию как"
#         )
#         if not output_path:
#             return False, ""
#
#     try:
#         doc = Document()
#         style = doc.styles['Normal']
#         style.font.name = 'Arial'
#         style.font.size = Pt(12)
#
#         # Заголовок документа
#         title = doc.add_heading('Моя музыкальная коллекция', level=1)
#         title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
#
#         def add_items(node, level=1):
#             for name, content in node.items():
#                 if name == "_files":
#                     for file_name, _ in content:
#                         p = doc.add_paragraph('    ' * level + f"🎵 {file_name}")
#                         p.runs[0].font.color.rgb = RGBColor(0, 0, 0)
#                 else:
#                     heading = doc.add_heading('    ' * (level - 1) + f"📁 {name}", level=min(level + 1, 6))
#                     heading.runs[0].font.color.rgb = RGBColor(0, 0, 128)
#                     add_items(content, level + 1)
#
#         add_items(self.music_library)
#         doc.save(output_path)
#         return True, output_path
#
#     except Exception as e:
#         return False, str(e)
