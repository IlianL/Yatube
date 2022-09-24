from django.core.paginator import Paginator

POST_PER_PAGE: int = 10


def get_page(request, object_with_posts, posts_number=POST_PER_PAGE):
    """Функция-пагинатор"""
    paginator = Paginator(object_with_posts, posts_number)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
