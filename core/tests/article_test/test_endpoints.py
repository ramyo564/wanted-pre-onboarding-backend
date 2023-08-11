import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
pytestmark = pytest.mark.django_db


class TestArticleEndpoints:
    # create post
    def test_create_post(self, article_factory):
        register_endpoint = "/api/user/register/"
        login_endpoint = "/api/user/login/"

        # Register the user
        client = APIClient()
        registration_data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        registration_response = client.post(register_endpoint, registration_data)
        if registration_response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            redirect_url = registration_response.url
            response = client.post(redirect_url, registration_data, format="json")
        else:
            response = registration_response

        assert response.status_code == status.HTTP_201_CREATED

        # Login with the registered user
        login_data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        login_response = client.post(login_endpoint, login_data)
        if login_response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            redirect_url = login_response.url
            response = client.post(redirect_url, login_data, format="json")
        else:
            response = login_response

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data

        # print(f"access_token : {response.data['access_token']}")

        # Create article
        access_token = response.data['access_token']
        article_endpoint = "/api/article/create_post/"
        data = {
            "title": "Test Article",
            "content": "This is a test article.",
        }
        article_response = client.post(
            article_endpoint,
            data,
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        if article_response.status_code == status.HTTP_301_MOVED_PERMANENTLY:
            redirect_url = article_response.url
            response = client.post(redirect_url, data, format="json")

        else:
            response = article_response

        assert article_response.status_code == status.HTTP_201_CREATED

        # Update the article using PATCH method with id
        article_id = article_response.data['id']
        update_endpoint = f"/api/article/{article_id}/update_article/"
        update_data = {
            "title": "Updated Test Article",
            "content": "This is the updated test article content.",
        }
        update_response = client.patch(
            update_endpoint,
            update_data,
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["title"] == update_data["title"]
        assert update_response.data["content"] == update_data["content"]

        # Delete the article using Delete method with id
        article_id = article_response.data['id']
        delete_endpoint = f"/api/article/{article_id}/delete_article/"

        delete_response = client.delete(
            delete_endpoint,
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT


class GetArticleList:

    # Get Article list with pagination
    def test_search_articles_list_with_pagination(self, article_factory):
        url = "/api/get_article/"
        client = APIClient()

        article_factory.create_batch(3)
        print(article_factory)
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # test pagination
        assert 'results' in response.data
        assert len(response.data['results']) == 2

        # test next page
        next_page_url = response.data['next']
        response = client.get(next_page_url)
        assert len(response.data['results']) == 1

    # Get Article with id
    def test_retrieve_specific_article(self, article_factory):
        # ArticleFactory를 사용하여 테스트 데이터 생성
        article = article_factory(title="Specific Article", content="Specific Content")

        url = reverse('get_article', args=[article.id])
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # 특정 게시글을 조회한 결과 확인
        assert response.data['title'] == "Specific Article"
        assert response.data['content'] == "Specific Content"
