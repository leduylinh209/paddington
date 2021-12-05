import concurrent.futures

import requests
from django.core.exceptions import SuspiciousOperation
from django.views.generic import TemplateView
from rest_framework.response import Response as APIResponse
from rest_framework.views import APIView

from service.facebook.models import Comment


class CommentView(TemplateView):

    feed_api = "https://graph.facebook.com/v4.0/{p_id}/feed"
    comments_api = "https://graph.facebook.com/v4.0/{p_id}/comments"
    template_name = "no-reply-comments.html"
    exclude_id = "481355419298155"

    def get_posts(self, fb_api, p_id, access_token):
        posts = []
        resp = requests.get(fb_api.format(p_id=p_id),
                            params={"access_token": access_token})
        page = resp.json()

        if 'data' not in page:
            raise SuspiciousOperation(page)

        posts = page['data']

        while True:
            next = page.get('paging') and page['paging'].get('next')
            if next is None:
                break

            resp = requests.get(next)
            page = resp.json()
            posts.extend(page['data'])

        return posts

    def get_context_data(self, **kwargs):
        page_id = kwargs['page_id']
        access_token = self.request.GET.get('access_token')
        exclude_id = self.request.GET.get('exclude_id') or self.exclude_id

        posts = self.get_posts(self.feed_api, page_id, access_token)
        posts_dict = {
            post['id']: {**post, 'no_reply_comments': []}
            for post in posts
        }

        comments_rank1 = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_post = {
                executor.submit(self.get_posts, self.comments_api, post['id'], access_token): post
                for post in posts
            }
            for future in concurrent.futures.as_completed(future_to_post):
                post = future_to_post[future]
                try:
                    comments = filter(lambda c: (c.get('from') and c['from']['id']) != exclude_id,
                                      future.result())
                except Exception as exc:
                    print('%r generated an exception: %s' % (comment, exc))
                else:
                    comments_rank1[post['id']] = comments

        no_reply_comments = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_comment = {
                executor.submit(self.get_posts, self.comments_api, comment['id'], access_token): (post_id, comment)
                for post_id, rank1_comments in comments_rank1.items()
                for comment in rank1_comments
                if not Comment.objects.filter(comment_id=comment['id']).exists()
            }

            for future in concurrent.futures.as_completed(future_to_comment):
                post_id, comment = future_to_comment[future]
                try:
                    comments_rank2 = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (comment, exc))
                else:
                    if not comments_rank2:
                        posts_dict[post_id]['no_reply_comments'].append(comment)

        return {
            'title': "No reply comments for page #{}".format(page_id),
            'posts': sorted(filter(lambda p: p['no_reply_comments'], posts_dict.values()),
                            key=lambda p: -len(p['no_reply_comments'])),
        }


class CommentAPI(APIView):

    def post(self, request, *args, **kwargs):
        comment_id = request.data.get('comment_id')
        if comment_id:
            Comment.objects.get_or_create(comment_id=comment_id)
            return APIResponse(comment_id)
        return APIResponse(status=400)


comment = CommentView.as_view()
comment_api = CommentAPI.as_view()
