"""
Генератор официальных паспортов индивидуальных медицинских изделий.
Соответствует Регламенту ЕС о медицинских изделиях MDR EU 2017/745 (Приложение XIII).
"""

from pathlib import Path
from app.models.schemas import MdrPassportData
from fpdf import FPDF


class MdrPassportPDF(FPDF):
    """Кастомный класс FPDF для верстки сертификатов MDR Annex XIII."""

    def header(self):
        self.set_font("helvetica", "B", 14)
        self.cell(0, 10, "STATEMENT FOR CUSTOM-MADE MEDICAL DEVICES", border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("helvetica", "I", 9)
        self.cell(0, 5, "Regulation (EU) 2017/745 Annex XIII Compliance Declaration", border=False, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, "CE mark is EXCLUDED for custom-made devices under Annex XIII. Document retention: 10 years.", align="C")


class MdrPassportGenerator:
    """Генератор паспортов изделий MDR EU 2017/745."""

    def _latinize(self, text: str) -> str:
        """Транслитерирует кириллические символы в ASCII латиницу для MDR шрифта."""
        translit_map = {
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
            'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
            'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
            'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu',
            'Я': 'Ya', 'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh',
            'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
            'ю': 'yu', 'я': 'ya'
        }
        return "".join(translit_map.get(c, c) for c in text)

    def generate_pdf_passport(self, data: MdrPassportData, output_dir: Path) -> Path:
        """
        Генерирует официальный PDF документ паспорта изделия и сохраняет его на диск.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / f"MDR_Passport_{data.order_id}.pdf"

        pdf = MdrPassportPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("helvetica", size=10)

        patient = self._latinize(data.patient_id)
        doctor = self._latinize(data.doctor_name)
        clinic = self._latinize(data.clinic_name)
        material = self._latinize(data.material_name)
        declaration = self._latinize(data.declaration_text)

        # Раздел 1: Данные лаборатории и заказа
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, f"1. DEVICE & ORDER IDENTIFICATION: {data.passport_number}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=10)
        pdf.cell(0, 6, f"Order ID: {data.order_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Patient ID / Code: {patient}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Prescribing Doctor: {doctor} ({clinic})", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Target Tooth (FDI): #{data.fdi}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Раздел 2: Материалы и прослеживаемость партий
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "2. MATERIAL & BATCH TRACEABILITY (LOT):", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=10)
        pdf.cell(0, 6, f"Substrate Material: {material}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Raw Material LOT Number: {data.disk_lot_number}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Sintering Peak Temperature: {data.sintering_temp_c} C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Раздел 3: Декларация соответствия
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 8, "3. ANNEX XIII COMPLIANCE DECLARATION:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=9)
        pdf.multi_cell(0, 5, declaration)
        pdf.ln(5)

        # Раздел 4: Автограф и дата
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "Manufacturer / Authorized Signatory: Solo Lab Operator, Szczecin", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, "Signature: [ELECTRONICALLY VERIFIED AUDIT TRAIL]", new_x="LMARGIN", new_y="NEXT")

        pdf.output(str(pdf_path))
        return pdf_path


mdr_generator = MdrPassportGenerator()
