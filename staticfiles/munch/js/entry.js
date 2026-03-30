//Source: Claude Sonnet 4.6
//Date Accessed: Mon, March 30, 2026
"use strict";

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function refreshLike(entry, img) {
  const authorSerial = entry.dataset.authorSerial;
  const entrySerial = entry.dataset.entrySerial;
  const like_count = entry.querySelector(".likes-count");

  fetch(`/api/authors/${authorSerial}/entries/${entrySerial}/likes/`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      like_count.textContent = data.count;
      if (data.user_liked === true) {
        entry.dataset.liked = "true";
        img.src = img.src.replace('like_no_fill.png', 'like_fill.png');
      } else {
        entry.dataset.liked = "false";
        img.src = img.src.replace('like_fill.png', 'like_no_fill.png');
      }
    });
}

window.addEventListener("load", function () {
  const entries = document.querySelectorAll(".entry-card");
  const csrftoken = getCookie('csrftoken');

  entries.forEach(entry => {
    const like_button = entry.querySelector(".like-button");
    const img = entry.querySelector(".like-icon");
    const entryFqid = entry.dataset.entryFqid;
    const currentAuthorSerial = entry.dataset.currentAuthorSerial;

    refreshLike(entry, img);

    like_button.addEventListener("click", function () {
      const data = { object: entryFqid };

      if (entry.dataset.liked === "false") {
        fetch(`/api/authors/${currentAuthorSerial}/liked/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": csrftoken,
          },
          credentials: "same-origin",
          body: JSON.stringify(data),
        })
          .then(response => response.json())
          .then(() => refreshLike(entry, img));

      } else if (entry.dataset.liked === "true") {
        fetch(`/api/authors/${currentAuthorSerial}/liked/`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": csrftoken,
          },
          credentials: "same-origin",
          body: JSON.stringify(data),
        })
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}`);
            }
          })
          .then(() => refreshLike(entry, img));
      }
    });
  });
});