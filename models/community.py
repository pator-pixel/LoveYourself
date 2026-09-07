from datetime import datetime

from extensions import db


# ============================================================
# COMMUNITY BEITRAG
# ============================================================

class CommunityPost(db.Model):
    __tablename__ = "community_post"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(120),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False,
        default=""
    )

    category = db.Column(
        db.String(40),
        nullable=False,
        default="Gedanke"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    author = db.relationship(
        "User",
        backref=db.backref(
            "community_posts",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    likes = db.relationship(
        "CommunityLike",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan",
    )

    comments = db.relationship(
        "CommunityComment",
        backref="post",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="CommunityComment.created_at.asc()",
    )

    image = db.relationship(
        "CommunityPostImage",
        backref="post",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def formatted_created_at(self):
        if not self.created_at:
            return ""

        return self.created_at.strftime(
            "%d.%m.%Y · %H:%M Uhr"
        )


# ============================================================
# BEITRAGSBILD
# Separate Tabelle, damit deine bestehende Datenbank
# NICHT gelöscht oder migriert werden muss.
# ============================================================

class CommunityPostImage(db.Model):
    __tablename__ = "community_post_image"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("community_post.id"),
        nullable=False,
        unique=True
    )


# ============================================================
# LIKE
# ============================================================

class CommunityLike(db.Model):
    __tablename__ = "community_like"

    __table_args__ = (
        db.UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_community_like_post_user"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("community_post.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


# ============================================================
# KOMMENTAR
# ============================================================

class CommunityComment(db.Model):
    __tablename__ = "community_comment"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    content = db.Column(
        db.Text,
        nullable=False,
        default=""
    )

    image_filename = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("community_post.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    author = db.relationship(
        "User",
        backref=db.backref(
            "community_comments",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    @property
    def formatted_created_at(self):
        if not self.created_at:
            return ""

        return self.created_at.strftime(
            "%d.%m.%Y · %H:%M Uhr"
        )