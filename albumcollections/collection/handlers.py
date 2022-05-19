from flask import render_template, request, url_for, jsonify, current_app
import json

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_interface as spotify_iface
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.user import is_user_logged_in, get_user_playback_playlist_id, set_user_playback_playlist_id
from albumcollections.errors.exceptions import albumcollectionsError

from . import bp


"""CONSTANTS"""


PLAYBACK_PLAYLIST_NAME_PREFIX = "Collection Playback"
PLAYBACK_PLAYLIST_DESCRIPTION = \
    "This playlist was automatically generated by https://albumcollections.herokuapp.com"


"""ROUTE HANDLERS"""


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    # Get a spotify interface to use based on whether user is logged in
    try:
        if is_user_logged_in():
            sp_interface = spotify_user_iface.SpotifyUserInterface()
        else:
            sp_interface = spotify_iface.SpotifyInterface()
    except Exception as e:
        raise albumcollectionsError(f"Failed to create spotify interface: {e}", url_for('main.index'))

    # Get collection based on the playlist id
    try:
        collection = sp_interface.get_collection(playlist_id)

    except Exception as e:
        raise albumcollectionsError(f"Failed to load collection {playlist_id}: {e}", url_for('main.index'))

    return render_template('collection/index.html', collection=collection)


@bp.route('/collection/remove_album', methods=['POST'])
def remove_album():
    """Interface to remove an album from the collection playlist
    """
    # POST request
    if request.method == 'POST':
        # Get values from post request
        playlist_id = request.form["playlist_id"]
        album_id = request.form["album_id"]

        # Initialize response dict
        response_dict = {"success": True, "exception": None}

        # Try removing the requested album
        try:
            spotify_user_iface.SpotifyUserInterface().remove_album_from_playlist(playlist_id, album_id)
        except Exception as e:
            current_app.logger.error(f"Failed to remove album {album_id} from playlist {playlist_id}: {e}")
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)


@bp.route('/collection/get_devices', methods=['POST'])
def get_devices():
    """Interface to get the spotify player devices that are
    available to play on currently.
    """
    if request.method == 'POST':
        # Initialize response dict
        response_dict = {"exception": None, "devices": None}

        try:
            response_dict["devices"] = spotify_user_iface.SpotifyUserInterface().get_devices()
        except Exception as e:
            response_dict["exception"] = str(e)

    return jsonify(response_dict)


@bp.route('/collection/play_collection', methods=['POST'])
def play_collection():
    """Interface to play a collection
    """
    # POST request
    if request.method == 'POST':
        # Get data from post request
        data = json.loads(request.form["data"])
        playlist_id = data["playlist_id"]
        device_id = data["device_id"]
        start_album_id = data["start_album_id"]
        shuffle_albums = data["shuffle_albums"]

        # Initialize response dict
        response_dict = {"played": True, "exception": None, "devices": None}

        try:
            # Get spotify user
            spotify_user = spotify_user_iface.SpotifyUserInterface()

            # Get the collection
            collection = spotify_user.get_collection(playlist_id)

            # Remove the last playback playlist for the user
            last_playback_playlist_id = get_user_playback_playlist_id()
            if last_playback_playlist_id is not None and spotify_user.playlist_exists(last_playback_playlist_id):
                spotify_user.remove_playlist(last_playback_playlist_id)

            # Create the new playback playlist for the user
            new_playback_playlist = spotify_user.create_playlist(
                f"{PLAYBACK_PLAYLIST_NAME_PREFIX}: {collection.name}",
                PLAYBACK_PLAYLIST_DESCRIPTION
            )
            set_user_playback_playlist_id(new_playback_playlist.id)

            # Play the collection useing the playback playlist
            spotify_user.play_collection(
                collection,
                start_album_id,
                shuffle_albums,
                new_playback_playlist,
                device_id=device_id
            )

        except Exception as e:
            current_app.logger.error(f"Failed to play collection {playlist_id}: {e}")
            response_dict["played"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)


@bp.route('/collection/reorder_collection', methods=['POST'])
def reorder_collection():
    """Interface to reorder a collection
    """
    # POST request
    if request.method == 'POST':
        # Get data from post request
        data = json.loads(request.form["data"])
        playlist_id = data["playlist_id"]
        moved_album_id = data['moved_album_id']
        next_album_id = data['next_album_id']

        # Initialize response dict
        response_dict = {"success": True, "exception": None}

        try:
            spotify_user_iface.SpotifyUserInterface().reorder_collection(playlist_id, moved_album_id, next_album_id)
        except Exception as e:
            current_app.logger.error(f"Failed to reorder collection {playlist_id}: {e}")
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)
