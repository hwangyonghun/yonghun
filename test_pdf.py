import os
from io import BytesIO
from xhtml2pdf import pisa
from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'app', 'templates'),
    static_folder=os.path.join(BASE_DIR, 'app', 'static')
)

def test():
    font_path = os.path.join(
        BASE_DIR, 'app', 'static', 'fonts', 'malgun.ttf'
    ).replace('\\', '/')

    font_path = f"file:///{font_path}"

    print(f"Testing font path: {font_path}")

    data = {
        'font_path': font_path,
        'title': "TEST",
        't': {
            'subtitle': "Subtitle",
            'cert_id_label': "ID:",
            'body_text': "Body",
            'date_label': "Date",
            'confidence_label': "Conf",
            'warning_text': "Warn",
            'user_name_label': "Name",
            'user_address_label': "Addr",
            'signatory_title': "Sign"
        },
        'cert_id': "123",
        'date': "2024",
        'verdict': "FAKE",
        'confidence': "99%",
        'color': "red",
        'disclaimer': "Disc",
        'is_fake': True,
        'show_user_info': True,
        'user_name': "User",
        'user_address': "Addr"
    }

    with app.app_context():
        try:
            rendered = render_template('certificate_view.html', **data)
            print("Template rendered successfully.")

            pdf = BytesIO()

            pisa_status = pisa.CreatePDF(
                rendered,
                dest=pdf,
                encoding='utf-8'
            )

            if pisa_status.err:
                print("❌ PISA PDF generation error")
            else:
                print(f"✅ PDF Generated (size: {len(pdf.getvalue())} bytes)")
                with open("test_out.pdf", "wb") as f:
                    f.write(pdf.getvalue())

        except Exception as e:
            print(f"🔥 EXCEPTION: {e}")

if __name__ == "__main__":
    test()