document.addEventListener('DOMContentLoaded', function() {
    let previousUrl = decodeURIComponent(document.cookie.replace(/(?:(?:^|.*;\s*)previousUrl\s*\=\s*([^;]*).*$)|^.*$/, "$1"));
    document.getElementById('previous_url').value = previousUrl;
});
