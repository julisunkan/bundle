import json
import os
from datetime import datetime, timedelta

DATA_FILE = 'flashcards_data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        return {
            'decks': [],
            'study_sessions': [],
            'quiz_results': [],
            'badges': [],
            'next_deck_id': 1,
            'next_card_id': 1,
            'next_session_id': 1,
            'next_quiz_id': 1
        }
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if 'next_deck_id' not in data:
                data['next_deck_id'] = 1
            if 'next_card_id' not in data:
                data['next_card_id'] = 1
            if 'next_session_id' not in data:
                data['next_session_id'] = 1
            if 'next_quiz_id' not in data:
                data['next_quiz_id'] = 1
            if 'study_sessions' not in data:
                data['study_sessions'] = []
            if 'quiz_results' not in data:
                data['quiz_results'] = []
            if 'badges' not in data:
                data['badges'] = []
            return data
    except (json.JSONDecodeError, IOError):
        return {
            'decks': [],
            'study_sessions': [],
            'quiz_results': [],
            'badges': [],
            'next_deck_id': 1,
            'next_card_id': 1,
            'next_session_id': 1,
            'next_quiz_id': 1
        }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init_db():
    data = get_data()
    if not data['badges']:
        data['badges'] = [
            {'id': 1, 'name': 'First Steps', 'description': 'Study your first flashcard', 'icon': '🎯', 'requirement': 1, 'earned': False, 'earned_at': None},
            {'id': 2, 'name': 'Beginner', 'description': 'Study 10 flashcards', 'icon': '📚', 'requirement': 10, 'earned': False, 'earned_at': None},
            {'id': 3, 'name': 'Scholar', 'description': 'Study 50 flashcards', 'icon': '🎓', 'requirement': 50, 'earned': False, 'earned_at': None},
            {'id': 4, 'name': 'Expert', 'description': 'Study 100 flashcards', 'icon': '👨‍🎓', 'requirement': 100, 'earned': False, 'earned_at': None},
            {'id': 5, 'name': 'Master', 'description': 'Study 500 flashcards', 'icon': '🏆', 'requirement': 500, 'earned': False, 'earned_at': None},
            {'id': 6, 'name': 'Quiz Starter', 'description': 'Complete your first quiz', 'icon': '✅', 'requirement': 1, 'earned': False, 'earned_at': None},
            {'id': 7, 'name': 'Perfect Score', 'description': 'Get 100% on a quiz', 'icon': '💯', 'requirement': 1, 'earned': False, 'earned_at': None},
            {'id': 8, 'name': 'Consistent Learner', 'description': 'Study 7 days in a row', 'icon': '🔥', 'requirement': 7, 'earned': False, 'earned_at': None},
        ]
    
    max_deck_id = max([d.get('id', 0) for d in data.get('decks', [])] + [0])
    max_card_id = 0
    for deck in data.get('decks', []):
        for card in deck.get('cards', []):
            if card.get('id', 0) > max_card_id:
                max_card_id = card.get('id', 0)
    
    data['next_deck_id'] = max(data.get('next_deck_id', 1), max_deck_id + 1)
    data['next_card_id'] = max(data.get('next_card_id', 1), max_card_id + 1)
    
    save_data(data)

class Deck:
    @staticmethod
    def create(name, description='', category='General'):
        data = get_data()
        deck_id = data['next_deck_id']
        data['next_deck_id'] += 1
        
        new_deck = {
            'id': deck_id,
            'name': name,
            'description': description,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'cards': []
        }
        data['decks'].append(new_deck)
        save_data(data)
        return deck_id

    @staticmethod
    def get_all():
        data = get_data()
        decks = []
        for deck in data.get('decks', []):
            decks.append({
                'id': deck['id'],
                'name': deck['name'],
                'description': deck.get('description', ''),
                'category': deck.get('category', 'General'),
                'card_count': len(deck.get('cards', [])),
                'created_at': deck.get('created_at', '')
            })
        return sorted(decks, key=lambda x: x.get('created_at', ''), reverse=True)

    @staticmethod
    def get_by_id(deck_id):
        data = get_data()
        for deck in data.get('decks', []):
            if deck['id'] == deck_id or str(deck['id']) == str(deck_id):
                return {
                    'id': deck['id'],
                    'name': deck['name'],
                    'description': deck.get('description', ''),
                    'category': deck.get('category', 'General'),
                    'card_count': len(deck.get('cards', [])),
                    'created_at': deck.get('created_at', '')
                }
        return None

    @staticmethod
    def delete(deck_id):
        data = get_data()
        data['decks'] = [d for d in data['decks'] if d['id'] != deck_id and str(d['id']) != str(deck_id)]
        data['study_sessions'] = [s for s in data.get('study_sessions', []) if s.get('deck_id') != deck_id]
        data['quiz_results'] = [q for q in data.get('quiz_results', []) if q.get('deck_id') != deck_id]
        save_data(data)

class Card:
    @staticmethod
    def create(deck_id, question, answer, choices=None):
        data = get_data()
        card_id = data['next_card_id']
        data['next_card_id'] += 1
        
        choices_data = None
        if choices:
            if isinstance(choices, str):
                try:
                    choices_data = json.loads(choices)
                except json.JSONDecodeError:
                    choices_data = None
            elif isinstance(choices, list):
                choices_data = choices
        
        new_card = {
            'id': card_id,
            'question': question,
            'answer': answer,
            'choices': choices_data,
            'difficulty': 0,
            'created_at': datetime.now().isoformat()
        }
        
        for deck in data['decks']:
            if deck['id'] == deck_id or str(deck['id']) == str(deck_id):
                if 'cards' not in deck:
                    deck['cards'] = []
                deck['cards'].append(new_card)
                break
        
        session_id = data['next_session_id']
        data['next_session_id'] += 1
        data['study_sessions'].append({
            'id': session_id,
            'card_id': card_id,
            'deck_id': deck_id,
            'easiness_factor': 2.5,
            'interval': 0,
            'repetitions': 0,
            'next_review': datetime.now().isoformat(),
            'last_reviewed': None
        })
        
        save_data(data)
        return card_id

    @staticmethod
    def get_by_deck(deck_id):
        data = get_data()
        for deck in data.get('decks', []):
            if deck['id'] == deck_id or str(deck['id']) == str(deck_id):
                cards = []
                for card in deck.get('cards', []):
                    session = None
                    for s in data.get('study_sessions', []):
                        if s.get('card_id') == card.get('id'):
                            session = s
                            break
                    
                    cards.append({
                        'id': card.get('id'),
                        'deck_id': deck_id,
                        'question': card.get('question', ''),
                        'answer': card.get('answer', ''),
                        'choices': card.get('choices'),
                        'difficulty': card.get('difficulty', 0),
                        'created_at': card.get('created_at', ''),
                        'easiness_factor': session.get('easiness_factor', 2.5) if session else 2.5,
                        'interval': session.get('interval', 0) if session else 0,
                        'repetitions': session.get('repetitions', 0) if session else 0,
                        'next_review': session.get('next_review') if session else None
                    })
                return cards
        return []

    @staticmethod
    def get_due_cards(deck_id):
        data = get_data()
        now = datetime.now().isoformat()
        cards = Card.get_by_deck(deck_id)
        due_cards = []
        for card in cards:
            next_review = card.get('next_review')
            if next_review is None or next_review <= now:
                due_cards.append(card)
        return due_cards

    @staticmethod
    def delete(card_id):
        data = get_data()
        for deck in data['decks']:
            deck['cards'] = [c for c in deck.get('cards', []) if c.get('id') != card_id]
        data['study_sessions'] = [s for s in data.get('study_sessions', []) if s.get('card_id') != card_id]
        save_data(data)

    @staticmethod
    def clear_for_deck(deck_id):
        data = get_data()
        card_ids_to_remove = []
        for deck in data['decks']:
            if deck['id'] == deck_id or str(deck['id']) == str(deck_id):
                card_ids_to_remove = [c.get('id') for c in deck.get('cards', [])]
                deck['cards'] = []
                break
        data['study_sessions'] = [s for s in data.get('study_sessions', []) 
                                   if s.get('card_id') not in card_ids_to_remove]
        save_data(data)

class StudySession:
    @staticmethod
    def update(card_id, quality):
        from srs_algorithm import sm2_algorithm
        
        data = get_data()
        
        for session in data.get('study_sessions', []):
            if session.get('card_id') == card_id:
                ef = session.get('easiness_factor', 2.5)
                interval = session.get('interval', 0)
                reps = session.get('repetitions', 0)
                
                new_ef, new_interval, new_reps = sm2_algorithm(quality, ef, interval, reps)
                
                session['easiness_factor'] = new_ef
                session['interval'] = new_interval
                session['repetitions'] = new_reps
                session['next_review'] = (datetime.now() + timedelta(days=new_interval)).isoformat()
                session['last_reviewed'] = datetime.now().isoformat()
                break
        
        save_data(data)

    @staticmethod
    def get_stats():
        data = get_data()
        
        total_studied = sum(1 for s in data.get('study_sessions', []) if s.get('last_reviewed'))
        
        now = datetime.now().isoformat()
        due_today = sum(1 for s in data.get('study_sessions', []) 
                       if s.get('next_review') and s.get('next_review') <= now)
        
        efs = [s.get('easiness_factor', 2.5) for s in data.get('study_sessions', []) if s.get('last_reviewed')]
        avg_ef = sum(efs) / len(efs) if efs else 0
        
        return {
            'total_studied': total_studied,
            'due_today': due_today,
            'average_retention': round(avg_ef, 2)
        }

class QuizResult:
    @staticmethod
    def save(deck_id, score, total):
        data = get_data()
        quiz_id = data['next_quiz_id']
        data['next_quiz_id'] += 1
        
        data['quiz_results'].append({
            'id': quiz_id,
            'deck_id': deck_id,
            'score': score,
            'total': total,
            'completed_at': datetime.now().isoformat()
        })
        save_data(data)

    @staticmethod
    def get_by_deck(deck_id):
        data = get_data()
        results = [r for r in data.get('quiz_results', []) 
                  if r.get('deck_id') == deck_id or str(r.get('deck_id')) == str(deck_id)]
        return sorted(results, key=lambda x: x.get('completed_at', ''), reverse=True)[:10]

class Badge:
    @staticmethod
    def check_and_award():
        data = get_data()
        
        cards_studied = sum(1 for s in data.get('study_sessions', []) if s.get('last_reviewed'))
        quizzes_completed = len(data.get('quiz_results', []))
        
        newly_earned = []
        for badge in data.get('badges', []):
            if badge.get('earned'):
                continue
                
            if badge['name'] in ['First Steps', 'Beginner', 'Scholar', 'Expert', 'Master']:
                if cards_studied >= badge['requirement']:
                    badge['earned'] = True
                    badge['earned_at'] = datetime.now().isoformat()
                    newly_earned.append(badge['name'])
            
            elif badge['name'] == 'Quiz Starter' and quizzes_completed >= 1:
                badge['earned'] = True
                badge['earned_at'] = datetime.now().isoformat()
                newly_earned.append(badge['name'])
            
            elif badge['name'] == 'Perfect Score':
                for result in data.get('quiz_results', []):
                    if result.get('score') == result.get('total'):
                        badge['earned'] = True
                        badge['earned_at'] = datetime.now().isoformat()
                        newly_earned.append(badge['name'])
                        break
        
        save_data(data)
        return newly_earned

    @staticmethod
    def get_all():
        data = get_data()
        return sorted(data.get('badges', []), key=lambda x: x.get('requirement', 0))
