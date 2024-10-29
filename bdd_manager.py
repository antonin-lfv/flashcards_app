import sqlite3
from datetime import datetime


# Fonction pour initialiser la base de données et créer les tables si elles n'existent pas
def init_db():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    # Créer la table 'cards'
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            reponse TEXT NOT NULL,
            theme TEXT NOT NULL,
            probabilite REAL,
            id_theme INTEGER,
            FOREIGN KEY(id_theme) REFERENCES themes(id_theme) ON DELETE RESTRICT
        )
    """
    )

    # Créer la table 'themes'
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS themes (
            id_theme INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT NOT NULL
        )
    """
    )

    # Init les themes avec Mathématiques, Statistiques, Probabilités, Terminal, Python, Github, Environnements virtuels, Machine Learning, Deep Learning
    c.execute(
        """
        INSERT INTO themes (theme)
        VALUES ('Mathématiques'),
        ('Statistiques'),
        ('Probabilités'),
        ('Terminal'),
        ('Python'),
        ('Github'),
        ('Environnements virtuels'),
        ('Machine Learning'),
        ('Deep Learning')
    """
    )

    # Créer la table 'stats'
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bonnes_reponses INTEGER DEFAULT 0,
            mauvaises_reponses INTEGER DEFAULT 0,
            date TEXT
        )
    """
    )

    conn.commit()
    conn.close()


# Fonctions CRUD pour les 'cards'
def create_card(question, reponse, theme, probabilite, id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO cards (question, reponse, theme, probabilite, id_theme)
        VALUES (?, ?, ?, ?, ?)
    """,
        (question, reponse, theme, probabilite, id_theme),
    )

    conn.commit()
    conn.close()


def get_card(id):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("SELECT * FROM cards WHERE id = ?", (id,))
    card = c.fetchone()

    conn.close()
    return card


def update_card(id, question, reponse, theme, probabilite, id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute(
        """
        UPDATE cards
        SET question = ?, reponse = ?, theme = ?, probabilite = ?, id_theme = ?
        WHERE id = ?
    """,
        (question, reponse, theme, probabilite, id_theme, id),
    )

    conn.commit()
    conn.close()


def delete_card(id):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("DELETE FROM cards WHERE id = ?", (id,))

    conn.commit()
    conn.close()


def get_all_cards():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("SELECT * FROM cards")
    cards = c.fetchall()

    conn.close()
    return cards


def get_number_of_cards():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM cards")
    count = c.fetchone()[0]

    conn.close()
    return count


def get_cards_by_theme(id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE id_theme = ?", (id_theme,))
    cards = c.fetchall()
    conn.close()
    return cards


# Fonctions CRUD pour les 'themes'
def create_theme(theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO themes (theme)
        VALUES (?)
    """,
        (theme,),
    )

    conn.commit()
    conn.close()


def get_theme(id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("SELECT * FROM themes WHERE id_theme = ?", (id_theme,))
    theme = c.fetchone()

    conn.close()
    return theme


def update_theme(id_theme, theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute(
        """
        UPDATE themes
        SET theme = ?
        WHERE id_theme = ?
    """,
        (theme, id_theme),
    )

    conn.commit()
    conn.close()


def delete_theme(id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("DELETE FROM themes WHERE id_theme = ?", (id_theme,))

    conn.commit()
    conn.close()


def get_all_themes():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT id_theme, theme FROM themes ORDER BY LOWER(theme)")
    themes = c.fetchall()
    conn.close()
    return themes


# Fonction pour mettre à jour les statistiques de l'utilisateur
def update_stats(is_correct):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    # Vérifier si une entrée de stats existe pour aujourd'hui
    c.execute("SELECT * FROM stats WHERE date = ?", (today,))
    stats = c.fetchone()

    if stats:
        id, bonnes_reponses, mauvaises_reponses, date = stats
        if is_correct:
            bonnes_reponses += 1
        else:
            mauvaises_reponses += 1

        c.execute(
            """
            UPDATE stats
            SET bonnes_reponses = ?, mauvaises_reponses = ?
            WHERE id = ?
        """,
            (bonnes_reponses, mauvaises_reponses, id),
        )
    else:
        bonnes_reponses = 1 if is_correct else 0
        mauvaises_reponses = 0 if is_correct else 1
        c.execute(
            """
            INSERT INTO stats (bonnes_reponses, mauvaises_reponses, date)
            VALUES (?, ?, ?)
        """,
            (bonnes_reponses, mauvaises_reponses, today),
        )

    conn.commit()
    conn.close()


# Fonction pour mettre à jour les statistiques de l'utilisateur
def update_card_probability(card_id, is_correct):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    # Récupérer la probabilité actuelle
    c.execute("SELECT probabilite FROM cards WHERE id = ?", (card_id,))
    result = c.fetchone()

    if result:
        probabilite = result[0]
        if is_correct:
            probabilite *= 0.9  # Diminue la probabilité après une bonne réponse
        else:
            probabilite *= 1.1  # Augmente la probabilité après une mauvaise réponse

        # Limiter la probabilité entre 0.1 et 1.0
        probabilite = max(0.1, min(probabilite, 1.0))

        # Mettre à jour la probabilité dans la base de données
        c.execute(
            """
            UPDATE cards
            SET probabilite = ?
            WHERE id = ?
        """,
            (probabilite, card_id),
        )

        conn.commit()
    else:
        print("Carte non trouvée.")

    conn.close()


def get_stats():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("SELECT * FROM stats")
    stats = c.fetchall()

    conn.close()
    return stats
