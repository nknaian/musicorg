/* Module Variables */

let playlist_id;

/* Functions */

function init(play_id) {
    playlist_id = play_id
}

document.querySelectorAll('.remove_album').forEach(item => {
    item.addEventListener("click", function() {
        album_id = this.closest('.div_spotify_item').getAttribute("data-album_id")
        album_name = this.closest('.div_spotify_item').getAttribute("data-album_name")

        if (confirm(`Are you sure you want to remove ${album_name} from the collection?`)) {
            $.post('/collection/remove_album', {
                playlist_id: playlist_id,
                album_id: album_id
            }).done(function (response) {
                if (response["success"]) {
                    $(`#${album_id}`).hide()
                }
                else {
                    alert(`Sorry, failed to remove album.\n\n${response["exception"]}`)
                }
            }).fail(function() {
                alert("Sorry, a server failure occured.")
            });
        }
    });
})
