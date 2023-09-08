# coding=utf-8

from unittest import TestCase

from zeeguu.api.test.api_test_mixin import APITestMixin


URL_1 = "https://www.faz.net/aktuell/sport/mehr-sport/leichtathletik-deutsche-beim-istaf-mit-bestleistungen-nach-der-wm-19150019.html"


class UserArticleTests(APITestMixin, TestCase):
    def setUp(self):
        super(UserArticleTests, self).setUp()

    def test_article_info_other_way(self):
        json_result = self.json_from_api_post(
            "/find_or_create_article", dict(url=URL_1)
        )
        article_id = json_result["id"]

        result = self.json_from_api_get(
            "/user_article", other_args=dict(article_id=article_id)
        )

        assert "content" in result
        assert "translations" in result

    def test_article_from_unsupported_language(self):
        response = self.response_from_api_post(
            "/find_or_create_article", dict(url=URL_2)
        )
        assert response.status == "406 NOT ACCEPTABLE"
        print(response.data)

    def test_article_update(self):
        # Article is not starred initially
        json_result = self.json_from_api_post(
            "/find_or_create_article", dict(url=URL_1)
        )
        article_id = json_result["id"]

        result = self.json_from_api_get(
            "/user_article", other_args=dict(article_id=article_id)
        )
        assert not result["starred"]

        # Make starred
        self.api_post(
            f"/user_article", formdata=dict(article_id=article_id, starred="True")
        )

        # Article should be starred
        result = self.json_from_api_get(
            "/user_article", other_args=dict(article_id=article_id)
        )
        assert result["starred"]

        # Make liked
        self.api_post(
            f"/user_article", formdata=dict(article_id=article_id, liked="True")
        )

        # Article should be both liked and starred
        result = self.json_from_api_get(
            "/user_article", other_args=dict(article_id=article_id)
        )
        assert result["starred"]
        assert result["liked"]

        # Article un-starred
        self.api_post(
            f"/user_article", formdata=dict(article_id=article_id, starred="False")
        )

        # Article is not starred anymore
        result = self.json_from_api_get(
            "/user_article", other_args=dict(article_id=article_id)
        )
        assert not result["starred"]
