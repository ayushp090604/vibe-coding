from html.parser import HTMLParser
from pathlib import Path


PAGE = Path(__file__).resolve().parents[1] / "src" / "index.html"
EXPECTED_GROUPS = {"chest", "back", "shoulders", "arms", "legs", "core"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class GymPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.current_group = None
        self.groups = set()
        self.exercise_counts = {}
        self.group_links = set()
        self.image_alts = []
        self.open_tags = []
        self.mismatched_tags = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "title":
            self.in_title = True
        elif tag == "section" and "muscle-group" in classes:
            self.current_group = attributes.get("id")
            self.groups.add(self.current_group)
            self.exercise_counts[self.current_group] = 0
        elif tag == "article" and "exercise-card" in classes:
            self.exercise_counts[self.current_group] += 1
        elif tag == "a" and "group-link" in classes:
            self.group_links.add(attributes["href"][1:])
        elif tag == "img":
            self.image_alts.append(attributes.get("alt", ""))

    def handle_endtag(self, tag):
        if tag not in VOID_TAGS:
            if self.open_tags and self.open_tags[-1] == tag:
                self.open_tags.pop()
            else:
                self.mismatched_tags.append(tag)

        if tag == "title":
            self.in_title = False
        elif tag == "section" and self.current_group is not None:
            self.current_group = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def test_gym_101_page_has_navigable_exercise_groups():
    parser = GymPageParser()
    parser.feed(PAGE.read_text(encoding="utf-8"))

    assert parser.title == "Gym 101"
    assert parser.groups == EXPECTED_GROUPS
    assert parser.group_links == EXPECTED_GROUPS
    assert parser.exercise_counts == {group: 3 for group in EXPECTED_GROUPS}
    assert len(parser.image_alts) == 19
    assert all(parser.image_alts)
    assert not parser.open_tags
    assert not parser.mismatched_tags