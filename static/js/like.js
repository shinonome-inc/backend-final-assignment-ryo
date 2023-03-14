const likeBtns = document.querySelectorAll(".like-btn");
const unlikeBtns = document.querySelectorAll(".unlike-btn");

const getCookie = name => {
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";").map(cookie => cookie.trim());
        for (let i = 0; i < cookies.length; i++) {
            if (cookies[i].startsWith(name + "=")) {
                return cookies[i].substring(name.length + 1);
            }
        }
    }
    return null;
};
const csrftoken = getCookie("csrftoken");

if (likeBtns) {
    likeBtns.forEach(likeBtn => {
        likeBtn.addEventListener("click", () => {
            const url = likeBtn.getAttribute("data-url");
            fetch(url, { method: "POST", headers: { "X-CSRFToken": csrftoken } })
                .then(response => response.json())
                .then(data => {
                    const likeNum = likeBtn.parentNode.querySelector(".like-num");
                    likeNum.textContent = data.likes;
                    likeBtn.style.display = "none";
                    likeBtn.nextElementSibling.style.display = "";
                });
        });
    });
}

if (unlikeBtns) {
    unlikeBtns.forEach(unlikeBtn => {
        unlikeBtn.addEventListener("click", () => {
            const url = unlikeBtn.getAttribute("data-url");
            fetch(url, { method: "POST", headers: { "X-CSRFToken": csrftoken } })
                .then(response => response.json())
                .then(data => {
                    const likeNum = unlikeBtn.parentNode.querySelector(".like-num");
                    likeNum.textContent = data.likes;
                    unlikeBtn.style.display = "none";
                    unlikeBtn.previousElementSibling.style.display = "";
                });
        });
    });
}
