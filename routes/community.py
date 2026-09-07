import os
import uuid

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from werkzeug.utils import secure_filename

from extensions import db

from models.community import (
    CommunityComment,
    CommunityLike,
    CommunityPost,
    CommunityPostImage,
)

from services.auth_service import (
    get_logged_in_user,
)

from utils.decorators import login_required


community_bp = Blueprint(
    "community",
    __name__
)


# ============================================================
# EINSTELLUNGEN
# ============================================================

ALLOWED_CATEGORIES = {
    "Erfolg",
    "Motivation",
    "Gedanke",
    "Herausforderung",
}


ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}


MAX_IMAGE_SIZE = (
    5 * 1024 * 1024
)


# ============================================================
# HILFSFUNKTIONEN FÜR BILDER
# ============================================================

def get_upload_folder():

    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "community",
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    return upload_folder


def allowed_image(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return (
        extension
        in ALLOWED_IMAGE_EXTENSIONS
    )


def save_community_image(file):

    if not file:
        return None, None

    if not file.filename:
        return None, None


    if not allowed_image(
        file.filename
    ):

        return (
            None,
            "Erlaubt sind nur JPG, JPEG, PNG und WEBP."
        )


    original_filename = secure_filename(
        file.filename
    )


    extension = (
        original_filename
        .rsplit(".", 1)[1]
        .lower()
    )


    new_filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )


    upload_folder = get_upload_folder()

    file_path = os.path.join(
        upload_folder,
        new_filename
    )


    file.save(
        file_path
    )


    # Dateigröße nach dem Speichern kontrollieren

    file_size = os.path.getsize(
        file_path
    )


    if file_size > MAX_IMAGE_SIZE:

        os.remove(
            file_path
        )

        return (
            None,
            "Das Bild darf maximal 5 MB groß sein."
        )


    return (
        new_filename,
        None
    )


def delete_community_image(
    filename
):

    if not filename:
        return


    file_path = os.path.join(
        get_upload_folder(),
        filename
    )


    if os.path.isfile(
        file_path
    ):

        os.remove(
            file_path
        )


# ============================================================
# COMMUNITY ANZEIGEN
# ============================================================

@community_bp.route(
    "/community",
    methods=["GET"]
)
def community():

    posts = (
        CommunityPost.query
        .order_by(
            CommunityPost.created_at.desc()
        )
        .all()
    )


    current_user = get_logged_in_user()

    liked_post_ids = set()


    if current_user:

        likes = (
            CommunityLike.query
            .filter_by(
                user_id=current_user.id
            )
            .all()
        )


        liked_post_ids = {
            like.post_id
            for like in likes
        }


    return render_template(
        "community.html",
        posts=posts,
        liked_post_ids=liked_post_ids,
        error=request.args.get(
            "error"
        ),
    )


# ============================================================
# BEITRAG ERSTELLEN
# ============================================================

@community_bp.route(
    "/community/posts",
    methods=["POST"]
)
@login_required
def create_post():

    title = request.form.get(
        "title",
        ""
    ).strip()


    content = request.form.get(
        "content",
        ""
    ).strip()


    category = request.form.get(
        "category",
        "Gedanke"
    ).strip()


    image_file = request.files.get(
        "image"
    )


    if (
        category
        not in ALLOWED_CATEGORIES
    ):

        category = "Gedanke"


    if (
        len(title) < 3
        or len(title) > 120
    ):

        return redirect(
            url_for(
                "community.community",
                error=(
                    "Dein Titel sollte zwischen "
                    "3 und 120 Zeichen lang sein."
                ),
            )
        )


    # Ein Beitrag braucht Text ODER ein Bild.

    if (
        not content
        and (
            not image_file
            or not image_file.filename
        )
    ):

        return redirect(
            url_for(
                "community.community",
                error=(
                    "Füge bitte einen Text "
                    "oder ein Bild zu deinem Beitrag hinzu."
                ),
            )
        )


    if len(content) > 2000:

        return redirect(
            url_for(
                "community.community",
                error=(
                    "Dein Beitrag darf maximal "
                    "2.000 Zeichen lang sein."
                ),
            )
        )


    image_filename = None


    if (
        image_file
        and image_file.filename
    ):

        (
            image_filename,
            image_error
        ) = save_community_image(
            image_file
        )


        if image_error:

            return redirect(
                url_for(
                    "community.community",
                    error=image_error,
                )
            )


    post = CommunityPost(
        title=title,
        content=content,
        category=category,
        user_id=g.current_user.id,
    )


    db.session.add(
        post
    )

    db.session.flush()


    if image_filename:

        post_image = (
            CommunityPostImage(
                filename=image_filename,
                post_id=post.id,
            )
        )

        db.session.add(
            post_image
        )


    db.session.commit()


    return redirect(
        url_for(
            "community.community",
            _anchor=f"post-{post.id}"
        )
    )


# ============================================================
# LIKE / UNLIKE
# ============================================================

@community_bp.route(
    "/community/posts/<int:post_id>/like",
    methods=["POST"]
)
@login_required
def toggle_like(post_id):

    post = db.session.get(
        CommunityPost,
        post_id
    )


    if not post:
        abort(404)


    existing_like = (
        CommunityLike.query
        .filter_by(
            post_id=post.id,
            user_id=g.current_user.id,
        )
        .first()
    )


    if existing_like:

        db.session.delete(
            existing_like
        )

    else:

        like = CommunityLike(
            post_id=post.id,
            user_id=g.current_user.id,
        )

        db.session.add(
            like
        )


    db.session.commit()


    return redirect(
        url_for(
            "community.community",
            _anchor=f"post-{post.id}"
        )
    )


# ============================================================
# KOMMENTAR ERSTELLEN
# ============================================================

@community_bp.route(
    "/community/posts/<int:post_id>/comments",
    methods=["POST"]
)
@login_required
def create_comment(post_id):

    post = db.session.get(
        CommunityPost,
        post_id
    )


    if not post:
        abort(404)


    content = request.form.get(
        "content",
        ""
    ).strip()


    image_file = request.files.get(
        "image"
    )


    # Kommentar braucht Text ODER Bild.

    if (
        not content
        and (
            not image_file
            or not image_file.filename
        )
    ):

        return redirect(
            url_for(
                "community.community",
                error=(
                    "Ein Kommentar braucht "
                    "einen Text oder ein Bild."
                ),
                _anchor=f"post-{post.id}"
            )
        )


    if len(content) > 1000:

        return redirect(
            url_for(
                "community.community",
                error=(
                    "Ein Kommentar darf maximal "
                    "1.000 Zeichen lang sein."
                ),
                _anchor=f"post-{post.id}"
            )
        )


    image_filename = None


    if (
        image_file
        and image_file.filename
    ):

        (
            image_filename,
            image_error
        ) = save_community_image(
            image_file
        )


        if image_error:

            return redirect(
                url_for(
                    "community.community",
                    error=image_error,
                    _anchor=f"post-{post.id}"
                )
            )


    comment = CommunityComment(
        content=content,
        image_filename=image_filename,
        post_id=post.id,
        user_id=g.current_user.id,
    )


    db.session.add(
        comment
    )

    db.session.commit()


    return redirect(
        url_for(
            "community.community",
            _anchor=f"post-{post.id}"
        )
    )


# ============================================================
# EIGENEN KOMMENTAR LÖSCHEN
# ============================================================

@community_bp.route(
    "/community/comments/<int:comment_id>/delete",
    methods=["POST"]
)
@login_required
def delete_comment(
    comment_id
):

    comment = db.session.get(
        CommunityComment,
        comment_id
    )


    if not comment:
        abort(404)


    if (
        comment.user_id
        != g.current_user.id
    ):

        abort(403)


    # Post-ID vor dem Löschen merken,
    # damit wir anschließend wieder
    # zum richtigen Beitrag springen.

    post_id = comment.post_id


    if comment.image_filename:

        delete_community_image(
            comment.image_filename
        )


    db.session.delete(
        comment
    )

    db.session.commit()


    return redirect(
        url_for(
            "community.community",
            _anchor=f"post-{post_id}"
        )
    )


# ============================================================
# EIGENEN BEITRAG LÖSCHEN
# ============================================================

@community_bp.route(
    "/community/posts/<int:post_id>/delete",
    methods=["POST"]
)
@login_required
def delete_post(post_id):

    post = db.session.get(
        CommunityPost,
        post_id
    )


    if not post:
        abort(404)


    if (
        post.user_id
        != g.current_user.id
    ):

        abort(403)


    # Beitragsbild löschen

    if (
        post.image
        and post.image.filename
    ):

        delete_community_image(
            post.image.filename
        )


    # Bilder aus Kommentaren löschen

    for comment in post.comments:

        if comment.image_filename:

            delete_community_image(
                comment.image_filename
            )


    db.session.delete(
        post
    )

    db.session.commit()


    # Der Beitrag existiert danach nicht mehr,
    # deshalb können wir hier nicht mehr
    # zu #post-ID springen.

    return redirect(
        url_for(
            "community.community"
        )
    )