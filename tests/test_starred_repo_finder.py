import unittest
from unittest.mock import patch, Mock
from starred_repo_finder.starred_repo_finder import (
    build_query,
    make_request,
    process_response,
    print_results,
    run,
    convert_and_format_results,
    main,
)


class TestStarredRepoFinder(unittest.TestCase):
    def test_build_query(self):
        result_query = build_query("test_repo", 50, "stargazers", None, None, None)
        self.assertIn("test_repo", result_query)
        self.assertIn("LIMIT 50", result_query)

    def test_build_query_with_stargazers(self):
        result_query = build_query("test_repo", 50, "stargazers", 10, None, None)
        self.assertIn("AND stargazers >= 10", result_query)

    def test_build_query_with_forkers(self):
        result_query = build_query("test_repo", 50, "stargazers", None, 10, None)
        self.assertIn("AND forkers >= 10", result_query)

    def test_build_query_with_ratio(self):
        result_query = build_query("test_repo", 50, "stargazers", None, None, 10)
        self.assertIn("AND ratio >= 10", result_query)

    @patch("starred_repo_finder.starred_repo_finder.requests.post")
    def test_make_request(self, mock_post):
        # setup
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = b"test_repo\t100\t20\t5\n"

        # action
        response = make_request(
            "test_query", "https://play.clickhouse.com/", {"user": "explorer"}
        )

        # assert
        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once_with(
            "https://play.clickhouse.com/",
            params={"user": "explorer"},
            data="test_query",
            timeout=10,
        )

    def test_process_response(self):
        # setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test_repo\t100\t20\t5\n"

        # action
        result = process_response(mock_response)

        # assert
        self.assertEqual(result, [["test_repo", "100", "20", "5"]])

    @patch("starred_repo_finder.starred_repo_finder.console.print")
    def test_print_results(self, mock_print):
        # action
        print_results([["test_repo", "100", "20", "5"]], "table")

        # since print_results prints to console, we only verify if print was called
        self.assertTrue(mock_print.called)

    def test_convert_and_format_results(self):
        converted_and_formatted_results = convert_and_format_results(
            [["test_repo", "100", "20", "5"]], "json"
        )
        self.assertEqual(
            converted_and_formatted_results[0][0]["repo_name"], "test_repo"
        )

    @patch("starred_repo_finder.starred_repo_finder.console.print")
    @patch("starred_repo_finder.starred_repo_finder.make_request")
    def test_run(self, mock_request, mock_print):
        # setup
        mock_request.return_value.status_code = 200
        mock_request.return_value.content = b"test_repo\t100\t20\t5\n"

        # action
        run("test_repo", 50, "stargazers", None, None, None, "table")

        # assert
        mock_request.assert_called_once()
        self.assertTrue(mock_print.called)

    @patch("starred_repo_finder.starred_repo_finder.argparse.ArgumentParser.parse_args")
    @patch("starred_repo_finder.starred_repo_finder.run")
    def test_main(self, mock_run, mock_parse_args):
        # setup
        mock_args = Mock()
        mock_args.repo_name = "test_repo"
        mock_args.limit = 50
        mock_args.order = "stargazers"
        mock_args.stargazers = None
        mock_args.forkers = None
        mock_args.ratio = None
        mock_args.format = "table"

        mock_parse_args.return_value = mock_args

        # action
        main()

        # assert
        mock_parse_args.assert_called_once()
        mock_run.assert_called_once_with(
            "test_repo", 50, "stargazers", None, None, None, "table"
        )


if __name__ == "__main__":
    unittest.main()
