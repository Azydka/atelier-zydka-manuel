from parser_manuscrit import parse_manuscript
from rapport_qualite import split_chapters

MANUSCRIPT = """# Titre du livre

## Sous-titre qui n'est pas un chapitre

Préface courte.

# Introduction

Premier paragraphe.

---

Deuxième paragraphe.

# Conclusion

Fin.
"""


def test_sous_titre_h2_nest_pas_un_chapitre():
    titles = [chapter.title for chapter in parse_manuscript(MANUSCRIPT)]
    assert titles == ["Titre du livre", "Introduction", "Conclusion"]


def test_rapport_qualite_utilise_le_parser_commun():
    assert [c.title for c in split_chapters(MANUSCRIPT)] == [c.title for c in parse_manuscript(MANUSCRIPT)]


def test_source_lines_excluent_le_titre_du_chapitre():
    intro = parse_manuscript(MANUSCRIPT)[1]
    text = "\n".join(intro.source_lines)
    assert "# Introduction" not in text
    assert "Premier paragraphe." in text and "Deuxième paragraphe." in text
    assert "Fin." not in text
