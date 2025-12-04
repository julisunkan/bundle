
from models import Deck, Card

def create_expanded_decks():
    """Create 100+ flashcards across 10 knowledge categories"""
    
    # Science - 10 cards
    science_deck_id = Deck.create("Science Fundamentals", "Essential scientific concepts and principles", "Science")
    science_cards = [
        ("What is the scientific method?", "A systematic process of observation, hypothesis formation, experimentation, analysis, and conclusion to acquire knowledge"),
        ("What is photosynthesis?", "The process by which plants convert light energy, carbon dioxide, and water into glucose and oxygen"),
        ("What is DNA?", "Deoxyribonucleic acid - the molecule that carries genetic instructions for development, functioning, growth, and reproduction"),
        ("What is Newton's First Law of Motion?", "An object at rest stays at rest and an object in motion stays in motion unless acted upon by an external force"),
        ("What is the difference between atoms and molecules?", "Atoms are the smallest units of elements; molecules are two or more atoms bonded together"),
        ("What is entropy?", "A measure of disorder or randomness in a system, which tends to increase over time according to the second law of thermodynamics"),
        ("What is evolution by natural selection?", "The process where organisms with favorable traits are more likely to survive and reproduce, passing those traits to offspring"),
        ("What is the pH scale?", "A measure of acidity or alkalinity ranging from 0-14, where 7 is neutral, below 7 is acidic, above 7 is alkaline"),
        ("What is electromagnetic radiation?", "Energy transmitted through space as waves, including visible light, radio waves, X-rays, and gamma rays"),
        ("What is the difference between mitosis and meiosis?", "Mitosis produces two identical daughter cells for growth; meiosis produces four genetically different cells for reproduction")
    ]
    for q, a in science_cards:
        Card.create(science_deck_id, q, a)
    
    # History - 10 cards
    history_deck_id = Deck.create("World History", "Major historical events and figures", "History")
    history_cards = [
        ("When did World War I occur?", "1914-1918, triggered by the assassination of Archduke Franz Ferdinand and involving major world powers"),
        ("What was the Renaissance?", "A cultural movement from 14th-17th century Europe marked by revival of classical learning, art, and humanism"),
        ("Who was Alexander the Great?", "Ancient Macedonian king (356-323 BC) who created one of the largest empires, spreading Greek culture across Asia"),
        ("What was the Industrial Revolution?", "Period of major industrialization (1760-1840) transitioning from hand production to machines, new chemical manufacturing, and iron production"),
        ("What were the Crusades?", "Series of religious wars (1095-1291) sanctioned by the Latin Church to recover the Holy Land from Islamic rule"),
        ("What was the Cold War?", "Period of geopolitical tension (1947-1991) between the United States and Soviet Union without direct military conflict"),
        ("Who was Genghis Khan?", "Founder of the Mongol Empire (c. 1162-1227), which became the largest contiguous empire in history"),
        ("What was the French Revolution?", "Period of radical social and political upheaval in France (1789-1799) that overthrew the monarchy and established a republic"),
        ("What was the Silk Road?", "Ancient network of trade routes connecting East and West, facilitating cultural, commercial, and technological exchange"),
        ("What was the Enlightenment?", "18th-century intellectual movement emphasizing reason, individualism, and skepticism of traditional authority")
    ]
    for q, a in history_cards:
        Card.create(history_deck_id, q, a)
    
    # Mathematics - 10 cards
    math_deck_id = Deck.create("Mathematics Essentials", "Core mathematical concepts and formulas", "Mathematics")
    math_cards = [
        ("What is the Pythagorean theorem?", "In a right triangle, a² + b² = c², where c is the hypotenuse and a and b are the other two sides"),
        ("What is a prime number?", "A natural number greater than 1 that has no positive divisors other than 1 and itself"),
        ("What is the quadratic formula?", "x = (-b ± √(b² - 4ac)) / 2a, used to solve equations of the form ax² + bx + c = 0"),
        ("What is pi (π)?", "The ratio of a circle's circumference to its diameter, approximately 3.14159, an irrational number"),
        ("What is the difference between mean, median, and mode?", "Mean is the average; median is the middle value; mode is the most frequent value in a dataset"),
        ("What is a derivative in calculus?", "The rate of change of a function at a given point, representing the slope of the tangent line"),
        ("What is the Fibonacci sequence?", "A series where each number is the sum of the two preceding ones: 0, 1, 1, 2, 3, 5, 8, 13..."),
        ("What is Euler's number (e)?", "An irrational constant approximately 2.71828, the base of natural logarithms, fundamental in calculus"),
        ("What is a matrix?", "A rectangular array of numbers arranged in rows and columns, used to represent linear transformations"),
        ("What is probability?", "The measure of the likelihood that an event will occur, expressed as a number between 0 and 1")
    ]
    for q, a in math_cards:
        Card.create(math_deck_id, q, a)
    
    # Literature - 10 cards
    literature_deck_id = Deck.create("Literature Classics", "Famous works and literary concepts", "Literature")
    literature_cards = [
        ("Who wrote '1984'?", "George Orwell - a dystopian novel about totalitarianism, surveillance, and the manipulation of truth"),
        ("What is a metaphor?", "A figure of speech that directly compares two unlike things without using 'like' or 'as'"),
        ("Who wrote 'Romeo and Juliet'?", "William Shakespeare - a tragedy about two star-crossed lovers from feuding families"),
        ("What is an allegory?", "A narrative where characters and events represent abstract ideas or moral qualities beyond the literal meaning"),
        ("Who wrote 'To Kill a Mockingbird'?", "Harper Lee - a novel addressing racial injustice and moral growth in the American South"),
        ("What is iambic pentameter?", "A metrical pattern in poetry with five iambs (unstressed-stressed syllable pairs) per line, used by Shakespeare"),
        ("What is the hero's journey?", "A narrative structure identified by Joseph Campbell where a hero goes on an adventure, faces a crisis, and returns transformed"),
        ("Who wrote 'Pride and Prejudice'?", "Jane Austen - a novel of manners exploring themes of love, reputation, and class in Regency England"),
        ("What is foreshadowing?", "A literary device where the author hints at future events in the narrative"),
        ("What is stream of consciousness?", "A narrative technique presenting a character's thoughts and feelings as a continuous, uninterrupted flow")
    ]
    for q, a in literature_cards:
        Card.create(literature_deck_id, q, a)
    
    # Computer Science - 10 cards
    cs_deck_id = Deck.create("Computer Science Basics", "Programming and CS fundamentals", "Computer Science")
    cs_cards = [
        ("What is an algorithm?", "A step-by-step procedure or formula for solving a problem or completing a task"),
        ("What is Object-Oriented Programming?", "A programming paradigm based on objects containing data (attributes) and code (methods)"),
        ("What is Big O notation?", "A mathematical notation describing the limiting behavior of an algorithm's time or space complexity"),
        ("What is recursion?", "A programming technique where a function calls itself to solve smaller instances of the same problem"),
        ("What is the difference between stack and heap memory?", "Stack stores local variables and function calls (LIFO); heap stores dynamically allocated objects with manual management"),
        ("What is a binary search tree?", "A data structure where each node has at most two children, with left child values less than parent and right greater"),
        ("What is SQL?", "Structured Query Language - a domain-specific language for managing and querying relational databases"),
        ("What is version control?", "A system that records changes to files over time, allowing you to recall specific versions (e.g., Git)"),
        ("What is API?", "Application Programming Interface - a set of rules and protocols for building and interacting with software applications"),
        ("What is machine learning?", "A subset of AI where systems learn from data to improve performance without explicit programming")
    ]
    for q, a in cs_cards:
        Card.create(cs_deck_id, q, a)
    
    # Psychology - 10 cards
    psych_deck_id = Deck.create("Psychology Fundamentals", "Key psychological concepts and theories", "Psychology")
    psych_cards = [
        ("What is classical conditioning?", "Learning process where a neutral stimulus becomes associated with a meaningful stimulus, eliciting a similar response (Pavlov's dogs)"),
        ("What is cognitive dissonance?", "Mental discomfort from holding contradictory beliefs, values, or attitudes, motivating attitude or behavior change"),
        ("What is Maslow's hierarchy of needs?", "A five-tier model of human needs: physiological, safety, love/belonging, esteem, and self-actualization"),
        ("What is the nature vs. nurture debate?", "The question of whether genetics (nature) or environment and experience (nurture) primarily shape human behavior"),
        ("What is confirmation bias?", "The tendency to search for, interpret, and recall information that confirms pre-existing beliefs"),
        ("What are the stages of grief?", "Kübler-Ross model: denial, anger, bargaining, depression, and acceptance (not necessarily in order)"),
        ("What is operant conditioning?", "Learning through consequences where behaviors are strengthened by reinforcement or weakened by punishment (Skinner)"),
        ("What is attachment theory?", "Psychological model describing the dynamics of long-term relationships, especially parent-child bonds (Bowlby)"),
        ("What is the bystander effect?", "Phenomenon where individuals are less likely to help a victim when other people are present"),
        ("What is working memory?", "A cognitive system with limited capacity for temporarily holding and manipulating information for complex tasks")
    ]
    for q, a in psych_cards:
        Card.create(psych_deck_id, q, a)
    
    # Chemistry - 10 cards
    chem_deck_id = Deck.create("Chemistry Concepts", "Essential chemistry principles", "Chemistry")
    chem_cards = [
        ("What is the periodic table?", "An arrangement of chemical elements ordered by atomic number, electron configuration, and recurring properties"),
        ("What is an ionic bond?", "A chemical bond formed by the electrostatic attraction between oppositely charged ions (electron transfer)"),
        ("What is a covalent bond?", "A chemical bond formed by sharing electron pairs between atoms"),
        ("What is Avogadro's number?", "6.022 × 10²³ - the number of atoms, molecules, or particles in one mole of a substance"),
        ("What is oxidation and reduction?", "Oxidation is loss of electrons; reduction is gain of electrons (OIL RIG mnemonic)"),
        ("What is an acid?", "A substance that donates protons (H⁺ ions) in solution and has a pH less than 7"),
        ("What is a catalyst?", "A substance that increases the rate of a chemical reaction without being consumed in the process"),
        ("What are isotopes?", "Atoms of the same element with the same number of protons but different numbers of neutrons"),
        ("What is the law of conservation of mass?", "Matter cannot be created or destroyed in a chemical reaction; mass of reactants equals mass of products"),
        ("What is electronegativity?", "The tendency of an atom to attract electrons toward itself in a chemical bond (Pauling scale)")
    ]
    for q, a in chem_cards:
        Card.create(chem_deck_id, q, a)
    
    # Philosophy - 10 cards
    phil_deck_id = Deck.create("Philosophy Basics", "Major philosophical ideas and thinkers", "Philosophy")
    phil_cards = [
        ("What is Plato's Theory of Forms?", "Reality consists of perfect, eternal, unchanging Forms or Ideas, of which physical objects are imperfect copies"),
        ("What is existentialism?", "Philosophy emphasizing individual existence, freedom, and choice, asserting that humans create their own meaning"),
        ("What is utilitarianism?", "Ethical theory that the best action is the one that maximizes overall happiness or utility for the greatest number"),
        ("What is Descartes' 'Cogito, ergo sum'?", "'I think, therefore I am' - the fundamental certainty that one's mind exists because one can doubt"),
        ("What is the categorical imperative?", "Kant's principle that one should act only according to maxims that could become universal laws"),
        ("What is determinism?", "The philosophical view that all events are determined by previously existing causes, questioning free will"),
        ("What is epistemology?", "The branch of philosophy concerned with the nature, sources, and limits of knowledge"),
        ("What is the social contract?", "Theory that individuals consent to surrender some freedoms to authority in exchange for protection of remaining rights"),
        ("What is nihilism?", "The philosophical belief that life is without objective meaning, purpose, or intrinsic value"),
        ("What is dualism?", "The view that mind and body are distinct and separable, often associated with Descartes")
    ]
    for q, a in phil_cards:
        Card.create(phil_deck_id, q, a)
    
    # Biology - 10 cards
    bio_deck_id = Deck.create("Biology Essentials", "Core biological concepts", "Biology")
    bio_cards = [
        ("What is a cell?", "The basic structural and functional unit of all living organisms, containing genetic material and organelles"),
        ("What is homeostasis?", "The ability of organisms to maintain stable internal conditions despite external changes"),
        ("What is the difference between prokaryotic and eukaryotic cells?", "Prokaryotes lack a nucleus and membrane-bound organelles; eukaryotes have both"),
        ("What is ATP?", "Adenosine triphosphate - the primary energy currency of cells, storing and transferring energy for cellular processes"),
        ("What is osmosis?", "The diffusion of water molecules across a semi-permeable membrane from low to high solute concentration"),
        ("What are enzymes?", "Biological catalysts (usually proteins) that speed up chemical reactions in living organisms without being consumed"),
        ("What is the central dogma of molecular biology?", "DNA is transcribed to RNA, which is translated to protein (DNA → RNA → Protein)"),
        ("What is an ecosystem?", "A community of living organisms interacting with each other and their physical environment"),
        ("What is the difference between genotype and phenotype?", "Genotype is the genetic makeup; phenotype is the observable physical or biochemical characteristics"),
        ("What is cellular respiration?", "The process by which cells convert glucose and oxygen into ATP, carbon dioxide, and water")
    ]
    for q, a in bio_cards:
        Card.create(bio_deck_id, q, a)
    
    # Art & Design - 10 cards
    art_deck_id = Deck.create("Art & Design History", "Art movements and design principles", "Art & Design")
    art_cards = [
        ("What is the Golden Ratio?", "A mathematical ratio of approximately 1.618:1 found in nature and used in art and design for aesthetic composition"),
        ("What is Impressionism?", "19th-century art movement characterized by small, visible brush strokes, emphasis on light, and ordinary subject matter"),
        ("What is the Bauhaus?", "German art school (1919-1933) combining crafts and fine arts, emphasizing functional design and modernist principles"),
        ("What is chiaroscuro?", "An artistic technique using strong contrasts between light and dark to create depth and volume (used by Caravaggio)"),
        ("What is negative space?", "The empty or white space around and between the subject(s) of an image, important for composition"),
        ("What is Abstract Expressionism?", "Post-WWII art movement emphasizing spontaneous, automatic, or subconscious creation (Pollock, Rothko)"),
        ("What are the primary colors?", "Red, blue, and yellow - colors that cannot be created by mixing other colors and form the basis of all other colors"),
        ("What is perspective in art?", "A technique for representing three-dimensional objects on a two-dimensional surface to create depth and spatial relationships"),
        ("What is Surrealism?", "20th-century movement featuring unexpected juxtapositions and illogical scenes inspired by the unconscious mind (Dalí, Magritte)"),
        ("What is typography?", "The art and technique of arranging type to make written language legible, readable, and appealing")
    ]
    for q, a in art_cards:
        Card.create(art_deck_id, q, a)
    
    print("✅ Successfully created 10 knowledge category decks with 100 flashcards:")
    print(f"   - Science Fundamentals (ID: {science_deck_id}) - 10 cards")
    print(f"   - World History (ID: {history_deck_id}) - 10 cards")
    print(f"   - Mathematics Essentials (ID: {math_deck_id}) - 10 cards")
    print(f"   - Literature Classics (ID: {literature_deck_id}) - 10 cards")
    print(f"   - Computer Science Basics (ID: {cs_deck_id}) - 10 cards")
    print(f"   - Psychology Fundamentals (ID: {psych_deck_id}) - 10 cards")
    print(f"   - Chemistry Concepts (ID: {chem_deck_id}) - 10 cards")
    print(f"   - Philosophy Basics (ID: {phil_deck_id}) - 10 cards")
    print(f"   - Biology Essentials (ID: {bio_deck_id}) - 10 cards")
    print(f"   - Art & Design History (ID: {art_deck_id}) - 10 cards")

if __name__ == "__main__":
    create_expanded_decks()
