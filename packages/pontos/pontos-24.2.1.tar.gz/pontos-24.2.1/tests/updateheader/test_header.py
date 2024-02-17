# SPDX-FileCopyrightText: 2020-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import datetime
import re
import struct
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest import TestCase
from unittest.mock import patch

from pontos.terminal.terminal import ConsoleTerminal
from pontos.testing import temp_file
from pontos.updateheader.updateheader import (
    OLD_COMPANY,
    _compile_copyright_regex,
    main,
    parse_args,
)
from pontos.updateheader.updateheader import _add_header as add_header
from pontos.updateheader.updateheader import (
    _compile_outdated_regex as compile_outdated_regex,
)
from pontos.updateheader.updateheader import _find_copyright as find_copyright
from pontos.updateheader.updateheader import (
    _get_exclude_list as get_exclude_list,
)
from pontos.updateheader.updateheader import (
    _get_modified_year as get_modified_year,
)
from pontos.updateheader.updateheader import (
    _remove_outdated_lines as remove_outdated_lines,
)
from pontos.updateheader.updateheader import _update_file as update_file

HEADER = """# SPDX-FileCopyrightText: {date} Greenbone AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later"""


class Terminal(ConsoleTerminal):
    @staticmethod
    def get_width() -> int:
        return 999


class UpdateHeaderTestCase(TestCase):
    def setUp(self):
        self.args = Namespace()
        self.args.company = "Greenbone AG"

        self.path = Path(__file__).parent

        self.regex = re.compile(
            "(SPDX-FileCopyrightText:|[Cc]opyright).*?(19[0-9]{2}|20[0-9]{2}) "
            f"?-? ?(19[0-9]{{2}}|20[0-9]{{2}})? ({self.args.company})"
        )

    @patch("pontos.updateheader.updateheader.run")
    def test_get_modified_year(self, run_mock):
        test_file = self.path / "test.py"
        test_file.touch(exist_ok=True)

        run_mock.return_value = CompletedProcess(
            args=[
                "git",
                "log",
                "-1",
                "--format=%ad",
                "--date=format:%Y",
                f"{test_file}",
            ],
            returncode=0,
            stdout="2020\n",
            stderr="",
        )

        year = get_modified_year(f=test_file)
        self.assertEqual(year, "2020")

        test_file.unlink()

    def test_get_modified_year_error(self):
        test_file = self.path / "test.py"
        if test_file.exists():
            test_file.unlink()

        with self.assertRaises(CalledProcessError):
            get_modified_year(f=test_file)

    def test_find_copyright(self):
        test_line = "# Copyright (C) 1995-2021 Greenbone AG"
        test2_line = "# Copyright (C) 1995 Greenbone AG"
        invalid_line = (
            "# This program is free software: "
            "you can redistribute it and/or modify"
        )

        # Full match
        found, match = find_copyright(
            copyright_regex=self.regex, line=test_line
        )
        self.assertTrue(found)
        self.assertIsNotNone(match)
        self.assertEqual(match["creation_year"], "1995")
        self.assertEqual(match["modification_year"], "2021")
        self.assertEqual(match["company"], self.args.company)

        # No modification Date
        found, match = find_copyright(
            copyright_regex=self.regex, line=test2_line
        )
        self.assertTrue(found)
        self.assertIsNotNone(match)
        self.assertEqual(match["creation_year"], "1995")
        self.assertEqual(match["modification_year"], None)
        self.assertEqual(match["company"], self.args.company)

        # No match
        found, match = find_copyright(
            copyright_regex=self.regex, line=invalid_line
        )
        self.assertFalse(found)
        self.assertIsNone(match)

    def test_find_spdx_copyright(self):
        test_line = "# SPDX-FileCopyrightText: 1995-2021 Greenbone AG"
        test2_line = "# SPDX-FileCopyrightText: 1995 Greenbone AG"
        invalid_line = (
            "# This program is free software: "
            "you can redistribute it and/or modify"
        )

        # Full match
        found, match = find_copyright(
            copyright_regex=self.regex, line=test_line
        )
        self.assertTrue(found)
        self.assertIsNotNone(match)
        self.assertEqual(match["creation_year"], "1995")
        self.assertEqual(match["modification_year"], "2021")
        self.assertEqual(match["company"], self.args.company)

        # No modification Date
        found, match = find_copyright(
            copyright_regex=self.regex, line=test2_line
        )
        self.assertTrue(found)
        self.assertIsNotNone(match)
        self.assertEqual(match["creation_year"], "1995")
        self.assertEqual(match["modification_year"], None)
        self.assertEqual(match["company"], self.args.company)

        # No match
        found, match = find_copyright(
            copyright_regex=self.regex, line=invalid_line
        )
        self.assertFalse(found)
        self.assertIsNone(match)

    def test_add_header(self):
        expected_header = HEADER.format(date="2021") + "\n"

        header = add_header(
            suffix=".py",
            license_id="AGPL-3.0-or-later",
            company=self.args.company,
            year="2021",
        )

        self.assertEqual(header, expected_header)

    def test_add_header_wrong_file_suffix(self):
        with self.assertRaises(ValueError):
            add_header(
                suffix=".prr",
                license_id="AGPL-3.0-or-later",
                company=self.args.company,
                year="2021",
            )

    def test_add_header_license_not_found(self):
        with self.assertRaises(FileNotFoundError):
            add_header(
                suffix=".py",
                license_id="AAAGPL-3.0-or-later",
                company=self.args.company,
                year="2021",
            )

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_file_not_existing(self, mock_stdout):
        self.args.year = "2020"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        test_file = self.path / "test.py"
        if test_file.exists():
            test_file.unlink()

        with self.assertRaises(FileNotFoundError):
            update_file(
                file=test_file,
                copyright_regex=self.regex,
                parsed_args=self.args,
                term=term,
            )

        ret = mock_stdout.getvalue()
        self.assertEqual(
            ret,
            f"{test_file}: File is not existing.\n",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_file_wrong_license(self, mock_stdout):
        self.args.year = "2020"
        self.args.changed = False
        self.args.license_id = "AAAGPL-3.0-or-later"

        term = Terminal()

        test_file = self.path / "test.py"
        test_file.touch()

        code = update_file(
            file=test_file,
            copyright_regex=self.regex,
            parsed_args=self.args,
            term=term,
        )
        self.assertEqual(code, 1)

        ret = mock_stdout.getvalue()
        self.assertEqual(
            ret,
            f"{test_file}: License file for "
            "AAAGPL-3.0-or-later is not existing.\n",
        )

        test_file.unlink()

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_file_suffix_invalid(self, mock_stdout):
        self.args.year = "2020"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        test_file = self.path / "test.pppy"
        test_file.touch()

        code = update_file(
            file=test_file,
            copyright_regex=self.regex,
            parsed_args=self.args,
            term=term,
        )
        self.assertEqual(code, 1)

        ret = mock_stdout.getvalue()
        self.assertEqual(
            ret,
            f"{test_file}: No license header for the format .pppy found.\n",
        )

        test_file.unlink()

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_file_binary_file(self, mock_stdout):
        self.args.year = "2020"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        test_file = self.path / "test.py"
        if test_file.exists():
            test_file.unlink()

        # create a Binary file ...
        # https://stackoverflow.com/a/30148554
        with open(test_file, "wb") as f:
            f.write(struct.pack(">if", 42, 2.71828182846))

        with self.assertRaises(UnicodeDecodeError):
            code = update_file(
                file=test_file,
                copyright_regex=self.regex,
                parsed_args=self.args,
                term=term,
            )
            self.assertEqual(code, 1)

        ret = mock_stdout.getvalue()
        self.assertEqual(
            ret,
            f"{test_file}: Ignoring binary file.\n",
        )

        test_file.unlink()

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_file_changed(self, mock_stdout):
        self.args.year = "1995"
        self.args.changed = True
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        test_file = self.path / "test.py"
        if test_file.exists():
            test_file.unlink()

        with self.assertRaises(FileNotFoundError):
            code = update_file(
                file=test_file,
                copyright_regex=self.regex,
                parsed_args=self.args,
                term=term,
            )
            self.assertEqual(code, 1)

        ret = mock_stdout.getvalue()

        self.assertIn(f"{test_file}", ret)
        self.assertIn("Could not get date", ret)
        self.assertIn("of last modification using git,", ret)
        self.assertIn(f"using {self.args.year} instead.", ret)
        self.assertIn("File is not existing.", ret)

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_create_header(self, mock_stdout):
        self.args.year = "1995"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        expected_header = HEADER.format(date="1995") + "\n\n"

        test_file = self.path / "test.py"
        test_file.touch()

        code = update_file(
            file=test_file,
            copyright_regex=self.regex,
            parsed_args=self.args,
            term=term,
        )

        ret = mock_stdout.getvalue()
        self.assertEqual(
            f"{test_file}: Added license header.\n",
            ret,
        )
        self.assertEqual(code, 0)
        self.assertEqual(expected_header, test_file.read_text(encoding="utf-8"))
        test_file.unlink()

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_header_in_file(self, mock_stdout):
        self.args.year = "2021"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        header = HEADER.format(date="2020")

        test_file = self.path / "test.py"
        if test_file.exists():
            test_file.unlink()

        test_file.write_text(header, encoding="utf-8")

        code = update_file(
            file=test_file,
            copyright_regex=self.regex,
            parsed_args=self.args,
            term=term,
        )

        self.assertEqual(code, 0)
        ret = mock_stdout.getvalue()
        self.assertEqual(
            ret,
            f"{test_file}: Changed License Header "
            "Copyright Year None -> 2021\n",
        )
        self.assertIn(
            "# SPDX-FileCopyrightText: 2020-2021 Greenbone AG",
            test_file.read_text(encoding="utf-8"),
        )

        test_file.unlink()

    @patch("sys.stdout", new_callable=StringIO)
    def test_update_header_ok_in_file(self, mock_stdout):
        self.args.year = "2021"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        term = Terminal()

        header = HEADER.format(date="2021")

        test_file = self.path / "test.py"
        if test_file.exists():
            test_file.unlink()

        test_file.write_text(header, encoding="utf-8")

        code = update_file(
            file=test_file,
            copyright_regex=self.regex,
            parsed_args=self.args,
            term=term,
        )

        self.assertEqual(code, 0)
        ret = mock_stdout.getvalue()
        self.assertEqual(
            ret,
            f"{test_file}: License Header is ok.\n",
        )
        self.assertIn(
            "# SPDX-FileCopyrightText: 2021 Greenbone AG",
            test_file.read_text(encoding="utf-8"),
        )

        test_file.unlink()

    def test_argparser_files(self):
        self.args.year = "2021"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        args = ["-f", "test.py", "-y", "2021", "-l", "AGPL-3.0-or-later"]

        args = parse_args(args)
        self.assertIsNotNone(args)
        self.assertEqual(args.company, self.args.company)
        self.assertEqual(args.files, ["test.py"])
        self.assertEqual(args.year, self.args.year)
        self.assertEqual(args.license_id, self.args.license_id)

    def test_argparser_dir(self):
        self.args.year = "2020"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"

        args = ["-d", ".", "-c", "-l", "AGPL-3.0-or-later"]

        args = parse_args(args)
        self.assertIsNotNone(args)
        self.assertEqual(args.company, self.args.company)
        self.assertEqual(args.directories, ["."])
        self.assertTrue(args.changed)
        self.assertEqual(args.year, str(datetime.datetime.now().year))
        self.assertEqual(args.license_id, self.args.license_id)

    def test_get_exclude_list(self):
        # Try to find the current file from two directories up...
        test_dirname = Path(__file__) / "../.."
        # with a relative glob
        test_ignore_file = Path("ignore.file")
        test_ignore_file.write_text("*.py\n", encoding="utf-8")

        exclude_list = get_exclude_list(
            test_ignore_file, [test_dirname.resolve()]
        )

        self.assertIn(Path(__file__), exclude_list)

        test_ignore_file.unlink()

    @patch("pontos.updateheader.updateheader.parse_args")
    def test_main(self, argparser_mock):
        self.args.year = "2021"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"
        self.args.files = ["test.py"]
        self.args.directories = None
        self.args.verbose = 0
        self.args.log_file = None
        self.args.quiet = False
        self.args.cleanup = False

        argparser_mock.return_value = self.args

        with redirect_stdout(StringIO()):
            code = True if not main() else False

        # I have no idea how or why test main ...
        self.assertTrue(code)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("pontos.updateheader.updateheader.parse_args")
    def test_main_never_happen(self, argparser_mock, mock_stdout):
        self.args.year = "2021"
        self.args.changed = False
        self.args.license_id = "AGPL-3.0-or-later"
        self.args.files = None
        self.args.directories = None
        self.args.verbose = 0
        self.args.log_file = None
        self.args.quiet = False
        self.args.cleanup = False

        argparser_mock.return_value = self.args

        # I have no idea how or why test main ...
        with self.assertRaises(SystemExit):
            main()

        ret = mock_stdout.getvalue()
        self.assertIn(
            "Specify files to update!",
            ret,
        )


class UpdateHeaderCleanupTestCase(TestCase):
    def setUp(self) -> None:
        self.compiled_regexes = compile_outdated_regex()

    def test_remove_outdated_lines(self):
        test_content = """* This program is free software: you can redistribute it and/or modify
*it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
//License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
# modify it under the terms of the GNU General Public License
# This program is free software; you can redistribute it and/or
# version 2 as published by the Free Software Foundation.
This program is free software: you can redistribute it and/or modify"""  # noqa: E501

        new_content = remove_outdated_lines(
            content=test_content, cleanup_regexes=self.compiled_regexes
        )
        self.assertEqual(new_content, "\n")

    def test_remove_outdated_lines2(self):
        test_content = """the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
* GNU General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA."""  # noqa: E501

        new_content = remove_outdated_lines(
            content=test_content, cleanup_regexes=self.compiled_regexes
        )
        self.assertEqual(new_content, "\n")

    def test_cleanup_file(self):
        test_content = """# Copyright (C) 2021-2022 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import foo
import bar

foo.baz(bar.boing)
"""  # noqa: E501

        expected_content = f"""# SPDX-FileCopyrightText: 2021-{str(datetime.datetime.now().year)} Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import foo
import bar

foo.baz(bar.boing)
"""  # noqa: E501

        with temp_file(content=test_content, name="foo.py") as tmp:
            args = Namespace()
            args.company = "Greenbone AG"
            args.year = str(datetime.datetime.now().year)
            args.changed = False
            args.license_id = "GPL-3.0-or-later"
            args.verbose = 0
            args.cleanup = True

            update_file(
                file=tmp,
                copyright_regex=_compile_copyright_regex(
                    ["Greenbone AG", OLD_COMPANY]
                ),
                parsed_args=args,
                term=Terminal(),
                cleanup_regexes=self.compiled_regexes,
            )

            new_content = tmp.read_text(encoding="utf-8")
            self.assertEqual(expected_content, new_content)
