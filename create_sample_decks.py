
from models import Deck, Card

def create_sample_decks():
    """Create five sample flashcard decks with content"""
    
    # Medicine Deck
    medicine_deck_id = Deck.create("Medicine", "Essential medical knowledge and terminology")
    medicine_cards = [
        ("What is the largest organ in the human body?", "The skin, covering approximately 20 square feet in adults"),
        ("What is the normal resting heart rate for adults?", "60-100 beats per minute"),
        ("What does MRI stand for?", "Magnetic Resonance Imaging"),
        ("What is the function of red blood cells?", "Transport oxygen from lungs to tissues and carbon dioxide back to lungs"),
        ("What is hypertension?", "High blood pressure, typically defined as readings consistently above 140/90 mmHg"),
        ("What is the hippocratic oath?", "An ethical code sworn by physicians pledging to practice medicine honestly"),
        ("What causes Type 1 diabetes?", "The pancreas produces little or no insulin due to autoimmune destruction of beta cells"),
        ("What is the difference between bacteria and viruses?", "Bacteria are single-celled organisms that can reproduce independently; viruses require host cells to replicate"),
        ("What is anemia?", "A condition where the blood lacks adequate healthy red blood cells or hemoglobin"),
        ("What is the function of the liver?", "Filters toxins, produces bile, stores vitamins, regulates blood clotting, and metabolizes nutrients")
    ]
    
    for question, answer in medicine_cards:
        Card.create(medicine_deck_id, question, answer)
    
    # Geography Deck
    geography_deck_id = Deck.create("Geography", "World geography facts and locations")
    geography_cards = [
        ("What is the largest ocean on Earth?", "The Pacific Ocean, covering approximately 165 million square kilometers"),
        ("What is the longest river in the world?", "The Nile River at approximately 6,650 kilometers"),
        ("What is the highest mountain peak?", "Mount Everest at 8,849 meters (29,032 feet) above sea level"),
        ("What is a peninsula?", "A piece of land surrounded by water on three sides"),
        ("What causes tides?", "The gravitational pull of the moon and sun on Earth's oceans"),
        ("What is the equator?", "An imaginary line at 0° latitude dividing Earth into Northern and Southern hemispheres"),
        ("What is the largest desert in the world?", "Antarctica (largest cold desert); Sahara (largest hot desert)"),
        ("What is a tectonic plate?", "Large slabs of Earth's lithosphere that move and interact, causing earthquakes and mountain formation"),
        ("What is the Ring of Fire?", "A horseshoe-shaped belt in the Pacific Ocean with frequent earthquakes and volcanic eruptions"),
        ("What is the difference between weather and climate?", "Weather is short-term atmospheric conditions; climate is long-term average weather patterns")
    ]
    
    for question, answer in geography_cards:
        Card.create(geography_deck_id, question, answer)
    
    # Architecture Deck
    architecture_deck_id = Deck.create("Architecture", "Architectural styles, terms, and history")
    architecture_cards = [
        ("What is a flying buttress?", "An external support structure that transfers roof weight to outer supports, common in Gothic architecture"),
        ("What defines Art Deco architecture?", "Bold geometric shapes, rich colors, lavish ornamentation, and streamlined forms from the 1920s-1930s"),
        ("What is a cantilever?", "A projecting beam or structure supported at only one end"),
        ("What is the Golden Ratio in architecture?", "A mathematical ratio of 1:1.618 believed to create aesthetically pleasing proportions"),
        ("What is Brutalism?", "An architectural style featuring raw concrete, angular geometric shapes, and massive forms from the 1950s-1970s"),
        ("What is a keystone?", "The central wedge-shaped stone at the top of an arch that locks all stones in place"),
        ("What is the difference between Doric, Ionic, and Corinthian columns?", "Doric: simple, no base; Ionic: scrolled capitals; Corinthian: ornate with acanthus leaves"),
        ("What is sustainable architecture?", "Design that minimizes environmental impact through energy efficiency, renewable materials, and reduced waste"),
        ("What is a facade?", "The front exterior face or elevation of a building"),
        ("What is the Bauhaus movement?", "A German school (1919-1933) emphasizing function, simplicity, and integration of art, craft, and technology")
    ]
    
    for question, answer in architecture_cards:
        Card.create(architecture_deck_id, question, answer)
    
    # Economics Deck
    economics_deck_id = Deck.create("Economics", "Economic principles and concepts")
    economics_cards = [
        ("What is GDP?", "Gross Domestic Product: the total monetary value of all goods and services produced in a country during a specific period"),
        ("What is inflation?", "The rate at which the general level of prices for goods and services rises, reducing purchasing power"),
        ("What is supply and demand?", "Economic model: supply is quantity producers offer; demand is quantity consumers want; price balances both"),
        ("What is a recession?", "A significant decline in economic activity lasting more than a few months, typically shown by falling GDP"),
        ("What is monetary policy?", "Central bank actions controlling money supply and interest rates to influence economic activity"),
        ("What is opportunity cost?", "The value of the next best alternative foregone when making a choice"),
        ("What is fiscal policy?", "Government use of taxation and spending to influence the economy"),
        ("What is elasticity in economics?", "A measure of how much quantity demanded or supplied responds to changes in price"),
        ("What is a monopoly?", "A market structure where a single seller controls the entire supply of a good or service"),
        ("What is the law of diminishing returns?", "Adding more of one input while holding others constant eventually yields lower per-unit returns")
    ]
    
    for question, answer in economics_cards:
        Card.create(economics_deck_id, question, answer)
    
    # Military Deck
    military_deck_id = Deck.create("Military", "Military strategy, history, and terminology")
    military_cards = [
        ("What is a flanking maneuver?", "A tactical movement to attack the side or rear of enemy forces rather than the front"),
        ("What does NATO stand for?", "North Atlantic Treaty Organization, a military alliance of 31 North American and European countries"),
        ("What is guerrilla warfare?", "Irregular warfare using small, mobile groups with hit-and-run tactics against larger traditional forces"),
        ("What is the fog of war?", "Uncertainty in situational awareness during military operations due to incomplete information"),
        ("What is a phalanx?", "An ancient Greek military formation of heavily armed infantry standing shoulder-to-shoulder in rows"),
        ("What is combined arms warfare?", "Coordinated use of different military branches (infantry, armor, artillery, air) to achieve synergy"),
        ("What is a pincer movement?", "A military maneuver where forces simultaneously attack both flanks to encircle the enemy"),
        ("What is strategic deterrence?", "Preventing enemy action by threatening unacceptable retaliation or consequences"),
        ("What is COIN?", "Counterinsurgency: military, political, and civil actions to defeat insurgency and address root causes"),
        ("What is the Clausewitz doctrine?", "War is a continuation of politics by other means, emphasizing war's political nature and objective")
    ]
    
    for question, answer in military_cards:
        Card.create(military_deck_id, question, answer)
    
    print("✅ Successfully created 5 decks:")
    print(f"   - Medicine (ID: {medicine_deck_id}) - 10 cards")
    print(f"   - Geography (ID: {geography_deck_id}) - 10 cards")
    print(f"   - Architecture (ID: {architecture_deck_id}) - 10 cards")
    print(f"   - Economics (ID: {economics_deck_id}) - 10 cards")
    print(f"   - Military (ID: {military_deck_id}) - 10 cards")

if __name__ == "__main__":
    create_sample_decks()
