from datatrove.data import Document
from datatrove.pipeline.formatter.base import BaseFormatter


EXACT_LINE_MATCH = {
    ("".join(x.strip()) for x in ('press', 'english', 'your email address', 'notify me of followup comments via email',
         'this topic is now archived and is closed to further replies', 'pin it', 'wishlist', 'french',
         'view public profile',
         'leave a reply your email address will not be published required fields are marked', 'home',
         'skip navigation', 'view single post', 'sign in', 'last', 'report', 'page content',
         'subscribe to our newsletter', 'login', 'follow', 'linkedin', 'welcome', 'message', 'browse',
         'en',
         'create an account or sign in to comment', 'home page', 'your first name', 'pictures',
         'confirm password', 'leave a reply', 'archived', 'register', 'my profile',
         'join the conversation',
         'name', 'your email address will not be published required fields are marked',
         'no products in the cart', 'registration', 'next post →',
         'you will be able to leave a comment after signing in', 'email', 'pricing', 'bookmark us',
         'close',
         'your review', 'notify me of new posts by email', 'leave a comment', 'posts', 'share', 'fr',
         'help',
         'tags', 'your last name', 'last name', 'comments', 'contact form', 'postal code', 'this month',
         'facebook', 'you need to be a member in order to leave a comment', 'shop', '← previous post',
         'comment', 'no comment yet', 'post', 'blog', 'reviews', 'please sign in to comment',
         'first name',
         'licence agreement', 'there are no reviews yet',
         'please be aware that the content of this thread may be outdated and no longer applicable',
         'note your post will require moderator approval before it will be visible', 'logout',
         'already have an account sign in here sign in now', 'menu', 'contact', 'page controls',
         'store policy', 'this week', 'next', 'rate it', 'all time', 'view cart',
         'save my name email and website in this browser for the next time i comment',
         'you can post now and register later if you have an account sign in now to post with your account',
         'recent comments', 'password', 'click to close', 'recommended posts', 'click to post',
         'send us a message', 'previous', 'select', 'buy now', 'load more', 'please comment',
         'create an account', 'faq', 'members',
         'sign up for a new account in our community its easy register a new account'))}


class GopherRepetitionFilter(BaseFormatter):
    name = "⚞ Templated Lines"

    def format(self, doc: Document) -> str:
        pass
