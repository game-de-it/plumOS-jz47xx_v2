"""Regression checks for moving installed sections without losing selection."""
import unittest

from simplemenu_section_layout import migrate_state


class LayoutMigration(unittest.TestCase):
    old = {'arcades': ['NEO GEO', 'FBA'],
           'consoles': ['NES', 'GENESIS', 'MASTER SYSTEM'],
           'handhelds': ['GB', 'POKEMON MINI', 'LYNX'],
           'home computers': ['MSX', 'CPC']}
    new = {'arcades': ['FBA'],
           'consoles': ['NES', 'MASTER SYSTEM', 'GENESIS', 'NEO GEO'],
           'handhelds': ['GB', 'LYNX', 'POKEMON MINI'],
           'home computers': ['CPC', 'MSX']}

    def fixture(self, group=0, section=0, back=0):
        lines = ['10;', '1;', '0;', '1;', '1;', '2;', '0;',
                 f'{group};', f'{section};', '4;']
        for g, names in enumerate(self.old.values()):
            for s in range(len(names) + 1):
                lines.append(f'{int(s == (section if g == group else 0))};{s};1;2;17;{back}')
        return '\n'.join(lines) + '\n'

    def result(self, group=0, section=0, back=0):
        lines = migrate_state(self.fixture(group, section, back), self.old, self.new).splitlines()
        records = [list(map(int, line.split(';'))) for line in lines[10:]]
        self.assertEqual(sum(row[0] for row in records), 4)
        self.assertEqual(lines[5], '2;')  # Keep selected theme.
        return lines, records

    def test_system_moves_category(self):
        lines, rows = self.result()
        self.assertEqual(lines[7:9], ['1;', '3;'])
        self.assertEqual(rows[5], [1, 3, 1, 2, 17, 3])

    def test_handheld_order_keeps_selected_system(self):
        lines, _ = self.result(2, 1)
        self.assertEqual(lines[7:9], ['2;', '2;'])

    def test_favorites_follow_return_system(self):
        lines, rows = self.result(0, 2)
        self.assertEqual(lines[7:9], ['1;', '4;'])
        self.assertEqual(rows[6], [1, 4, 1, 2, 17, 3])

    def test_header_only_seed(self):
        text = '\n'.join(self.fixture().splitlines()[:10])
        self.assertEqual(migrate_state(text, self.old, self.new).splitlines()[7:9], ['1;', '3;'])

    def test_reject_unknown_version(self):
        with self.assertRaises(ValueError):
            migrate_state(self.fixture().replace('10;', '11;', 1), self.old, self.new)

    def test_reject_group_order_change(self):
        with self.assertRaises(ValueError):
            migrate_state(self.fixture(), self.old, dict(reversed(list(self.new.items()))))


if __name__ == '__main__':
    unittest.main()
