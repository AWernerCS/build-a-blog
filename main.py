import os
import webapp2
import jinja2
import google

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
    def render_newPost(self, title="", body="", error="", postCount=""):
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_newPost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Post(title = title, body=body)
            a.put()
            self.redirect("/blog/"+str(a.key().id()))
        else:
            error = "We need both a title and a body!"
            self.render_newPost(title, body, error)

        # If cleaning is needed:
        # db.delete(db.Query())

class ViewPostHandler(Handler):
    def render_post(self, id):
        self.render("singlepost.html", post = Post.get_by_id(int(id)))

    def get(self, id):
        self.render_post(id=id)

class Blog(Handler):
    def render_blog(self, page, title="", body="", error="", postCount=""):
        userOffset = 0
        page = int(page)
        if page > 1:
            userOffset = (page - 1)*5
        posts = get_posts(5,userOffset)

        next = page + 1
        previous = page - 1

        self.render("blog.html", title=title, body=body, error=error, posts=posts, next=next, previous=previous, offset=userOffset, limit=5)

    def get(self):
        if self.request.GET.get('page'):
            self.render_blog(self.request.GET.get('page'))
        else:
            self.render_blog(0)

def get_posts(limit, offset):
    return db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT %d OFFSET %d" % (limit,offset))

app = webapp2.WSGIApplication([('/newpost', NewPost),
                               ('/blog', Blog),
                               webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
                               ], debug=True)
