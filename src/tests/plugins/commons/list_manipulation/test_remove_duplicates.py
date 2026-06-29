from plugins.commons.list_manipulation.remove_duplicates import RemoveDuplicates


class TestRemoveDuplicates:
    def test_removes_duplicates_preserving_order(self):
        plugin = RemoveDuplicates()
        result = plugin.run(["apple", "banana", "apple", "cherry", "banana"])

        assert result == ["apple", "banana", "cherry"]

    def test_keeps_unique_lines_unchanged(self):
        plugin = RemoveDuplicates()
        result = plugin.run(["cherry", "apple", "banana"])

        assert result == ["cherry", "apple", "banana"]

    def test_empty_input_returns_empty_list(self):
        plugin = RemoveDuplicates()
        result = plugin.run([])

        assert result == []

    def test_treats_lines_as_exact_values(self):
        plugin = RemoveDuplicates()
        result = plugin.run(["apple", " apple", "apple"])

        assert result == ["apple", " apple"]
