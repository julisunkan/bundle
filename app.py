import os
import secrets
import hashlib
import threading
import time
import requests
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import json
import csv
from io import StringIO
from datetime import datetime, timedelta

from models import init_db, Deck, Card, StudySession, QuizResult, Badge
from ai_service import generate_summary, generate_flashcards, generate_multiple_choice
from utils import process_pdf_file, allowed_file, clean_text
from pdf_generator import generate_flashcards_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
admin_tokens = {}

def generate_admin_token():
    token = secrets.token_hex(32)
    admin_tokens[token] = datetime.now() + timedelta(hours=24)
    return token

def verify_admin_token(token):
    if token in admin_tokens:
        if datetime.now() < admin_tokens[token]:
            return True
        else:
            del admin_tokens[token]
    return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        token = auth_header[7:]
        if not verify_admin_token(token):
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_header(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/decks', methods=['GET', 'POST'])
def handle_decks():
    if request.method == 'GET':
        # Get decks from database
        db_decks = Deck.get_all()
        
        # Get decks from JSON
        json_decks = []
        json_file = 'flashcards_data.json'
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    flash_data = json.load(f)
                
                for deck in flash_data.get('decks', []):
                    json_decks.append({
                        'id': deck['id'],
                        'name': deck['name'],
                        'description': f"Generated deck - {len(deck['cards'])} cards",
                        'category': deck.get('category', 'General'),
                        'card_count': len(deck['cards']),
                        'created_at': deck.get('created_at', '')
                    })
            except Exception as e:
                print(f"Error loading JSON decks: {e}")
        
        # Merge decks, prioritizing JSON decks
        all_decks = {deck['id']: deck for deck in db_decks}
        for deck in json_decks:
            all_decks[deck['id']] = deck
        
        return jsonify(list(all_decks.values()))
    
    elif request.method == 'POST':
        data = request.json
        deck_id = Deck.create(data['name'], data.get('description', ''), data.get('category', 'General'))
        return jsonify({'id': deck_id, 'message': 'Deck created successfully'})

@app.route('/api/decks/<int:deck_id>', methods=['GET'])
def handle_deck(deck_id):
    deck = Deck.get_by_id(deck_id)
    if deck:
        return jsonify(deck)
    return jsonify({'error': 'Deck not found'}), 404

@app.route('/api/decks/<int:deck_id>/cards', methods=['GET', 'POST'])
def handle_cards(deck_id):
    if request.method == 'GET':
        # Try to load from JSON first
        json_cards = load_cards_from_json(deck_id)
        
        # If JSON cards exist, return them
        if json_cards is not None and len(json_cards) > 0:
            return jsonify(json_cards)
        
        # Otherwise fall back to database
        db_cards = Card.get_by_deck(deck_id)
        return jsonify(db_cards)
    
    elif request.method == 'POST':
        if not request.json:
            return jsonify({'error': 'Invalid request'}), 400
        
        data = request.json
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        if len(question) > 1000 or len(answer) > 2000:
            return jsonify({'error': 'Question or answer too long'}), 400
        
        try:
            card_id = Card.create(
                deck_id,
                question,
                answer,
                data.get('choices')
            )
            return jsonify({'id': card_id, 'message': 'Card created successfully'})
        except Exception as e:
            return jsonify({'error': 'Failed to create card'}), 500

@app.route('/api/save-flashcards-json', methods=['POST'])
def save_flashcards_json():
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    data = request.json
    deck_id = data.get('deck_id')
    deck_name = data.get('deck_name')
    category = data.get('category', 'General')
    cards = data.get('cards', [])
    
    if not deck_id or not deck_name or not cards:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Load existing data
        json_file = 'flashcards_data.json'
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                flash_data = json.load(f)
        else:
            flash_data = {'decks': []}
        
        # Add new deck
        deck_entry = {
            'id': deck_id,
            'name': deck_name,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'cards': cards
        }
        
        # Remove existing deck with same ID if exists
        flash_data['decks'] = [d for d in flash_data['decks'] if d['id'] != deck_id]
        flash_data['decks'].append(deck_entry)
        
        # Save to file
        with open(json_file, 'w') as f:
            json.dump(flash_data, f, indent=2)
        
        return jsonify({'message': 'Flashcards saved successfully', 'count': len(cards)})
    except Exception as e:
        return jsonify({'error': f'Failed to save: {str(e)}'}), 500

def load_cards_from_json(deck_id):
    """Load cards from JSON file for a specific deck"""
    json_file = 'flashcards_data.json'
    if not os.path.exists(json_file):
        print(f"JSON file not found: {json_file}")
        return None
    
    try:
        with open(json_file, 'r') as f:
            flash_data = json.load(f)
        
        print(f"Looking for deck_id {deck_id} in JSON")
        print(f"Available decks: {[d.get('id') for d in flash_data.get('decks', [])]}")
        
        for deck in flash_data.get('decks', []):
            # Try both int and string comparison
            if deck.get('id') == deck_id or str(deck.get('id')) == str(deck_id):
                print(f"Found deck {deck_id} with {len(deck.get('cards', []))} cards")
                
                # Format cards to match database format
                formatted_cards = []
                for i, card in enumerate(deck.get('cards', [])):
                    formatted_card = {
                        'id': i + 1,
                        'deck_id': deck_id,
                        'question': card.get('question', ''),
                        'answer': card.get('answer', ''),
                        'choices': json.dumps(card['choices']) if card.get('choices') else None,
                        'difficulty': 'medium',
                        'created_at': deck.get('created_at', ''),
                        'next_review': deck.get('created_at', '')
                    }
                    formatted_cards.append(formatted_card)
                
                print(f"Returning {len(formatted_cards)} formatted cards")
                return formatted_cards
        
        print(f"Deck {deck_id} not found in JSON")
        return None
    except Exception as e:
        print(f"Error loading cards from JSON: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/api/process-text', methods=['POST'])
def process_text():
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    data = request.json
    text = clean_text(data.get('text', ''))
    action = data.get('action', 'flashcards')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if len(text) < 50:
        return jsonify({'error': 'Text too short. Please provide at least 50 characters.'}), 400
    
    try:
        user_api_key = data.get('api_key')
        
        if action == 'summary':
            result = generate_summary(text, user_api_key=user_api_key)
            return jsonify({'summary': result})
        
        elif action == 'flashcards':
            num_cards = min(int(data.get('num_cards', 10)), 50)
            flashcards = generate_flashcards(text, num_cards, user_api_key=user_api_key)
            return jsonify({'flashcards': flashcards})
        
        elif action == 'multiple_choice':
            num_questions = min(int(data.get('num_questions', 5)), 25)
            questions = generate_multiple_choice(text, num_questions, user_api_key=user_api_key)
            return jsonify({'questions': questions})
        
        else:
            return jsonify({'error': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to process text'}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
    
    if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 400
    
    filename = secure_filename(file.filename)
    import uuid
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    try:
        file.save(filepath)
        
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return jsonify({'error': 'File upload failed'}), 500
        
        if os.path.getsize(filepath) > 16 * 1024 * 1024:
            os.remove(filepath)
            return jsonify({'error': 'File too large'}), 400
        
        text = process_pdf_file(filepath)
        
        os.remove(filepath)
        
        if text and len(text.strip()) > 0:
            return jsonify({'text': clean_text(text), 'message': 'PDF processed successfully'})
        else:
            return jsonify({'error': 'Could not extract text from PDF. File may be scanned or empty.'}), 400
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': 'Error processing PDF. Please try again.'}), 500

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    import google.generativeai as genai
    
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    api_key = request.json.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 400
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    try:
        genai.configure(api_key=api_key)
        test_model = genai.GenerativeModel('gemini-2.0-flash')
        
        response = test_model.generate_content("Say hello")
        
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        
        return jsonify({'message': 'API key is valid', 'test_response': response.text})
    except Exception as e:
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        return jsonify({'error': f'API key test failed: {str(e)}'}), 400

@app.route('/api/study/<int:card_id>', methods=['POST'])
def study_card(card_id):
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    data = request.json
    quality = data.get('quality', 3)
    
    try:
        quality = int(quality)
        if quality < 0 or quality > 5:
            return jsonify({'error': 'Quality must be between 0 and 5'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quality value'}), 400
    
    try:
        StudySession.update(card_id, quality)
        newly_earned = Badge.check_and_award()
        
        return jsonify({
            'message': 'Study session recorded',
            'badges_earned': newly_earned
        })
    except Exception as e:
        return jsonify({'error': 'Failed to record study session'}), 500

@app.route('/api/decks/<int:deck_id>/due-cards', methods=['GET'])
def get_due_cards(deck_id):
    cards = Card.get_due_cards(deck_id)
    return jsonify(cards)

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/quiz-results', methods=['POST'])
def save_quiz_result():
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    data = request.json
    
    try:
        deck_id = int(data.get('deck_id', 0))
        score = int(data.get('score', 0))
        total = int(data.get('total', 0))
        
        if deck_id <= 0 or score < 0 or total <= 0 or score > total:
            return jsonify({'error': 'Invalid quiz data'}), 400
        
        QuizResult.save(deck_id, score, total)
        newly_earned = Badge.check_and_award()
        
        return jsonify({
            'message': 'Quiz result saved',
            'badges_earned': newly_earned
        })
    except (ValueError, TypeError, KeyError) as e:
        return jsonify({'error': 'Invalid request data'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to save quiz result'}), 500

@app.route('/api/decks/<int:deck_id>/quiz-results', methods=['GET'])
def get_quiz_results(deck_id):
    results = QuizResult.get_by_deck(deck_id)
    return jsonify(results)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = StudySession.get_stats()
    return jsonify(stats)

@app.route('/api/badges', methods=['GET'])
def get_badges():
    badges = Badge.get_all()
    return jsonify(badges)

@app.route('/api/export/<int:deck_id>/<format>', methods=['GET'])
def export_deck(deck_id, format):
    deck = Deck.get_by_id(deck_id)
    cards = Card.get_by_deck(deck_id)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    # Sanitize filename
    safe_deck_name = "".join(c for c in deck['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
    
    if format == 'json':
        data = {
            'deck': deck,
            'cards': cards
        }
        from flask import Response
        import json as json_lib
        
        response = Response(
            json_lib.dumps(data, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename={safe_deck_name or "deck"}.json'
            }
        )
        return response
    
    elif format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Question', 'Answer'])
        
        for card in cards:
            writer.writerow([card['question'], card['answer']])
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename={safe_deck_name or "deck"}.csv'
        }
    
    elif format == 'anki':
        output = StringIO()
        for card in cards:
            output.write(f"{card['question']}\t{card['answer']}\n")
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/plain',
            'Content-Disposition': f'attachment; filename={safe_deck_name or "deck"}_anki.txt'
        }
    
    elif format == 'pdf':
        # Convert cards to the format expected by PDF generator
        pdf_cards = []
        for card in cards:
            pdf_card = {
                'question': card['question'],
                'answer': card['answer']
            }
            if card.get('choices'):
                try:
                    pdf_card['choices'] = json.loads(card['choices'])
                except:
                    pass
            pdf_cards.append(pdf_card)
        
        try:
            pdf_buffer = generate_flashcards_pdf(pdf_cards, deck['name'])
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{safe_deck_name or 'deck'}_flashcards.pdf"
            )
        except Exception as e:
            print(f"PDF generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/export-cards-pdf', methods=['POST'])
def export_cards_pdf():
    """Export generated cards to PDF"""
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    cards = request.json.get('cards', [])
    deck_name = request.json.get('deck_name', 'Flashcards')
    
    # Validate input
    if not cards or not isinstance(cards, list):
        return jsonify({'error': 'No cards provided'}), 400
    
    if len(cards) > 100:
        return jsonify({'error': 'Cannot export more than 100 cards at once'}), 400
    
    if not isinstance(deck_name, str):
        deck_name = 'Flashcards'
    
    # Validate total payload size
    total_size = len(str(cards))
    if total_size > 1_000_000:  # 1MB limit for total payload
        return jsonify({'error': 'Payload too large'}), 400
    
    # Validate each card structure
    for i, card in enumerate(cards):
        if not isinstance(card, dict):
            return jsonify({'error': f'Card {i+1} is invalid'}), 400
        
        if 'question' not in card or 'answer' not in card:
            return jsonify({'error': f'Card {i+1} is missing required fields'}), 400
        
        if not isinstance(card['question'], str) or not isinstance(card['answer'], str):
            return jsonify({'error': f'Card {i+1} has invalid field types'}), 400
        
        # Trim and validate length
        question = card['question'].strip()
        answer = card['answer'].strip()
        
        if not question or not answer:
            return jsonify({'error': f'Card {i+1} has empty question or answer'}), 400
        
        if len(question) > 10000 or len(answer) > 10000:
            return jsonify({'error': f'Card {i+1} fields are too long (max 10,000 characters)'}), 400
        
        # Update card with trimmed values
        card['question'] = question
        card['answer'] = answer
        
        # Validate choices if present
        if 'choices' in card:
            if not isinstance(card['choices'], list):
                return jsonify({'error': f'Card {i+1} has invalid choices format'}), 400
            
            if len(card['choices']) > 10:
                return jsonify({'error': f'Card {i+1} has too many choices (max 10)'}), 400
            
            trimmed_choices = []
            for choice in card['choices']:
                if not isinstance(choice, str):
                    return jsonify({'error': f'Card {i+1} has invalid choice format'}), 400
                
                trimmed_choice = choice.strip()
                if not trimmed_choice:
                    return jsonify({'error': f'Card {i+1} has empty choice'}), 400
                
                if len(trimmed_choice) > 5000:
                    return jsonify({'error': f'Card {i+1} has choice that is too long (max 5,000 characters)'}), 400
                
                trimmed_choices.append(trimmed_choice)
            
            card['choices'] = trimmed_choices
    
    try:
        pdf_buffer = generate_flashcards_pdf(cards, deck_name)
        
        # Sanitize filename
        safe_filename = "".join(c for c in deck_name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_filename or 'Flashcards'}_flashcards.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to generate PDF. Please try again.'}), 500

@app.route('/deck/<int:deck_id>')
def deck_page(deck_id):
    return render_template('deck.html', deck_id=deck_id)

@app.route('/study/<int:deck_id>')
def study_page(deck_id):
    return render_template('study.html', deck_id=deck_id)

@app.route('/quiz/<int:deck_id>')
def quiz_page(deck_id):
    return render_template('quiz.html', deck_id=deck_id)

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/privacy')
def privacy_page():
    return render_template('privacy.html')

@app.route('/terms')
def terms_page():
    return render_template('terms.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/sw.js')
def service_worker():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/ads.txt')
def ads_txt():
    return send_file('ads.txt', mimetype='text/plain')

@app.route('/manifest.json')
def manifest():
    return send_file('static/manifest.json', mimetype='application/manifest+json')

@app.route('/xadmin7829')
def admin_page():
    return render_template('admin.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    password = request.json.get('password', '')
    
    if password == ADMIN_PASSWORD:
        token = generate_admin_token()
        return jsonify({'token': token, 'message': 'Login successful'})
    
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/admin/verify', methods=['GET'])
def admin_verify():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = auth_header[7:]
    if verify_admin_token(token):
        return jsonify({'valid': True})
    
    return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/admin/decks/<int:deck_id>', methods=['DELETE'])
def admin_delete_deck(deck_id):
    try:
        Deck.delete(deck_id)
        
        json_file = 'flashcards_data.json'
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    flash_data = json.load(f)
                
                flash_data['decks'] = [d for d in flash_data.get('decks', []) if d.get('id') != deck_id and str(d.get('id')) != str(deck_id)]
                
                with open(json_file, 'w') as f:
                    json.dump(flash_data, f, indent=2)
            except Exception as e:
                print(f"Error removing deck from JSON: {e}")
        
        return jsonify({'message': 'Deck deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Failed to delete deck'}), 500

@app.route('/api/admin/cards/<int:card_id>', methods=['DELETE'])
def admin_delete_card(card_id):
    try:
        Card.delete(card_id)
        
        deck_id = request.args.get('deck_id')
        if deck_id:
            json_file = 'flashcards_data.json'
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        flash_data = json.load(f)
                    
                    for deck in flash_data.get('decks', []):
                        if str(deck.get('id')) == str(deck_id):
                            cards = deck.get('cards', [])
                            if 0 < card_id <= len(cards):
                                cards.pop(card_id - 1)
                                deck['cards'] = cards
                            break
                    
                    with open(json_file, 'w') as f:
                        json.dump(flash_data, f, indent=2)
                except Exception as e:
                    print(f"Error removing card from JSON: {e}")
        
        return jsonify({'message': 'Card deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Failed to delete card'}), 500

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Route not found'}), 404
    
    from flask import redirect
    return redirect('/')

@app.route('/api/ping')
def ping():
    return jsonify({'status': 'alive', 'timestamp': datetime.now().isoformat()})

def keep_alive():
    while True:
        time.sleep(300)
        try:
            requests.get('http://localhost:5000/api/ping', timeout=10)
            print(f"[Keep-Alive] Ping successful at {datetime.now().isoformat()}")
        except Exception as e:
            print(f"[Keep-Alive] Ping failed: {e}")

if __name__ == '__main__':
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("[Keep-Alive] Self-ping started (every 5 minutes)")
    app.run(host='0.0.0.0', port=5000, debug=True)
