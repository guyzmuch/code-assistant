from plugins.commons.list_manipulation.sort_data import SortData


class TestSortData:
    def test_sorts_lines_ascending(self):
        plugin = SortData()
        result = plugin.run(["cherry", "apple", "banana"])

        assert result == ["apple", "banana", "cherry"]

    def test_sorts_numbers_as_text(self):
        plugin = SortData()
        result = plugin.run(["10", "2", "1"])

        assert result == ["1", "10", "2"]

    def test_reverse_sort(self):
        plugin = SortData(options='{"reverse": true}')
        result = plugin.run(["cherry", "apple", "banana"])

        assert result == ["cherry", "banana", "apple"]

    def test_empty_input_returns_empty_list(self):
        plugin = SortData()
        result = plugin.run([])

        assert result == []
