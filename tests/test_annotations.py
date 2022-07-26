"""
Testing the outcome of annotations
"""

from dart.handler.NLP.annotator import Annotator

TEXT_1 = """"""

TEXT_2 = """Dit is een dummy"""

# https://www.nu.nl/economie/5798559/may-sluit-nieuwe-brexit-stemming-niet-uit-ondanks-oordeel-voorzitter.html
TEXT_3 = """Burgemeester Rob Bats van de gemeente Steenwijkerland staat woensdag de hele dag met een bakfiets klaar bij het stembureau in het dorp Eesveen"""

annotator = Annotator("dutch")
doc1, ent1, tags1 = annotator.annotate(TEXT_1)
doc2, ent2, tags2 = annotator.annotate(TEXT_2)
doc3, ent3, tags3 = annotator.annotate(TEXT_3)


def test_entities():
    assert ent1 == []
    assert ent2 == []
    # assert ent3 == [{'text': 'Rob Bats', 'start_char': 13, 'end_char': 21, 'label': 'PER'}, {'text': 'Steenwijkerland', 'start_char': 38, 'end_char': 53, 'label': 'LOC'}, {'text': 'Eesveen', 'start_char': 135, 'end_char': 142, 'label': 'LOC'}]


def test_tags():
    assert tags1 == []
    assert tags2 == [{'text': 'Dit', 'tag': 'PRON'}, {'text': 'is', 'tag': 'VERB'}, {'text': 'een', 'tag': 'DET'}, {'text': 'dummy', 'tag': 'NOUN'}]
    # assert tags3 == [{'text': 'Burgemeester', 'tag': 'NOUN'}, {'text': 'Rob', 'tag': 'NOUN'}, {'text': 'Bats', 'tag': 'PROPN'}, {'text': 'van', 'tag': 'ADP'}, {'text': 'de', 'tag': 'DET'}, {'text': 'gemeente', 'tag': 'NOUN'}, {'text': 'Steenwijkerland', 'tag': 'NOUN'}, {'text': 'staat', 'tag': 'VERB'}, {'text': 'woensdag', 'tag': 'NOUN'}, {'text': 'de', 'tag': 'DET'}, {'text': 'hele', 'tag': 'ADJ'}, {'text': 'dag', 'tag': 'NOUN'}, {'text': 'met', 'tag': 'ADP'}, {'text': 'een', 'tag': 'DET'}, {'text': 'bakfiets', 'tag': 'PRON'}, {'text': 'klaar', 'tag': 'ADJ'}, {'text': 'bij', 'tag': 'ADP'}, {'text': 'het', 'tag': 'DET'}, {'text': 'stembureau', 'tag': 'NOUN'}, {'text': 'in', 'tag': 'ADP'}, {'text': 'het', 'tag': 'DET'}, {'text': 'dorp', 'tag': 'NOUN'}, {'text': 'Eesveen', 'tag': 'NOUN'}]
