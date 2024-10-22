Version 0.1.0

Base de données SQLite, application en local

Les cards:
-> Les clés: id, question, reponse, theme, probabilite, id_theme
CRUD questions et réponses

Les thèmes:
Mathématiques, Statistiques, Probabilités, Terminal, Python, Github, Environnements virtuels, Machine Learning, Deep Learning
-> Les clés: id_theme, theme
CRUD thèmes

Les stats de l'utilisateur:
-> Les clés: id, bonnes_reponses, mauvaises_reponses, date
Quand l'utilisateur répond à une question, on incrémente bonnes_reponses ou mauvaises_reponses

## Aperçu des tables de la base de données

### Table cards
| id  | question                              | reponse | theme         | probabilite | id_theme |
| --- | ------------------------------------- | ------- | ------------- | ----------- | -------- |
| 1   | Qu'est ce que le Vanishing Gradient ? | 2       | Deep Learning | 0.5         | 4        |
| 2   | 2+2                                   | 4       | Mathématiques | 0.5         | 1        |
| 3   | 3+3                                   | 6       | Mathématiques | 0.5         | 1        |

### Table themes
| id_theme | theme         |
| -------- | ------------- |
| 1        | Mathématiques |
| 2        | Statistiques  |
| 3        | Probabilités  |
| 4        | Deep Learning |

### Table stats
| id  | bonnes_reponses | mauvaises_reponses | date       |
| --- | --------------- | ------------------ | ---------- |
| 1   | 2               | 1                  | 2021-09-01 |
| 2   | 3               | 2                  | 2021-09-02 |
| 3   | 4               | 3                  | 2021-09-03 |

