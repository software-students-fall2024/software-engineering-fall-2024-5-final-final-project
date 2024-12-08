from datetime import datetime, timezone
from bson import ObjectId


class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data):
        user = User(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
        )
        user.created_at = data.get("created_at", datetime.now(timezone.utc))
        return user


class Post:
    TITLE_MIN_LENGTH = 1
    TITLE_MAX_LENGTH = 200
    CONTENT_MIN_LENGTH = 1
    CONTENT_MAX_LENGTH = 50000
    MAX_TAGS = 10
    TAG_MAX_LENGTH = 50

    def __init__(self, title, content, author_id, tags=None):
        self.validate_title(title)
        self.validate_content(content)
        self.validate_tags(tags)

        self.title = title
        self.content = content
        self.author_id = author_id
        self.tags = tags or []
        self.comments = []
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def update(self, title=None, content=None, tags=None):
        if title is not None:
            self.validate_title(title)
            self.title = title
        if content is not None:
            self.validate_content(content)
            self.content = content
        if tags is not None:
            self.validate_tags(tags)
            self.tags = tags
        self.updated_at = datetime.now(timezone.utc)

    def add_comment(self, comment):
        self.comments.append(comment)

    @staticmethod
    def validate_title(title):
        if not title or len(title.strip()) < Post.TITLE_MIN_LENGTH:
            raise ValueError(
                f"Title must be at least {Post.TITLE_MIN_LENGTH} characters long"
            )
        if len(title) > Post.TITLE_MAX_LENGTH:
            raise ValueError(
                f"Title must not exceed {Post.TITLE_MAX_LENGTH} characters"
            )

    @staticmethod
    def validate_content(content):
        if not content or len(content.strip()) < Post.CONTENT_MIN_LENGTH:
            raise ValueError(
                f"Content must be at least {Post.CONTENT_MIN_LENGTH} characters long"
            )
        if len(content) > Post.CONTENT_MAX_LENGTH:
            raise ValueError(
                f"Content must not exceed {Post.CONTENT_MAX_LENGTH} characters"
            )

    @staticmethod
    def validate_tags(tags):
        if tags is None:
            return
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list")
        if len(tags) > Post.MAX_TAGS:
            raise ValueError(f"Number of tags must not exceed {Post.MAX_TAGS}")
        for tag in tags:
            if not isinstance(tag, str):
                raise ValueError("Tags must be strings")
            if len(tag) > Post.TAG_MAX_LENGTH:
                raise ValueError(
                    f"Tag length must not exceed {Post.TAG_MAX_LENGTH} characters"
                )

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "author_id": str(self.author_id),
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data):
        post = Post(
            title=data.get("title"),
            content=data.get("content"),
            author_id=ObjectId(data.get("author_id")),
            tags=data.get("tags", []),
        )
        if "created_at" in data:
            post.created_at = data["created_at"]
        if "updated_at" in data:
            post.updated_at = data["updated_at"]
        return post


class Comment:
    def __init__(self, content, author_username):
        self.content = content
        self.author_username = author_username
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "content": self.content,
            "author_username": str(self.author_username),
            "created_at": self.created_at,
        }
