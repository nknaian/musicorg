from flask import redirect, url_for, flash
from flask.globals import request

from albumcollections.spotify import spotify_user
from albumcollections.spotify.spotify_user import SpotifyUserAuthFailure

from . import bp


"""USER INTERFACE ROUTES"""


@bp.route('/user/login', methods=['GET', 'POST'])
def login():
    # Attempt to get user id. This will trigger spotify authentication
    # the first time around, and second time have no side effect
    spotify_user.get_user_id()

    flash(f"Hello {spotify_user.get_user_display_name()}! You are now logged in through your Spotify account.",
          "success")

    return redirect(url_for('main.index'))


@bp.route('/user/logout', methods=['POST'])
def logout():
    spotify_user.logout()

    flash("You are now logged out.", "warning")

    # Send user back to main page after logging out
    return redirect(url_for('main.index'))


"""EXTERNAL AUTHENTICATION CALLBACK ROUTES"""


@bp.route('/sp_auth_complete')
def sp_auth_complete():
    """Callback route for spotify authorization"""

    permission_granted = False

    # User granted permission
    if request.args.get("code"):
        permission_granted = True

        # Save their authorization code
        spotify_user.auth_new_user(request.args.get("code"))

    if permission_granted:
        return redirect(url_for('user.login'))
    else:
        return url_for('main.index')


"""EXCEPTION HANDLER ROUTES"""


@bp.app_errorhandler(SpotifyUserAuthFailure)
def handle_external_auth_exception(e):
    return redirect(e.auth_url)
