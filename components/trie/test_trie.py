import pytest

from trie import Trie


def test_insert_and_search():
    t = Trie()
    t.insert("apple")
    t.insert("app")
    assert t.search("apple")
    assert t.search("app")
    assert not t.search("ap")
    assert not t.search("banana")
    assert len(t) == 2


def test_starts_with():
    t = Trie()
    for w in ("cat", "car", "card", "dog"):
        t.insert(w)
    assert t.starts_with("ca")
    assert t.starts_with("car")
    assert t.starts_with("")
    assert not t.starts_with("z")
    assert not t.starts_with("cats")


def test_autocomplete_order_and_limit():
    t = Trie()
    for w in ("apple", "app", "apricot", "banana", "application"):
        t.insert(w)
    assert t.autocomplete("app") == ["app", "apple", "application"]
    assert t.autocomplete("app", limit=2) == ["app", "apple"]
    assert t.autocomplete("ban") == ["banana"]
    assert t.autocomplete("xyz") == []
    assert t.autocomplete() == sorted(["apple", "app", "apricot", "banana", "application"])


def test_delete_and_prune():
    t = Trie()
    t.insert("apple")
    t.insert("app")
    assert t.delete("apple") is True
    assert not t.search("apple")
    assert t.search("app")
    assert t.delete("apple") is False
    assert t.delete("missing") is False
    assert len(t) == 1
    # shared prefix still works
    assert t.autocomplete("ap") == ["app"]


def test_duplicate_insert_and_empty():
    t = Trie()
    t.insert("hi")
    t.insert("hi")
    assert len(t) == 1
    with pytest.raises(ValueError):
        t.insert("")
    assert t.delete("") is False


def test_case_sensitive_and_special_chars():
    t = Trie()
    t.insert("Hello")
    t.insert("hello")
    t.insert("a-b")
    assert t.search("Hello")
    assert not t.search("hello ")
    assert t.autocomplete("h") == ["hello"]
    assert t.search("a-b")
    assert t.autocomplete("a") == ["a-b"]
