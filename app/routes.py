from flask import Blueprint, render_template, request, jsonify, current_app, session, make_response
from werkzeug.utils import secure_filename
import os
from app.services.detector import DeepfakeDetector
from app import db
from app.models import Certificate, Violation
import random
import string
import time
import requests
from io import BytesIO
import datetime
import hashlib
import uuid

try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# Dependency check trigger

main = Blueprint('main', __name__)

# ... (detector init) ...
# ... (detector init) ...
detector = DeepfakeDetector()  # Initialized as before

try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    
    font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'malgun.ttf')
    nanum_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'NanumGothic.ttf')
    
    # Register Fonts
    pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
    pdfmetrics.registerFont(TTFont('NanumGothic', nanum_path))
    
    # Map variants to the same font file to prevent broken chars in Bold/Italic text
    addMapping('MalgunGothic', 0, 0, 'MalgunGothic') # Regular
    addMapping('MalgunGothic', 0, 1, 'MalgunGothic') # Italic -> Regular (Fallback)
    addMapping('MalgunGothic', 1, 0, 'MalgunGothic') # Bold -> Regular (Fallback)
    addMapping('MalgunGothic', 1, 1, 'MalgunGothic') # Bold Italic -> Regular (Fallback)

    addMapping('NanumGothic', 0, 0, 'NanumGothic')
    addMapping('NanumGothic', 0, 1, 'NanumGothic')
    addMapping('NanumGothic', 1, 0, 'NanumGothic')
    addMapping('NanumGothic', 1, 1, 'NanumGothic')
    
    print(f"Registered fonts: MalgunGothic, NanumGothic")
except Exception as e:
    print(f"Font Registration Failed: {e}")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf', 'mp4', 'avi', 'mov', 'webm'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    # Get the absolute path to the static directory
    static_url = '/static/'
    if uri.startswith(static_url):
        # Remove '/static/' from the beginning of the URI
        path = uri[len(static_url):]
        # Build the absolute path
        abs_path = os.path.join(current_app.root_path, 'static', path)
        if os.path.exists(abs_path):
             # FORCE FORWARD SLASHES for xhtml2pdf compatibility
             final_path = abs_path.replace('\\', '/')
             current_app.logger.info(f"Link Callback Resolved: {uri} -> {final_path}")
             return final_path
             
    current_app.logger.info(f"Link Callback Skipped: {uri}")

    # Handle other cases or return original URI if not found
    return uri

def get_cert_id(file_hash, user_identifier):
    # 1. Check Upload File (same file -> same ID)
    same_file_cert = Certificate.query.filter_by(file_hash=file_hash).first()
    if same_file_cert:
        return same_file_cert.cert_id
        
    # 2. New (If file hash is new, generate new ID regardless of user)
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@main.route('/')
def index():
    response = make_response(render_template('index.html'))
    # Critical: Disable caching for main page to force UI updates
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main.route('/api/analyze', methods=['POST'])
def analyze():
    # 1. Handle URL Input (YouTube)
    input_url = request.form.get('url')
    lang = request.form.get('lang', 'US') # Frontend now sends this
    
    # helper for result processing
    def process_result(prob, cert_id, file_hash, original_filename, lang='US'):
        is_fake = prob > 0.5
        
        # Localization for Result
        msgs = {
            'US': {
                'res_fake': "DEEPFAKE", 'res_real': "REAL",
                'verdict_fake': "DEEPFAKE DETECTED", 'verdict_real': "REAL / AUTHENTIC",
                'expl_fake': "CRITICAL ALERT: AI-Generated Content Detected. Analysis reveals high markers of synthetic generation including temporal inconsistencies.",
                'expl_real': "No manipulation artifacts detected. Media integrity is preserved."
            },
            'KR': {
                'res_fake': "DEEPFAKE", 'res_real': "REAL",
                'verdict_fake': "DEEPFAKE DETECTED", 'verdict_real': "REAL / AUTHENTIC",
                'expl_fake': "CRITICAL ALERT: AI-Generated Content Detected. Analysis reveals high markers of synthetic generation including temporal inconsistencies.",
                'expl_real': "No manipulation artifacts detected. Media integrity is preserved."
            }
        }
        
        t = msgs.get(lang, msgs['US'])
        
        result_text = t['res_fake'] if is_fake else t['res_real']
        confidence = prob if is_fake else (1 - prob)
        
        if is_fake:
            explanation = t['expl_fake']
        else:
            explanation = t['expl_real']
            
        # Store in session for certificate (store raw status, Cert route handles translation again)
        # But we store localized verdict here just in case specific logic uses it.
        # Actually Cert route now re-generates verdict string, so this is mainly for 'result' return.
        
        session['last_analysis'] = {
            'verdict': t['verdict_fake'] if is_fake else t['verdict_real'],
            'is_fake': is_fake,
            'confidence': f"{confidence * 100:.1f}%",
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'id': cert_id,
            'file_hash': file_hash,
            'original_filename': original_filename,
            'analysis_uuid': str(uuid.uuid4())
        }
        
        return {
            'result': result_text,
            'probability': prob,
            'confidence': f"{confidence * 100:.2f}%",
            'is_fake': is_fake,
            'explanation': explanation,
            'verdict_text': t['verdict_fake'] if is_fake else t['verdict_real'] # Pass to frontend
        }

    if input_url:
        global yt_dlp
        if not yt_dlp:
            try:
                import yt_dlp
            except ImportError:
                 return jsonify({'error': 'YouTube download service not available'}), 500
        
        # 1. Cleaner URL Handling
        input_url = input_url.strip()
        
        # Helper to simplify KBS Mobile URLs to correct Desktop Format
        # Mobile: https://news.kbs.co.kr/news/mobile/view/view.do?ncd=8455511
        # Desktop: https://news.kbs.co.kr/news/view.do?ncd=8455511
        if 'news.kbs.co.kr/news/mobile/view/view.do' in input_url:
            current_app.logger.info(f"Converting KBS Mobile URL: {input_url}")
            input_url = input_url.replace('/news/mobile/view/view.do', '/news/view.do')
            current_app.logger.info(f"Converted URL -> {input_url}")
        
        # General Mobile Cleanup for other sites if needed (e.g. m.youtube)
        if 'm.youtube.com' in input_url:
             input_url = input_url.replace('m.youtube.com', 'www.youtube.com')

        process_log = f"Processing Video URL: {input_url}"
        current_app.logger.info(process_log)
        
        try:
            filename = f"yt_{int(time.time())}.mp4"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # 2. Enhanced Options for Compatibility
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': filepath,
                'quiet': True,
                'noplaylist': True,
                'max_filesize': 100 * 1024 * 1024, # Increased to 100MB
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'referer': input_url,
                'ignoreerrors': True, # Skip errors in playlists
                'no_warnings': True,
                # 'force_generic_extractor': True, # Use this as last resort if needed
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(input_url, download=True)
                # handle generic extractor returning no file
                if not os.path.exists(filepath):
                     # Try to find if the filename is different (sometimes yt-dlp changes ext)
                     if info and 'ext' in info:
                         alt_filepath = filepath.replace('.mp4', f".{info['ext']}")
                         if os.path.exists(alt_filepath):
                             filepath = alt_filepath
                
            if not os.path.exists(filepath):
                 return jsonify({'error': 'Failed to download video. The URL might be unsupported or the video is private.'}), 400
                 
            file_hash = calculate_file_hash(filepath)
            cert_id = get_cert_id(file_hash, request.remote_addr)

            probability = detector.detect_deepfake(filepath)
            
            data = process_result(probability, cert_id, file_hash, input_url, lang)

            if os.path.exists(filepath):
                os.remove(filepath)
                
            return jsonify(data)

        except Exception as e:
            current_app.logger.error(f"Video Download Error: {e}")
            msg = str(e)
            if "Unsupported URL" in msg:
                msg = "Unsupported Video URL. Please try a direct video link or a major platform (YouTube, etc)."
            return jsonify({'error': msg}), 400

    # 2. Handle File Input (Existing)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not filename:
             filename = f"upload_{int(time.time())}.{file.filename.rsplit('.', 1)[1].lower()}"

        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            
            file_hash = calculate_file_hash(filepath)
            cert_id = get_cert_id(file_hash, request.remote_addr)

            probability = detector.detect_deepfake(filepath)
            
            data = process_result(probability, cert_id, file_hash, file.filename, lang)

            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify(data)
            
        except Exception as e:
            current_app.logger.error(f"Error processing file: {e}")
            if os.path.exists(filepath):
                 os.remove(filepath)
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'File type not allowed'}), 400

@main.route('/api/certificate')
def certificate():
    """
    Generate PDF Certificate based on last analysis result.
    """
    paid = request.args.get('paid') == 'true'
    analysis = session.get('last_analysis')
    
    # If no analysis, mock one for demo (or return 400)
    if not analysis:
        # Fallback for demo
        analysis = {
            'verdict': "Not Analyzed",
            'is_fake': False,
            'confidence': "N/A",
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'id': "DEMO-MODE"
        }
    
    # Check Issuance Limit (10 times Free)
    # Check Issuance Limit and Usage Count
    ip_address = request.remote_addr
    cert_id = analysis['id']
    analysis_uuid = analysis.get('analysis_uuid')
    file_hash = analysis.get('file_hash')
    original_filename = analysis.get('original_filename')
    
    # Check if this specific certificate was already issued (re-download)
    existing_cert = Certificate.query.filter_by(analysis_uuid=analysis_uuid).first()
    
    if not existing_cert:
        # Save new certificate record
        new_cert = Certificate(
            cert_id=cert_id,
            analysis_uuid=analysis_uuid,
            file_hash=file_hash,
            original_filename=original_filename,
            filename=f"Cert_{cert_id}",
            verdict=analysis['verdict'],
            confidence_score=analysis['confidence'],
            ip_address=ip_address,
            issued_at=datetime.datetime.utcnow()
        )
        db.session.add(new_cert)
        db.session.commit()
    
    # Check Usage Count for this ID
    usage_count = Certificate.query.filter_by(cert_id=cert_id).count()
    
    user_name = ""
    user_address = ""
    show_user_info = False

    # Rule: < 10 skip, >= 10 show
    if usage_count >= 10:
        show_user_info = True
        
        # Try to find existing info for this cert_id from previous entries
        last_info_cert = Certificate.query.filter(
            Certificate.cert_id == cert_id, 
            Certificate.user_name != None
        ).order_by(Certificate.issued_at.desc()).first()
        
        if last_info_cert:
            user_name = last_info_cert.user_name
            user_address = last_info_cert.user_address
        
        # Update with current request args if provided
        arg_name = request.args.get('user_name')
        arg_addr = request.args.get('user_address')
        
        if arg_name:
            user_name = arg_name
        if arg_addr:
            user_address = arg_addr
            
        # Save to current record if we have info
        current_cert = Certificate.query.filter_by(analysis_uuid=analysis_uuid).first()
        if current_cert and (arg_name or arg_addr):
            current_cert.user_name = user_name
            current_cert.user_address = user_address
            db.session.commit()
    
    # Language Selection
    lang = request.args.get('lang', 'US')
    
    # Translation Dictionary
    translations = {
        'US': {
            'title': "Certificate of Authenticity",
            'title_fake': "Deepfake Analysis Report",
            'subtitle': "Issued by Toubina AI Forensic Lab",
            'cert_id_label': "Certificate ID:",
            'body_text': "This document certifies that the analyzed media file<br>has undergone rigorous forensic deepfake detection analysis<br>using <strong>Toubina's Advanced AI Engine</strong>.",
            'date_label': "Analysis Date:",
            'verdict_label': "Analysis Verdict",
            'confidence_label': "Confidence Score:",
            'warning_text': "※ WARNING: Synthetic manipulation markers detected.",
            'disclaimer_cert': "This Certificate may be used for commercial purposes at the user’s own responsibility.",
            'disclaimer_report': "This Report may be used for commercial purposes at the user’s own responsibility.",
            'user_name_label': "User Name:",
            'user_address_label': "Address:",
            'signatory_name': "Hwang Yong Hun",
            'signatory_title': "Chief Technology Officer<br>AISolute Inc.",
            'verdict_real': "REAL / AUTHENTIC",
            'verdict_fake': "DEEPFAKE DETECTED"
        },
        'KR': {
            'title': "Certificate of Authenticity",
            'title_fake': "Deepfake Analysis Report",
            'subtitle': "Issued by Toubina AI Forensic Lab",
            'cert_id_label': "Certificate ID:",
            'body_text': "This document certifies that the analyzed media file<br>has undergone rigorous forensic deepfake detection analysis<br>using <strong>Toubina's Advanced AI Engine</strong>.",
            'date_label': "Analysis Date:",
            'verdict_label': "Analysis Verdict",
            'confidence_label': "Confidence Score:",
            'warning_text': "※ WARNING: Synthetic manipulation markers detected.",
            'disclaimer_cert': "This Certificate may be used for commercial purposes at the user’s own responsibility.",
            'disclaimer_report': "This Report may be used for commercial purposes at the user’s own responsibility.",
            'user_name_label': "User Name:",
            'user_address_label': "Address:",
            'signatory_name': "Hwang Yong Hun",
            'signatory_title': "Chief Technology Officer<br>AISolute Inc.",
            'verdict_real': "REAL / AUTHENTIC",
            'verdict_fake': "DEEPFAKE DETECTED"
        }
    }
    
    t = translations.get(lang, translations['US'])

    # Determine Verdict Text Dynamically
    if analysis['is_fake']:
        title = t['title_fake']
        color = "#ef4444" # Red
        disclaimer = t['disclaimer_report']
        verdict_text = t['verdict_fake']
    else:
        title = t['title']
        color = "#28a745" # Green
        disclaimer = t['disclaimer_cert']
        verdict_text = t['verdict_real']
        
    # ... (Previous code) ...

    rendered = render_template('certificate_view.html', 
                               t=t,
                               title=title,
                               cert_id=analysis['id'],
                               date=analysis['date'],
                               verdict=verdict_text, 
                               confidence=analysis['confidence'],
                               color=color,
                               disclaimer=disclaimer,
                               is_fake=analysis['is_fake'],
                               show_user_info=show_user_info,
                               show_signature=(usage_count >= 10),
                               user_name=user_name,
                               user_address=user_address)
                               
    if not pisa:
        return rendered 
    
    pdf = BytesIO()
    
    # Generate PDF with link_callback
    try:
        pisa_status = pisa.CreatePDF(
            BytesIO(rendered.encode('utf-8')), 
            dest=pdf,
            link_callback=link_callback,
            encoding='UTF-8'
        )
        if pisa_status.err:
            raise Exception("Pisa reported errors")
    except Exception as e:
        current_app.logger.error(f"PDF Generation failed: {e}")
        return "PDF Generation Error", 500
        
    pdf.seek(0)
    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    
    filename = "Analysis_Report.pdf" if analysis['is_fake'] else "Toubina_Certificate.pdf"
    if paid:
        filename = filename.replace(".pdf", "_Premium.pdf")
        
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@main.route('/api/create-promo', methods=['POST'])
def create_promo():
    """
    Generate a promo video using FFMPEG/OpenCV if available.
    Since we can't browse, we'll create a text-based animation video or use a placeholder image.
    """
    try:
        import cv2
        import numpy as np
    except:
        return jsonify({'error': 'OpenCV not available for video generation'}), 500

    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'toubina_promo.mp4')
    
    # Create a simple video: Black background with text "Toubina AI"
    # Specs
    width, height = 1280, 720
    fps = 30
    seconds = 5
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for i in range(fps * seconds):
        # Frame background
        frame = np.zeros((height, width, 3), dtype='uint8')
        
        # Color gradient effect
        t = i / (fps * seconds) # 0 to 1
        color = (int(255 * t), int(50 + 100*t), 200)
        
        cv2.putText(frame, "TOUBINA", (400, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5)
        cv2.putText(frame, "Deepfake Detection", (480, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.putText(frame, "aisolute.com", (550, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150,150,150), 1)
        
        out.write(frame)
        
    out.release()
    
    return jsonify({'message': 'Promo video created', 'file_url': '/download-promo'})

@main.route('/download-promo')
def download_promo():
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'toubina_promo.mp4')
    from flask import send_file
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Promo video not found", 404

@main.route('/api/upload-youtube', methods=['POST'])
def upload_youtube():
    """
    Mock endpoint to simulate YouTube upload locally since we don't have user tokens.
    In production, this would use google-auth-oauthlib and youtube data api.
    """
    # Simulate process
    time.sleep(2) 
    return jsonify({
        'success': True, 
        'message': 'Upload Authorized! (Simulation)',
        'info': 'To upload to real YouTube, download our "youtube_uploader.py" script and allow permission.'
    })

@main.route('/api/upload-instagram', methods=['POST'])
def upload_instagram():
    """
    Mock endpoint to simulate Instagram Reels upload.
    Real implementation requires private API wrappers like 'instagrapi' or official Graph API (Business).
    """
    time.sleep(2.5)
    return jsonify({
        'success': True,
        'message': 'Successfully scheduled for Instagram Reels! (Simulation)\n\nNote: For automated posting to personal accounts, we recommend using the "instagrapi" Python library with our generated video.'
    })

@main.route('/api/upload-tiktok', methods=['POST'])
def upload_tiktok():
    """
    Mock endpoint to simulate TikTok upload.
    Real implementation requires 'TikTokAPI' (unofficial) or TikTok Developers API.
    """
    time.sleep(2)
    return jsonify({
        'success': True,
        'message': 'Successfully uploaded to TikTok! (Simulation)\n\nFor real automation, integration with the official TikTok for Business API is recommended.'
    })


