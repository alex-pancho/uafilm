function openItem(id) {
    window.location.href = "/item/" + id;
}

function fetchM3U(playlist_id) {

    fetch(`/fetch_m3u/${playlist_id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            ua: navigator.userAgent,
            ref: document.referrer,
            lang: navigator.language
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === "exists") {
            if (confirm(data.message)) {
                // користувач нажав OK - перезаписати
                openItem(playlist_id);
            }
        } else {
            alert(data.message);
            openItem(playlist_id);
        }
    });
}