const likeBtn = document.getElementById('like-btn');
const unlikeBtn = document.getElementById('unlike-btn');
const likeNumSpan = document.getElementById('like-num');

likeBtn.addEventListener('click', () => {
    const url = this.dataset.url;
    updateLikes(url);
});

unlikeBtn.addEventListener('click', () => {
    const url = this.dataset.url;
    updateLikes(url);
});

function updateLikes(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            likeNumSpan.innerHTML = data.likes;
        })
        .catch(error => console.log(error));
}
